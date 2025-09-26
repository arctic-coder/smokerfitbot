import logging

def setup_logging(level: str = "INFO") -> None:
    logging.basicConfig(
        level=getattr(logging, level, logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        datefmt="%H:%M:%S",
        force=True,
    )
    
    logging.getLogger("aiogram").setLevel(logging.WARNING)
    logging.getLogger("aiohttp.access").setLevel(logging.WARNING)
    logging.getLogger("asyncpg").setLevel(logging.INFO)
    logging.getLogger("aiosqlite").setLevel(logging.WARNING)

    logging.getLogger("workout").setLevel(logging.INFO)

    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("urllib3.connectionpool").setLevel(logging.WARNING)
    logging.getLogger("billing.yookassa").setLevel(logging.DEBUG)
