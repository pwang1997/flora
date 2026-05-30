import asyncio

from flora_worker.polling import Worker


async def run() -> None:
    worker = Worker()
    await worker.run_once()


if __name__ == "__main__":
    asyncio.run(run())
