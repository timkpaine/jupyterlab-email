import json
import logging
import os
import os.path

import tornado.escape
import tornado.web
from jupyter_server.base.handlers import JupyterHandler

from ._email import email as email_smtp, make_email


def get_template(type, code, template, handler, user_template=""):
    if user_template:
        return user_template
    if "email" in type:
        if code == "code":
            return handler.templates["email"]
        else:
            return handler.templates["email_nocode"]
    elif "html" in type:
        if code == "code":
            return handler.templates["html"]
        else:
            return handler.templates["html_nocode"]

    elif "pdf" in type:
        if code == "code":
            return handler.templates["pdf"]
        else:
            return handler.templates["pdf_nocode"]
    else:
        if template in handler.templates:
            return handler.templates[template]
        else:
            return handler.templates["email"]


class EmailHandler(JupyterHandler):
    def initialize(
        self,
        emails=None,
        templates=None,
        user_templates=None,
        headers=None,
        footers=None,
        signatures=None,
        postprocessors=None,
        logger=None,
    ):
        self.emails = emails
        self.templates = templates
        self.user_templates = user_templates
        self.headers = headers
        self.footers = footers
        self.signatures = signatures
        self.postprocessors = postprocessors
        self.logger = logger or logging

    @tornado.web.authenticated
    def post(self):
        body = tornado.escape.json_decode(self.request.body)

        email = body.get("email", "")
        code = body.get("code", "code").lower()
        to = body.get("to", "")
        subject = body.get("subject", "")
        type = body.get("type", "email").lower()
        also_attach = body.get("also_attach", "none").lower()
        template = body.get("type")
        user_template = body.get("user_template", "")
        postprocessor = body.get("postprocessor", "")

        header = self.headers.get(body.get("header", ""), "")
        footer = self.footers.get(body.get("footer", ""), "")
        signature = self.signatures.get(body.get("signature", ""), "")
        user_template = self.user_templates.get(user_template)
        postprocessor = self.postprocessors.get(postprocessor)

        template = get_template(type, code, template, self, user_template)
        attach_html_template = get_template("html", code, None, self)
        attach_pdf_template = get_template("pdf", code, None, self)

        if type == "html attachment":
            if also_attach == "html":
                also_attach = "none"
            elif also_attach == "both":
                also_attach = "pdf"

        elif type == "pdf attachment":
            if also_attach == "pdf":
                also_attach = "none"
            elif also_attach == "both":
                also_attach = "html"

        self.logger.critical("converting to <%s> with template <%s>", type, template)
        path = os.path.join(os.getcwd(), body.get("path"))
        model = body.get("model")

        for account in self.emails:
            if account["name"] == email:
                if not to:
                    to = account["username"] + "@" + account["domain"]
                else:
                    to = to.split(",")

                message, error = make_email(
                    path=path,
                    model=model,
                    from_=account["username"] + "@" + account["domain"],
                    type=type,
                    template=template,
                    code=code,
                    subject=subject,
                    header=header,
                    footer=footer or signature,
                    also_attach=also_attach,
                    also_attach_pdf_template=attach_pdf_template,
                    also_attach_html_template=attach_html_template,
                    postprocessor=postprocessor,
                    logger=self.logger,
                )
                if error:
                    # set "to" to be "from"
                    to = account["username"] + "@" + account["domain"]
                if "function" in account:
                    r = account["function"](
                        message,
                        to,
                        account.get("username"),
                        account.get("password"),
                        account.get("domain"),
                        account.get("smtp"),
                        account.get("port"),
                    )
                else:
                    r = email_smtp(
                        message=message,
                        to=to,
                        username=account["username"],
                        password=account["password"],
                        domain=account["domain"],
                        host=account["smtp"],
                        port=account["port"],
                        logger=self.logger,
                    )
                if error:
                    self.set_status(500)
                    raise RuntimeError("Error during conversion!")
                self.finish(str(r))
                return
        raise ValueError("Email not found!")


class EmailsListHandler(JupyterHandler):
    def initialize(
        self,
        emails=None,
        templates=None,
        user_templates=None,
        headers=None,
        footers=None,
        signatures=None,
        postprocessors=None,
        logger=None,
    ):
        self.emails = emails
        self.templates = templates
        self.user_templates = user_templates
        self.headers = headers
        self.footers = footers
        self.signatures = signatures
        self.postprocessors = postprocessors
        self.logger = logger or logging

    @tornado.web.authenticated
    def get(self):
        ret = {}
        ret["emails"] = [_["name"] for _ in self.emails]
        ret["templates"] = [_ for _ in self.templates]
        ret["user_templates"] = [""] + [_ for _ in self.user_templates] if self.user_templates else []
        ret["headers"] = [""] + [_ for _ in self.headers] if self.headers else []
        ret["footers"] = [""] + [_ for _ in self.footers] if self.footers else []
        ret["signatures"] = [""] + [_ for _ in self.signatures] if self.signatures else []
        ret["postprocessors"] = [""] + [_ for _ in self.postprocessors] if self.postprocessors else []
        self.finish(json.dumps(ret))
