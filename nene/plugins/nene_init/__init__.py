# from pathlib import Path

# from peewee import SqliteDatabase
from nonebot import get_driver

from nene.utils_.models import sql

driver = get_driver()


@driver.on_startup
async def _():
    sql.create_tables()


@driver.on_shutdown
async def _():
    sql.__del__()
