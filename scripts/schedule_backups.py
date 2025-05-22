import schedule
import time
import logging
from app.core.backup import BackupManager
from app.core.logging import setup_logging

logger = setup_logging()

def perform_backup():
    """Perform a backup and cleanup old backups."""
    try:
        backup_manager = BackupManager()
        backup_path = backup_manager.create_backup()
        logger.info(f"Automated backup created at {backup_path}")
        
        # Cleanup old backups, keeping last 5
        backup_manager.cleanup_old_backups(keep_last_n=5)
        
    except Exception as e:
        logger.error(f"Automated backup failed: {str(e)}")

def main():
    """Schedule and run backups."""
    # Schedule daily backup at 2 AM
    schedule.every().day.at("02:00").do(perform_backup)
    
    logger.info("Backup scheduler started")
    
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    main() 