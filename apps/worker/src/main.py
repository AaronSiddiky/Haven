"""
Haven background worker.

Jobs:
  1. poll_official_alerts  — fetch NWS alerts every 5 minutes
  2. expire_old_alerts     — mark ended alerts inactive every 10 minutes
  3. notify_users          — send SMS notifications for new high-severity alerts

Run with:  python -m src.main
"""
import asyncio
import logging
import signal
import sys

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from src.jobs import expire_old_alerts, notify_users, poll_official_alerts
from src.settings import get_settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)


async def main() -> None:
    settings = get_settings()
    scheduler = AsyncIOScheduler()

    scheduler.add_job(
        poll_official_alerts.run,
        "interval",
        seconds=settings.poll_interval_seconds,
        id="poll_nws",
        replace_existing=True,
    )

    scheduler.add_job(
        expire_old_alerts.run,
        "interval",
        seconds=settings.expiry_check_interval_seconds,
        id="expire_alerts",
        replace_existing=True,
    )

    scheduler.add_job(
        notify_users.run,
        "interval",
        seconds=settings.poll_interval_seconds,
        id="notify_users",
        replace_existing=True,
    )

    scheduler.start()
    logger.info(
        "Worker started — polling NWS every %ds for states: %s",
        settings.poll_interval_seconds,
        settings.nws_poll_states,
    )

    loop = asyncio.get_running_loop()
    stop_event = asyncio.Event()

    def _shutdown(*_):
        logger.info("Shutdown signal received")
        stop_event.set()

    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, _shutdown)

    await stop_event.wait()
    scheduler.shutdown()
    logger.info("Worker stopped")


if __name__ == "__main__":
    asyncio.run(main())
