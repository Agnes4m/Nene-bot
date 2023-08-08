from nonebot import on_command, on_fullmatch  # noqa: N999
from nonebot.adapters import Message
from nonebot.log import logger
from nonebot.matcher import Matcher
from nonebot.params import CommandArg
from nonebot.plugin import PluginMetadata
from nonebot_plugin_userinfo import EventUserInfo, UserInfo

from nene.plugins.models import LoginTable
from nene.plugins.sign import Config
from nene.utils_.event import MessageEvent_, S

from .data_source import bind_login, check_login_msg, get_sign_in

__plugin_meta__ = PluginMetadata(
    name="nonebot_plugin_dailysign",
    description="简单的签到插件",
    usage="发送 签到 即可",
    type="application",
    homepage="https://github.com/Agnes4m/nonebot-plugin-dailysign",
    config=Config,
    supported_adapters={"~onebot.v11"},
)

sign = on_fullmatch("签到", priority=5, block=False)
bind = on_command("绑定", priority=5, block=False)
check_bind = on_command("登录信息", aliases={"绑定信息"}, priority=5, block=False)


@sign.handle()
async def _(event: MessageEvent_, usr: UserInfo = EventUserInfo()):
    user_id = usr.user_id
    user_info = await LoginTable.new_bind(event, user_id)
    logger.info(user_info.id)
    logger.debug(f"用户 {user_info.id} 签到")
    msg = await get_sign_in(user_info.id)
    await S.send_text(msg)


@bind.handle()
async def _(event: MessageEvent_, matcher: Matcher, arg: Message = CommandArg()):
    text = arg.extract_plain_text().strip()
    text.replace("qq", "").replace("QQ", "")
    if text.isdigit() and 5 <= len(text) <= 12:
        if await bind_login(text, event):
            await matcher.send("绑定成功，可使用`绑定信息`指令查看")
        else:
            await matcher.send("绑定出错了、、")
        ...
    await matcher.send("参数不正确")


@check_bind.handle()
async def _(
    event: MessageEvent_,
    matcher: Matcher,
):
    data = await check_login_msg(event)
    if data is not None:
        msg = f"""
        'qq': {data.qq}
        'qq频道': {data.qqguild}
        'kook': {data.kook}
        'Telegram': {data.Telegram}
        'Discord': {data.Discord}
        'Bilibili': {data.Bilibili}
        'Arcaea': {data.Arcaea}
        'Phigros': {data.Phigros}
        """.strip()
        await matcher.send(msg)
    else:
        await matcher.send("没有绑定信息")
