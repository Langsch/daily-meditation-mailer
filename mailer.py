"""Renders the meditation into an email and sends it via Gmail SMTP."""
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 465


def render_html(meditation):
    sections_html = ""
    for section in meditation["sections"]:
        paragraphs_html = "".join(f'<p style="margin:0 0 14px;line-height:1.6;">{p}</p>' for p in section["paragraphs"])
        title_html = f'<h2 style="font-size:18px;margin:28px 0 10px;color:#2e2e2e;">{section["title"]}</h2>' if section["title"] else ""
        sections_html += title_html + paragraphs_html

    footnotes_html = ""
    if meditation["footnotes"]:
        items = "".join(f'<li style="margin-bottom:4px;">{f}</li>' for f in meditation["footnotes"])
        footnotes_html = f'<hr style="border:none;border-top:1px solid #ddd;margin:24px 0;"><ol style="font-size:12px;color:#666;padding-left:18px;">{items}</ol>'

    image_html = f'<img src="{meditation["image_url"]}" alt="" style="width:100%;max-width:600px;border-radius:8px;margin-bottom:20px;">' if meditation["image_url"] else ""

    return f"""\
<html>
<body style="font-family:Georgia,serif;background:#fefcf6;padding:20px;color:#2e2e2e;">
  <div style="max-width:600px;margin:0 auto;background:#fff;padding:30px;border-radius:10px;">
    {image_html}
    <p style="color:#ef9f13;font-weight:bold;letter-spacing:1px;text-transform:uppercase;font-size:12px;">{meditation["date_display"]}</p>
    <h1 style="font-size:24px;margin:6px 0 16px;">{meditation["title"]}</h1>
    <p style="font-style:italic;color:#555;margin-bottom:24px;">{meditation["description"]}</p>
    {sections_html}
    {footnotes_html}
    <p style="margin-top:30px;font-size:12px;color:#999;">
      Fonte: <a href="{meditation["url"]}" style="color:#999;">opusdei.org</a>
    </p>
  </div>
</body>
</html>"""


def render_text(meditation):
    lines = [meditation["date_display"], meditation["title"], "", meditation["description"], ""]
    for section in meditation["sections"]:
        if section["title"]:
            lines.append(section["title"].upper())
        lines.extend(section["paragraphs"])
        lines.append("")
    if meditation["footnotes"]:
        lines.extend(meditation["footnotes"])
        lines.append("")
    lines.append(f'Fonte: {meditation["url"]}')
    return "\n\n".join(lines)


def send_email(meditation, recipients, sender_email, app_password):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f'Meditação do dia — {meditation["date_display"]}'
    msg["From"] = sender_email
    msg["To"] = sender_email
    msg.attach(MIMEText(render_text(meditation), "plain", "utf-8"))
    msg.attach(MIMEText(render_html(meditation), "html", "utf-8"))

    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
        server.login(sender_email, app_password)
        server.sendmail(sender_email, recipients, msg.as_string())
