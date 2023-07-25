from datetime import date, timedelta
from pathlib import Path
from random import randint
from typing import Optional

from peewee import AutoField, CharField, DateField, IntegerField, Model, SqliteDatabase

from .config import BASE, MAX_LUCKY, MULTIPLIER
from .data_model import SignData
from .event import MessageEvent_, kaiheilaMessageEvent, qqguidChannelEvent

db_path = Path.home() / ".nene-bot" / "nene.db"
db_path.parent.mkdir(parents=True, exist_ok=True)
db = SqliteDatabase(str(db_path))


class DailySign(Model):
    id = AutoField()
    user_id = IntegerField()
    name = CharField()
    gold = IntegerField(default=0)
    sign_times = IntegerField(default=0)
    last_sign = DateField(default=date(2000, 1, 1))
    streak = IntegerField(default=0)

    class Meta:
        database = db
        table_name = "sign"

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
    async def get_last_sign(cls, user_id: int) -> date:
        """
        :说明: `get_last_sign`
        > 获取最近的签到日期

        :参数:
          * `user_id: int`: 用户ID

        :返回:
          - `date`: 签到日期
        """
        record, _ = await DailySign.get_or_create(
            user_id=user_id,
        )
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
    id = AutoField()
    qq = IntegerField(null=True)
    qqguild = IntegerField(null=True)
    kook = IntegerField(null=True)
    Telegram = IntegerField(null=True)
    Discord = IntegerField(null=True)
    Bilibili = IntegerField(null=True)
    Arcaea = IntegerField(null=True)
    Phigros = IntegerField(null=True)

    class Meta:
        table = db
        table_description = "login"

    @classmethod
    async def create_msg(
        cls,
        user_id: int,
        event: MessageEvent_,
        ex_mode: Optional[str] = None,
        ex_number: Optional[int] = None,
    ):
        """绑定平台或qq

        Args:
            user_id (int): 事件对象id
            event (MessageEvent_): 消息事件
            ex_mode (Optional[str], optional): 信息中str字段. Defaults to None.
            ex_number (Optional[int], optional): 信息中Int字段. Defaults to None.

        Returns:
            bool: _description_
        """
        if not ex_mode and not ex_number:
            """qq绑定"""
            await LoginTable.get_or_create(qq=user_id)
        elif ex_mode and ex_number:
            if ex_mode in ["qq", "QQ"]:
                """为当前平台绑定"""
                login = await LoginTable.get_or_none(qq=ex_number)
                if not login:
                    return False
                if isinstance(event, kaiheilaMessageEvent):
                    login.kook = int(event.user_id)
                elif isinstance(event, qqguidChannelEvent):
                    login.qqguild = int(event.get_user_id())
            else:
                """为其他账户绑定"""
                login = await LoginTable.get_or_none(qq=user_id)
                if not login:
                    return False
                if ex_mode in "bilibilib站B站":
                    login.Bilibili = int(ex_number)
                elif ex_mode in "Arcaearcaea":
                    login.Arcaea = int(ex_number)
            await login.save()
        return True


# 创建数据库
for i in [DailySign, LoginTable]:
    if not db.table_exists(i):
        db.create_tables([i], safe=True)
