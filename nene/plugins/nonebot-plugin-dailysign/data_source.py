from datetime import date

from nonebot.log import logger

from nene.plugins.models import DailySign, LoginTable
from nene.utils_.event import MessageEvent_


async def get_sign_in(nene_id: int):
    msg: str = ""
    last_sign = await DailySign.get_last_sign(nene_id)
    # 判断是否已签到
    today = date.today()
    logger.debug(f"last_sign: {last_sign}")
    logger.debug(f"today: {today}")
    if today == last_sign:
        return "你今天已经签到了，不要贪心噢。"

    # 签到名次
    sign_num = await DailySign.filter(last_sign=today).count() + 1

    # 设置签到
    data = await DailySign.sign_in(nene_id=nene_id)

    msg_txt = f"本群第 {sign_num} 位 签到完成\n"
    msg_txt += f"获得金币：+{data.today_gold} (总金币：{data.all_gold})\n"
    msg_txt += f"累计签到次数：{data.sign_times}\n"
    msg_txt += f"连续签到次数：{data.streak}\n"
    msg += msg_txt
    return msg


async def check_login_msg(event: MessageEvent_):
    return await LoginTable.which_adapter(event)


def split_text_and_number(text: str):
    """文字与数字分离"""
    string_part = ""
    number_part = ""

    for char in text:
        if char.isdigit():
            number_part += char
        else:
            string_part += char

    return string_part, number_part


async def bind_login(text, event):
    platform, account_number = split_text_and_number(text)
    return await LoginTable.add_bind(event, platform, account_number)
