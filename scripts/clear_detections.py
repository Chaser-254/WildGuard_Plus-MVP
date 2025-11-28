import os
import shutil
import argparse
import sys
from datetime import datetime, timezone

# Ensure project root is on sys.path so `import app` works when running
# this script directly from the project root or from the scripts/ folder.
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app import create_app, db


def _resolve_db_path(db_path: str, app_root: str) -> str:
    """Resolve DB path to absolute, handling both absolute and relative paths."""
    if os.path.isabs(db_path):
        return db_path
    # If relative, resolve relative to app root
    return os.path.join(app_root, db_path)


def backup_db(db_path: str) -> str:
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Database not found: {db_path}")
    ts = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    bak_path = f"{db_path}.bak-{ts}"
    shutil.copy2(db_path, bak_path)
    return bak_path


def clear_detections(app, remove_images: bool = False):
    from app.models.detection import Detection

    with app.app_context():
        total = Detection.query.count()
        print(f"Found {total} detections in the database.")

        if total == 0:
            print("No detections to remove.")
            return 0

        # Collect image paths before deleting rows
        image_paths = []
        if remove_images:
            detections = Detection.query.with_entities(Detection.image_path).all()
            for (img_path,) in detections:
                if not img_path:
                    continue
                # If path is relative, try to resolve against static/uploads
                if not os.path.isabs(img_path):
                    candidate = os.path.join(app.static_folder, 'uploads', img_path)
                else:
                    candidate = img_path
                image_paths.append(candidate)

        # Delete all detection rows
        deleted = db.session.query(Detection).delete()
        db.session.commit()
        print(f"Deleted {deleted} detection rows.")

        # Optionally remove image files
        removed_count = 0
        if remove_images and image_paths:
            for p in image_paths:
                try:
                    if os.path.exists(p):
                        os.remove(p)
                        removed_count += 1
                except Exception as e:
                    print(f"Failed to remove {p}: {e}")
            print(f"Removed {removed_count} image files from uploads (if present).")

        return deleted


def main():
    parser = argparse.ArgumentParser(description='Clear all detections from the WildGuard DB')
    parser.add_argument('--db', default=os.path.join('instance', 'wildguard.db'),
                        help='Path to the SQLite database file (default: instance/wildguard.db)')
    parser.add_argument('--remove-images', action='store_true',
                        help='Also remove uploaded image files referenced by detections')
    parser.add_argument('--yes', '-y', action='store_true', help='Skip confirmation prompt')

    args = parser.parse_args()

    # Resolve DB path relative to project root
    db_path = _resolve_db_path(args.db, str(ROOT))

    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}. Nothing to do.")
        return

    print(f"Backing up database: {db_path}")
    bak = backup_db(db_path)
    print(f"Backup created at: {bak}")

    if not args.yes:
        confirm = input("This will permanently delete all detections. Continue? [y/N]: ")
        if confirm.lower() not in ('y', 'yes'):
            print('Aborted by user.')
            return

    # Create app using the factory (loads config.default by default)
    # Update config to point to absolute DB path to avoid SQLAlchemy path resolution issues
    app = create_app()
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'

    deleted = clear_detections(app, remove_images=args.remove_images)
    print('Done.')


if __name__ == '__main__':
    main()
