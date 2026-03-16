from enum import Enum

class UserGroupEnum(str, Enum):
    USER = "USER"
    ADMIN = "ADMIN"
    MODERATOR = "MODERATOR"

class GenderEnum(str, Enum):
    MAN = "MAN"
    WOMAN = "WOMAN"
