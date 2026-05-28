import asyncio
import os

from flora_api.database import init_db
from flora_worker.polling import Worker


async def run() -> None:
    init_db()
    worker = Worker(worker_id=os.getenv("WORKER_ID", "flora-worker-local"))
    await worker.run_forever()


if __name__ == "__main__":
    asyncio.run(run())
