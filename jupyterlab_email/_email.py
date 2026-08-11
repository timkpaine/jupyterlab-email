import base64
import json
import logging
import os

import emails
import nbformat
from bs4 import BeautifulSoup
from six import iteritems

from .attachments import CUSTOM_TAG
from .nbconvert import run


def make_email(
    path,
    model,
    from_,
    type="email",
    template="",
    code=False,
    subject="",
    header="",
    footer="",
    also_attach="none",
    also_attach_pdf_template="",
    also_attach_html_template="",
    postprocessor=None,
    postprocessor_kwargs=None,
    logger=None,
):
    """
    path        : path to notebook
    model       : notebook itself (in case deployment strips outputs or
                  notebook not available except through ContentsManager)
    from_       : address to send the email from
    type        : type to convert notebook to
    template    : template to use when converting notebook
    code        : include input cells in notebook
    subject     : subject of email
    header      : header to inject
    footer      : footer to inject
    also_attach : also attach pdf/html/both
    postprocessor : run postprocessor on soup
    """
    name = path.rsplit(os.pathsep, 1)[1].rsplit(".", 1)[0]
    model = nbformat.writes(nbformat.reads(json.dumps(model), 4))

    logger = logger or logging

    if type == "email" or type == "html attachment":
        type_to = "html"
    elif type == "pdf attachment":
        type_to = "pdf"
    else:
        raise ValueError("Type not recognized")

    nb, error = run(to=type_to, name=name, in_=model, template=template, logger=logger)

    if error:
        message = emails.html(charset="utf-8", subject=subject, html=nb, mail_from=from_)
        return message, error

    if not nb:
        raise RuntimeError("Something went wrong with NBConvert")

    if also_attach in ("pdf", "both"):
        pdf_nb, error1 = run("pdf", name, model, also_attach_pdf_template)
        error += error1
    if also_attach in ("html", "both"):
        html_nb, error2 = run("html", name, model, also_attach_html_template)
        error += error2

    if error:
        # from pdf or html conversion specifically
        message = emails.html(charset="utf-8", subject=subject, html=nb, mail_from=from_)
        return message, error

    if type == "email":
        soup = BeautifulSoup(nb, "html.parser")

        # strip markdown links
        for item in soup.findAll("a", {"class": "anchor-link"}):
            item.decompose()

        # strip matplotlib base outs
        for item in soup.find_all("div", class_="output_text output_subarea output_execute_result"):
            for c in item.contents:
                if "&lt;matplotlib" in str(c):
                    item.decompose()

        # remove dataframe table borders
        for item in soup.findAll("table", {"border": 1}):
            item["border"] = 0
            item["cellspacing"] = 0
            item["cellpadding"] = 0

        # extract imgs for outlook
        imgs = soup.find_all("img")
        imgs_to_attach = {}

        # attach main part
        for i, img in enumerate(imgs):
            if not img.get("localdata"):
                continue
            imgs_to_attach[img.get("cell_id") + "_" + str(i) + ".png"] = base64.b64decode(img.get("localdata"))
            img["src"] = "cid:" + img.get("cell_id") + "_" + str(i) + ".png"
            # encoders.encode_base64(part)
            del img["localdata"]

        attaches = soup.find_all(CUSTOM_TAG)
        att_to_attach = {}

        # attach custom attachments
        for i, att in enumerate(attaches):
            if not att.get("localdata"):
                continue
            filename = att.get("filename")
            if filename.endswith((".png", ".xls", ".xlsx", ".pdf")):
                att_to_attach[filename] = base64.b64decode(att.get("localdata"))
            else:
                att_to_attach[filename] = att.get("localdata")
            att.decompose()

        # attach header/footer
        if header or footer:
            head = soup.find("div", {"class": "header"})
            foot = soup.find("div", {"class": "footer"})
            head.append(BeautifulSoup(header, "html.parser"))
            foot.append(BeautifulSoup(footer, "html.parser"))

        if postprocessor:
            if postprocessor_kwargs is None:
                postprocessor_kwargs = {}
            tmp = postprocessor(soup, **postprocessor_kwargs)
            if tmp is not None:
                # returned the soup
                soup = tmp

        # assemble email soup
        soup = str(soup)
        message = emails.html(charset="utf-8", subject=subject, html=soup, mail_from=from_)

        for img, data in iteritems(imgs_to_attach):
            message.attach(filename=img, content_disposition="inline", data=data)

        for att, data in iteritems(att_to_attach):
            message.attach(filename=att, content_disposition="inline", data=data)

        if also_attach in ("pdf", "both"):
            message.attach(filename=name + ".pdf", data=pdf_nb)

        if also_attach in ("html", "both"):
            message.attach(filename=name + ".html", data=html_nb)

        return message, 0

    message = emails.html(
        subject=subject,
        html=f"<html>Attachment: {name}.{type_to}</html>",
        mail_from=from_,
    )
    message.attach(filename=name + "." + type_to, data=nb)

    if also_attach in ("pdf", "both"):
        message.attach(filename=name + ".pdf", data=pdf_nb)

    if also_attach in ("html", "both"):
        message.attach(filename=name + ".html", data=html_nb)

    return message, 0


def email(message, to, username, password, domain, host, port, logger=None):
    """
    to          : who to send notebook to
    username    : email account username
    password    : email account password
    domain      : email account provider
    host        : smtp host
    port        : smtp port
    """
    logger = logger or logging
    r = message.send(
        to=to,
        smtp={
            "host": host,
            "port": port,
            "ssl": True,
            "user": username,
            "password": password,
        },
    )
    if r.status_code != 250:
        logger.critical(r)
        raise RuntimeError("Email exception! Check username and password")
    return r
