"""
Base class for SQLAlchemy models in the AI Stock Portfolio Platform Backend.

Provides automatic table name generation for all ORM models.
"""
from typing import Any
from sqlalchemy.ext.declarative import as_declarative, declared_attr

@as_declarative()
class Base:
    """
    Declarative base class for all SQLAlchemy ORM models.
    Automatically generates __tablename__ based on the class name.
    """
    id: Any
    __name__: str

    # Generate __tablename__ automatically
    @declared_attr
    def __tablename__(cls) -> str:
        """
        Generate the table name for the model based on the class name.

        Returns:
            str: Lowercase class name as table name.
        """
        return cls.__name__.lower() 