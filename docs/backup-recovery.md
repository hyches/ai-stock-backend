# Backup and Recovery Guide

This guide covers the backup and recovery procedures for the AI Stock Analysis Platform.

## Table of Contents
1. [Backup System Overview](#backup-system-overview)
2. [Automated Backups](#automated-backups)
3. [Manual Backups](#manual-backups)
4. [Recovery Procedures](#recovery-procedures)
5. [Backup Management](#backup-management)
6. [Troubleshooting](#troubleshooting)

## Backup System Overview

The backup system includes:
- Database backups
- Report files
- Configuration files
- Backup metadata

### Backup Structure
```
backups/
├── backup_20240315_020000/
│   ├── app.db
│   ├── reports/
│   └── backup_info.txt
├── backup_20240314_020000/
└── ...
```

## Automated Backups

### Schedule
- Daily backups at 2 AM
- Retention: Last 5 backups
- Location: `backups/` directory

### Configuration
1. Start the backup scheduler:
```bash
python scripts/schedule_backups.py
```

2. Monitor backup status:
```bash
tail -f logs/app.log
```

## Manual Backups

### Using the API
1. Create a backup:
```bash
curl -X POST http://localhost:8000/api/v1/backup
```

2. List backups:
```bash
curl http://localhost:8000/api/v1/backup/list
```

3. Clean up old backups:
```bash
curl -X DELETE http://localhost:8000/api/v1/backup/cleanup?keep_last_n=5
```

### Using Python
```python
from app.core.backup import BackupManager

# Create backup
backup_manager = BackupManager()
backup_path = backup_manager.create_backup()

# List backups
backups = backup_manager.list_backups()

# Clean up
backup_manager.cleanup_old_backups(keep_last_n=5)
```

## Recovery Procedures

### Full System Recovery
1. Stop the application
2. Restore from backup:
```bash
curl -X POST http://localhost:8000/api/v1/backup/restore/backups/backup_20240315_020000
```

3. Verify the restoration:
   - Check database integrity
   - Verify report files
   - Test API endpoints

### Partial Recovery
1. Database only:
```python
from app.core.backup import BackupManager
backup_manager = BackupManager()
backup_manager.restore_backup("backups/backup_20240315_020000", restore_reports=False)
```

2. Reports only:
```python
backup_manager.restore_backup("backups/backup_20240315_020000", restore_database=False)
```

## Backup Management

### Monitoring
- Check backup logs: `logs/app.log`
- Verify backup sizes
- Monitor disk space

### Maintenance
1. Regular verification:
```bash
# List backups
curl http://localhost:8000/api/v1/backup/list

# Check backup sizes
du -sh backups/*
```

2. Cleanup:
```bash
# Remove old backups
curl -X DELETE http://localhost:8000/api/v1/backup/cleanup?keep_last_n=5
```

## Troubleshooting

### Common Issues

1. **Backup Creation Fails**
   - Check disk space
   - Verify file permissions
   - Check application logs

2. **Restore Fails**
   - Verify backup integrity
   - Check file permissions
   - Ensure application is stopped

3. **Scheduler Issues**
   - Check process status
   - Verify cron job
   - Check system time

### Recovery Steps

1. **Failed Backup**
   ```bash
   # Check logs
   tail -f logs/app.log
   
   # Manual backup
   curl -X POST http://localhost:8000/api/v1/backup
   ```

2. **Failed Restore**
   ```bash
   # Verify backup
   ls -l backups/backup_20240315_020000
   
   # Manual restore
   curl -X POST http://localhost:8000/api/v1/backup/restore/backups/backup_20240315_020000
   ```

### Best Practices

1. **Regular Testing**
   - Test backup creation weekly
   - Verify restore monthly
   - Monitor backup sizes

2. **Security**
   - Secure backup storage
   - Encrypt sensitive data
   - Regular access review

3. **Documentation**
   - Keep recovery procedures updated
   - Document all manual interventions
   - Maintain backup logs 