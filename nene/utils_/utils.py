# import shlex
# from typing import List

# from nonebot.adapters.onebot.v11 import Bot as V11


# def split_text(text: str) -> List[str]:
#     try:
#         return shlex.split(text)
#     except:
#         return text.split()

# def check_user_id(bot: Union[V11Bot, V12Bot], user_id: str) -> bool:
#     platform = "qq" if isinstance(bot, V11Bot) else bot.platform

#     if platform == "qq":
#         return user_id.isdigit() and 11 >= len(user_id) >= 5

#     return False
