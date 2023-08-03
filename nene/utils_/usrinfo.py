import asyncio
import hashlib
from typing import List, Optional, Union

import httpx
from nonebot import on_command
from nonebot.log import logger
from nonebot_plugin_userinfo import UserInfo, get_user_info
from pydantic import BaseModel

from .event import (
    Bot_,
    GroupEvent_,
    MessageEvent_,
    V11Bot,
    V11GroupMessageEvent,
    V12Bot,
    V12GroupMessageEvent,
    kaiheilaBot,
    kaiheilaChannelMessageEvent,
    qqguidBot,
    qqguidChannelEvent,
)

a = on_command("测试")


@a.handle()
async def get_group_usrinfo_list(bot: qqguidBot, event: qqguidChannelEvent):
    msg_list = await bot.channel_userList(channel_id=event.guild_id)
    logger.info(msg_list)


class GourpUserinfo(BaseModel):
    user_id: Optional[str]
    username: Optional[str]
    nickname: Optional[str] = None
    avatar: Optional[str] = None


async def download_avatar(user_id: int) -> str:
    url = f"http://q1.qlogo.cn/g?b=qq&nk={user_id}&s=640"
    data = await download_url(url)
    if hashlib.md5(data).hexdigest() == "acef72340ac0e914090bd35799f5594e":
        url = f"http://q1.qlogo.cn/g?b=qq&nk={user_id}&s=100"
    return url


async def download_url(url: str) -> bytes:
    async with httpx.AsyncClient() as client:
        for _i in range(3):
            try:
                resp = await client.get(url, timeout=20)
                resp.raise_for_status()
                if resp:
                    return resp.content
            except Exception:
                await asyncio.sleep(3)
    raise Exception(f"{url} 下载失败！")


class GroupInfo(BaseModel):
    def __init__(self):
        ...

    async def get_group_usrinfo_list(self, bot: Bot_, event: GroupEvent_):
        """获取群聊用户信息"""
        msg_list: List[UserInfo] = []
        if isinstance(bot, V11Bot) and isinstance(event, V11GroupMessageEvent):
            logger.info("V11")
            msg_lists = await bot.get_group_member_list(group_id=event.group_id)
            for one_msg in msg_lists:
                msg = await get_user_info(bot, event, one_msg["user_id"])
                if msg:
                    msg_list.append(msg)
        elif isinstance(bot, V12Bot) and isinstance(event, V12GroupMessageEvent):
            logger.info("V12")
            msg_lists = await bot.get_group_member_list(group_id=event.group_id)
            for one_msg in msg_lists:
                msg = await get_user_info(bot, event, one_msg["user_id"])
                if msg:
                    msg_list.append(msg)
        elif isinstance(bot, kaiheilaBot) and isinstance(
            event,
            kaiheilaChannelMessageEvent,
        ):
            if not event.extra.guild_id:
                return None
            msg_lists = await bot.guild_userList(
                guild_id=event.extra.guild_id,
                channel_id=event.group_id,
            )
            if not msg_lists.users:
                return None
            for one_msg in msg_lists.users:
                if one_msg.id_:
                    msg = await get_user_info(bot, event, one_msg.id_)
                    if msg:
                        msg_list.append(msg)

        elif isinstance(bot, qqguidBot) and isinstance(event, qqguidChannelEvent):
            logger.warning("qq频道暂不支持获取用户列表,to do")
            return None
        else:
            return None
        logger.info(msg_list)
        return msg_list

    async def get_group_id(self, event: GroupEvent_):
        """获取群聊组号"""
        if isinstance(
            event,
            Union[
                V11GroupMessageEvent,
                V12GroupMessageEvent,
                kaiheilaChannelMessageEvent,
            ],
        ):
            msg = int(event.group_id)
        elif isinstance(event, qqguidChannelEvent):
            msg = event.guild_id
        else:
            msg = None
        if msg is None:
            msg = 114514
        return msg


class UsrInfo(BaseModel):
    def __init__(self):
        ...

    async def get_user_id(self, event: MessageEvent_):
        """获取事件对象组号"""
        if isinstance(
            event,
            Union[
                V11GroupMessageEvent,
                V12GroupMessageEvent,
                kaiheilaChannelMessageEvent,
            ],
        ):
            return int(event.user_id)
        if isinstance(event, qqguidChannelEvent):
            return event.guild_id
        return None


G = GroupInfo()
U = UsrInfo()
