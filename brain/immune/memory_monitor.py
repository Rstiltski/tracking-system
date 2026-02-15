"""
Lightweight memory monitor for the immune system.
Periodically snapshots process memory usage (RSS) and keeps a bounded history.

Usage:
    from brain.immune.memory_monitor import MemoryMonitor
    monitor = MemoryMonitor(interval=10, max_samples=60)
    monitor.start()
    # ... later
    monitor.stop()
    samples = monitor.get_samples()
"""
from __future__ import annotations
import threading
import time
from collections import deque
from typing import Deque, Tuple, List


class MemoryMonitor:
    def __init__(self, interval: int = 10, max_samples: int = 360):
        """Create a memory monitor.

        interval: seconds between snapshots
        max_samples: maximum number of snapshots to retain
        """
        self.interval = interval
        self.max_samples = max_samples
        self._samples: Deque[Tuple[float, int]] = deque(maxlen=max_samples)
        self._thread: threading.Thread | None = None
        self._stop = threading.Event()

    def _snapshot_rss(self) -> int:
        """Return RSS in bytes. Falls back to 0 if not available."""
        try:
            import psutil
            p = psutil.Process()
            return int(p.memory_info().rss)
        except Exception:
            # fallback using resource (may be platform dependent)
            try:
                import resource
                usage = resource.getrusage(resource.RUSAGE_SELF)
                # ru_maxrss is in kilobytes on Linux, bytes on macOS; try to normalize
                val = getattr(usage, 'ru_maxrss', 0)
                if val > 0 and val < 10 ** 9:
                    # assume kilobytes
                    return int(val * 1024)
                return int(val)
            except Exception:
                return 0

    def _run(self):
        while not self._stop.is_set():
            ts = time.time()
            rss = self._snapshot_rss()
            self._samples.append((ts, rss))
            self._stop.wait(self.interval)

    def start(self):
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=1)
            self._thread = None

    def get_samples(self) -> List[Tuple[float, int]]:
        return list(self._samples)


__all__ = ["MemoryMonitor"]
