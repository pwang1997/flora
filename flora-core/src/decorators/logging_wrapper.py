import functools
import logging
import pydantic
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
        if isinstance(v, Session):
            continue
        payloads[k] = serialize_value(v)
    for i, v in enumerate(args):
        if isinstance(v, Session):
            continue
        payloads[f"arg{i}"] = serialize_value(v)
    return payloads


def logging_wrapper(func, logging_level=None):
    log_func = logging_level or logging.getLogger(func.__module__).debug

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        payload = extract_payload(*args, **kwargs)
        log_func(
            f"{func.__name__} starts: {payload}",
            extra={
                "payload": payload,
            },
        )
        result = func(*args, **kwargs)

        serialized_result = serialize_value(result)
        log_func(
            f"{func.__name__} completed: {serialized_result}",
            extra={
                "return_value": serialized_result,
            },
        )
        return result

    return wrapper
