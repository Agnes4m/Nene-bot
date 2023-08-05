from typing import Union

from nonebot.adapters import Event as BaseEvent
from nonebot.adapters.kaiheila.event import Event as KEvent
from nonebot.adapters.onebot.v11.event import Event as V11Eevent
from nonebot.adapters.onebot.v12.event import ChannelMessageEvent as V12CMEvent
from nonebot.adapters.onebot.v12.event import MessageEvent as V12MEvent
from nonebot.adapters.qqguild.event import Event as qqguildE
from nonebot.adapters.telegram.event import Event as TEvent
from tortoise.exceptions import DoesNotExist

from nene.plugins.models import LoginTable


def get_user_id_(self: BaseEvent) -> str:
    """获取事件主体 id 的方法，通常是用户 id 。修改后返回为qqid"""
    if isinstance(self, Union[V11Eevent, V12MEvent]):
        return self.get_user_id()
    if isinstance(self, Union[qqguildE, V12CMEvent]):
        try:
            user_info = LoginTable.get(qqguild=self.get_user_id())
            # type: ignore
        except DoesNotExist:
            return ""
        return user_info.qq  # type: ignore
    if isinstance(self, KEvent):
        try:
            user_info = LoginTable.get(kook=self.get_user_id())
        except DoesNotExist:
            return ""
        return user_info.qq  # type: ignore
    if isinstance(self, TEvent):
        try:
            user_info = LoginTable.get(Telegram=self.get_user_id())
        except DoesNotExist:
            return ""
        return user_info.qq  # type: ignore
    raise NotImplementedError


BaseEvent.get_user_id = get_user_id_
