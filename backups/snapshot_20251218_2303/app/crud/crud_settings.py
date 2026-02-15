"""
CRUD operations for settings
"""
from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.settings import Settings
from app.schemas.settings import SettingsCreate, SettingsUpdate

class CRUDSettings:
    """CRUD operations for settings"""
    
    def get(self, db: Session, setting_id: int) -> Optional[Settings]:
        """Get a setting by ID"""
        return db.query(Settings).filter(Settings.id == setting_id).first()
    
    def get_by_key(self, db: Session, key: str) -> Optional[Settings]:
        """Get a setting by key"""
        return db.query(Settings).filter(Settings.key == key).first()
    
    def get_multi(self, db: Session, skip: int = 0, limit: int = 100) -> List[Settings]:
        """Get multiple settings"""
        return db.query(Settings).offset(skip).limit(limit).all()
    
    def create(self, db: Session, obj_in: SettingsCreate) -> Settings:
        """Create a new setting"""
        db_obj = Settings(**obj_in.dict())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def update(self, db: Session, db_obj: Settings, obj_in: SettingsUpdate) -> Settings:
        """Update a setting"""
        for field, value in obj_in.dict(exclude_unset=True).items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def delete(self, db: Session, setting_id: int) -> Settings:
        """Delete a setting"""
        obj = db.query(Settings).get(setting_id)
        db.delete(obj)
        db.commit()
        return obj

crud_settings = CRUDSettings() 