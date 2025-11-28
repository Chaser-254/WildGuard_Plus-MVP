import os
import shutil
from datetime import datetime, timezone

import click

from app import db


def _find_sqlite_path(app):
    """Resolve SQLite DB path from app config or instance folder."""
    uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
    if uri and uri.startswith('sqlite:'):
        # formats: sqlite:///absolute/path or sqlite:///:memory:
        if uri == 'sqlite:///:memory:':
            return None
        # strip prefix sqlite:///
        path = uri.split('sqlite:///')[-1]
        # Convert to absolute if relative
        if not os.path.isabs(path):
            path = os.path.join(app.root_path, '..', path)
        return os.path.normpath(path)
    # fallback to instance/wildguard.db
    return os.path.join(app.instance_path, 'wildguard.db')


def _backup_db(db_path: str) -> str:
    if not db_path or not os.path.exists(db_path):
        raise FileNotFoundError(f"Database not found: {db_path}")
    ts = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    bak = f"{db_path}.bak-{ts}"
    shutil.copy2(db_path, bak)
    return bak


def register_commands(app):
    @app.cli.command('clear-detections')
    @click.option('--remove-images', is_flag=True, help='Also remove uploaded image files')
    @click.option('--yes', '-y', is_flag=True, help='Skip confirmation prompt')
    def clear_detections_cmd(remove_images, yes):
        """Delete all Detection rows from the database (creates a backup first)."""
        from flask import current_app
        from app.models.detection import Detection

        db_path = _find_sqlite_path(app)
        if not db_path:
            click.echo('Could not determine SQLite DB path from configuration.')
            return

        if not os.path.exists(db_path):
            click.echo(f'Database not found at {db_path}. Nothing to do.')
            return

        click.echo(f'Backing up database: {db_path}')
        try:
            bak = _backup_db(db_path)
        except Exception as e:
            click.echo(f'Failed to back up DB: {e}')
            return
        click.echo(f'Backup created at: {bak}')
        
        # Update app config to use absolute path to avoid SQLAlchemy resolution issues
        app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'

        if not yes:
            if not click.confirm('This will permanently delete all detections. Continue?'):
                click.echo('Aborted.')
                return

        with app.app_context():
            total = Detection.query.count()
            click.echo(f'Found {total} detections.')

            image_paths = []
            if remove_images and total > 0:
                rows = Detection.query.with_entities(Detection.image_path).all()
                for (img_path,) in rows:
                    if not img_path:
                        continue
                    if not os.path.isabs(img_path):
                        candidate = os.path.join(app.static_folder, 'uploads', img_path)
                    else:
                        candidate = img_path
                    image_paths.append(candidate)

            deleted = db.session.query(Detection).delete()
            db.session.commit()
            click.echo(f'Deleted {deleted} detection rows.')

            removed_count = 0
            if remove_images and image_paths:
                for p in image_paths:
                    try:
                        if os.path.exists(p):
                            os.remove(p)
                            removed_count += 1
                    except Exception as e:
                        click.echo(f'Failed to remove {p}: {e}')
                click.echo(f'Removed {removed_count} image files (if present).')
