import os
import shutil
import datetime
import logging
from pathlib import Path
from app.config import Settings

logger = logging.getLogger("ai_stock_analysis")
settings = Settings()

class BackupManager:
    def __init__(self):
        self.backup_dir = Path("backups")
        self.backup_dir.mkdir(exist_ok=True)
        
    def create_backup(self):
        """Create a backup of the database and important files."""
        try:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = self.backup_dir / f"backup_{timestamp}"
            backup_path.mkdir(exist_ok=True)
            
            # Backup database
            if os.path.exists("app.db"):
                shutil.copy2("app.db", backup_path / "app.db")
            
            # Backup reports directory
            reports_dir = Path("reports")
            if reports_dir.exists():
                shutil.copytree(reports_dir, backup_path / "reports", dirs_exist_ok=True)
            
            # Create backup metadata
            with open(backup_path / "backup_info.txt", "w") as f:
                f.write(f"Backup created at: {timestamp}\n")
                f.write(f"Database URL: {settings.DATABASE_URL}\n")
            
            logger.info(f"Backup created successfully at {backup_path}")
            return str(backup_path)
            
        except Exception as e:
            logger.error(f"Backup failed: {str(e)}")
            raise
    
    def restore_backup(self, backup_path: str):
        """Restore from a backup."""
        try:
            backup_dir = Path(backup_path)
            if not backup_dir.exists():
                raise ValueError(f"Backup directory {backup_path} does not exist")
            
            # Restore database
            db_backup = backup_dir / "app.db"
            if db_backup.exists():
                shutil.copy2(db_backup, "app.db")
            
            # Restore reports
            reports_backup = backup_dir / "reports"
            if reports_backup.exists():
                shutil.copytree(reports_backup, "reports", dirs_exist_ok=True)
            
            logger.info(f"Backup restored successfully from {backup_path}")
            
        except Exception as e:
            logger.error(f"Restore failed: {str(e)}")
            raise
    
    def list_backups(self):
        """List all available backups."""
        try:
            backups = []
            for backup_dir in self.backup_dir.glob("backup_*"):
                if backup_dir.is_dir():
                    backup_info = {
                        "path": str(backup_dir),
                        "created_at": backup_dir.name.split("_")[1],
                        "size": sum(f.stat().st_size for f in backup_dir.rglob("*") if f.is_file())
                    }
                    backups.append(backup_info)
            return sorted(backups, key=lambda x: x["created_at"], reverse=True)
            
        except Exception as e:
            logger.error(f"Failed to list backups: {str(e)}")
            raise
    
    def cleanup_old_backups(self, keep_last_n: int = 5):
        """Remove old backups, keeping only the last N backups."""
        try:
            backups = self.list_backups()
            if len(backups) > keep_last_n:
                for backup in backups[keep_last_n:]:
                    shutil.rmtree(backup["path"])
                    logger.info(f"Removed old backup: {backup['path']}")
                    
        except Exception as e:
            logger.error(f"Cleanup failed: {str(e)}")
            raise 