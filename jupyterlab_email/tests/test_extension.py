from unittest.mock import MagicMock

from jupyterlab_email.extension import load_jupyter_server_extension


class TestExtension:
    def test_load_jupyter_server_extension(self):
        m = MagicMock()

        m.web_app.settings = {}
        m.web_app.settings["base_url"] = "/test"
        load_jupyter_server_extension(m)
