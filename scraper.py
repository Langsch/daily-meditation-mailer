"""Scrapes the daily meditation from opusdei.org."""
import re
from datetime import datetime
from zoneinfo import ZoneInfo

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

MEDITATION_URL = "https://opusdei.org/pt-br/meditation/"
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; meditation-mailer/1.0)"}
TIMEZONE = ZoneInfo("America/Sao_Paulo")
MONTHS_PT = ("janeiro", "fevereiro", "março", "abril", "maio", "junho",
             "julho", "agosto", "setembro", "outubro", "novembro", "dezembro")


class MeditationParseError(RuntimeError):
    """The page loaded but has none of the content the email needs."""


def clean_text(tag):
    text = tag.get_text(" ", strip=True)
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"\s+([.,;:!?])", r"\1", text)
    return text


def text_of(tag, default=""):
    """get_text on a tag that may be missing."""
    return tag.get_text(strip=True) if tag else default


def today_display():
    now = datetime.now(TIMEZONE)
    return f"{now.day} de {MONTHS_PT[now.month - 1]} de {now.year}"


def build_session():
    retry = Retry(total=3, backoff_factor=2, status_forcelist=(429, 500, 502, 503, 504))
    session = requests.Session()
    session.mount("https://", HTTPAdapter(max_retries=retry))
    return session


def parse_meditation(html, url=MEDITATION_URL):
    soup = BeautifulSoup(html, "html.parser")

    title = text_of(soup.select_one("h1.title[itemprop=name]"))
    if not title:
        og_title = soup.select_one("meta[property='og:title']")
        # soup.title would also match a <title> inside an inline SVG, so stay in the head.
        title = (og_title.get("content", "").strip() if og_title else "") or text_of(soup.select_one("head > title"))

    description = text_of(soup.select_one("p.description[itemprop=description]"))

    time_tag = soup.find("time")
    date_iso = time_tag.get("datetime") if time_tag else None
    date_display = text_of(time_tag) or today_display()

    image_tag = soup.select_one("meta[itemprop=image]")
    image_url = image_tag.get("content") if image_tag else None

    article_body = soup.find(attrs={"itemprop": "articleBody"})
    body = article_body or soup.find("article") or soup.find("main")

    # The <ul> is the article's table of contents; without it sections just lose their headings.
    # Only trust it inside articleBody — in the wider fallbacks the first <ul> is the share menu.
    toc = article_body.find("ul") if article_body else None
    section_titles = [a.get_text(strip=True) for a in toc.find_all("a")] if toc else []

    sections = []
    footnotes = []
    current = None
    for p in body.find_all("p") if body else []:
        text = clean_text(p)
        if not text:
            continue
        if re.match(r"^\[\d+\]", text):
            footnotes.append(text)
            continue
        section_id = p.get("id", "")
        if section_id.startswith("id_"):
            index = int(section_id.split("_")[1]) - 1
            current = {"title": section_titles[index] if index < len(section_titles) else "", "paragraphs": []}
            sections.append(current)
        if current is None:
            current = {"title": "", "paragraphs": []}
            sections.append(current)
        current["paragraphs"].append(text)

    if not title:
        raise MeditationParseError("não achei o título da meditação na página")
    if not any(section["paragraphs"] for section in sections):
        raise MeditationParseError("não achei nenhum parágrafo do texto da meditação na página")

    return {
        "title": title,
        "description": description,
        "date_iso": date_iso,
        "date_display": date_display,
        "image_url": image_url,
        "sections": sections,
        "footnotes": footnotes,
        "url": url,
    }


def fetch_meditation(url=MEDITATION_URL):
    response = build_session().get(url, headers=HEADERS, timeout=15)
    response.raise_for_status()
    return parse_meditation(response.text, url)


if __name__ == "__main__":
    import json

    print(json.dumps(fetch_meditation(), indent=2, ensure_ascii=False))
