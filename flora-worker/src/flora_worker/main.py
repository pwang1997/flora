import asyncio

from flora_worker.polling import Worker


async def run() -> None:
    worker = Worker()
    await worker.run_forever()


if __name__ == "__main__":
    asyncio.run(run())
