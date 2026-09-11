"""Scrapes the daily meditation from opusdei.org."""
import re

import requests
from bs4 import BeautifulSoup

MEDITATION_URL = "https://opusdei.org/pt-br/meditation/"
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; meditation-mailer/1.0)"}


def clean_text(tag):
    text = tag.get_text(" ", strip=True)
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"\s+([.,;:!?])", r"\1", text)
    return text


def fetch_meditation(url=MEDITATION_URL):
    response = requests.get(url, headers=HEADERS, timeout=15)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    title = soup.select_one("h1.title[itemprop=name]").get_text(strip=True)
    description = soup.select_one("p.description[itemprop=description]").get_text(strip=True)

    time_tag = soup.find("time")
    date_iso = time_tag.get("datetime")
    date_display = time_tag.get_text(strip=True)

    image_tag = soup.select_one("meta[itemprop=image]")
    image_url = image_tag.get("content") if image_tag else None

    body = soup.find(attrs={"itemprop": "articleBody"})
    section_titles = [a.get_text(strip=True) for a in body.find("ul").find_all("a")]

    sections = []
    footnotes = []
    current = None
    for p in body.find_all("p"):
        text = clean_text(p)
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


if __name__ == "__main__":
    import json

    print(json.dumps(fetch_meditation(), indent=2, ensure_ascii=False))
