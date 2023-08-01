from typing import Union

from tortoise import fields
from tortoise.models import Model

from nene.utils_.event import (
    MessageEvent_,
    V11MessageEvent,
    V12MessageEvent,
    qqguidMessageEvent,
    kaiheilaMessageEvent,
)


async def is_adapter(name: str):
    if name in ["qq", "qqguild", "kook", "Telegram", "Discord"]:
        return True
    elif name in ["Bilibili", "Arcaea", "Phigros"]:
        return False
    return None


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
            return login_msg.id
        return login_msg

    @classmethod
    async def new_bind(cls, event: MessageEvent_):
        """创建新用户信息"""
        usr_id = event.get_user_id()
        if isinstance(event, Union[V11MessageEvent, V12MessageEvent]):
            login_msg, _ = await cls.get_or_create(qq=usr_id)
        elif isinstance(event, kaiheilaMessageEvent):
            login_msg, _ = await cls.get_or_create(kook=usr_id)
        elif isinstance(event, qqguidMessageEvent):
            login_msg, _ = await cls.get_or_create(qqguild=usr_id)
        return login_msg

    @classmethod
    async def add_bind(cls, event: MessageEvent_, bind_u: str, bind_id: int):
        """添加绑定"""
        await cls.which_adapter(event)
        if await is_adapter(bind_u) is None:
            return False
        if record := await cls.get_or_none(id=id):
            setattr(record, bind_u, bind_id)
            await record.save()
            return True

    @classmethod
    async def del_bind(cls, id: int, bind_u: str):
        """删除绑定"""
        if record := await cls.get_or_none(id=id):
            setattr(record, bind_u, None)
            await record.save()

    @classmethod
    async def del_all_bind(cls, id: int):
        """删除全部绑定"""
        if record := await cls.get_or_none(id=id):
            await record.delete()
            await record.save()
