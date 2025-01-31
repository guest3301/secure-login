import os
import shutil
from datetime import datetime, timedelta


def restore_backup(date_str):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(script_dir, 'instance', 'database.sqlite')
    backup_path = os.path.join(script_dir, 'instance', f'database_{date_str}.sqlite.bak')
    if os.path.exists(backup_path):
        shutil.copy2(backup_path, db_path)
        os.remove(backup_path)
        return f'Backup for {date_str} restored successfully.'
    else:
        return f'Error: Backup for {date_str} not found. Date format: YYYY-MM-DD.'
    
def backup_database():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(script_dir, 'instance', 'database.sqlite')
    today = datetime.now()
    backup_path = os.path.join(script_dir, 'instance', f'database_{today.strftime("%Y-%m-%d")}.sqlite.bak')
    yesterday = today - timedelta(days=1)
    yesterday_backup_path = os.path.join(script_dir, 'instance', f'database_{yesterday.strftime("%Y-%m-%d")}.sqlite.bak')

    if os.path.exists(yesterday_backup_path):
        print(f'Backup for {yesterday.strftime("%Y-%m-%d")} already exists. Skipping backup.')
    else:
        shutil.copy2(db_path, backup_path)
        print(f'Backup created at: {backup_path}')
    
    three_days_ago = today - timedelta(days=3)
    for filename in os.listdir(os.path.join(script_dir, 'instance')):
        if filename.startswith('database_') and filename.endswith('.sqlite.bak'):
            date_str = filename[len('database_'):-len('.sqlite.bak')]
            file_date = datetime.strptime(date_str, "%Y-%m-%d")
            if file_date < three_days_ago:
                os.remove(os.path.join(script_dir, 'instance', filename))
                print(f'Deleted old backup: {filename}')

def db_path():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(script_dir, 'instance', 'database.sqlite')
    return db_path
    
if __name__ == "__main__":
    backup_database()