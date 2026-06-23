import shutil
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent
BACKUP_DIR = ROOT / "backups"
REPORTS_DIR = ROOT / "reports"

BACKUP_DIR.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
current_backup = BACKUP_DIR / f"backup_{timestamp}"
current_backup.mkdir(exist_ok=True)

files_to_backup = [
    "seo_history.db",
    "seo_cache.db",
    ".env",
]

for file_name in files_to_backup:
    source = ROOT / file_name
    if source.exists():
        shutil.copy2(source, current_backup / file_name)

if REPORTS_DIR.exists():
    shutil.copytree(
        REPORTS_DIR,
        current_backup / "reports",
        dirs_exist_ok=True
    )

print(f"Backup completed: {current_backup}")