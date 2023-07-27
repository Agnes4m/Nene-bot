from io import BytesIO
from pathlib import Path
from typing import Union, Optional, get_args

from nonebot.adapters.onebot.v11 import Bot as V11Bot
from nonebot.adapters.onebot.v12 import Bot as V12Bot
from nonebot.adapters.qqguild import Bot as qqguidBot
from nonebot.adapters.kaiheila import Bot as kaiheilaBot
from nonebot.adapters.onebot.v11 import Message as V11Message
from nonebot.adapters.onebot.v12 import Message as V12Message
from nonebot.adapters.qqguild import Message as qqguidMessage
from nonebot.adapters.kaiheila import Message as kaiheilaMessage
from nonebot.adapters.qqguild import ChannelEvent as qqguidChannelEvent
from nonebot.adapters.onebot.v11 import MessageSegment as V11MessageSegment
from nonebot.adapters.onebot.v11.event import NoticeEvent as V11NoticeEvent
from nonebot.adapters.onebot.v12 import MessageSegment as V12MessageSegment
from nonebot.adapters.onebot.v12.event import NoticeEvent as V12NoticeEvent
from nonebot.adapters.qqguild import MessageSegment as qqguidMessageSegment
from nonebot.adapters.onebot.v11.event import MessageEvent as V11MessageEvent
from nonebot.adapters.onebot.v12.event import MessageEvent as V12MessageEvent
from nonebot.adapters.qqguild.event import MessageEvent as qqguidMessageEvent
from nonebot.adapters.kaiheila import MessageSegment as kaiheilaMessageSegment
from nonebot.adapters.kaiheila.event import NoticeEvent as kaiheilaNoticeEvent
from nonebot.adapters.kaiheila.event import MessageEvent as kaiheilaMessageEvent
from nonebot.adapters.onebot.v11 import GroupMessageEvent as V11GroupMessageEvent
from nonebot.adapters.onebot.v12 import GroupMessageEvent as V12GroupMessageEvent
from nonebot.adapters.onebot.v11.event import PrivateMessageEvent as V11PrivateEvent
from nonebot.adapters.onebot.v12.event import PrivateMessageEvent as V12PrivateEvent
from nonebot.adapters.kaiheila.event import PrivateMessageEvent as KaiheilaPrivateEvent
from nonebot.adapters.kaiheila.event import (
    ChannelMessageEvent as kaiheilaChannelMessageEvent,
)

# from nonebot.internal.adapter import Bot, Event
from nonebot_plugin_saa import (
    Text,
    Image,
    Mention,
    TargetQQGroup,
    MessageFactory,
    TargetQQPrivate,
    TargetOB12Unknow,
    TargetQQGuildChannel,
    TargetKaiheilaChannel,
    TargetKaiheilaPrivate,
)

# from nonebot_plugin_saa.utils.types import TMSF

MessageEvent_ = Union[
    V11MessageEvent, V12MessageEvent, kaiheilaMessageEvent, qqguidMessageEvent
]
"""消息事件"""
Message_ = Union[V11Message, V12Message, kaiheilaMessage, qqguidMessage]
"""消息信息"""
NoticeEvent_ = Union[V11NoticeEvent, V12NoticeEvent, kaiheilaNoticeEvent]
"""通知信息"""
GroupEvent_ = Union[
    V11GroupMessageEvent,
    V12GroupMessageEvent,
    kaiheilaChannelMessageEvent,
    qqguidChannelEvent,
]
"""群聊信息事件"""
for t in get_args(GroupEvent_):
    if issubclass(t, qqguidChannelEvent):
        t.__annotations__["group_id"] = t.__annotations__.get("guild_id", int)

Bot_ = Union[V11Bot, V12Bot, kaiheilaBot, qqguidBot]
"""机器人对象"""

PrivateEvent = Union[V11PrivateEvent, V12PrivateEvent, KaiheilaPrivateEvent]
"""私聊事件(qq频道暂无)"""

TargetGroup = (
    TargetQQGroup | TargetOB12Unknow,
    TargetKaiheilaChannel,
    TargetQQGuildChannel,
)
"""主动群聊事件"""
TargetPrivate = Union[TargetQQPrivate, TargetOB12Unknow, TargetKaiheilaPrivate]
"""主动私聊事件"""

MessageSegment_ = Union[
    V11MessageSegment, V12MessageSegment, kaiheilaMessageSegment, qqguidMessageSegment
]
"""构造信息"""


class MessageSender:
    def __init__(self):
        pass

    async def send_text(
        self, msg: str, usr_id: str | bool = False, reply: bool = False
    ):  # noqa: E501
        """发送文字信息

        Args:
            msg (str): 发送的信息
            usr_id (str, bool): 是否艾特,如果是str则选择艾特对象.
            reply (bool): 回复的消息对象,类型是消息事件,无参数则不回复

        Returns:
            None
        """
        if isinstance(usr_id, bool):
            send_msg = MessageFactory(msg)
            await send_msg.send(at_sender=usr_id, reply=reply)
        else:
            send_msg = MessageFactory([Text(msg), Mention(usr_id)])  # type: ignore
            await send_msg.send(reply=reply)

    async def send_Target(
        self,
        is_group: bool,
        adapter: str,
        text: Optional[str] = None,
        data: Optional[Union[str, bytes, Path, BytesIO]] = None,
        usr_id: Optional[str] = None,
        group_id: Optional[str] = None,
    ):
        """主动发送信息

        Args:
            is_group (bool):是否是群聊消息
            adapter (str): V11 | V12 | Kaiheila | qqguild
            data (Union[str,bytes,Path,BytesIO]): 发送的图片
            usr_id (str, bool): 是否艾特,如果是str则选择对象.
            reply (bool): 回复的消息对象,类型是消息事件,无参数则不回复

        Returns:
            None
        """
        if is_group and group_id:
            if adapter in ["V11", "V12"]:
                target = TargetQQGroup(group_id=int(group_id))
            # elif adapter == "V12":
            #     target = TargetOB12Unknow(group_id=group_id)
            elif adapter == "Kaiheila":
                target = TargetKaiheilaChannel(channel_id=str(group_id))
            elif adapter == "qqguild":
                target = TargetQQGuildChannel(channel_id=int(group_id))
            else:
                return

        elif not is_group and usr_id:
            if adapter in ["V11", "V12"]:
                target = TargetQQPrivate(user_id=int(usr_id))
            # elif adapter == "V12":
            #     target = TargetOB12Unknow(group_id=group_id)
            elif adapter == "Kaiheila":
                target = TargetKaiheilaPrivate(user_id=str(usr_id))
            elif adapter == "qqguild":
                ...
                # 暂无qq私聊
                # target = TargetQQGuildChannel(channel_id=int(group_id))
                return
            else:
                return
        else:
            return
        if text and not data:
            send_msg = MessageFactory(text)
        elif not text and data:
            send_msg = MessageFactory([Image(data)])
        elif text and data:
            send_msg = MessageFactory([Image(data), Text(text)])
        else:
            return
        await MessageFactory(send_msg).send_to(target)

    async def send_pic(
        self,
        data: Union[str, bytes, Path, BytesIO],
        usr_id: str | bool = False,
        reply: bool = False,
    ):
        """发送图片信息

        Args:
            data (Union[str,bytes,Path,BytesIO]): 发送的图片
            usr_id (str, bool): 是否艾特,如果是str则选择对象.
            reply (bool): 回复的消息对象,类型是消息事件,无参数则不回复

        Returns:
            _type_: _description_
        """
        if isinstance(usr_id, bool):
            send_msg = MessageFactory([Image(data)])
            await MessageFactory(send_msg).send(at_sender=usr_id, reply=reply)
        else:
            send_msg = MessageFactory([Image(data), Mention(usr_id)])
            await MessageFactory(send_msg).send(reply=reply)


S = MessageSender()
