"""Local configuration contract; never reads the developer's real Maps key."""
import importlib.util
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

spec=importlib.util.spec_from_file_location('preview',Path(__file__).resolve().parents[1]/'serve.py')
preview=importlib.util.module_from_spec(spec);spec.loader.exec_module(preview)

class MapConfigTests(unittest.TestCase):
    def test_missing_configuration_keeps_local_mode(self):
        with tempfile.TemporaryDirectory() as folder, patch.object(preview,'ROOT',Path(folder)), patch.dict(os.environ,{},clear=True):
            self.assertEqual(preview.map_config(),{'apiKey':'','mapId':'DEMO_MAP_ID'})

    def test_only_browser_map_settings_are_exposed(self):
        with tempfile.TemporaryDirectory() as folder, patch.object(preview,'ROOT',Path(folder)), patch.dict(os.environ,{},clear=True):
            (Path(folder)/'.env.maps.local').write_text('GOOGLE_MAPS_API_KEY="example-key"\nGOOGLE_MAPS_MAP_ID=example-map\nOTHER_SECRET=do-not-publish\n')
            self.assertEqual(preview.map_config(),{'apiKey':'example-key','mapId':'example-map'})

    def test_environment_override_does_not_rewrite_file(self):
        with tempfile.TemporaryDirectory() as folder, patch.object(preview,'ROOT',Path(folder)), patch.dict(os.environ,{'GOOGLE_MAPS_API_KEY':'override','GOOGLE_MAPS_MAP_ID':'override-map'},clear=True):
            path=Path(folder)/'.env.maps.local';path.write_text('GOOGLE_MAPS_API_KEY=file-key\n')
            self.assertEqual(preview.map_config(),{'apiKey':'override','mapId':'override-map'})
            self.assertEqual(path.read_text(),'GOOGLE_MAPS_API_KEY=file-key\n')

if __name__=='__main__':unittest.main()
