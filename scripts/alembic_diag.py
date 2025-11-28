from alembic.config import Config
from alembic.script import ScriptDirectory
import os
cfg_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'migrations', 'alembic.ini')
print('alembic.ini path:', cfg_path)
cfg = Config(cfg_path)
cfg.set_main_option('script_location', os.path.join(os.path.dirname(os.path.dirname(__file__)), 'migrations'))
script = ScriptDirectory.from_config(cfg)
print('Revisions found:')
for rev in script.walk_revisions():
    print('rev:', rev.revision, 'down:', rev.down_revision)
print('Heads:', script.get_heads())
