# from datetime import datetime
from time import time

# from typing import Optional
from nonebot import on_command
from nonebot.log import logger

# from nonebot_plugin_userinfo import get_user_info
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

a = time()

a = on_command("测试")


# @a.handle()
# async def get_group_usrinfo_list(bot: Bot_, event: GroupEvent_):
#     """获取信息"""
#     if isinstance(bot, V11Bot) and isinstance(event, V11GroupMessageEvent):
#         logger.info("V11")
#         msg_list = await bot.get_group_member_list(group_id=event.group_id)
#     elif isinstance(bot, V12Bot) and isinstance(event, V12GroupMessageEvent):
#         logger.info("V12")
#         msg_list = await bot.get_group_member_list(group_id=event.group_id)
#     elif isinstance(bot, kaiheilaBot) and isinstance(
#         event, kaiheilaChannelMessageEvent
#     ):
#         # logger.warning("kook暂不支持获取用户列表")
#         msg_list = await bot.channel_userList(channel_id=event.group_id)
#         logger.info(msg_list)
#         return
#     elif isinstance(bot, qqguidBot) and isinstance(event, qqguidChannelEvent):
#         logger.warning("qq频道暂不支持获取用户列表，to do")
#         return
#     else:
#         return
#     logger.info(msg_list)
#     await a.send(str(msg_list))


# a = on_command("测试")


@a.handle()
async def get_group_usrinfo_list(bot: qqguidBot, event: qqguidChannelEvent):
    msg_list = await bot.channel_userList(channel_id=event.guild_id)
    logger.info(msg_list)


class GroupInfo(BaseModel):
    def __init__(self):
        ...

    async def get_group_usrinfo_list(self, bot: Bot_, event: GroupEvent_):
        """获取群聊用户信息"""
        if isinstance(bot, V11Bot) and isinstance(event, V11GroupMessageEvent):
            logger.info("V11")
            msg_list = await bot.get_group_member_list(group_id=event.group_id)
        elif isinstance(bot, V12Bot) and isinstance(event, V12GroupMessageEvent):
            logger.info("V12")
            msg_list = await bot.get_group_member_list(group_id=event.group_id)
        elif isinstance(bot, kaiheilaBot) and isinstance(
            event, kaiheilaChannelMessageEvent
        ):
            if not event.extra.guild_id:
                return
            msg_list = await bot.guild_userList(
                guild_id=event.extra.guild_id, channel_id=event.group_id
            )
            logger.info(msg_list)
        elif isinstance(bot, qqguidBot) and isinstance(event, qqguidChannelEvent):
            logger.warning("qq频道暂不支持获取用户列表,to do")
            return
        else:
            return
        logger.info(msg_list)
        return msg_list

    async def get_group_id(self, event: GroupEvent_):
        """获取群聊组号"""
        if isinstance(
            event,
            V11GroupMessageEvent | V12GroupMessageEvent | kaiheilaChannelMessageEvent,
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
            V11GroupMessageEvent | V12GroupMessageEvent | kaiheilaChannelMessageEvent,
        ):
            return int(event.user_id)
        elif isinstance(event, qqguidChannelEvent):
            return event.guild_id
        else:
            return None


G = GroupInfo()
U = UsrInfo()
