from nonebot.adapters.onebot.v11 import MessageEvent
from nonebot.adapters.onebot.v11.permission import GROUP_ADMIN, GROUP_OWNER
from nonebot.permission import SUPERUSER, Permission
from nonebot.rule import Rule


def check_tome(is_tome: bool) -> Rule:  # noqa: FBT001
    def checker(event: MessageEvent) -> bool:
        if not is_tome:
            return True
        return event.is_tome()

    return Rule(checker)


def check_modify(modify_admin_only: bool) -> Permission:  # noqa: FBT001
    if modify_admin_only:
        return GROUP_OWNER | GROUP_ADMIN | SUPERUSER

    def permission() -> bool:
        return True

    return Permission(permission)
