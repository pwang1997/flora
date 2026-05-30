import asyncio

from flora_worker.polling import Worker


def test_worker_placeholder_returns_no_work() -> None:
    assert asyncio.run(Worker().run_once()) == 0
