import random
from datetime import datetime
from typing import Set

import nonebot
from nonebot import require
from nonebot.matcher import Matcher
from nonebot.plugin.on import on_command

from nene.plugins.models import GetWife
from nene.utils_.event import Bot_, GroupEvent_
from nene.utils_.usrinfo import G

from .config import Config

global_config = nonebot.get_driver().config
config = Config.parse_obj(global_config.dict())

scheduler = require("nonebot_plugin_apscheduler").scheduler
waifu = on_command(
    "娶群友",
    aliases={"抽老婆", "选妃", "男同匹配", "男同配对"},
    priority=10,
    block=True,
)


@waifu.handle()
async def _(bot: Bot_, event: GroupEvent_, matcher: Matcher):
    group_id = await G.get_group_id(event)
    user_id = int(event.get_user_id())
    # 判断是否cd
    data_time = await GetWife.get_or_none(user_id=user_id, group_id=group_id)
    if data_time is not None:
        now_time = datetime.now()
        delta = (now_time - data_time.cd_time).total_seconds()
        cd = int(delta // 30) + (1 if delta % 60 > 0 else 0)
        if cd <= 60:
            flag = random.random()
            send_msg = [
                f"你的cd还有{round(cd/60,1)}分钟。",
                f"你已经问过了哦~ 你的cd还有{cd}分钟。",
                "哼！",
            ]
            if flag < 0.9:
                await matcher.finish(random.choice(send_msg), at_sender=True)
            else:
                t = random.randint(1, 10)
                await matcher.send(message=f"还问!罚时!你的cd还有{cd}+{t}分钟")
            matcher.stop_propagation()
    group_list = await G.get_group_usrinfo_list(bot, event)
    if group_list is None:
        return
    # 删除已经被抽的对象
    be_wifes: Set[str] = set()
    be_wife = await GetWife.filter(group_id=group_id).all()
    for one_wife in be_wife:
        be_wifes.add(str(one_wife.user_id1))
        be_wifes.add(str(one_wife.user_id2))
    for one_user in group_list:
        if one_user.user_id in be_wifes:
            group_list.remove(one_user)

    # 随机选一个
    wife_msg = random.choice(group_list)
    if wife_msg.user_id == user_id:
        # 抽到自己了
        await matcher.finish("")

    # req_user_card = req_user_info["card"]
    # # 判断别来抽老婆或者老公
    # if not r性eq_user_card:
    #     req_user_card = req_user_info["nickname"]
    # req_user_sex = req_user_info["sex"]
    # is_nick = "老婆" if req_user_sex == "male" else "老公"

    usr_list = await G.get_group_usrinfo_list(bot, event)
    if usr_list is None:
        return
    wife_msg = random.choice(usr_list)
