import logging
from time import perf_counter
from typing import Dict, Any
from contextlib import contextmanager

log = logging.getLogger(__name__)

class Metrics:
    """Metrics collector for RAG pipeline stages"""
    
    def __init__(self, component: str):
        self.component = component
        self._timings: Dict[str, float] = {}
        self._counters: Dict[str, int] = {}
    
    @contextmanager
    def stage(self, name: str):
        """Context manager để đo thời gian một stage"""
        start = perf_counter()
        try:
            yield self
        finally:
            elapsed = perf_counter() - start
            self._timings[name] = elapsed
    
    def record(self, name: str, value: float):
        """Record a timing value manually"""
        self._timings[name] = value
    
    def increment(self, name: str, value: int = 1):
        """Increment a counter"""
        self._counters[name] = self._counters.get(name, 0) + value
    
    def get_timing(self, name: str) -> float:
        """Get timing for a specific stage"""
        return self._timings.get(name, 0.0)
    
    def total_time(self) -> float:
        """Get total time of all stages"""
        return sum(self._timings.values())
    
    def log_summary(self):
        """Log metrics summary"""
        if not self._timings:
            return
        
        lines = [f"[{self.component}]"]
        for name, seconds in self._timings.items():
            lines.append(f"{name}: {seconds:.2f}s")
        if self._counters:
            for name, count in self._counters.items():
                lines.append(f"{name}: {count}")
        lines.append(f"total: {self.total_time():.2f}s")
        
        print("\n".join(lines))
    
    def to_dict(self) -> Dict[str, Any]:
        """Export metrics as dictionary"""
        return {
            "component": self.component,
            "timings": self._timings.copy(),
            "counters": self._counters.copy(),
            "total_time": self.total_time()
        }
