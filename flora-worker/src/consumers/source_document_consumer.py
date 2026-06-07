from __future__ import annotations

import asyncio
import json
from collections.abc import Callable
from dataclasses import dataclass

from kafka import KafkaConsumer
from kafka.structs import OffsetAndMetadata, TopicPartition

from config import settings
from models import DocumentIngestionEventPayload


def build_kafka_consumer() -> KafkaConsumer:
    return KafkaConsumer(
        settings.kafka_documents_topic,
        auto_offset_reset="earliest",
        enable_auto_commit=False,
        bootstrap_servers=settings.kafka_bootstrap_servers,
        client_id=settings.kafka_consumer_client_id,
        group_id=settings.kafka_consumer_group_id,
        sasl_mechanism=settings.kafka_sasl_mechanism,
        sasl_plain_username=settings.kafka_username,
        sasl_plain_password=settings.kafka_password,
        security_protocol="SASL_SSL",
        ssl_cafile=settings.kafka_ssl_cafile,
        value_deserializer=lambda value: json.loads(value.decode("utf-8")),
        key_deserializer=lambda value: value.decode("utf-8") if value else None,
    )


class SourceDocumentConsumer:
    def __init__(self, consumer_factory: Callable[[], KafkaConsumer] = build_kafka_consumer) -> None:
        self._consumer = consumer_factory()

    async def poll(self) -> list["ConsumedDocumentEvent"]:
        message_batches = await asyncio.to_thread(
            self._consumer.poll,
            timeout_ms=settings.kafka_poll_timeout_ms,
        )
        payloads: list[ConsumedDocumentEvent] = []
        for messages in message_batches.values():
            for message in messages:
                payloads.append(
                    ConsumedDocumentEvent(
                        payload=DocumentIngestionEventPayload.model_validate(message.value),
                        topic=message.topic,
                        partition=message.partition,
                        offset=message.offset,
                    )
                )
        return payloads

    async def commit(self, event: "ConsumedDocumentEvent") -> None:
        partition = TopicPartition(event.topic, event.partition)
        offsets = {partition: OffsetAndMetadata(event.offset + 1, "")}
        await asyncio.to_thread(self._consumer.commit, offsets=offsets)

    async def close(self) -> None:
        await asyncio.to_thread(self._consumer.close)


@dataclass(slots=True)
class ConsumedDocumentEvent:
    payload: DocumentIngestionEventPayload
    topic: str
    partition: int
    offset: int
