import asyncio
import logging
import os
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Callable, Optional
from SharedKernel.base.Logger import get_logger
from SharedKernel.persistence.Decorators import Service

logger = get_logger(__name__)

class ThreadPoolManager:
    def __init__(self, max_workers: Optional[int] = None, timeout: int = 300):
        self.max_workers = max_workers or min(32, (os.cpu_count() or 1) + 4)
        self.timeout = timeout
        self.executor = ThreadPoolExecutor(
            max_workers=self.max_workers,
            thread_name_prefix="AI_HelpDesk"
        )
        logger.info(f"ThreadPoolManager initialized with {self.max_workers} workers")
    
    async def run_in_executor(self, func: Callable, *args, **kwargs) -> Any:
        """
        Run a synchronous function in the thread pool
        
        Args:
            func: Function to run
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Result of the function
        """
        try:
            loop = asyncio.get_event_loop()
            result = await asyncio.wait_for(
                loop.run_in_executor(self.executor, lambda: func(*args, **kwargs)),
                timeout=self.timeout
            )
            return result
        except asyncio.TimeoutError:
            logger.error(f"Function {func.__name__} timed out after {self.timeout}s")
            raise
        except Exception as e:
            logger.error(f"Error in thread pool execution: {e}")
            raise
    
    async def run_batch(self, tasks: list[tuple[Callable, tuple, dict]]) -> list[Any]:
        """
        Run multiple functions concurrently in the thread pool
        
        Args:
            tasks: List of (function, args, kwargs) tuples
            
        Returns:
            List of results in the same order as input tasks
        """
        if not tasks:
            return []
            
        async def run_single_task(func, args, kwargs):
            return await self.run_in_executor(func, *args, **kwargs)
        
        # Create coroutines for all tasks
        coroutines = [
            run_single_task(func, args, kwargs) 
            for func, args, kwargs in tasks
        ]
        
        # Run all tasks concurrently
        try:
            results = await asyncio.gather(*coroutines, return_exceptions=True)
            
            # Log exceptions if any
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"Task {i} failed: {result}")
                    
            return results
        except Exception as e:
            logger.error(f"Error in batch execution: {e}")
            raise
    
    def shutdown(self):
        """Shutdown the thread pool gracefully"""
        logger.info("Shutting down ThreadPoolManager")
        self.executor.shutdown(wait=True)
    
    def get_stats(self) -> dict:
        """Get thread pool statistics"""
        return {
            "max_workers": self.max_workers,
            "timeout": self.timeout,
            "active_threads": self.executor._threads.__len__() if hasattr(self.executor, '_threads') else 0
        }

_thread_pool_manager: Optional[ThreadPoolManager] = None

def get_thread_pool_manager() -> ThreadPoolManager:
    """Get or create the global thread pool manager"""
    global _thread_pool_manager
    if _thread_pool_manager is None:
        _thread_pool_manager = ThreadPoolManager()
    return _thread_pool_manager

def shutdown_thread_pool():
    """Shutdown the global thread pool manager"""
    global _thread_pool_manager
    if _thread_pool_manager is not None:
        _thread_pool_manager.shutdown()
        _thread_pool_manager = None
