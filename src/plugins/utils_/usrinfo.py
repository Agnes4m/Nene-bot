from nonebot_plugin_userinfo import get_user_info
from nonebot.log import logger
from .event import *
from nonebot import on_command
from pydantic import BaseModel
from time import time
from datetime import datetime
a = on_command("测试")

a = time()

from pydantic import BaseModel

class USRINFO_G_V11(BaseModel):
    """
    用户信息类
    """
    age: int  # 年龄
    area: str  # 地区
    card: str  # 群名片
    card_changeable: bool  # 是否允许修改群名片
    group_id: int  # 群号
    join_time: float  # 加入时间（时间戳）
    last_send_time: int  # 上次发言时间（时间戳）
    level: int  # 等级
    nickname: str  # 昵称
    role: str  # 角色
    sex: str  # 性别
    shut_up_timestamp: int  # 禁言截止时间（时间戳）
    title: str  # 头衔
    title_expire_time: int  # 头衔过期时间（时间戳）
    unfriendly: bool  # 是否允许该用户发送消息
    user_id: int  # QQ号

# a= on_command("测试")
# @a.handle()
# async def get_group_usrinfo_list(bot:Bot_,event:GroupEvent_):
#     """获取信息"""
#     if isinstance(bot,V11Bot) and isinstance(event,V11GroupMessageEvent):
#         logger.info("V11")
#         msg_list = await bot.get_group_member_list(group_id= event.group_id)
#     elif isinstance(bot,V12Bot) and isinstance(event,V12GroupMessageEvent):
#         logger.info("V12")
#         msg_list = await bot.get_group_member_list(group_id= event.group_id)
#     elif isinstance(bot,kaiheilaBot) and isinstance(event,kaiheilaChannelMessageEvent):
#         # logger.warning("kook暂不支持获取用户列表")
#         msg_list = await bot.channel_userList(channel_id=event.group_id)
#         logger.info(msg_list)
#         return
#     elif isinstance(bot,qqguidBot) and isinstance(event,qqguidChannelEvent):
#         logger.warning("qq频道暂不支持获取用户列表，to do")
#         return
#     else:
#         return
#     logger.info(msg_list)
    # await a.send(str(msg_list))

a= on_command("测试")
@a.handle()
async def get_group_usrinfo_list(bot:qqguidBot,event:qqguidChannelEvent):

    msg_list = await bot.channel_userList(channel_id=event.guild_id)
    logger.info(msg_list)
    