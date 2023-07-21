from typing import Optional, Union, List, get_args
from pathlib import Path
from io import BytesIO

from nonebot.adapters.onebot.v11.event import MessageEvent as V11MessageEvent
from nonebot.adapters.onebot.v12.event import MessageEvent as V12MessageEvent
from nonebot.adapters.kaiheila.event import MessageEvent as kaiheilaMessageEvent
from nonebot.adapters.qqguild.event import MessageEvent as qqguidMessageEvent

from nonebot.adapters.onebot.v11 import Message  as V11Message
from nonebot.adapters.onebot.v12 import Message  as V12Message
from nonebot.adapters.kaiheila import Message as kaiheilaMessage
from nonebot.adapters.qqguild import Message as qqguidMessage

from nonebot.adapters.onebot.v11.event import NoticeEvent as V11NoticeEvent
from nonebot.adapters.onebot.v12.event import NoticeEvent as V12NoticeEvent
from nonebot.adapters.kaiheila.event import NoticeEvent as kaiheilaNoticeEvent

from nonebot.adapters.onebot.v11 import MessageSegment as V11MessageSegment
from nonebot.adapters.onebot.v12 import MessageSegment as V12MessageSegment
from  nonebot.adapters.kaiheila import MessageSegment as kaiheilaMessageSegment
from  nonebot.adapters.qqguild import MessageSegment as qqguidMessageSegment

from nonebot.adapters.onebot.v11 import GroupMessageEvent as V11GroupMessageEvent
from nonebot.adapters.onebot.v12 import GroupMessageEvent as V12GroupMessageEvent
from  nonebot.adapters.kaiheila.event import ChannelMessageEvent as kaiheilaChannelMessageEvent
from  nonebot.adapters.qqguild import ChannelEvent as qqguidChannelEvent

from nonebot.adapters.onebot.v11 import Bot as V11Bot
from nonebot.adapters.onebot.v12 import Bot as V12Bot
from  nonebot.adapters.kaiheila import Bot as kaiheilaBot
from  nonebot.adapters.qqguild import Bot as qqguidBot

from nonebot.internal.adapter import Event,Bot

Event_ = Union[
    V11MessageEvent, V12MessageEvent,kaiheilaMessageEvent, qqguidMessageEvent
]
"""消息事件"""
Message_ = Union[
    V11Message, V12Message,kaiheilaMessage, qqguidMessage
]
"""消息信息"""
NoticeEvent_ = Union[
    V11NoticeEvent, V12NoticeEvent,kaiheilaNoticeEvent
]
"""通知信息"""
GroupEvent_ = Union[
    V11GroupMessageEvent,V12GroupMessageEvent,kaiheilaChannelMessageEvent,qqguidChannelEvent
]
"""群聊信息事件"""
for t in get_args(GroupEvent_):
    if issubclass(t, qqguidChannelEvent):
        t.__annotations__['group_id'] = t.__annotations__.get('guild_id', int)

Bot_ = Union[
    V11Bot,
    V12Bot,
    kaiheilaBot,
    qqguidBot
]
"""机器人对象"""


from nonebot_plugin_saa import Image, Text, Reply, Mention, MessageFactory
from nonebot_plugin_saa.utils.types import TMSF
from nonebot_plugin_saa import (
    TargetQQGroup,
    TargetQQGuildChannel,
    TargetOB12Unknow,
    TargetKaiheilaChannel,
)
MessageSegment_ = Union[V11MessageSegment,V12MessageSegment,kaiheilaMessageSegment,qqguidMessageSegment]




class MessageSender:
    def __init__(self):
        pass

    def send_text(self, msg: str, usr_id: Optional[str] = None, reply: Optional[Event_] = None):
        """发送文字信息

        Args:
            msg (str): 发送的信息
            usr_id (Optional[str], optional): 艾特的对象,无参数则不艾特.
            reply (Optional[Event_], optional): 回复的消息对象,类型是消息事件,无参数则不回复

        Returns:
            None
        """
        if usr_id:
            if reply:
                return MessageFactory([Text(msg), Reply(Event_.message_id)], Mention(usr_id)) # type: ignore
            else:
                return MessageFactory([Text(msg), Mention(usr_id)])
        else:
            if reply:
                return MessageFactory([Text(msg), Reply(Event_.message_id)]) # type: ignore
            else:
                return MessageFactory([Text(msg)])

    def send_pic(self, data: Union[str, bytes, Path, BytesIO], usr_id: Optional[str] = None, reply: Optional[Event_] = None):
        """发送图片信息

        Args:
            data (Union[str,bytes,Path,BytesIO]): 发送的图片
            usr_id (Optional[str], optional): 艾特的对象,无参数则不艾特.
            reply (Optional[Event_], optional): 回复的消息对象,类型是消息事件,无参数则不回复

        Returns:
            _type_: _description_
        """
        pic = [Image(data)]
        if usr_id:
            pic.append(Mention(usr_id))
        if reply:
            pic.append(Reply(Event_.message_id))
        return MessageFactory(pic)

S = MessageSender()