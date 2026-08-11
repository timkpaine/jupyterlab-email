# jupyterlab_email

A jupyterlab extension to email notebooks from the browser.

[![Build Status](https://github.com/timkpaine/jupyterlab_email/actions/workflows/build.yaml/badge.svg?branch=main&event=push)](https://github.com/timkpaine/jupyterlab_email/actions/workflows/build.yaml)
[![codecov](https://codecov.io/gh/timkpaine/jupyterlab_email/branch/main/graph/badge.svg)](https://codecov.io/gh/timkpaine/jupyterlab_email)
[![License](https://img.shields.io/github/license/timkpaine/jupyterlab_email)](https://github.com/timkpaine/jupyterlab_email)
[![PyPI](https://img.shields.io/pypi/v/jupyterlab-email.svg)](https://pypi.python.org/pypi/jupyterlab-email)

![](https://raw.githubusercontent.com/timkpaine/jupyterlab_email/main/docs/example.gif)

## Options

- Inline notebook as email, with code
- Inline notebook as email, without code
- Send notebook as HTML attachment, with code
- Send notebook as HTML attachment, without code
- Send notebook as PDF attachment, with code
- Send notebook as PDF attachment, without code
- Attach output data as CSV, TSV, PDF, PNG, or Excel Spreadsheet

## Install

```bash
pip install jupyterlab_email
jupyter labextension install jupyterlab_email
jupyter serverextension enable --py jupyterlab_email
```

## Adding templates

install the server extension, and add the following to `jupyter_notebook_config.py`

```python3
c.JupyterLabEmail.smtp_servers = [{'name': 'gmail',
                                   'domain': 'gmail.com',
                                   'username': '<YOUR USERNAME>',
                                   'smtp': 'smtp.gmail.com',
                                   'port': 465}]

```

## Create email from notebook:

Use the function in `jupyterlab_email._email`

```python3
def make_email(path, model, from_, type='email', template='', code=False, subject='',
               also_attach='none', also_attach_pdf_template='', also_attach_html_template=''):
    '''
        path        : path to notebook
        model       : notebook itself (in case deployment strips outputs or
                      notebook not available except through ContentsManager)
        from_       : address to send the email from
        type        : type to convert notebook to
        template    : template to use when converting notebook
        code        : include input cells in notebook
        subject     : subject of email
        also_attach : also attach pdf/html/both
    '''
```

## Attach dataframe as csv or spreadsheet

In `jupyterlab_email.attachments`

```python3
def attach(data, filename, type):
```

Modify `jupyterlab_email.attachments.EXCEL_ENGINE` to use a different excel writer (defaults to `xlsxwriter`)

## Inline LaTeX

In `jupyterlab_email.attachments`

```python3

def latex(expression):
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(10, 1))
    ax.xaxis.set_visible(False)
    ax.yaxis.set_visible(False)
    ax.axis('off')
    plt.text(0, 0.6, r'$%s$' % expression, fontsize=25)
    plt.show()
```

> [!NOTE]
> This library was generated using [copier](https://copier.readthedocs.io/en/stable/) from the [Base Python Project Template repository](https://github.com/python-project-templates/base).
