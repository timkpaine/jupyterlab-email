# from nbconvert.nbconvertapp import NbConvertApp
import html
import logging
import os
import os.path
import re
import subprocess
import sys
import tempfile

_COLOR_CODES = {
    "black": r"(?:\x1b[^m]\d\;30m)([^\x1b]*)",
    "red": r"(?:\x1b[^m]\d\;31m)([^\x1b]*)",
    "green": r"(?:\x1b[^m]\d\;32m)([^\x1b]*)",
    "yellow": r"(?:\x1b[^m]\d\;33m)([^\x1b]*)",
    "blue": r"(?:\x1b[^m]\d\;34m)([^\x1b]*)",
    "magenta": r"(?:\x1b[^m]\d\;35m)([^\x1b]*)",
    "cyan": r"(?:\x1b[^m]\d\;36m)([^\x1b]*)",
    "white": r"(?:\x1b[^m]\d\;37m)([^\x1b]*)",
}

_CLOSERS = re.compile(r"(?:\x1b[^m]*m)")

with open(os.path.join(os.path.dirname(__file__), "templates", "error.tpl"), "r") as fp:
    _ERROR_TEMPLATE = fp.read()


def run(
    to="html",
    name="",
    in_="",
    template="",
    execute=False,
    execute_timeout=600,
    logger=None,
):
    logger = logger or logging

    # write notebook string to disk
    _dir = tempfile.mkdtemp()
    inname = os.path.join(_dir, name)
    with open(inname, "w") as fp:
        fp.write(in_)

    # output file name
    outname = name.rsplit(".", 1)[0]

    # hack for pdfs
    if to != "pdf":
        outname += "." + to

    # assemble nbconvert command
    argv = []
    argv = [sys.executable, "-m", "nbconvert", "--to", to]

    # reexecute if needed
    if execute:
        argv.extend(["--execute", "--ExecutePreprocessor.timeout=" + str(execute_timeout)])

    # pass in template arg
    if template:
        argv.extend(["--template", template])

    # output to outname
    argv.extend([inname, "--output", outname])

    try:
        p = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        _, error = p.communicate()

        if p.returncode != 0:
            error = error.decode("ascii")

            # extract out the cell error
            m = re.search(".*CellExecutionError:(?P<CellError>(.*\n)*)", error, flags=re.MULTILINE)

            g = m.groupdict()

            # dump it in mail
            err = g["CellError"]

            # do the escape of <, > before adding real tags
            err = html.escape(err)

            # convert escape colors to css colors
            for color, reg in _COLOR_CODES.items():
                err = re.sub(
                    reg,
                    f'<span style="color: {color}">{err}</span> ',
                )

            # remove and closers
            err = re.sub(_CLOSERS, "", err)

            # return with template
            ret = _ERROR_TEMPLATE.format(err.replace("\n", "<br>"))
            return ret, 1

        else:
            outname = os.path.join(_dir, outname)

            # hack for pdfs
            if to == "pdf":
                outname += "." + to

            with open(outname, "rb") as fp:
                ret = fp.read()

            os.remove(outname)
            os.remove(inname)
            return ret, 0

    except Exception:
        logger.exception("Exception:")
        return (
            "<html><h1>Notebook Run error has occurred - see raw log for details</h1></html>",
            1,
        )
