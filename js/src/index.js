import {ILayoutRestorer} from "@jupyterlab/application";

import {Dialog, ICommandPalette, showDialog} from "@jupyterlab/apputils";

import {PageConfig} from "@jupyterlab/coreutils";

import {IDocumentManager} from "@jupyterlab/docmanager";

import {Menu, Widget} from "@lumino/widgets";

import {IFileBrowserFactory} from "@jupyterlab/filebrowser";

import {IMainMenu} from "@jupyterlab/mainmenu";

import {request} from "requests-helper";

import "../style/index.css";

const default_none = document.createElement("option");
default_none.selected = false;
default_none.disabled = true;
default_none.hidden = false;
default_none.style.display = "none";
default_none.value = "";

const _Private = {
  buildLabel(text) {
    const label = document.createElement("label");
    label.textContent = text;
    return label;
  },

  buildTextarea(text) {
    const area = document.createElement("textarea");
    area.placeholder = text;
    area.style.marginBottom = "15px";
    return area;
  },

  buildSelect(list, _class, def) {
    const select = document.createElement("select");
    select.classList.add(_class || "");
    select.appendChild(default_none);
    list.forEach((x) => {
      const option = document.createElement("option");
      option.value = x;
      option.textContent = x;
      select.appendChild(option);

      if (def && x === def) {
        option.selected = true;
      }
    });
    select.style.marginBottom = "15px";
    select.style.minHeight = "25px";
    return select;
  },
};

export class SendEmailWidget extends Widget {
  constructor(accounts = [], hide_code = false, account_name = "", templates = [], signatures = [], headers = [], footers = [], user_templates = [], postprocessors = []) {
    const body = document.createElement("div");
    body.style.display = "flex";
    body.style.flexDirection = "column";
    body.classList.add("jupyterlab_email_form");

    const basic = document.createElement("div");
    basic.style.flex = "1";
    body.appendChild(basic);

    basic.appendChild(_Private.buildLabel("Type:"));
    basic.appendChild(_Private.buildSelect(["Email", "HTML Attachment", "PDF Attachment"], "type", "Email"));
    basic.appendChild(_Private.buildLabel("Code or no Code:"));
    basic.appendChild(_Private.buildSelect(["Code", "No code"], "code", "No code"));
    basic.appendChild(_Private.buildLabel("Send email to:"));
    basic.appendChild(_Private.buildTextarea("list, of, emails, default is to self"));
    basic.appendChild(_Private.buildLabel("Email Subject:"));
    basic.appendChild(_Private.buildTextarea("Subject of email"));

    /* Advanced options */
    const advanced = document.createElement("div");
    advanced.style.flex = "1";

    const expand_div = document.createElement("div");
    expand_div.style.display = "flex";
    expand_div.style.flexDirection = "row";

    const advanced_label = document.createElement("label");
    advanced_label.textContent = "Advanced";

    expand_div.appendChild(advanced_label);

    const advanced_button_open = document.createElement("button");
    const advanced_span_open = document.createElement("span");
    const advanced_button_close = document.createElement("button");
    const advanced_span_close = document.createElement("span");

    advanced_button_open.classList.add("jp-ToolbarButtonComponent");
    advanced_button_close.classList.add("jp-ToolbarButtonComponent");

    advanced_button_open.appendChild(advanced_span_open);
    advanced_button_close.appendChild(advanced_span_close);
    advanced_span_open.classList.add("jupyterlab_email_open");

    advanced_span_close.classList.add("jupyterlab_email_close");

    expand_div.appendChild(advanced_button_open);
    expand_div.appendChild(advanced_button_close);

    body.appendChild(expand_div);
    body.appendChild(advanced);

    advanced.style.display = "none";
    advanced_button_open.style.display = "block";
    advanced_button_close.style.display = "none";

    advanced_button_open.onclick = () => {
      advanced.style.display = "block";
      advanced_button_open.style.display = "none";
      advanced_button_close.style.display = "block";
    };

    advanced_button_close.onclick = () => {
      advanced.style.display = "none";
      advanced_button_open.style.display = "block";
      advanced_button_close.style.display = "none";
    };

    if (accounts.length > 0) {
      advanced.appendChild(_Private.buildLabel("Account:"));
      advanced.appendChild(_Private.buildSelect(accounts, "accounts", account_name));
    }

    advanced.appendChild(_Private.buildLabel("Also attach as:"));
    advanced.appendChild(_Private.buildSelect(["None", "PDF", "HTML", "Both"], "attach", "None"));

    if (templates.length > 0) {
      advanced.appendChild(_Private.buildLabel("Template:"));
      advanced.appendChild(_Private.buildSelect(templates, "templates"));
    }

    if (user_templates.length > 0) {
      advanced.appendChild(_Private.buildLabel("User Templates (Overrides 'builtin' template choice):"));
      advanced.appendChild(_Private.buildSelect(user_templates, "user_template"));
    }

    if (signatures.length > 0) {
      advanced.appendChild(_Private.buildLabel("Signature:"));
      advanced.appendChild(_Private.buildSelect(signatures, "signatures"));
    }

    if (headers.length > 0) {
      advanced.appendChild(_Private.buildLabel("Header:"));
      advanced.appendChild(_Private.buildSelect(headers, "headers"));
    }

    if (footers.length > 0) {
      advanced.appendChild(_Private.buildLabel("Footer:"));
      advanced.appendChild(_Private.buildSelect(footers, "footers"));
    }

    if (postprocessors.length > 0) {
      advanced.appendChild(_Private.buildLabel("Post Processors:"));
      advanced.appendChild(_Private.buildSelect(postprocessors, "postprocessor"));
    }

    super({node: body});
  }

  getCode() {
    return this.codeNode.value;
  }

  getEmail() {
    return this.emailNode.value;
  }

  getType() {
    return this.typeNode.value;
  }

  getTo() {
    return this.toNode.value;
  }

  getSubject() {
    return this.subjectNode.value;
  }

  getAlsoAttach() {
    return this.alsoAttachNode.value;
  }

  getTemplate() {
    return this.templateNode ? this.templateNode.value : "";
  }

  getSignature() {
    return this.signatureNode ? this.signatureNode.value : "";
  }

  getHeader() {
    return this.headerNode ? this.headerNode.value : "";
  }

  getFooter() {
    return this.footerNode ? this.footerNode.value : "";
  }

  getUserTemplate() {
    return this.userTemplateNode ? this.userTemplateNode.value : "";
  }

  getPostprocessor() {
    return this.userTemplateNode ? this.userTemplateNode.value : "";
  }

  get typeNode() {
    return this.node.getElementsByTagName("select")[0];
  }

  get codeNode() {
    return this.node.getElementsByTagName("select")[1];
  }

  get emailNode() {
    return this.node.getElementsByTagName("select")[2];
  }

  get toNode() {
    return this.node.getElementsByTagName("textarea")[0];
  }

  get subjectNode() {
    return this.node.getElementsByTagName("textarea")[1];
  }

  get alsoAttachNode() {
    return this.node.getElementsByTagName("select")[3];
  }

  get templateNode() {
    return this.node.querySelector("select.templates");
  }

  get signatureNode() {
    return this.node.querySelector("select.signatures");
  }

  get headerNode() {
    return this.node.querySelector("select.headers");
  }

  get footerNode() {
    return this.node.querySelector("select.footers");
  }

  get userTemplateNode() {
    return this.node.querySelector("select.user_template");
  }

  get postprocessorNode() {
    return this.node.querySelector("select.postprocessor");
  }
}

function activate(app, docManager, palette, restorer, mainMenu, browser) {
  const {commands} = app;
  const all_emails1 = [];
  const all_accounts = [];
  const all_templates = [];
  const all_user_templates = [];
  const all_signatures = [];
  const all_headers = [];
  const all_footers = [];
  let loaded = false;

  // grab templates from serverextension
  request("get", `${PageConfig.getBaseUrl()}email/get`).then((res) => {
    if (res.ok) {
      const info = res.json();

      info.templates.forEach((template) => {
        all_templates.push(template);
      });

      info.user_templates.forEach((template) => {
        all_user_templates.push(template);
      });

      info.signatures.forEach((signature) => {
        all_signatures.push(signature);
      });

      info.headers.forEach((header) => {
        all_headers.push(header);
      });

      info.footers.forEach((footer) => {
        all_footers.push(footer);
      });

      info.emails.forEach((email) => {
        const command1 = `send-email:${email}`;

        all_accounts.push(email);
        all_emails1.push(command1);

        const send_widget = new SendEmailWidget(all_accounts, false, email, all_templates, all_signatures, all_headers, all_footers, all_user_templates);
        app.commands.addCommand(command1, {
          execute: () => {
            showDialog({
              body: send_widget,
              buttons: [Dialog.cancelButton(), Dialog.okButton({label: "Ok"})],
              title: "Send email:",
            }).then((result) => {
              if (result.button.label === "Cancel") {
                return;
              }

              const folder = browser.defaultBrowser.model.path || "";
              const context = docManager.contextForWidget(app.shell.currentWidget);

              const type = send_widget.getType();

              // eslint-disable-next-line no-shadow
              const email = send_widget.getEmail();
              const code = send_widget.getCode();
              const to = send_widget.getTo();
              const subject = send_widget.getSubject();
              const also_attach = send_widget.getAlsoAttach();
              const template = send_widget.getTemplate();
              const user_template = send_widget.getUserTemplate();
              const signature = send_widget.getSignature();
              const header = send_widget.getHeader();
              const footer = send_widget.getFooter();
              const postprocessor = send_widget.getPostprocessor();

              let path = "";
              let model = {};
              if (context) {
                path = context.path;
                model = context.model.toJSON();
              }

              // eslint-disable-next-line consistent-return
              return new Promise((resolve) => {
                request(
                  "post",
                  `${PageConfig.getBaseUrl()}email/run`,
                  {},
                  {also_attach, code, email, folder, footer, header, model, path, postprocessor, signature, subject, template, to, type, user_template},
                  {timeout: 30000},
                ).then(
                  // eslint-disable-next-line no-shadow
                  (res) => {
                    if (res.ok) {
                      showDialog({
                        buttons: [Dialog.okButton({label: "Ok"})],
                        title: "Mail sent!",
                      }).then(() => {
                        resolve();
                      });
                    } else {
                      showDialog({
                        body: "Check the Jupyter logs for the exception.",
                        buttons: [Dialog.okButton({label: "Ok"})],
                        title: "Something went wrong!",
                      }).then(() => {
                        resolve();
                      });
                    }
                  },
                );
              });
            });
          },
          isEnabled: () => {
            if (app.shell.currentWidget && docManager.contextForWidget(app.shell.currentWidget) && docManager.contextForWidget(app.shell.currentWidget).model) {
              return true;
            }
            return false;
          },
          label: command1,
        });

        palette.addItem({command: command1, category: "Email"});

        const menu = new Menu({commands});
        menu.title.label = "Send Emails";

        app.restored.then(() => {
          all_emails1.forEach((command) => {
            menu.addItem({command, args: {}});
          });

          if (mainMenu && !loaded) {
            loaded = true;
            mainMenu.fileMenu.addGroup([{type: "submenu", submenu: menu}], 11);
          }
        });
      });
    }
  });

  // eslint-disable-next-line no-console
  console.log("JupyterLab extension jupyterlab_email is activated!");
}

const extension = {
  activate,
  autoStart: true,
  id: "jupyterlab_email",
  optional: [],
  requires: [IDocumentManager, ICommandPalette, ILayoutRestorer, IMainMenu, IFileBrowserFactory],
};

export default extension;
export {activate as _activate};
