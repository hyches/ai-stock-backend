from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List, Dict
from app.core.backup import BackupManager
from app.core.logging import logger

router = APIRouter()
backup_manager = BackupManager()

@router.post("/backup", response_model=Dict[str, str])
async def create_backup(background_tasks: BackgroundTasks):
    """Create a new backup."""
    try:
        backup_path = backup_manager.create_backup()
        return {"message": "Backup created successfully", "path": backup_path}
    except Exception as e:
        logger.error(f"Backup creation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/backup/restore/{backup_path:path}")
async def restore_backup(backup_path: str):
    """Restore from a specific backup."""
    try:
        backup_manager.restore_backup(backup_path)
        return {"message": "Backup restored successfully"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Backup restoration failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/backup/list", response_model=List[Dict[str, str]])
async def list_backups():
    """List all available backups."""
    try:
        return backup_manager.list_backups()
    except Exception as e:
        logger.error(f"Failed to list backups: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/backup/cleanup")
async def cleanup_backups(keep_last_n: int = 5):
    """Clean up old backups, keeping only the specified number of recent backups."""
    try:
        backup_manager.cleanup_old_backups(keep_last_n)
        return {"message": f"Cleanup completed. Kept last {keep_last_n} backups."}
    except Exception as e:
        logger.error(f"Backup cleanup failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 