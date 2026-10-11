import base64
from unittest.mock import MagicMock, call

import nbformat
import pytest

from jupyterlab_email import _email


def test_make_email_embeds_images_and_attachments(tmp_path, monkeypatch):
    image = base64.b64encode(b"image").decode()
    attachment = base64.b64encode(b"workbook").decode()
    html = (
        '<div class="header"></div><div class="footer"></div>'
        '<a class="anchor-link">Link</a><table border="1"></table>'
        '<img src="image.png">'
        f'<img cell_id="cell" localdata="{image}">'
        f'<jupyterlab_email_data filename="report.xlsx" localdata="{attachment}"></jupyterlab_email_data>'
    )
    monkeypatch.setattr(_email, "run", lambda **kwargs: (html, 0))
    message = MagicMock()
    factory = MagicMock(return_value=message)
    monkeypatch.setattr(_email.emails, "html", factory)

    result, error = _email.make_email(
        str(tmp_path / "report.ipynb"), nbformat.v4.new_notebook(), "sender@example.com", header="Header", footer="Footer"
    )

    assert result is message
    assert error == 0
    content = factory.call_args.kwargs["html"]
    assert "Header" in content and "Footer" in content
    assert "anchor-link" not in content
    assert 'src="cid:cell_1.png"' in content
    assert "localdata" not in content
    assert message.attach.call_args_list == [
        call(filename="cell_1.png", content_disposition="inline", data=b"image"),
        call(filename="report.xlsx", content_disposition="inline", data=b"workbook"),
    ]


@pytest.mark.parametrize("stderr", ["CellExecutionError: \x1b[0;31mFailed\x1b[0m\n", "Converter failed"])
def test_nbconvert_preserves_error_details(tmp_path, monkeypatch, stderr):
    from jupyterlab_email import nbconvert

    process = MagicMock(returncode=1)
    process.communicate.return_value = (b"", stderr.encode())
    monkeypatch.setattr(nbconvert.subprocess, "Popen", lambda *args, **kwargs: process)
    monkeypatch.setattr(nbconvert.tempfile, "mkdtemp", lambda: str(tmp_path))

    result, error = nbconvert.run(name="report.ipynb", in_="{}")
    assert error == 1
    assert ("Failed" if "CellExecutionError" in stderr else stderr) in result
    assert "<pre>" in result
    assert "th.pivot_row_header{}" in result
    if "CellExecutionError" in stderr:
        assert '<span style="color: red">' in result
        assert "\x1b" not in result
