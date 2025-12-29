"""
Utility module for implementing retry logic with exponential backoff.
"""
import time
import random
import logging
from functools import wraps
from typing import Callable, Type, Any


def retry_with_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    backoff_factor: float = 2.0,
    exceptions: tuple = (Exception,),
    logger: logging.Logger = None
):
    """
    Decorator to implement retry logic with exponential backoff.

    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay between retries in seconds
        max_delay: Maximum delay between retries in seconds
        backoff_factor: Factor by which delay increases after each retry
        exceptions: Tuple of exception types to catch and retry on
        logger: Logger instance for logging retry attempts
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt == max_retries:
                        # No more retries left, raise the last exception
                        if logger:
                            logger.error(f"Function {func.__name__} failed after {max_retries} retries: {str(e)}")
                        raise e
                    
                    # Calculate delay with exponential backoff and jitter
                    delay = min(base_delay * (backoff_factor ** attempt), max_delay)
                    jitter = random.uniform(0, 0.1 * delay)  # Add 0-10% jitter to prevent thundering herd
                    total_delay = delay + jitter
                    
                    if logger:
                        logger.warning(
                            f"Function {func.__name__} failed on attempt {attempt + 1}/{max_retries + 1}, "
                            f"retrying in {total_delay:.2f}s: {str(e)}"
                        )
                    
                    time.sleep(total_delay)
            
            # This should never be reached, but added for type checker
            raise last_exception
        
        return wrapper
    return decorator


def retry_on_exception(
    func: Callable,
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    backoff_factor: float = 2.0,
    exceptions: tuple = (Exception,),
    logger: logging.Logger = None
):
    """
    Function wrapper to implement retry logic with exponential backoff.

    Args:
        func: Function to execute with retry logic
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay between retries in seconds
        max_delay: Maximum delay between retries in seconds
        backoff_factor: Factor by which delay increases after each retry
        exceptions: Tuple of exception types to catch and retry on
        logger: Logger instance for logging retry attempts

    Returns:
        Result of the function call
    """
    for attempt in range(max_retries + 1):
        try:
            return func()
        except exceptions as e:
            if attempt == max_retries:
                # No more retries left, raise the last exception
                if logger:
                    logger.error(f"Function {func.__name__} failed after {max_retries} retries: {str(e)}")
                raise e
            
            # Calculate delay with exponential backoff and jitter
            delay = min(base_delay * (backoff_factor ** attempt), max_delay)
            jitter = random.uniform(0, 0.1 * delay)  # Add 0-10% jitter to prevent thundering herd
            total_delay = delay + jitter
            
            if logger:
                logger.warning(
                    f"Function {func.__name__} failed on attempt {attempt + 1}/{max_retries + 1}, "
                    f"retrying in {total_delay:.2f}s: {str(e)}"
                )
            
            time.sleep(total_delay)