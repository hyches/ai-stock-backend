from enum import Enum

class UserRole(str, Enum):
    ADMIN = "admin"
    TRADER = "trader"
    VIEWER = "viewer" 