"""
Immune System Worker

Background worker that consumes SYSTEM_ERROR events and orchestrates
triage + repair in the slow-path immune system.
📚 REQUIRED READING BEFORE MODIFICATION:
- BRAIN_USAGE_GUIDE.md
- AI_NATIVE_ARCHITECTURE_GUIDE.md
- LLM_AGENT_QUICKSTART.md
"""
from __future__ import annotations
import asyncio
import json
import logging
import os
import threading
import time
import weakref
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from statistics import mean
from typing import Any, Callable, Deque, Dict, Iterable, List, Optional, Tuple
from cachetools import LRUCache
from brain.utils import get_fact_window_seconds
from brain.core.contracts import EventType
from brain import nervous_system
from services import ai_provider
from brain.invariants.scorer import Scorer, Emotion
from brain.immune.memory_monitor import MemoryMonitor
from services.github_cortex_client import GitHubCortexClient, build_emotional_pr_body
logger = logging.getLogger(__name__)

@dataclass
class ResourceLimits:
    max_queue_size: int = 1000
    max_context_mb: int = 50
    max_history_events: int = 100
    batch_window_sec: int = 5
    max_batch_size: int = 10

@dataclass
class CrashContextPack:
    fingerprint: str
    tool_name: str
    error_type: str
    error_message: str
    stack_trace: str
    command: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)

@dataclass
class FactWindow:
    window_id: str
    collected_at: datetime
    facts: List[Tuple[str, str]]

class FactWindowBuffer:
    """Stores a rolling buffer of fact windows for replay tolerance."""

    def __init__(self, max_windows: int=2):
        self._buffer: Deque[FactWindow] = deque(maxlen=max_windows)

    def add_window(self, window: FactWindow) -> None:
        self._buffer.append(window)

    def get_recent_facts(self) -> List[Tuple[str, str, str]]:
        recent: List[Tuple[str, str, str]] = []
        for window in self._buffer:
            for domain, value in window.facts:
                recent.append((domain, value, window.window_id))
        return recent

    def get_latest_fact(self, domain: Optional[str]) -> Optional[Tuple[str, str, str]]:
        if not domain:
            return None
        for window in reversed(self._buffer):
            for fact_domain, fact_value in window.facts:
                if fact_domain == domain:
                    return (fact_domain, fact_value, window.window_id)
        return None

class TCellCache:
    """In-memory + database-backed cache for verified patches."""

    def __init__(self, db_connection=None, max_entries: int=512):
        self._cache = LRUCache(maxsize=max_entries)
        self._db_connection = db_connection

    async def check_immunity(self, fingerprint: str) -> Optional[Dict[str, Any]]:
        patch = self._cache.get(fingerprint)
        if patch:
            return patch
        if not self._db_connection:
            return None
        cursor = self._db_connection.cursor()
        cursor.execute('\n            SELECT patch_content, patch_type, verification_level\n            FROM golden_patches\n            WHERE fingerprint = ?\n              AND (expires_at IS NULL OR expires_at > CURRENT_TIMESTAMP)\n            ORDER BY verified_at DESC\n            LIMIT 1\n            ', (fingerprint,))
        row = cursor.fetchone()
        if not row:
            return None
        patch_payload = {'content': json.loads(row[0] if row and row[0] else '{}'), 'patch_type': row[1], 'verification_level': row[2]}
        self._cache[fingerprint] = patch_payload
        return patch_payload

    async def store_golden_patch(self, fingerprint: str, patch: Dict[str, Any]) -> None:
        self._cache[fingerprint] = patch
        if not self._db_connection:
            return
        cursor = self._db_connection.cursor()
        cursor.execute('\n            INSERT INTO golden_patches (\n                fingerprint,\n                patch_type,\n                patch_content,\n                verification_level,\n                verified_at,\n                verified_by,\n                success_count,\n                failure_count,\n                avg_apply_time_ms,\n                last_used,\n                created_at\n            ) VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP, ?, 0, 0, 0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)\n            ', (fingerprint, patch.get('patch_type', 'unknown'), json.dumps(patch.get('content')), patch.get('verification_level', 'SANDBOX'), patch.get('verified_by', 'immune_worker')))
        self._db_connection.commit()

class HeuristicHealer:
    """Deterministic repair heuristics (placeholder)."""

    async def try_fix(self, crash_report: Any) -> Optional[Dict[str, Any]]:
        return None

class AISynthesizer:
    """AI-driven patch synthesizer (placeholder)."""

    def __init__(self, nervous_system, ai_provider: Optional[Any]=None):
        self._nervous_system = nervous_system
        self._ai_provider = ai_provider

    async def generate_patch(self, context_pack: CrashContextPack) -> Optional[Dict[str, Any]]:
        return None

class RepairThrottler:
    """Tracks repeated failures and applies exponential backoff."""

    def __init__(self, base_backoff_sec: int=5, max_backoff_sec: int=3600):
        self._base_backoff_sec = base_backoff_sec
        self._max_backoff_sec = max_backoff_sec
        self._state: Dict[str, Dict[str, Any]] = {}

    async def should_attempt_repair(self, fingerprint: str) -> bool:
        state = self._state.get(fingerprint)
        if not state:
            return True
        backoff_until = state.get('backoff_until')
        if not backoff_until:
            return True
        return datetime.utcnow() >= backoff_until

    def record_failure(self, fingerprint: str) -> None:
        state = self._state.setdefault(fingerprint, {'failures': 0, 'backoff_until': None})
        state['failures'] += 1
        delay = min(self._base_backoff_sec * 2 ** (state.get('failures', 0) - 1), self._max_backoff_sec)
        state['backoff_until'] = datetime.utcnow() + timedelta(seconds=delay)

    def record_success(self, fingerprint: str) -> None:
        if fingerprint in self._state:
            self._state.pop(fingerprint, None)

class RepairBatcher:
    """Batch similar crash reports for AI synthesis."""

    def __init__(self, window_sec: int=5, max_batch: int=10):
        self._window_sec = window_sec
        self._max_batch = max_batch
        self._batch: List[Any] = []
        self._lock = asyncio.Lock()
        self._flush_task: Optional[asyncio.Task] = None

    async def add_to_batch(self, crash_report: Any, callback: Callable[[List[Any]], Any]) -> None:
        async with self._lock:
            self._batch.append(crash_report)
            if len(self._batch) >= self._max_batch:
                await self._flush(callback)
                return
            if not self._flush_task or self._flush_task.done():
                self._flush_task = asyncio.create_task(self._flush_after_window(callback))

    async def _flush_after_window(self, callback: Callable[[List[Any]], Any]) -> None:
        await asyncio.sleep(self._window_sec)
        async with self._lock:
            await self._flush(callback)

    async def _flush(self, callback: Callable[[List[Any]], Any]) -> None:
        if not self._batch:
            return
        batch = list(self._batch)
        self._batch.clear()
        await callback(batch)

class ImmuneSystemMetrics:
    """Tracks immune system performance metrics and persists snapshots."""

    def __init__(self, db_connection=None):
        self._db_connection = db_connection
        self._queue_overflow_count = 0
        self._patches_attempted = 0
        self._patches_successful = 0
        self._patches_failed = 0
        self._repair_times: List[float] = []
        self._sandbox_tests_run = 0
        self._sandbox_tests_passed = 0

    def record_pathogen_detected(self) -> None:
        return None

    def record_queue_overflow(self) -> None:
        self._queue_overflow_count += 1

    def record_repair_success(self, _repair_type: str, elapsed_ms: float) -> None:
        self._patches_attempted += 1
        self._patches_successful += 1
        self._repair_times.append(elapsed_ms)

    def record_repair_failure(self) -> None:
        self._patches_attempted += 1
        self._patches_failed += 1

    def record_sandbox_result(self, passed: bool) -> None:
        self._sandbox_tests_run += 1
        if passed:
            self._sandbox_tests_passed += 1

    def get_sandbox_accuracy(self) -> float:
        if self._sandbox_tests_run == 0:
            return 1.0
        return self._sandbox_tests_passed / self._sandbox_tests_run

    def get_memory_usage(self) -> int:
        # prefer memory monitor samples if available
        try:
            parent = getattr(self, 'memory_monitor', None)
            if parent:
                samples = parent.get_samples()
                if samples:
                    # return latest rss
                    return int(samples[-1][1])
        except Exception:
            pass
        # auto PR flag
        try:
            import resource
            usage = resource.getrusage(resource.RUSAGE_SELF)
            return int(getattr(usage, 'ru_maxrss', 0) * 1024)
        except Exception:
            return 0

    async def save_snapshot(self, queue_depth: int=0, active_repair_count: int=0) -> None:
        if not self._db_connection:
            return
        avg_repair_time = mean(self._repair_times) if self._repair_times else 0.0
        p95_repair_time = 0.0
        if self._repair_times:
            sorted_times = sorted(self._repair_times)
            index = max(int(len(sorted_times) * 0.95) - 1, 0)
            p95_repair_time = sorted_times[index]
        cursor = self._db_connection.cursor()
        cursor.execute('\n            INSERT INTO immune_metrics (\n                timestamp,\n                queue_depth,\n                queue_overflow_count,\n                memory_usage_bytes,\n                active_repair_count,\n                patches_attempted_hour,\n                patches_successful_hour,\n                patches_failed_hour,\n                avg_repair_time_ms,\n                p95_repair_time_ms,\n                sandbox_tests_run,\n                sandbox_tests_passed,\n                sandbox_accuracy_pct,\n                fever_active\n            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)\n            ', (datetime.utcnow().isoformat(), queue_depth, self._queue_overflow_count, self.get_memory_usage(), active_repair_count, self._patches_attempted, self._patches_successful, self._patches_failed, avg_repair_time, p95_repair_time, self._sandbox_tests_run, self._sandbox_tests_passed, self.get_sandbox_accuracy() * 100, 0))
        self._db_connection.commit()

class ContextPackBuilder:
    """Builds a constrained context pack for AI synthesis."""

    def __init__(self, max_history: int=100, max_size_bytes: int=50 * 1024 * 1024):
        self._max_history = max_history
        self._max_size_bytes = max_size_bytes

    async def build(self, crash_report: Any) -> CrashContextPack:
        stack_trace = getattr(crash_report, 'traceback', None) or getattr(crash_report, 'stack_trace', '')
        payload = CrashContextPack(fingerprint=getattr(crash_report, 'fingerprint', ''), tool_name=getattr(crash_report, 'tool_name', ''), error_type=getattr(crash_report, 'error_type', ''), error_message=getattr(crash_report, 'error_message', ''), stack_trace=stack_trace, command=getattr(crash_report, 'command', None), context=getattr(crash_report, 'context', {}) or {})
        serialized = json.dumps(payload.__dict__, default=str)
        if len(serialized.encode('utf-8')) > self._max_size_bytes:
            payload.context = {'warning': 'context truncated'}
        return payload

class ImmuneSystemWorker:
    """
    The autonomous "White Blood Cell" that consumes SYSTEM_ERROR events
    and orchestrates the repair pipeline in the background.
    """

    def __init__(self, nervous_system, limits: Optional[ResourceLimits]=None, db_connection=None):
        self.nervous_system = nervous_system
        self.limits = limits or ResourceLimits()
        self.db_connection = db_connection
        self.pathogen_queue: asyncio.Queue = asyncio.Queue(maxsize=self.limits.max_queue_size)
        # use weak references so finished tasks don't keep strong refs and grow memory
        self.active_repairs: weakref.WeakValueDictionary = weakref.WeakValueDictionary()
        self.tcell_cache = TCellCache(db_connection=db_connection)
        self.heuristic_healer = HeuristicHealer()
        self.ai_synthesizer = AISynthesizer(nervous_system)
        self.repair_throttler = RepairThrottler()
        self.repair_batcher = RepairBatcher(window_sec=self.limits.batch_window_sec, max_batch=self.limits.max_batch_size)
        self.metrics = ImmuneSystemMetrics(db_connection=db_connection)
        # memory monitor for snapshots
        try:
            self.memory_monitor = MemoryMonitor(interval=10, max_samples=360)
            self.memory_monitor.start()
        except Exception:
            self.memory_monitor = None
        # expose memory monitor to metrics for preferred sampling
        try:
            self.metrics.memory_monitor = self.memory_monitor
        except Exception:
            pass
        # scorer for coring
        try:
            self.scorer = Scorer()
        except Exception:
            self.scorer = None
        self.fact_refresh_interval = 15
        self.hash_drift_interval = 300  # 5 minutes
        self.fact_oracles: List[Callable[[], Iterable[Tuple[str, str]]]] = []
        self.fact_buffer = FactWindowBuffer(max_windows=2)
        self.active_fact_domain: Optional[str] = None
        self._auto_pr_enabled = os.environ.get('IMMUNE_AUTO_PR', '0') in ('1', 'true', 'True')
        self._worker_task: Optional[asyncio.Task] = None
        self._health_task: Optional[asyncio.Task] = None
        self._fact_task: Optional[asyncio.Task] = None
        self._running = False
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._loop_thread: Optional[threading.Thread] = None
        self._loop_ready = threading.Event()
        self.hash_drift_interval = 3600

    def _load_fact_refresh_interval(self) -> int:
        return get_fact_window_seconds(300)

    def start(self) -> None:
        if self._running:
            return
        self._ensure_loop()
        self._run_coroutine(self._start_async())

    def stop(self) -> None:
        if not self._running:
            return
        if self._loop and self._loop.is_running():
            future = self._run_coroutine(self._stop_async())
            try:
                future.result(timeout=5)
            except Exception:
                logger.exception('Immune worker shutdown timed out')
        if self._loop:
            self._loop.call_soon_threadsafe(self._loop.stop)
        if self._loop_thread:
            self._loop_thread.join(timeout=5)

    def _ensure_loop(self) -> None:
        if self._loop and self._loop.is_running():
            return

        def _runner():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            self._loop = loop
            self._loop_ready.set()
            loop.run_forever()
            loop.close()
        self._loop_thread = threading.Thread(target=_runner, name='immune-worker-loop', daemon=True)
        self._loop_thread.start()
        self._loop_ready.wait(timeout=5)

    def _run_coroutine(self, coro: asyncio.Future) -> asyncio.Future:
        if not self._loop:
            raise RuntimeError('Immune worker loop not initialized')
        return asyncio.run_coroutine_threadsafe(coro, self._loop)

    async def _start_async(self) -> None:
        if self._running:
            return
        self._running = True
        self.nervous_system.subscribe(EventType.SYSTEM_ERROR, self._on_pathogen_detected, brain_name='ImmuneSystem', priority=0)
        self._worker_task = asyncio.create_task(self._process_queue())
        self._health_task = asyncio.create_task(self._health_monitor())
        self._fact_task = asyncio.create_task(self._fact_heartbeat())
        logger.info('🦠 Immune System Worker: ONLINE')

    async def _stop_async(self) -> None:
        self._running = False
        tasks: Iterable[asyncio.Task] = [t for t in [self._worker_task, self._health_task, self._fact_task] if t]
        for task in tasks:
            task.cancel()
        for task in tasks:
            try:
                await task
            except asyncio.CancelledError:
                pass
        self.active_repairs.clear()
        logger.info('🦠 Immune System Worker: SHUTDOWN')

    def _on_pathogen_detected(self, event: Any) -> None:
        crash_report = event.payload.get('crash_report') if hasattr(event, 'payload') else None
        if not crash_report:
            logger.warning('Immune worker received SYSTEM_ERROR without crash_report')
            return
        try:
            self._run_coroutine(self._enqueue_pathogen(crash_report))
        except Exception:
            logger.exception('Failed to enqueue crash report')

    def register_fact_oracle(self, oracle: Callable[[], Iterable[Tuple[str, str]]]) -> None:
        """Register a fact oracle callable for the heartbeat."""
        self.fact_oracles.append(oracle)

    def set_active_fact_domain(self, domain: Optional[str]) -> None:
        """Set the active fact domain selected by the LLM."""
        self.active_fact_domain = domain

    def get_recent_fact_bundle(self) -> List[Tuple[str, str, str]]:
        """Return the last two windows of facts with window identifiers."""
        return self.fact_buffer.get_recent_facts()

    def get_active_fact_context(self) -> Optional[Dict[str, str]]:
        """Return the latest fact for the active domain, if available."""
        latest = self.fact_buffer.get_latest_fact(self.active_fact_domain)
        if not latest:
            return None
        domain, value, window_id = latest
        return {'domain': domain, 'value': value, 'window': window_id}

    async def _enqueue_pathogen(self, crash_report: Any) -> None:
        try:
            await asyncio.wait_for(self.pathogen_queue.put(crash_report), timeout=0.1)
            self.metrics.record_pathogen_detected()
        except asyncio.TimeoutError:
            self.metrics.record_queue_overflow()
            logger.warning('Immune queue overflow - dropping crash: %s', getattr(crash_report, 'fingerprint', 'unknown'))

    async def _fact_heartbeat(self) -> None:
        while self._running:
            try:
                await self._refresh_fact_bundle()
            except Exception:
                logger.exception('Fact heartbeat refresh failed')
            await asyncio.sleep(self.fact_refresh_interval)

    async def _refresh_fact_bundle(self) -> None:
        facts: List[Tuple[str, str]] = []
        for oracle in self.fact_oracles:
            try:
                oracle_facts = list(oracle())
            except Exception:
                logger.exception('Fact oracle failed')
                continue
            facts.extend(oracle_facts)
        window_start = int(time.time() // self.fact_refresh_interval * self.fact_refresh_interval)
        window_id = datetime.utcfromtimestamp(window_start).isoformat() + 'Z'
        self.fact_buffer.add_window(FactWindow(window_id=window_id, collected_at=datetime.utcnow(), facts=facts))

    async def _process_queue(self) -> None:
        while self._running:
            try:
                crash_report = await self.pathogen_queue.get()
                fingerprint = getattr(crash_report, 'fingerprint', None)
                if fingerprint in self.active_repairs:
                    continue
                if fingerprint and (not await self.repair_throttler.should_attempt_repair(fingerprint)):
                    continue
                repair_task = asyncio.create_task(self._tiered_repair(crash_report))
                if fingerprint:
                    self.active_repairs[fingerprint] = repair_task
                    repair_task.add_done_callback(lambda _: self.active_repairs.pop(fingerprint, None))
            except Exception:
                logger.exception('Immune worker error')
                await asyncio.sleep(1)

    async def _tiered_repair(self, crash_report: Any) -> None:
        start_time = time.perf_counter()
        fingerprint = getattr(crash_report, 'fingerprint', None)
        try:
            if fingerprint:
                patch = await self.tcell_cache.check_immunity(fingerprint)
                if patch and await self._apply_known_patch(crash_report, patch):
                    elapsed_ms = (time.perf_counter() - start_time) * 1000
                    self.metrics.record_repair_success('tcell', elapsed_ms)
                    self.repair_throttler.record_success(fingerprint)
                    return
            patch = await self.heuristic_healer.try_fix(crash_report)
            if patch and await self._verify_and_apply(crash_report, patch, 'heuristic'):
                elapsed_ms = (time.perf_counter() - start_time) * 1000
                self.metrics.record_repair_success('heuristic', elapsed_ms)
                if fingerprint:
                    self.repair_throttler.record_success(fingerprint)
                return
            await self.repair_batcher.add_to_batch(crash_report, self._ai_repair_callback)
        except Exception:
            if fingerprint:
                self.repair_throttler.record_failure(fingerprint)
            self.metrics.record_repair_failure()
            logger.exception('Repair failed for %s', fingerprint)

    async def _ai_repair_callback(self, batch: List[Any]) -> None:
        for crash_report in batch:
            fingerprint = getattr(crash_report, 'fingerprint', None)
            try:
                context_pack = await self._build_context_pack(crash_report)
                patch = await self.ai_synthesizer.generate_patch(context_pack)
                if patch:
                    # compute coring score if scorer available
                    try:
                        invariants = patch.get('invariants', []) if isinstance(patch, dict) else []
                        demographic = patch.get('demographic') if isinstance(patch, dict) else None
                        emotion = Emotion.ANXIOUS if getattr(crash_report, 'tool_name', '').lower().startswith('payment') else Emotion.NEUTRAL
                        score = self.scorer.score(invariants=invariants, demographic=demographic, emotion=emotion) if self.scorer else 0.0
                        patch['_coring_score'] = score
                    except Exception:
                        patch['_coring_score'] = 0.0

                    if await self._verify_and_apply(crash_report, patch, 'ai'):
                        if fingerprint:
                            await self.tcell_cache.store_golden_patch(fingerprint, patch)
                            self.repair_throttler.record_success(fingerprint)
                            # if patch scores high enough, request consensus (harvest)
                            try:
                                score = float(patch.get('_coring_score', 0.0))
                                if self.scorer and self.scorer.will_harvest(score):
                                    payload = {
                                        'proposal_id': fingerprint,
                                        'fingerprint': fingerprint,
                                        'coring_score': score,
                                        'patch_summary': (patch.get('summary') if isinstance(patch, dict) else None)
                                    }
                                    try:
                                        if self.nervous_system:
                                            self.nervous_system.emit(self.nervous_system.create_event(EventType.CONSENSUS_REQUESTED, caused_by_command_id='IMMUNE', caused_by_user_id=0, payload=payload))
                                        else:
                                            # fallback: use module-level nervous_system
                                            nervous_system.emit(self.nervous_system.create_event(EventType.CONSENSUS_REQUESTED, caused_by_command_id='IMMUNE', caused_by_user_id=0, payload=payload))
                                    except Exception:
                                        # best-effort emit; do not fail repair
                                        try:
                                            # alternate simpler emit signature if available
                                            if self.nervous_system:
                                                self.nervous_system.emit(EventType.CONSENSUS_REQUESTED)
                                        except Exception:
                                            pass
                            except Exception:
                                pass
                            # attempt auto PR creation if enabled
                            try:
                                if self._auto_pr_enabled and self.scorer and self.scorer.will_harvest(patch.get('_coring_score', 0.0)):
                                    # run in background so we don't block worker loop
                                    asyncio.create_task(self._auto_create_pr_for_proposal(fingerprint, patch))
                            except Exception:
                                logger.exception('Auto PR scheduling failed for %s', fingerprint)
                    else:
                        if fingerprint:
                            self.repair_throttler.record_failure(fingerprint)
            except Exception:
                if fingerprint:
                    self.repair_throttler.record_failure(fingerprint)
                logger.exception('AI repair failed for %s', fingerprint)

    async def _build_context_pack(self, crash_report: Any) -> CrashContextPack:
        builder = ContextPackBuilder(max_history=self.limits.max_history_events, max_size_bytes=self.limits.max_context_mb * 1024 * 1024)
        return await builder.build(crash_report)

    async def _auto_create_pr_for_proposal(self, fingerprint: str, patch: Dict[str, Any]) -> None:
        """Create a branch + PR for a harvest proposal using GitHubCortexClient.

        This is best-effort and runs asynchronously. It requires GITHUB_TOKEN and GITHUB_REPOSITORY env vars.
        """
        try:
            client = GitHubCortexClient()
        except Exception:
            logger.exception('GitHubCortexClient not available')
            return

        branch_name = f"immune/harvest-{fingerprint[:8]}"
        created = client.create_branch_from_default(branch_name)
        if not created:
            logger.warning('Failed to create branch %s', branch_name)
            return

        # prepare patch file(s)
        files = {}
        try:
            # store patch content as a single diff file
            diff_content = patch.get('diff') or patch.get('content') or json.dumps(patch)
            path = f"proposals/{fingerprint[:8]}.diff"
            ok = client.create_or_update_file(path, diff_content, branch=branch_name, message=f"Immune proposal: {fingerprint[:8]}")
            if ok:
                files[path] = True
        except Exception:
            logger.exception('Failed to upload patch file for %s', fingerprint)

        title = f"[Immune] Harvest proposal {fingerprint[:8]}"
        desc = patch.get('summary', 'Automated harvest proposal generated by Immune System')
        coring_score = float(patch.get('_coring_score', 0.0))
        emotion = patch.get('_emotion', 'neutral')
        confidence = float(patch.get('_confidence', 0.9))

        body = build_emotional_pr_body(title, desc, coring_score, emotion, confidence, files)
        pr = client.create_pr(title=title, body=body, head=branch_name)
        if pr:
            pr_num = pr.get('number')
            logger.info('Created harvest PR #%s for %s', pr_num, fingerprint)
            # annotate proposal in DB if possible
            try:
                cur = self.db_connection.cursor()
                cur.execute('UPDATE harvest_proposals SET status=?, patch_summary=?, created_at=CURRENT_TIMESTAMP WHERE fingerprint=?', ('PR_CREATED', desc, fingerprint))
                self.db_connection.commit()
            except Exception:
                logger.exception('Failed to update harvest_proposals for %s', fingerprint)

    async def _health_monitor(self) -> None:
        last_drift_check = 0.0
        while self._running:
            await asyncio.sleep(60)
            queue_depth = self.pathogen_queue.qsize()
            await self.metrics.save_snapshot(queue_depth=queue_depth, active_repair_count=len(self.active_repairs))
            # persist raw memory sample to immune_memory_samples table (best-effort)
            try:
                if self.db_connection and self.memory_monitor:
                    samples = self.memory_monitor.get_samples()
                    if samples:
                        ts, rss = samples[-1]
                        cur = self.db_connection.cursor()
                        cur.execute('''
                            CREATE TABLE IF NOT EXISTS immune_memory_samples (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                timestamp TEXT NOT NULL,
                                rss_bytes INTEGER NOT NULL
                            )
                        ''')
                        cur.execute('INSERT INTO immune_memory_samples (timestamp, rss_bytes) VALUES (?, ?)', (datetime.utcfromtimestamp(ts).isoformat(), int(rss)))
                        self.db_connection.commit()
            except Exception:
                logger.exception('Failed to persist memory sample')
            now = time.time()
            if now - last_drift_check >= self.hash_drift_interval:
                self._check_hash_drift()
                last_drift_check = now

    async def _apply_known_patch(self, crash_report: Any, patch: Dict[str, Any]) -> bool:
        logger.info('Applying known patch for %s', getattr(crash_report, 'fingerprint', 'unknown'))
        return False

    async def _verify_and_apply(self, crash_report: Any, patch: Dict[str, Any], patch_type: str) -> bool:
        logger.info('Verifying %s patch for %s', patch_type, getattr(crash_report, 'fingerprint', 'unknown'))
        return False

    async def _check_hash_drift(self) -> None:
        """Check for hash drift in the system (placeholder)."""
        # Placeholder for hash drift checking logic
        pass
