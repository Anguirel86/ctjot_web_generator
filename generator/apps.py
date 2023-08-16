from hashlib import md5
from pathlib import Path
from typing import Dict

from django.apps import AppConfig


class GeneratorConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'generator'

    # map truncated path to each static .js file to it's MD5 checksum
    # to use as a "version" query for cache-busting
    # so browser consistently reloads js files on changes
    js_versions : Dict[str, str] = {
        str(Path(*path.parts[2:])): md5(path.read_bytes()).hexdigest()
        for path in Path('generator/static').rglob('*.js')
    }

