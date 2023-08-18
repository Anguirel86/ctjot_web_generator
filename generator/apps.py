import os

from collections import defaultdict
from hashlib import md5
from pathlib import Path
from typing import DefaultDict

from django.apps import AppConfig


class GeneratorConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'generator'

    js_debug_query: DefaultDict[str, str] = defaultdict(lambda: '')

    # when DEBUG is not set, django is using ManifestStaticFilesStorage
    # to automatically manage hashing of static files and replacing
    # in templates, however, we want DEBUG in some settings like dev,
    # so this alternative method can be used there
    if bool(int(os.getenv("DEBUG", "0"))):
        # map truncated path to each static .js file to it's MD5 checksum
        # to use as a "version" query for cache-busting
        # so browser consistently reloads js files on changes
        js_debug_query = defaultdict(
            lambda: '',
            {
                str(Path(*path.parts[2:])): (
                    f"?v={md5(path.read_bytes()).hexdigest()}"
                )
                for path in Path('generator/static').rglob('*.js')
            }
        )
