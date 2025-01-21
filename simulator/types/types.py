from enum import Enum


class Model4Use(Enum):
    GPT_4o_MINI = "gpt-4o-mini"
    DEEPSEEK = "deepseek"

    # a func given str back to Enum, if not found, return None
    # a function to get key from value
    @classmethod
    def get_key(cls, value):
        for key, member in cls.__members__.items():
            if member.value == value:
                return member
        return None

