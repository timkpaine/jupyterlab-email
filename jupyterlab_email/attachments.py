import base64
from html import escape
from io import BytesIO

import pandas as pd
from IPython.display import HTML

CUSTOM_TAG = "jupyterlab_email_data"
EXCEL_ENGINE = "xlsxwriter"


def attach(data, filename, type):
    if isinstance(data, (pd.DataFrame, pd.Series)):
        if type == "csv":
            data = data.to_csv()
        elif type == "tsv":
            data = data.to_csv(sep="\t")
        elif type in ("xls", "xlsx"):
            io = BytesIO()
            writer = pd.ExcelWriter(io, engine=EXCEL_ENGINE)
            data.to_excel(writer)
            writer.save()
            data = base64.b64encode(io.getvalue()).decode("ascii")
        elif type == "html":
            data = escape(data)

    if type not in ("csv", "tsv", "png", "pdf", "xls", "xlsx", "txt", "html"):
        raise ValueError(f"Attachment type not recognized {type}")

    if not filename.endswith("." + type):
        filename = filename + "." + type

    html = f'<{CUSTOM_TAG} filename="{filename}" localdata="{data}">(Attachment: {filename})</{CUSTOM_TAG}>'
    return HTML(html)


def latex(expression):
    import matplotlib.pyplot as plt

    _fig, ax = plt.subplots(figsize=(10, 1))
    ax.xaxis.set_visible(False)
    ax.yaxis.set_visible(False)
    ax.axis("off")
    plt.text(0, 0.6, rf"${expression}$", fontsize=25)
    plt.show()
