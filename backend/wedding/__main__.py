import asyncio
import logging
import os
import ssl

import asyncpg
import websockets

import wedding
from wedding.core import Server


LOGGER = logging.getLogger(wedding.__name__)


async def main():
    logging.basicConfig(
        level=logging.WARNING,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    logging.getLogger(wedding.__name__).level = logging.DEBUG

    LOGGER.info("Connecting to Postgres")

    pg_params = {
        "user": os.getenv("PG_USERNAME"),
        "password": os.getenv("PG_PASSWORD"),
        "database": os.getenv("PG_DATABASE"),
        "host": os.getenv("PG_HOST"),
        "port": os.getenv("PG_PORT"),
    }
    if cadata := os.getenv("PG_CADATA"):
        pg_params["ssl"] = ssl.create_default_context(cadata=cadata)
    pg_conn = await asyncpg.connect(**pg_params)

    LOGGER.info("Starting websocket server")

    server = Server(
        pg_conn,
        next_stage_code=os.getenv("NEXT_STAGE_CODE"),
        reset_code=os.getenv("RESET_CODE"),
    )
    await server.next_stage()
    await websockets.serve(server.serve, "0.0.0.0", 8000)

    LOGGER.info("Ready to go")


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
loop.run_forever()
