"""Entry point: scrape today's meditation and email it. Safe to run once a day or on demand."""
import argparse
import os
import sys

from mailer import render_html, send_email
from scraper import fetch_meditation


def get_recipients():
    raw = os.environ.get("RECIPIENTS", "")
    return [email.strip() for email in raw.split(",") if email.strip()]


def main():
    parser = argparse.ArgumentParser(description="Fetch and email today's Opus Dei meditation.")
    parser.add_argument("--dry-run", action="store_true", help="Render the email to meditation_preview.html instead of sending it.")
    args = parser.parse_args()

    meditation = fetch_meditation()

    if args.dry_run:
        with open("meditation_preview.html", "w", encoding="utf-8") as f:
            f.write(render_html(meditation))
        print("Dry run: wrote meditation_preview.html")
        return

    sender_email = os.environ["GMAIL_USER"]
    app_password = os.environ["GMAIL_APP_PASSWORD"]
    recipients = get_recipients()
    if not recipients:
        sys.exit("No recipients configured. Set the RECIPIENTS environment variable.")

    send_email(meditation, recipients, sender_email, app_password)
    print(f"Sent '{meditation['title']}' to {len(recipients)} recipient(s).")


if __name__ == "__main__":
    main()
