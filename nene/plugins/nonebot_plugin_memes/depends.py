from typing import List

from meme_generator.meme import Meme
from nonebot.adapters.kaiheila import Bot as KookBot
from nonebot.adapters.kaiheila import Message as KookMsg
from nonebot.adapters.kaiheila import MessageSegment as KookMsgSeg
from nonebot.adapters.kaiheila.event import MessageEvent as KookMsgEvent
from nonebot.adapters.onebot.v11 import Bot as V11Bot
from nonebot.adapters.onebot.v11 import Message as V11Msg
from nonebot.adapters.onebot.v11 import MessageEvent as V11MEvent
from nonebot.adapters.onebot.v11 import MessageSegment as V11MsgSeg
from nonebot.adapters.onebot.v11.utils import unescape
from nonebot.adapters.onebot.v12 import Bot as V12Bot
from nonebot.adapters.onebot.v12 import Message as V12Msg
from nonebot.adapters.onebot.v12 import MessageEvent as V12MEvent
from nonebot.adapters.onebot.v12 import MessageSegment as V12MsgSeg
from nonebot.log import logger
from nonebot.params import Depends
from nonebot.typing import T_State
from nonebot_plugin_userinfo import get_user_info

from .config import memes_config
from .data_source import (
    ImageSource,
    ImageUrl,
    KookUser,
    User,
    V11User,
    V12User,
    check_user_id,
    user_avatar,
)
from .utils import split_text

MSG_KEY = "MSG"
TEXTS_KEY = "TEXTS"
USERS_KEY = "USERS"
IMAGE_SOURCES_KEY = "IMAGE_SOURCES"


def restore_last_at_me_seg(event: V11MEvent, msg: V11Msg):
    def _is_at_me_seg(seg: V11MsgSeg):
        return seg.type == "at" and str(seg.data["qq"]) == str(event.self_id)

    if event.to_me:
        raw_msg = event.original_message
        i = -1
        last_msg_seg = raw_msg[i]
        if (
            last_msg_seg.type == "text"
            and not str(last_msg_seg.data["text"]).strip()
            and len(raw_msg) >= 2
        ):
            i -= 1
            last_msg_seg = raw_msg[i]

        if _is_at_me_seg(last_msg_seg):
            msg.append(last_msg_seg)


def restore_last_mention_me_seg(event: V12MEvent, msg: V12Msg):
    def _is_mention_me_seg(seg: V12MsgSeg):
        return seg.type == "mention" and str(seg.data["user_id"]) == str(
            event.self.user_id,
        )

    if event.to_me:
        raw_msg = event.original_message
        i = -1
        last_msg_seg = raw_msg[i]
        if (
            last_msg_seg.type == "text"
            and not str(last_msg_seg.data["text"]).strip()
            and len(raw_msg) >= 2
        ):
            i -= 1
            last_msg_seg = raw_msg[i]

        if _is_mention_me_seg(last_msg_seg):
            msg.append(last_msg_seg)


def restore_last_mentionk_me_seg(event: KookMsgEvent, msg: KookMsg):
    def _is_at_me_seg(seg: KookMsgSeg):
        return seg.type == "at" and str(seg.data["qq"]) == str(event.self_id)

    if event.is_tome():
        raw_msg = event.get_message()
        i = -1
        last_msg_seg = raw_msg[i]
        if (
            last_msg_seg.type == "text"
            and not str(last_msg_seg.data["text"]).strip()
            and len(raw_msg) >= 2
        ):
            i -= 1
            last_msg_seg = raw_msg[i]

        if _is_at_me_seg(last_msg_seg):
            msg.append(last_msg_seg)


def split_msg_v11(meme: Meme):
    async def dependency(bot: V11Bot, event: V11MEvent, state: T_State):
        texts: List[str] = []
        users: List[User] = []
        image_sources: List[ImageSource] = []

        msg: V11Msg = state[MSG_KEY]
        restore_last_at_me_seg(event, msg)

        if event.reply:
            for msg_seg in event.reply.message["image"]:
                image_sources.append(ImageUrl(url=msg_seg.data["url"]))

        for msg_seg in msg:
            if msg_seg.type == "at":
                image_sources.append(user_avatar(bot, event, str(msg_seg.data["qq"])))
                users.append(V11User(bot, event, int(msg_seg.data["qq"])))

            elif msg_seg.type == "image":
                image_sources.append(ImageUrl(url=msg_seg.data["url"]))

            elif msg_seg.type == "text":
                raw_text = msg_seg.data["text"]
                for text in split_text(raw_text):
                    if text.startswith("@") and check_user_id(bot, text[1:]):
                        user_id = text[1:]
                        image_sources.append(user_avatar(bot, event, user_id))
                        users.append(V11User(bot, event, int(user_id)))

                    elif text == "自己":
                        image_sources.append(
                            user_avatar(bot, event, str(event.user_id)),
                        )
                        users.append(V11User(bot, event, event.user_id))

                    elif text := unescape(text):
                        texts.append(text)

        # 当所需图片数为 2 且已指定图片数为 1 时，使用 发送者的头像 作为第一张图
        if meme.params_type.min_images == 2 and len(image_sources) == 1:
            image_sources.insert(0, user_avatar(bot, event, str(event.user_id)))
            users.insert(0, V11User(bot, event, event.user_id))

        # 当所需图片数为 1 且没有已指定图片时，使用发送者的头像
        if memes_config.memes_use_sender_when_no_image and (
            meme.params_type.min_images == 1 and len(image_sources) == 0
        ):
            image_sources.append(user_avatar(bot, event, str(event.user_id)))
            users.append(V11User(bot, event, event.user_id))

        # 当所需文字数 >0 且没有输入文字时，使用默认文字
        texts = state.get(TEXTS_KEY, []) + texts
        if memes_config.memes_use_default_when_no_text and (
            meme.params_type.min_texts > 0 and len(texts) == 0
        ):
            texts = meme.params_type.default_texts

        state[TEXTS_KEY] = texts
        state[USERS_KEY] = users
        state[IMAGE_SOURCES_KEY] = image_sources

    return Depends(dependency)


def split_msg_v12(meme: Meme):
    async def dependency(bot: V12Bot, event: V12MEvent, state: T_State):
        texts: List[str] = []
        users: List[User] = []
        image_sources: List[ImageSource] = []

        msg: V12Msg = state[MSG_KEY]
        restore_last_mention_me_seg(event, msg)

        for msg_seg in msg:
            if msg_seg.type == "mention":
                image_sources.append(user_avatar(bot, event, msg_seg.data["user_id"]))
                users.append(V12User(bot, event, msg_seg.data["user_id"]))

            elif msg_seg.type == "image":
                file_id = msg_seg.data["file_id"]
                data = await bot.get_file(type="url", file_id=file_id)
                image_sources.append(ImageUrl(url=data["url"]))

            elif msg_seg.type == "text":
                raw_text = msg_seg.data["text"]
                for text in split_text(raw_text):
                    if text.startswith("@") and check_user_id(bot, text[1:]):
                        user_id = text[1:]
                        image_sources.append(user_avatar(bot, event, user_id))
                        users.append(V12User(bot, event, user_id))

                    elif text == "自己":
                        image_sources.append(user_avatar(bot, event, event.user_id))
                        users.append(V12User(bot, event, event.user_id))

                    elif text:
                        texts.append(text)

        # 当所需图片数为 2 且已指定图片数为 1 时，使用 发送者的头像 作为第一张图
        if meme.params_type.min_images == 2 and len(image_sources) == 1:
            image_sources.insert(0, user_avatar(bot, event, event.user_id))
            users.insert(0, V12User(bot, event, event.user_id))

        # 当所需图片数为 1 且没有已指定图片时，使用发送者的头像
        if memes_config.memes_use_sender_when_no_image and (
            meme.params_type.min_images == 1 and len(image_sources) == 0
        ):
            image_sources.append(user_avatar(bot, event, event.user_id))
            users.append(V12User(bot, event, event.user_id))

        # 当所需文字数 >0 且没有输入文字时，使用默认文字
        texts = state.get(TEXTS_KEY, []) + texts
        if memes_config.memes_use_default_when_no_text and (
            meme.params_type.min_texts > 0 and len(texts) == 0
        ):
            texts = meme.params_type.default_texts

        state[TEXTS_KEY] = texts
        state[USERS_KEY] = users
        state[IMAGE_SOURCES_KEY] = image_sources

    return Depends(dependency)


async def split_msg_kook(meme: Meme):
    async def dependency(bot: KookBot, event: KookMsgEvent, state: T_State):
        texts: List[str] = []
        users: List[User] = []
        image_sources: List[ImageSource] = []

        msg: KookMsg = state[MSG_KEY]
        restore_last_mentionk_me_seg(event, msg)

        msg_kook = event.dict()["event"]
        at_kook_user: List[str] = msg_kook["mention"]
        for one_user in at_kook_user:
            user_info = await get_user_info(bot, event, one_user)
            if user_info and user_info.user_name:
                users.append(KookUser(bot, event, one_user))
        for one_user in at_kook_user:
            at_ko_user = await get_user_info(bot, event, one_user)
            if at_ko_user and at_ko_user.user_avatar:
                image_sources.append(user_avatar(bot, event, one_user))
            # 没有图文模式
            # elif msg_seg.type == "image":
            #     file_id = msg_seg.data["file_id"]
            #     data = await bot.get_file(type="url", file_id=file_id)
            #     image_sources.append(ImageUrl(url=data["url"]))
        logger.info(f"原消息:{msg}")
        for msg_seg in msg:
            # logger.info(f"消息类型:{msg_seg.type}")
            # logger.info(f"消息内容:{msg_seg.data}")
            if msg_seg.type == "text":
                raw_text: str = msg_seg.data["content"]
                while raw_text.count("(met)") >= 2:
                    # logger.info(f"当前信息是{raw_text}")
                    first_index = raw_text.find("(met)")
                    second_index = raw_text.find("(met)", first_index + 1)
                    raw_text = raw_text[:first_index] + raw_text[second_index + 5 :]

                # logger.info(f"最终的信息是{raw_text}")
                if raw_text:
                    for text in split_text(raw_text):
                        if text.startswith("@") and check_user_id(bot, text[1:]):
                            user_id = text[1:]
                            image_sources.append(user_avatar(bot, event, user_id))
                            users.append(KookUser(bot, event, user_id))

                        elif text == "自己":
                            image_sources.append(
                                user_avatar(bot, event, event.get_user_id()),
                            )
                            users.append(KookUser(bot, event, event.get_user_id()))

                        elif text:
                            texts.append(text)

        # 当所需图片数为 2 且已指定图片数为 1 时，使用 发送者的头像 作为第一张图
        if meme.params_type.min_images == 2 and len(image_sources) == 1:
            image_sources.insert(0, user_avatar(bot, event, event.get_user_id()))
            users.insert(0, KookUser(bot, event, event.get_user_id()))

        # 当所需图片数为 1 且没有已指定图片时，使用发送者的头像
        if memes_config.memes_use_sender_when_no_image and (
            meme.params_type.min_images == 1 and len(image_sources) == 0
        ):
            image_sources.append(user_avatar(bot, event, event.get_user_id()))
            users.append(KookUser(bot, event, event.get_user_id()))

        # 当所需文字数 >0 且没有输入文字时，使用默认文字
        texts = state.get(TEXTS_KEY, []) + texts
        if memes_config.memes_use_default_when_no_text and (
            meme.params_type.min_texts > 0 and len(texts) == 0
        ):
            texts = meme.params_type.default_texts

        state[TEXTS_KEY] = texts
        # logger.info("文字:", texts)
        state[USERS_KEY] = users
        # logger.info("用户数量:", len(users))
        state[IMAGE_SOURCES_KEY] = image_sources
        # logger.info("图片数量:", len(image_sources))

    return Depends(dependency)
