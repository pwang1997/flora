import functools
import inspect
import logging
import pydantic
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


def serialize_value(val):
    if isinstance(val, pydantic.BaseModel):
        return val.model_dump()
    if isinstance(val, list):
        return [serialize_value(item) for item in val]
    if isinstance(val, dict):
        return {k: serialize_value(v) for k, v in val.items()}
    return val


def extract_payload(*args, **kwargs):
    payloads = {}
    for k, v in kwargs.items():
        if isinstance(v, Session | AsyncSession):
            continue
        payloads[k] = serialize_value(v)
    for i, v in enumerate(args):
        if isinstance(v, Session | AsyncSession):
            continue
        payloads[f"arg{i}"] = serialize_value(v)
    return payloads


def logging_wrapper(func, logging_level=None):
    log_func = logging_level or logging.getLogger(func.__module__).debug

    def log_start(payload):
        log_func(
            f"{func.__name__} starts: {payload}",
            extra={
                "payload": payload,
            },
        )

    def log_complete(result):
        serialized_result = serialize_value(result)
        log_func(
            f"{func.__name__} completed: {serialized_result}",
            extra={
                "return_value": serialized_result,
            },
        )

    if inspect.iscoroutinefunction(func):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            payload = extract_payload(*args, **kwargs)
            log_start(payload)
            result = await func(*args, **kwargs)
            log_complete(result)
            return result

        return async_wrapper

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        payload = extract_payload(*args, **kwargs)
        log_start(payload)
        result = func(*args, **kwargs)
        log_complete(result)
        return result

    return wrapper
