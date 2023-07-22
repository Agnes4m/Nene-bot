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
