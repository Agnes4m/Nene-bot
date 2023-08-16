from typing import List

DRAW_OUTPUT_TYPES = ["text", "image", "record", "video"]
MESSAGE_TYPES = ["command", "keyword", "regex"]


def is_list_str(value) -> bool:
    return isinstance(value, list) and all(isinstance(item, str) for item in value)


class RandomDetailConfig:
    draw_output: str
    message_type: str
    message: List[str]
    insert_message: List[str]
    delete_message: List[str]
    modify_admin_only: bool
    is_tome: bool
    output_prefix: str
    output_suffix: str
    is_at_sender: bool

    def __init__(self, dir_name: str, config_dict: dict):
        self.draw_output = config_dict.get("draw_output", "image")
        if self.draw_output not in DRAW_OUTPUT_TYPES:
            self.draw_output = "image"

        self.message_type = config_dict.get("message_type", "command")
        if self.message_type not in MESSAGE_TYPES:
            self.message_type = "command"

        self.message: List[str] = (
            config_dict.get("message", [f"随机{dir_name}"])
            if is_list_str(config_dict.get("message"))
            else [f"随机{dir_name}"]
        )

        if self.draw_output and self.draw_output == "image":
            self.insert_message: List[str] = (
                config_dict.get("insert_message", [f"添加{msg}" for msg in self.message])
                if is_list_str(config_dict.get("insert_message"))
                else [f"添加{msg}" for msg in self.message]
            )

            self.delete_message: List[str] = (
                config_dict.get("delete_message", [f"删除{msg}" for msg in self.message])
                if is_list_str(config_dict.get("delete_message"))
                else [f"删除{msg}" for msg in self.message]
            )

            self.modify_admin_only: bool = bool(config_dict.get("modify_admin_only"))

        self.is_tome: bool = bool(config_dict.get("is_tome"))

        self.output_prefix: str = config_dict.get("output_prefix", "")

        self.output_suffix: str = config_dict.get("output_suffix", "")

        self.is_at_sender: bool = bool(config_dict.get("is_at_sender"))


# class RandomDetailConfig:
#     def __init__(self, dir_name: str, config_dict: dict):
#         self.draw_output: Optional[str] = config_dict.get("draw_output", "image")
#         if self.draw_output not in DRAW_OUTPUT_TYPES:
#             self.draw_output = "image"

#         self.message_type: Optional[str] = config_dict.get("message_type", "command")
#         if self.message_type not in MESSAGE_TYPES:
#             self.message_type = "command"

#         self.message: List[str] = config_dict.get("message", [f"随机{dir_name}"]) if is_list_str(config_dict.get("message")) else [f"随机{dir_name}"]

#         if self.draw_output and self.draw_output == "image":
#             self.insert_message: List[str] = config_dict.get("insert_message", [f"添加{msg}" for msg in self.message]) if is_list_str(config_dict.get("insert_message")) else [f"添加{msg}" for msg in self.message]

#             self.delete_message: List[str] = config_dict.get("delete_message", [f"删除{msg}" for msg in self.message]) if is_list_str(config_dict.get("delete_message")) else [f"删除{msg}" for msg in self.message]

#             self.modify_admin_only: bool = bool(config_dict.get("modify_admin_only"))

#         self.is_tome: bool = bool(config_dict.get("is_tome"))

#         self.output_prefix: str = config_dict.get("output_prefix", "")

#         self.output_suffix: str = config_dict.get("output_suffix", "")

#         self.is_at_sender: bool = bool(config_dict.get("is_at_sender"))
