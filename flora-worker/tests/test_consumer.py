import asyncio
from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from flora_worker.consumers.source_document_consumer import SourceDocumentConsumer


class FakeKafkaConsumer:
    def __init__(self, messages):
        self._messages = messages

    def poll(self, timeout_ms: int):
        return {"partition-0": self._messages}

    def commit(self, offsets=None):
        return None

    def close(self):
        return None


def _message(value: dict, offset: int = 0):
    return SimpleNamespace(
        topic="flora.documents.created",
        partition=0,
        offset=offset,
        value=value,
    )


def test_consumer_validates_document_ingestion_payload() -> None:
    consumer = SourceDocumentConsumer(
        consumer_factory=lambda: FakeKafkaConsumer(
            [
                _message(
                    {
                        "event_type": "document.version.created",
                        "source_document_id": "doc_1",
                        "document_version_id": "ver_1",
                        "source_id": "src_1",
                        "version_number": 1,
                        "change_type": "created",
                        "content_hash": "hash_1",
                        "content": "content",
                        "title": "Readme",
                        "uri": "file:///README.md",
                        "metadata": {},
                        "occurred_at": "2026-06-07T00:00:00Z",
                    }
                )
            ]
        )
    )

    events = asyncio.run(consumer.poll())
    assert len(events) == 1
    assert events[0].payload.document_version_id == "ver_1"


def test_consumer_rejects_invalid_payload() -> None:
    consumer = SourceDocumentConsumer(
        consumer_factory=lambda: FakeKafkaConsumer(
            [
                _message(
                    {
                        "event_type": "document.version.created",
                        "source_document_id": "doc_1",
                    }
                )
            ]
        )
    )

    with pytest.raises(ValidationError):
        asyncio.run(consumer.poll())
