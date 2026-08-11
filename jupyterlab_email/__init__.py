from ._email import email as email_notebook
from .attachments import attach, latex
from .extension import load_jupyter_server_extension
from .nbconvert import run as run_nbconvert

__version__ = "0.3.1"


def _jupyter_server_extension_paths():
    return [{"module": "jupyterlab_email.extension"}]


def _jupyter_server_extension_points():
    return [{"module": "jupyterlab_email"}]


def _load_jupyter_server_extension(serverapp, nb6_entrypoint=False):
    load_jupyter_server_extension(serverapp)


def _jupyter_nbextension_paths():
    return [
        {
            "section": "tree",
            "src": "nbextension/static",
            "dest": "jupyterlab_email",
            "require": "jupyterlab_email/notebook",
        }
    ]
