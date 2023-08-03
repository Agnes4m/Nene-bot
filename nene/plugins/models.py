from datetime import date, timedelta
from random import randint
from typing import Union

from tortoise import fields
from tortoise.models import Model

from nene.utils_.event import (
    MessageEvent_,
    V11MessageEvent,
    V12MessageEvent,
    kaiheilaMessageEvent,
    qqguidMessageEvent,
)

from .sign import BASE, MAX_LUCKY, MULTIPLIER, SignData


async def is_adapter(name: str):
    if name in ["qq", "qqguild", "kook", "Telegram", "Discord"]:
        return True
    if name in ["Bilibili", "Arcaea", "Phigros"]:
        return False
    return None


class LoginTable(Model):
    id_ = fields.IntField(pk=True, generated=True)
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
    async def which_adapter(cls, event: MessageEvent_):
        """判断是否存在绑定信息,正确返回全部信息,否则为None"""
        usr_id = event.get_user_id()
        if isinstance(event, Union[V11MessageEvent, V12MessageEvent]):
            login_msg = await cls.get_or_none(qq=usr_id)
        elif isinstance(event, kaiheilaMessageEvent):
            login_msg = await cls.get_or_none(kook=usr_id)
        elif isinstance(event, qqguidMessageEvent):
            login_msg = await cls.get_or_none(qqguild=usr_id)
        else:
            login_msg = None
        return login_msg

    @classmethod
    async def which_adapter_id(cls, event: MessageEvent_):
        usr_id = event.get_user_id()
        if isinstance(event, Union[V11MessageEvent, V12MessageEvent]):
            login_msg = await cls.get_or_none(qq=usr_id)
        elif isinstance(event, kaiheilaMessageEvent):
            login_msg = await cls.get_or_none(kook=usr_id)
        elif isinstance(event, qqguidMessageEvent):
            login_msg = await cls.get_or_none(qqguild=usr_id)
        else:
            login_msg = None
        if login_msg is not None:
            return login_msg.id_
        return login_msg

    @classmethod
    async def new_bind(cls, event: MessageEvent_, usr_id: str = ""):
        """获取或创建新用户信息"""
        if not usr_id:
            usr_id = event.get_user_id()
        print(usr_id)
        if isinstance(event, Union[V11MessageEvent, V12MessageEvent]):
            login_msg, _ = await cls.get_or_create(qq=usr_id)
        elif isinstance(event, kaiheilaMessageEvent):
            login_msg, _ = await cls.get_or_create(kook=usr_id)
        elif isinstance(event, qqguidMessageEvent):
            login_msg, _ = await cls.get_or_create(qqguild=usr_id)
        return login_msg

    @classmethod
    async def add_bind(cls, event: MessageEvent_, bind_u: str, bind_id: str = ""):
        """添加绑定"""
        await cls.which_adapter(event)
        if await is_adapter(bind_u) is None:
            return False
        if record := await cls.get_or_none(id_=id):
            setattr(record, bind_u, int(bind_id))
            await record.save()
            return True
        await cls.new_bind(event)
        return None

    @classmethod
    async def del_bind(cls, id_: int, bind_u: str):
        """删除绑定"""
        if record := await cls.get_or_none(id_=id_):
            setattr(record, bind_u, None)
            await record.save()

    @classmethod
    async def del_all_bind(cls, id_: int):
        """删除全部绑定"""
        if record := await cls.get_or_none(id_=id_):
            await record.delete()
            await record.save()


class GetWife(Model):
    id_ = fields.IntField(pk=True, generated=True)
    user_id1 = fields.IntField()
    user_id2 = fields.IntField()
    group_id = fields.IntField()
    day_time = fields.DateField(default=date(2000, 1, 1))
    cd_time = fields.DatetimeField()
    ejaculation_cd = fields.DatetimeField()

    class Meta:
        table = "getwife"

    @classmethod
    async def add_wife(cls, user_id1: int, user_id2: int, group_id: int, time: date):
        msg, msg_is = await cls.get_or_create(
            user_id1=user_id1,
            user_id2=user_id2,
            group_id=group_id,
            last_time=time,
        )
        if msg_is:
            """新建操作"""
            return True
        return None

    @classmethod
    async def send_wife(cls, user_id: int, group_id: int):
        """查询输出对象"""
        return await cls.get_or_none(user_id=user_id, group_id=group_id)


class DailySign(Model):
    id_ = fields.IntField(pk=True, generated=True)
    nene_id = fields.IntField()
    gold = fields.IntField(default=0)
    sign_times = fields.IntField(default=0)
    last_sign = fields.DateField(default=date(2000, 1, 1))
    streak = fields.IntField(default=0)

    class Meta:
        table = "sign"

    @classmethod
    async def sign_in(cls, nene_id: int) -> SignData:
        """
        :说明: `sign_in`
        > 添加签到记录

        :参数:
          * `nene_id: int`: 用户ID

        :返回:
          - `SignData`: 签到数据
        """
        record, _ = await DailySign.get_or_create(nene_id=nene_id)

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
    async def get_last_sign(cls, nene_id: int) -> date:
        """
        :说明: `get_last_sign`
        > 获取最近的签到日期

        :参数:
          * `nene_id: int`: 用户ID

        :返回:
          - `date`: 签到日期
        """
        try:
            record, _ = await DailySign.get_or_create(
                nene_id=nene_id,
            )
        except Exception:
            record, _ = await DailySign.get_or_create(nene_id=nene_id, name="无名氏")
        return record.last_sign

    @classmethod
    async def get_gold(cls, nene_id: int) -> int:
        """
        :说明: `get_gold`
        > 获取金币

        :参数:
          * `nene_id: int`: 用户ID

        :返回:
          - `int`: 当前金币数量
        """
        record, _ = await DailySign.get_or_create(
            nene_id=nene_id,
        )
        return record.gold

    @classmethod
    async def adjust_gold(cls, adjust: int, nene_id: int) -> int:
        """
        :说明: `adjust_gold`
        > 调整金币

        :参数:
          * `adjust: int`: 调整金币数量 为正 则添加 为负 则减少
          * `nene_id: int`: 用户ID

        :返回:
          - `int`: 当前金币数量
        """
        record, _ = await DailySign.get_or_create(
            nene_id=nene_id,
        )
        record.gold += adjust
        await record.save(update_fields=["gold"])
        return record.gold
