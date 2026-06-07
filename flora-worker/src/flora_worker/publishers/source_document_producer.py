from __future__ import annotations

import json
from collections.abc import Callable

from kafka import KafkaProducer

from flora_worker.config import settings


def _serialize_key(key: str) -> bytes:
    return key.encode("utf-8")


def _serialize_value(payload: dict) -> bytes:
    return json.dumps(payload).encode("utf-8")


def build_kafka_producer() -> KafkaProducer:
    return KafkaProducer(
        bootstrap_servers=settings.kafka_bootstrap_servers,
        sasl_mechanism=settings.kafka_sasl_mechanism,
        sasl_plain_username=settings.kafka_username,
        sasl_plain_password=settings.kafka_password,
        security_protocol="SASL_SSL",
        ssl_cafile=settings.kafka_ssl_cafile,
        client_id=settings.kafka_producer_client_id,
        key_serializer=_serialize_key,
        value_serializer=_serialize_value,
    )


class SourceDocumentProducer:
    def __init__(self, producer_factory: Callable[[], KafkaProducer] = build_kafka_producer) -> None:
        self._producer = producer_factory()

    def publish(self, *, topic: str, key: str, payload: dict) -> None:
        future = self._producer.send(topic, key=key, value=payload)
        future.get(timeout=10)

    def close(self) -> None:
        self._producer.close()
