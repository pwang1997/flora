from __future__ import annotations

import json
from collections.abc import Callable

from kafka import KafkaProducer

from config import settings


def _serialize_key(key: str) -> bytes:
    return key.encode("utf-8")


def _serialize_value(payload: dict) -> bytes:
    return json.dumps(payload).encode("utf-8")


def build_kafka_producer() -> KafkaProducer:
    return KafkaProducer(
        bootstrap_servers=settings.kafka_bootstrap_servers,
        client_id=settings.kafka_producer_client_id,
        key_serializer=_serialize_key,
        value_serializer=_serialize_value,
        security_protocol="SSL",
        ssl_cafile="ca.pem",
        ssl_certfile="service.cert",
        ssl_keyfile="service.key",
    )


class SourceDocumentProducer:
    def __init__(self, producer_factory: Callable[[], KafkaProducer] = build_kafka_producer) -> None:
        self._producer = producer_factory()

    def publish(self, *, topic: str, key: str, payload: dict) -> None:
        future = self._producer.send(topic, key=key, value=payload)
        future.get(timeout=10)

    def close(self) -> None:
        self._producer.close()
