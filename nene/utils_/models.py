import asyncio
from datetime import date, timedelta
from pathlib import Path
from random import randint
from typing import Optional

from nonebot.log import logger
from tortoise import Tortoise, fields
from tortoise.models import Model

from nene.utils_.event import (
    MessageEvent_,
    V11MessageEvent,
    V12MessageEvent,
    kaiheilaMessageEvent,
    qqguidChannelEvent,
    qqguidMessageEvent,
)

# from pydantic import BaseModel
from .config import BASE, MAX_LUCKY, MULTIPLIER
from .data_model import SignData


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


class DailySign(Model):
    id = fields.IntField(pk=True)
    user_id = fields.IntField()
    gold = fields.IntField(default=0)
    sign_times = fields.IntField(default=0)
    last_sign = fields.DateField(default=date(2000, 1, 1))
    streak = fields.IntField(default=0)

    class Meta:
        table = "sign"

    @classmethod
    async def sign_in(cls, user_id: int) -> SignData:
        """
        :说明: `sign_in`
        > 添加签到记录

        :参数:
          * `user_id: int`: 用户ID

        :返回:
          - `SignData`: 签到数据
        """
        record, _ = await DailySign.get_or_create(user_id=user_id)

        today = date.today()
        if record.last_sign == (today - timedelta(days=1)):
            record.streak += 1

        record.last_sign = today

        gold_base = BASE + randint(-MAX_LUCKY, MAX_LUCKY)
        """基础金币"""

        today_gold = round(gold_base * (1 + record.streak * MULTIPLIER))
        """计算连续签到加成"""

        record.gold += today_gold

        record.sign_times += 1

        await record.save(update_fields=["last_sign", "gold", "sign_times", "streak"])
        return SignData(
            all_gold=record.gold,
            today_gold=today_gold,
            sign_times=record.sign_times,
            streak=record.streak,
        )

    @classmethod
    async def get_last_sign(cls, user_id: int, event: MessageEvent_) -> date:
        """
        :说明: `get_last_sign`
        > 获取最近的签到日期

        :参数:
          * `user_id: int`: 用户ID

        :返回:
          - `date`: 签到日期
        """
        try:
            record, _ = await DailySign.get_or_create(
                user_id=user_id,
            )
        except Exception:
            record, _ = await DailySign.get_or_create(user_id=user_id, name="无名氏")
        return record.last_sign

    @classmethod
    async def get_gold(cls, user_id: int) -> int:
        """
        :说明: `get_gold`
        > 获取金币

        :参数:
          * `user_id: int`: 用户ID
          * `group_id: int`: 群ID

        :返回:
          - `int`: 当前金币数量
        """
        record, _ = await DailySign.get_or_create(
            user_id=user_id,
        )
        return record.gold

    @classmethod
    async def adjust_gold(cls, adjust: int, user_id: int, group_id: int) -> int:
        """
        :说明: `adjust_gold`
        > 调整金币

        :参数:
          * `adjust: int`: 调整金币数量 为正 则添加 为负 则减少
          * `user_id: int`: 用户ID
          * `group_id: int`: 群ID

        :返回:
          - `int`: 当前金币数量
        """
        record, _ = await DailySign.get_or_create(
            group_id=group_id,
            user_id=user_id,
        )
        record.gold += adjust
        await record.save(update_fields=["gold"])
        return record.gold


class LoginTable(Model):
    id = fields.IntField(pk=True)
    qq = fields.IntField(null=True)
    qqguild = fields.IntField(null=True)
    kook = fields.IntField(null=True)
    Telegram = fields.IntField(null=True)
    Discord = fields.IntField(null=True)
    Bilibili = fields.IntField(null=True)
    Arcaea = fields.IntField(null=True)
    Phigros = fields.IntField(null=True)

    class Meta:
        table = "login"

    @classmethod
    async def create_login(
        cls,
        event: MessageEvent_,
        platform: Optional[str] = None,
        account_number: Optional[int] = None,
    ):
        """绑定平台或qq
        绑定qq114514
        绑定b站1145114
        Args:
            event (MessageEvent): 消息事件
            platform (Optional[str], optional): 平台名称. Defaults to None.
            account_number (Optional[int], optional): 账号数字. Defaults to None.

        Returns:
            bool: 返回是否绑定成功
        """
        if not platform and not account_number:
            # 进行qq绑定
            await LoginTable.get_or_create(qq=event.get_user_id())
            return True
        elif platform and account_number:
            platform = platform.lower()
            login = await LoginTable.get_or_none(qq=event.get_user_id())
            if login is None:
                return False

            if platform in ["qq"]:
                # 为当前平台绑定
                login.kook = (
                    int(event.user_id)
                    if isinstance(event, kaiheilaMessageEvent)
                    else None
                )
                login.qqguild = (
                    int(event.get_user_id())
                    if isinstance(event, qqguidChannelEvent)
                    else None
                )
            else:
                # 为其他账户绑定
                if platform in ["bilibili", "b站"]:
                    login.Bilibili = int(account_number)
                elif platform in ["arcaea"]:
                    login.Arcaea = int(account_number)
                else:
                    return False  # 不支持的平台名称

            try:
                await login.save()
                return True
            except Exception as e:
                print(f"Error saving login details: {e}")
                return False

        return False  # 参数不完整，无法执行绑定

    @classmethod
    async def get_user_info(cls, event: MessageEvent_):
        # 查询指定 QQ 号或 Kook 号或 QQ Guild 号的用户绑定信息
        try:
            if isinstance(event, (V11MessageEvent, V12MessageEvent)):
                qq = int(event.user_id)
                user = await LoginTable.get_or_none(qq=qq)
            elif isinstance(event, kaiheilaMessageEvent):
                kook = int(event.user_id)
                user = await LoginTable.get_or_none(kook=kook)
            elif isinstance(event, qqguidMessageEvent):
                qqguild = int(event.get_user_id())
                user = await LoginTable.get_or_none(qqguild=qqguild)
            else:
                return None

            return user
        except Exception as e:
            logger.warning(e)
            return None


sql = SQL()
