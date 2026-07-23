import os
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import mock

from django.test import SimpleTestCase

from config.settings import _load_dotenv_file


class DotenvAutoloadTests(SimpleTestCase):
    def test_loads_provider_key_for_command_runtime(self):
        with TemporaryDirectory() as temp_dir:
            dotenv_path = Path(temp_dir) / ".env"
            dotenv_path.write_text("TOGETHER_API_KEY=test-key\n", encoding="utf-8")

            with mock.patch.dict(os.environ, {}, clear=False):
                os.environ.pop("TOGETHER_API_KEY", None)
                _load_dotenv_file(dotenv_path)
                self.assertEqual(os.getenv("TOGETHER_API_KEY"), "test-key")

    def test_existing_env_value_is_not_overwritten(self):
        with TemporaryDirectory() as temp_dir:
            dotenv_path = Path(temp_dir) / ".env"
            dotenv_path.write_text("TOGETHER_API_KEY=from-dotenv\n", encoding="utf-8")

            with mock.patch.dict(os.environ, {"TOGETHER_API_KEY": "from-process"}, clear=False):
                _load_dotenv_file(dotenv_path)
                self.assertEqual(os.getenv("TOGETHER_API_KEY"), "from-process")

    def test_ignores_comments_blank_and_malformed_lines(self):
        with TemporaryDirectory() as temp_dir:
            dotenv_path = Path(temp_dir) / ".env"
            dotenv_path.write_text(
                "\n# comment\nBADLINE\n=missing_key\nVALID_KEY='quoted-value'\n",
                encoding="utf-8",
            )

            with mock.patch.dict(os.environ, {}, clear=False):
                os.environ.pop("VALID_KEY", None)
                os.environ.pop("BADLINE", None)
                _load_dotenv_file(dotenv_path)
                self.assertEqual(os.getenv("VALID_KEY"), "quoted-value")
                self.assertIsNone(os.getenv("BADLINE"))
