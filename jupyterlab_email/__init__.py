from ._email import email as email_notebook
from ._version import __version__
from .attachments import attach, latex
from .extension import load_jupyter_server_extension
from .nbconvert import run as run_nbconvert


def _jupyter_server_extension_paths():
    return [{"module": "jupyterlab_email.extension"}]
