from io import BytesIO
from pathlib import Path
from typing import Dict, List, Optional, Union, get_args

from nonebot.adapters import Event, MessageSegment
from nonebot.adapters.kaiheila import Bot as kaiheilaBot
from nonebot.adapters.kaiheila import Message as kaiheilaMessage

# from nonebot.adapters.kaiheila import MessageSegment as kaiheilaMSegment
from nonebot.adapters.kaiheila.event import (
    ChannelMessageEvent as kaiheilaCMEvent,
)
from nonebot.adapters.kaiheila.event import MessageEvent as kaiheilaMEvent
from nonebot.adapters.kaiheila.event import NoticeEvent as kaiheilaNoticeEvent
from nonebot.adapters.kaiheila.event import PrivateMessageEvent as KaiheilaPEvent
from nonebot.adapters.onebot.v11 import Bot as V11Bot
from nonebot.adapters.onebot.v11 import GroupMessageEvent as V11GMEvent
from nonebot.adapters.onebot.v11 import Message as V11Message

# from nonebot.adapters.onebot.v11 import MessageSegment as V11MSegment
# from nonebot.adapters.onebot.v11 import unescape
from nonebot.adapters.onebot.v11.event import MessageEvent as V11MEvent
from nonebot.adapters.onebot.v11.event import NoticeEvent as V11NoticeEvent
from nonebot.adapters.onebot.v11.event import PrivateMessageEvent as V11PEvent
from nonebot.adapters.onebot.v12 import Bot as V12Bot
from nonebot.adapters.onebot.v12 import ChannelMessageEvent as V12CMEvent
from nonebot.adapters.onebot.v12 import GroupMessageEvent as V12GMEvent
from nonebot.adapters.onebot.v12 import Message as V12Message

# from nonebot.adapters.onebot.v12 import MessageSegment as V12MSegment
from nonebot.adapters.onebot.v12.event import MessageEvent as V12MEvent
from nonebot.adapters.onebot.v12.event import NoticeEvent as V12NoticeEvent
from nonebot.adapters.onebot.v12.event import PrivateMessageEvent as V12PrivateEvent
from nonebot.adapters.qqguild import Bot as qqguidBot
from nonebot.adapters.qqguild import ChannelEvent as qqguidChannelEvent
from nonebot.adapters.qqguild import Message as qqguidMessage
from nonebot.adapters.qqguild.event import MessageEvent as qqguidMEvent
from nonebot_plugin_saa import (
    Image,
    Mention,
    MessageFactory,
    TargetKaiheilaChannel,
    TargetKaiheilaPrivate,
    TargetOB12Unknow,
    TargetQQGroup,
    TargetQQGuildChannel,
    TargetQQPrivate,
    Text,
)

# from nonebot_plugin_saa.utils.types import TMSF

MessageEvent_ = Union[
    V11MEvent,
    V12MEvent,
    kaiheilaMEvent,
    qqguidMEvent,
]
"""消息事件"""
Message_ = Union[V11Message, V12Message, kaiheilaMessage, qqguidMessage]
"""消息信息"""
NoticeEvent_ = Union[V11NoticeEvent, V12NoticeEvent, kaiheilaNoticeEvent]
"""通知信息"""
GroupEvent_ = Union[
    V11GMEvent,
    V12GMEvent,
    kaiheilaCMEvent,
    qqguidChannelEvent,
    V12CMEvent,
]
"""群聊信息事件"""
for t in get_args(GroupEvent_):
    if issubclass(t, qqguidChannelEvent):
        t.__annotations__["group_id"] = t.__annotations__.get("guild_id", int)

Bot_ = Union[V11Bot, V12Bot, kaiheilaBot, qqguidBot]
"""机器人对象"""

PrivateEvent = Union[V11PEvent, V12PrivateEvent, KaiheilaPEvent]
"""私聊事件(qq频道暂无)"""

TargetGroup = (
    TargetQQGroup,
    TargetOB12Unknow,
    TargetKaiheilaChannel,
    TargetQQGuildChannel,
)
"""主动群聊事件"""
TargetPrivate = Union[TargetQQPrivate, TargetOB12Unknow, TargetKaiheilaPrivate]
"""主动私聊事件"""


class MessageSender:
    def __init__(self):
        pass

    async def send_text(
        self,
        msg: str,
        usr_id: Union[str, bool] = False,
        reply=False,
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

    async def send_target(
        self,
        is_group,
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
        usr_id: Union[str, bool] = False,
        reply=False,
    ):
        """发送图片信息

        Args:
            data (Union[str,bytes,Path,BytesIO]): 发送的图片
            usr_id (str, bool): 是否艾特,如果是str则选择对象.
            reply (bool): 回复的消息对象,类型是消息事件,无参数则不回复

        Returns:
            None
        """
        if isinstance(usr_id, bool):
            send_msg = MessageFactory([Image(data)])
            await MessageFactory(send_msg).send(at_sender=usr_id, reply=reply)
        else:
            send_msg = MessageFactory([Image(data), Mention(usr_id)])
            await MessageFactory(send_msg).send(reply=reply)


class MSement:
    def __init__(self):
        pass

    async def get_at(
        self,
        event: Event,
    ):
        """获取at对象id列表

        Returns:
            List[str]
        """
        at_list: List[str] = []
        if isinstance(event, V11MEvent):
            msgment_list: List[MessageSegment] = event.dict()["message"]
            for one in msgment_list:
                if one.type == "at":
                    at_list.append(one.data["qq"])
        if isinstance(event, kaiheilaMEvent):
            msg_event: List[str] = event.dict()["event"]["mention"]
            at_list = msg_event
        if isinstance(event, qqguidMEvent):
            msg_list: List[Dict[str, str]] = event.dict()["mentions"]
            if msg_list:
                for one_msg in msg_list:
                    if one_msg:
                        at_list.append(str(one_msg["id"]))
        return at_list

    async def get_image(
        self,
        event: Event,
    ):
        """获取消息中图片列表

        Returns:
            List[str]
        """
        at_list: List[str] = []
        if isinstance(event, V11MEvent):
            msgment_list: List[MessageSegment] = event.dict()["message"]
            for one in msgment_list:
                if one.type == "at":
                    at_list.append(one.data["qq"])
        if isinstance(event, kaiheilaMEvent):
            msg_event: List[str] = event.dict()["event"]["mention"]
            at_list = msg_event
        if isinstance(event, qqguidMEvent):
            msg_list: List[Dict[str, str]] = event.dict()["mentions"]
            if msg_list:
                for one_msg in msg_list:
                    if one_msg:
                        at_list.append(str(one_msg["id"]))
        return at_list

    # async def get_text_user(self,bot: Bot_, event: Event):
    #     texts: List[str] = []
    #     """消息"""
    #     users: List[str] = []
    #     """获取对象"""
    #     image_sources: List[Union[str,bytes]] = []
    #     """图片信息url"""

    #     if isinstance(event,V11MEvent):
    #         msg_v11:List[V11MSegment] =event.dict()["message"]
    #         if event.reply:
    #             for msg_seg in event.reply.message["image"]:
    #                 image_sources.append(msg_seg.data["url"])

    #         for msg_seg in msg_v11:
    #             if msg_seg.type == "at":
    #                 at_user = await get_user_info(bot,event,str(msg_seg.data["qq"]))
    #                 if at_user and at_user.user_avatar:
    #                     image_sources.append(await (at_user.user_avatar).get_image())
    #                     users.append(str(msg_seg.data["qq"]))

    #             elif msg_seg.type == "image":
    #                 image_sources.append(msg_seg.data["url"])

    #             elif msg_seg.type == "text":
    #                 raw_text = msg_seg.data["text"]
    #                 for text in split_text(raw_text):
    #                     if text.startswith("@") and check_user_id(bot, text[1:]):
    #                         user_id = text[1:]
    #                         user_info = await get_user_info(bot,event,user_id)
    #                         if user_info and user_info.user_avatar:
    #                             image_sources.append(await (user_info.user_avatar).get_image())
    #                             users.append(user_id)

    #                     elif text == "自己":
    #                         my_info = await get_user_info(bot,event,event.get_user_id())
    #                         if my_info and my_info.user_avatar:
    #                             image_sources.append(await my_info.user_avatar.get_image())
    #                             users.append(event.get_user_id())

    #                     elif text := unescape(text):
    #                         texts.append(text)
    #     elif isinstance(event,V12MEvent):
    #         msg_v12:List[V12MSegment] =event.dict()["message"]
    #         for msg_seg in msg_v12:
    #             if msg_seg.type == "mention":
    #                 mention_user = await get_user_info(bot,event,msg_seg.data["user_id"])
    #                 if mention_user and mention_user.user_avatar:
    #                     image_sources.append(await mention_user.user_avatar.get_image())
    #                     users.append(msg_seg.data["user_id"])

    #             elif msg_seg.type == "image":
    #                 file_id = msg_seg.data["file_id"]
    #                 data = await bot.get_file(type="url", file_id=file_id)
    #                 image_sources.append(data["url"])

    #             elif msg_seg.type == "text":
    #                 raw_text = msg_seg.data["text"]
    #                 for text in split_text(raw_text):
    #                     if text.startswith("@") and check_user_id(bot, text[1:]):
    #                         user_id = text[1:]
    #                         user_info = await get_user_info(bot,event,user_id)
    #                         if user_info and user_info.user_avatar:
    #                             image_sources.append(await (user_info.user_avatar).get_image())
    #                             users.append(user_id)

    #                     elif text == "自己":
    #                         my_info = await get_user_info(bot,event,event.get_user_id())
    #                         if my_info and my_info.user_avatar:
    #                             image_sources.append(await my_info.user_avatar.get_image())
    #                             users.append(event.get_user_id())

    #                     elif text := unescape(text):
    #                         texts.append(text)

    #     elif isinstance(event,kaiheilaMEvent):
    #         msg_kook =  event.dict()["event"]
    #         at_kook_user:List[str] = msg_kook["mention"]
    #         users = at_kook_user
    #         for one_user in at_kook_user:
    #             at_ko_user = await get_user_info(bot,event,one_user)
    #             if at_ko_user and at_ko_user.user_avatar:
    #                 image_sources.append(await at_ko_user.user_avatar.get_image())
    #                     # users = at_user

    #             # elif msg_seg.type == "image":
    #             #     file_id = msg_seg.data["file_id"]
    #             #     data = await bot.get_file(type="url", file_id=file_id)
    #             #     image_sources.append(data["url"])

    #         raw_text = event.get_plaintext()
    #         for text in split_text(raw_text):
    #             if text.startswith("@") and check_user_id(bot, text[1:]):
    #                 user_id = text[1:]
    #                 user_info = await get_user_info(bot,event,user_id)
    #                 if user_info and user_info.user_avatar:
    #                     image_sources.append(await (user_info.user_avatar).get_image())
    #                     users.append(user_id)

    #             elif text == "自己":
    #                 my_info = await get_user_info(bot,event,event.get_user_id())
    #                 if my_info and my_info.user_avatar:
    #                     image_sources.append(await my_info.user_avatar.get_image())
    #                     users.append(event.get_user_id())

    #             elif text := unescape(text):
    #                 texts.append(text)
    #     return texts,users,image_sources


S = MessageSender()
M = MSement()
