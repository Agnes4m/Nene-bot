import nonebot
import pytest
from nonebot.adapters.kaiheila import Adapter as 开黑啦Adapter
from nonebot.adapters.onebot.v11 import Adapter as ONEBOT_V11Adapter
from nonebot.adapters.onebot.v12 import Adapter as ONEBOT_V12Adapter
from nonebot.adapters.qqguild import Adapter as QQ_频道Adapter


@pytest.mark.asyncio
async def test_init():
    nonebot.init()

    driver = nonebot.get_driver()
    driver.register_adapter(ONEBOT_V11Adapter)

    driver.register_adapter(开黑啦Adapter)

    driver.register_adapter(QQ_频道Adapter)

    driver.register_adapter(ONEBOT_V12Adapter)

    nonebot.load_builtin_plugins("echo")

    nonebot.load_from_toml("pyproject.toml")
    assert True
