# backend/app/utils/telemetry.py
import logging
from typing import Any, Dict
import time
from functools import wraps
import json

logger = logging.getLogger("telemetry")
logger.setLevel(logging.INFO)

class Telemetry:
    """
    Simple telemetry for monitoring performance and usage.
    """

    @staticmethod
    def log_event(event_name: str, data: Dict[str, Any]):
        """Log a telemetry event."""
        data["timestamp"] = time.time()
        logger.info(json.dumps({"event": event_name, **data}))

    @staticmethod
    def time_function(func):
        """Decorator to time function execution."""
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start = time.perf_counter()
            result = await func(*args, **kwargs)
            duration = time.perf_counter() - start
            Telemetry.log_event("function_timing", {
                "function": func.__name__,
                "duration_ms": duration * 1000,
                "args_count": len(args) + len(kwargs)
            })
            return result
        return wrapper