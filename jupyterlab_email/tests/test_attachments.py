import base64
from io import BytesIO
from zipfile import ZipFile

import pandas as pd
from bs4 import BeautifulSoup

from jupyterlab_email.attachments import CUSTOM_TAG, attach


def test_excel_attachment_contains_workbook():
    result = attach(pd.DataFrame({"value": [42]}), "report", "xlsx")
    tag = BeautifulSoup(result.data, "html.parser").find(CUSTOM_TAG)
    assert tag is not None
    assert tag["filename"] == "report.xlsx"
    data = tag["localdata"]
    assert isinstance(data, str)
    with ZipFile(BytesIO(base64.b64decode(data))) as workbook:
        assert "xl/workbook.xml" in workbook.namelist()
        assert b"42" in workbook.read("xl/worksheets/sheet1.xml")
