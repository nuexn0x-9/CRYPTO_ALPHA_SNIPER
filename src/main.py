"""Application Entry Point and Lifecycle Supervisor for CRYPTO_ALPHA_SNIPER."""

import asyncio
import os
import signal
import sys

from loguru import logger

from src.config.settings import get_settings
from src.engine.scanner import ScannerEngine
from src.services.tracker import PerformanceTracker
from src.version import PROJECT_NAME, VERSION


def setup_logging() -> None:
    """Configures structured logging with Loguru."""
    settings = get_settings()

    # Remove default handler
    logger.remove()

    # 1. Console colorized output
    logger.add(
        sys.stdout,
        level=settings.LOG_LEVEL,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        colorize=True,
    )

    # 2. File rotation output
    log_dir = os.path.dirname(settings.LOG_FILE_PATH)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)

    logger.add(
        settings.LOG_FILE_PATH,
        level=settings.LOG_LEVEL,
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{line} - {message}",
        rotation=settings.LOG_ROTATION,
        retention=settings.LOG_RETENTION,
        compression="zip",
        enqueue=True,
    )


async def main() -> None:
    """Async main application entry point."""
    setup_logging()

    print(
        "======================================================================\n"
        "  CRYPTO_ALPHA_SNIPER - High-Throughput Intelligence Engine           \n"
        "======================================================================"
    )

    settings = get_settings()
    logger.info(f"Initializing {PROJECT_NAME} v{VERSION}...")
    logger.info(f"Supported Chains : {settings.SUPPORTED_CHAINS}")
    logger.info(f"Database Target  : {settings.DATABASE_URL}")
    logger.info(f"Telegram Alerts  : {'ENABLED' if settings.has_telegram else 'DISABLED'}")

    scanner = ScannerEngine()
    tracker = PerformanceTracker(dexscreener_client=scanner.dexscreener)

    await scanner.initialize()

    stop_event = asyncio.Event()

    def request_shutdown():
        logger.info("Shutdown signal received. Initiating graceful teardown...")
        scanner.stop()
        tracker.stop()
        stop_event.set()

    # Register OS signals where available
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, request_shutdown)
        except (NotImplementedError, RuntimeError):
            # Windows fallback
            pass

    # Launch background tasks
    scanner_task = asyncio.create_task(scanner.run_scanner_loop())
    tracker_task = asyncio.create_task(tracker.run_tracker_loop())

    try:
        # Wait for either tasks to complete or shutdown event
        await asyncio.gather(scanner_task, tracker_task)
    except (asyncio.CancelledError, KeyboardInterrupt):
        request_shutdown()
    finally:
        logger.info("Closing active network sessions...")
        await scanner.close()
        logger.info("CRYPTO_ALPHA_SNIPER shut down gracefully.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
