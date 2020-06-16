import argparse
import asyncio

from asyncpg import DuplicateTableError, DuplicateSchemaError, Connection

from common.config import load_db_config
from common.logging import logger
from sink.db.dbops import connect, table_ddl


async def create_tables(connection: Connection, table_name: str, schema: str, live=False):
    for table_name, ddl in table_ddl(table_name, schema).items():
        logger.info(f"creating table {table_name}")
        if live:
            await connection.execute(ddl)
        else:
            logger.info(ddl)


async def create_schema(connection: Connection, schema: str, live=False):
    schema_create = f"CREATE SCHEMA IF NOT EXISTS {schema}"
    logger.info(f"creating schema {schema}")
    if live:
        await connection.execute(schema_create)
    else:
        logger.info(schema_create)


async def drop_schema(connection: Connection, schema: str, live=False, destroy=False):
    schema_drop = f"DROP SCHEMA IF EXISTS {schema} cascade"
    logger.warning(f"dropping schema {schema}")
    if live and destroy:
        await connection.execute(schema_drop)
    else:
        logger.info(schema_drop)


async def main(db_config: dict, live=False, destroy=False):
    if destroy:
        logger.warning(
            "!!!!Running with destroy mode and this will destory the existing schema!!!! The script will wait for 5 secs to help you reevaluate the decision.")
        await asyncio.sleep(5)
    if live:
        logger.warning("Running in live mode. This will create tables and schemas")
    else:
        logger.info("Running in dry run mode. Just the DDLs will be printed")
    connection = None
    try:
        connection = await connect(db_config['conn_string'])
        async with connection.transaction():
            if destroy:
                logger.warning("destroying the existing schema")
            await drop_schema(connection, db_config['schema'], live, destroy)
            await create_schema(connection, db_config['schema'], live)
            await create_tables(connection, db_config['table'], db_config['schema'], live)

    except DuplicateTableError as e:
        logger.error("Always run the fixtures on clean database. We don't support incremental migrations yet!",
                     exc_info=e)
    finally:
        await connection.close()


def run():
    parser = argparse.ArgumentParser(description='Create the database fixtures')
    parser.add_argument('--destroy', action="store_true", help="Destroy existing database before creating fixtures")
    parser.add_argument('--live', action="store_true", help='Enable live run mode')
    args = parser.parse_args()
    asyncio.run(main(load_db_config(), args.live, args.destroy))


if __name__ == "__main__":
    run()
