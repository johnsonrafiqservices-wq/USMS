"""
Management command: python manage.py backup_db

Creates a timestamped SQLite backup in BASE_DIR/backups/.
For PostgreSQL/MySQL, runs pg_dump / mysqldump via subprocess.
"""
import os
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Backup the database to the backups/ directory'

    def add_arguments(self, parser):
        parser.add_argument(
            '--keep', type=int, default=10,
            help='Number of most-recent backups to keep (default: 10)'
        )

    def handle(self, *args, **options):
        backup_dir = Path(settings.BASE_DIR) / 'backups'
        backup_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        db_cfg = settings.DATABASES['default']
        engine = db_cfg['ENGINE']

        if 'sqlite3' in engine:
            src = Path(db_cfg['NAME'])
            dest = backup_dir / f'db_backup_{timestamp}.sqlite3'
            shutil.copy2(src, dest)
            self.stdout.write(self.style.SUCCESS(f'SQLite backup saved: {dest}'))

        elif 'postgresql' in engine:
            dest = backup_dir / f'db_backup_{timestamp}.sql'
            cmd = [
                'pg_dump',
                f'--host={db_cfg.get("HOST", "localhost")}',
                f'--port={db_cfg.get("PORT", "5432")}',
                f'--username={db_cfg["USER"]}',
                f'--dbname={db_cfg["NAME"]}',
                f'--file={dest}',
            ]
            env = os.environ.copy()
            env['PGPASSWORD'] = db_cfg.get('PASSWORD', '')
            subprocess.run(cmd, env=env, check=True)
            self.stdout.write(self.style.SUCCESS(f'PostgreSQL backup saved: {dest}'))

        elif 'mysql' in engine:
            dest = backup_dir / f'db_backup_{timestamp}.sql'
            cmd = [
                'mysqldump',
                f'--host={db_cfg.get("HOST", "localhost")}',
                f'--port={db_cfg.get("PORT", "3306")}',
                f'--user={db_cfg["USER"]}',
                f'--password={db_cfg.get("PASSWORD", "")}',
                db_cfg['NAME'],
            ]
            with open(dest, 'w') as f:
                subprocess.run(cmd, stdout=f, check=True)
            self.stdout.write(self.style.SUCCESS(f'MySQL backup saved: {dest}'))

        else:
            self.stderr.write(f'Unsupported engine: {engine}')
            return

        # Prune old backups
        keep = options['keep']
        backups = sorted(backup_dir.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True)
        for old in backups[keep:]:
            old.unlink()
            self.stdout.write(f'Removed old backup: {old.name}')
