import os

from urllib.parse import quote, urljoin
from hashlib import md5
from pathlib import Path
from typing import Dict

from django.apps import AppConfig


class GeneratorConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'generator'

    def __init__(self, app_name, app_module):
        if bool(int(os.getenv("DEBUG", "0"))):
            self._monkey_patch_static_node()

        super(GeneratorConfig, self).__init__(app_name, app_module)

    @staticmethod
    def _monkey_patch_static_node():
        '''
        Updates 'static' template tag to append a query string on static
        assets to compel browser to consistently reload the updated files.

        When DEBUG is not set, django is using ManifestStaticFilesStorage
        to automatically manage hashing of static files and replacing
        in templates. However, we want DEBUG in some settings like dev,
        so use this alternative method there.
        '''
        # map truncated path to each static file to it's MD5 checksum
        md5sums: Dict[str, str] = {
            str(Path(*path.parts[2:])): md5(path.read_bytes()).hexdigest()
            for path in Path('generator/static').rglob('*')
            if path.is_file()
        }

        # monkeypatch the 'static' template tag to automatically
        # append a "?v={md5sum}" query on static files
        # to cache-bust browser caching when the files are updated
        from django.templatetags.static import PrefixNode, StaticNode

        def handle_simple_cache_bust(cls, path):
            quoted_path = quote(path)

            md5sum = md5sums.get(path)
            if md5sum:
                quoted_path += f"?v={md5sum}"

            return urljoin(PrefixNode.handle_simple("STATIC_URL"), quoted_path)

        StaticNode.handle_simple = classmethod(handle_simple_cache_bust)
