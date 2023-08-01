import asyncio
from pathlib import Path

from tortoise import Tortoise
from nonebot.log import logger


class SQL:
    async def __init__(self):
        db_path = Path.home() / ".nene-bot" / "nene.db"
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self.db_path = str(db_path)
        self._init_db = Tortoise.init(
            db_url=f'sqlite:///{self.db_path}', modules={'models': ['models']}
        )
        logger.debug("宁宁已连接本地数据库")

    async def create_table(self):
        await Tortoise.generate_schemas()

    async def close_db(self):
        await Tortoise.close_connections()

    def __del__(self):
        asyncio.run(self.close_db())


sql = SQL()
