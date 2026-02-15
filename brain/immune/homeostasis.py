#!/usr/bin/env python3
"""
Homeostatic Regulator

Monitors immune system load and records neuro-synapse metrics to prevent
systemic overload.
📚 REQUIRED READING BEFORE MODIFICATION:
- BRAIN_USAGE_GUIDE.md
- AI_NATIVE_ARCHITECTURE_GUIDE.md
- LLM_AGENT_QUICKSTART.md
"""

from __future__ import annotations

import logging
import threading
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Callable, Optional

logger = logging.getLogger(__name__)


@dataclass
class HomeostasisSnapshot:
    timestamp: str
    queue_depth: int
    memory_usage_bytes: int
    sandbox_accuracy_pct: float
    load_ratio: float
    arousal: float
    valence: float


class HomeostaticRegulator:
    """Background monitor that records neuro-synapse metrics and triggers resets."""

    def __init__(
        self,
        db_connection,
        queue_threshold: int = 500,
        memory_threshold_bytes: int = 1_000_000_000,
        interval_sec: int = 60,
        on_reset: Optional[Callable[[], None]] = None,
    ):
        self._db = db_connection
        self._queue_threshold = queue_threshold
        self._memory_threshold_bytes = memory_threshold_bytes
        self._interval_sec = interval_sec
        self._on_reset = on_reset
        self._running = False
        self._thread: Optional[threading.Thread] = None

    def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._loop, name="homeostatic-regulator", daemon=True)
        self._thread.start()
        logger.info("🧠 Homeostatic Regulator: ONLINE")

    def stop(self) -> None:
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)
        logger.info("🧠 Homeostatic Regulator: SHUTDOWN")

    def run_once(self) -> Optional[HomeostasisSnapshot]:
        snapshot = self._collect_snapshot()
        if not snapshot:
            return None

        self._record_synapse(snapshot)
        if snapshot.queue_depth >= self._queue_threshold or snapshot.memory_usage_bytes >= self._memory_threshold_bytes:
            logger.warning("🔥 Homeostasis trigger: queue or memory overload")
            if self._on_reset:
                self._on_reset()
        return snapshot

    def _loop(self) -> None:
        while self._running:
            try:
                self.run_once()
            except Exception:
                logger.exception("Homeostatic regulator failure")
            time.sleep(self._interval_sec)

    def _collect_snapshot(self) -> Optional[HomeostasisSnapshot]:
        row = self._db.execute(
            """
            SELECT queue_depth, memory_usage_bytes, sandbox_accuracy_pct
            FROM immune_metrics
            ORDER BY timestamp DESC
            LIMIT 1
            """
        ).fetchone()
        if not row:
            return None

        queue_depth, memory_usage_bytes, sandbox_accuracy_pct = row
        load_ratio = min(queue_depth / max(self._queue_threshold, 1), 1.0)
        arousal = min(load_ratio + (memory_usage_bytes / max(self._memory_threshold_bytes, 1)), 1.0)
        valence = min((sandbox_accuracy_pct or 0) / 100.0, 1.0)

        return HomeostasisSnapshot(
            timestamp=datetime.utcnow().isoformat(),
            queue_depth=int(queue_depth or 0),
            memory_usage_bytes=int(memory_usage_bytes or 0),
            sandbox_accuracy_pct=float(sandbox_accuracy_pct or 0),
            load_ratio=load_ratio,
            arousal=arousal,
            valence=valence,
        )

    def _record_synapse(self, snapshot: HomeostasisSnapshot) -> None:
        self._db.execute(
            """
            INSERT INTO neuro_synapse (
                timestamp,
                queue_depth,
                memory_usage_bytes,
                sandbox_accuracy_pct,
                load_ratio,
                arousal,
                valence
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                snapshot.timestamp,
                snapshot.queue_depth,
                snapshot.memory_usage_bytes,
                snapshot.sandbox_accuracy_pct,
                snapshot.load_ratio,
                snapshot.arousal,
                snapshot.valence,
            ),
        )
        self._db.commit()
