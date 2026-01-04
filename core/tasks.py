"""
Scheduled tasks for Django Q
"""
import os
import subprocess
from datetime import datetime
from django.conf import settings


def backup_database():
    """
    Create a PostgreSQL backup using pg_dump.
    Scheduled to run daily via Django Q.
    """
    # Create backups directory if it doesn't exist
    backup_dir = os.path.join(settings.BASE_DIR.parent, 'backups')
    os.makedirs(backup_dir, exist_ok=True)
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = os.path.join(backup_dir, f'lifepal_backup_{timestamp}.sql')
    
    # Database credentials from settings
    db_config = settings.DATABASES['default']
    db_name = db_config['NAME']
    db_user = db_config['USER']
    db_password = db_config.get('PASSWORD', '')
    db_host = db_config.get('HOST', 'localhost')
    db_port = db_config.get('PORT', '5432')
    
    # Set PGPASSWORD environment variable for pg_dump
    env = os.environ.copy()
    if db_password:
        env['PGPASSWORD'] = db_password
    
    try:
        # Run pg_dump
        cmd = [
            'pg_dump',
            '-U', db_user,
            '-h', db_host,
            '-p', str(db_port),
            '-F', 'c',  # Custom format (compressed)
            '-f', backup_file,
            db_name
        ]
        
        subprocess.run(cmd, env=env, check=True, capture_output=True)
        
        # Clean up old backups (keep last 30 days)
        cleanup_old_backups(backup_dir, days=30)
        
        print(f"✓ Database backup created: {backup_file}")
        return f"Backup successful: {backup_file}"
        
    except subprocess.CalledProcessError as e:
        error_msg = f"Backup failed: {e.stderr.decode() if e.stderr else str(e)}"
        print(f"✗ {error_msg}")
        return error_msg


def cleanup_old_backups(backup_dir, days=30):
    """Remove backup files older than specified days"""
    import time
    
    current_time = time.time()
    cutoff_time = current_time - (days * 86400)  # days to seconds
    
    for filename in os.listdir(backup_dir):
        if filename.startswith('lifepal_backup_') and filename.endswith('.sql'):
            file_path = os.path.join(backup_dir, filename)
            file_modified = os.path.getmtime(file_path)
            
            if file_modified < cutoff_time:
                os.remove(file_path)
                print(f"Removed old backup: {filename}")


def backup_database_docker():
    """
    Alternative backup method for Docker deployments.
    Uses docker-compose exec to run pg_dump inside the container.
    """
    backup_dir = os.path.join(settings.BASE_DIR.parent, 'backups')
    os.makedirs(backup_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = os.path.join(backup_dir, f'lifepal_backup_{timestamp}.sql')
    
    try:
        # Run pg_dump via docker-compose
        cmd = [
            'docker-compose', 'exec', '-T', 'db',
            'pg_dump', '-U', 'postgres', 'lifepal'
        ]
        
        # Run command and write output to file
        with open(backup_file, 'w') as f:
            result = subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE, check=True)
        
        cleanup_old_backups(backup_dir, days=30)
        
        print(f"✓ Database backup created: {backup_file}")
        return f"Backup successful: {backup_file}"
        
    except subprocess.CalledProcessError as e:
        error_msg = f"Backup failed: {e.stderr.decode() if e.stderr else str(e)}"
        print(f"✗ {error_msg}")
        return error_msg
