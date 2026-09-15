"""Entry point: scrape today's meditation and email it. Safe to run once a day or on demand."""
import argparse
import os
import sys

import requests

from mailer import render_html, send_email, send_fallback_email
from scraper import MEDITATION_URL, MeditationParseError, fetch_meditation


def get_recipients():
    raw = os.environ.get("RECIPIENTS", "")
    return [email.strip() for email in raw.split(",") if email.strip()]


def main():
    parser = argparse.ArgumentParser(description="Fetch and email today's Opus Dei meditation.")
    parser.add_argument("--dry-run", action="store_true", help="Render the email to meditation_preview.html instead of sending it.")
    args = parser.parse_args()

    # Read the credentials before scraping so a parsing failure can still send the fallback email.
    if not args.dry_run:
        sender_email = os.environ["GMAIL_USER"]
        app_password = os.environ["GMAIL_APP_PASSWORD"]
        recipients = get_recipients()
        if not recipients:
            sys.exit("No recipients configured. Set the RECIPIENTS environment variable.")

    try:
        meditation = fetch_meditation()
    except (MeditationParseError, requests.RequestException) as error:
        if args.dry_run:
            sys.exit(f"Dry run: {error}")
        send_fallback_email(str(error), MEDITATION_URL, recipients, sender_email, app_password)
        sys.exit(f"Sent fallback notice instead: {error}")

    if args.dry_run:
        with open("meditation_preview.html", "w", encoding="utf-8") as f:
            f.write(render_html(meditation))
        print("Dry run: wrote meditation_preview.html")
        return

    send_email(meditation, recipients, sender_email, app_password)
    print(f"Sent '{meditation['title']}' to {len(recipients)} recipient(s).")


if __name__ == "__main__":
    main()
