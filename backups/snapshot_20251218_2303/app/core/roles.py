"""
User role definitions for the AI Stock Portfolio Platform Backend.

Defines the UserRole enum for role-based access control throughout the application.
"""
from enum import Enum

class UserRole(str, Enum):
    """
    Enum representing user roles for access control.
    Roles:
        ADMIN: Full administrative access
        TRADER: Standard trading access
        VIEWER: Read-only access
    """
    ADMIN = "admin"
    TRADER = "trader"
    VIEWER = "viewer" 