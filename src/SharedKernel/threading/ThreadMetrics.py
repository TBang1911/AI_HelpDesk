import time
import threading
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from SharedKernel.base.Logger import get_logger

logger = get_logger(__name__)

@dataclass
class ThreadMetric:
    """Single thread operation metric"""
    operation: str
    start_time: float
    end_time: Optional[float] = None
    duration: Optional[float] = None
    success: bool = True
    error: Optional[str] = None
    thread_id: Optional[int] = None
    
    def complete(self, success: bool = True, error: Optional[str] = None):
        """Mark the metric as completed"""
        self.end_time = time.time()
        self.duration = self.end_time - self.start_time
        self.success = success
        self.error = error
        self.thread_id = threading.get_ident()

@dataclass
class ThreadStats:
    """Thread pool statistics"""
    total_operations: int = 0
    successful_operations: int = 0
    failed_operations: int = 0
    total_duration: float = 0.0
    avg_duration: float = 0.0
    min_duration: float = float('inf')
    max_duration: float = 0.0
    active_threads: int = 0
    operations_by_type: Dict[str, int] = field(default_factory=dict)
    
    def update(self, metric: ThreadMetric):
        """Update statistics with a new metric"""
        self.total_operations += 1
        
        if metric.success:
            self.successful_operations += 1
        else:
            self.failed_operations += 1
            
        if metric.duration:
            self.total_duration += metric.duration
            self.min_duration = min(self.min_duration, metric.duration)
            self.max_duration = max(self.max_duration, metric.duration)
            self.avg_duration = self.total_duration / self.total_operations
            
        # Track operations by type
        op_type = metric.operation
        self.operations_by_type[op_type] = self.operations_by_type.get(op_type, 0) + 1
    
    def get_success_rate(self) -> float:
        """Get success rate as percentage"""
        if self.total_operations == 0:
            return 0.0
        return (self.successful_operations / self.total_operations) * 100

class ThreadMetrics:
    """Thread metrics collector"""
    
    def __init__(self):
        self._metrics: List[ThreadMetric] = []
        self._stats = ThreadStats()
        self._lock = threading.Lock()
        self._max_metrics = 1000  # Keep last 1000 metrics
        
    def start_operation(self, operation: str) -> ThreadMetric:
        """Start tracking a new operation"""
        metric = ThreadMetric(
            operation=operation,
            start_time=time.time()
        )
        
        with self._lock:
            self._metrics.append(metric)
            
            # Keep only recent metrics
            if len(self._metrics) > self._max_metrics:
                self._metrics = self._metrics[-self._max_metrics:]
                
        return metric
    
    def complete_operation(self, metric: ThreadMetric, success: bool = True, error: Optional[str] = None):
        """Complete an operation and update statistics"""
        metric.complete(success, error)
        
        with self._lock:
            self._stats.update(metric)
            
            # Log failed operations
            if not success:
                logger.error(f"Thread operation failed: {metric.operation} - {error}")
    
    def get_stats(self) -> ThreadStats:
        """Get current statistics"""
        with self._lock:
            return ThreadStats(
                total_operations=self._stats.total_operations,
                successful_operations=self._stats.successful_operations,
                failed_operations=self._stats.failed_operations,
                total_duration=self._stats.total_duration,
                avg_duration=self._stats.avg_duration,
                min_duration=self._stats.min_duration if self._stats.min_duration != float('inf') else 0.0,
                max_duration=self._stats.max_duration,
                active_threads=threading.active_count(),
                operations_by_type=self._stats.operations_by_type.copy()
            )
    
    def reset(self):
        """Reset all metrics"""
        with self._lock:
            self._metrics.clear()
            self._stats = ThreadStats()
    
    def get_recent_metrics(self, count: int = 100) -> List[ThreadMetric]:
        """Get recent metrics"""
        with self._lock:
            return self._metrics[-count:]

# Global metrics instance
_thread_metrics: Optional[ThreadMetrics] = None

def get_thread_metrics() -> ThreadMetrics:
    """Get or create the global thread metrics instance"""
    global _thread_metrics
    if _thread_metrics is None:
        _thread_metrics = ThreadMetrics()
    return _thread_metrics

def reset_thread_metrics():
    """Reset the global thread metrics"""
    global _thread_metrics
    if _thread_metrics is not None:
        _thread_metrics.reset()
