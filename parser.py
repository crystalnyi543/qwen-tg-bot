"""
Парсер сайтов: скачивает страницу и возвращает чистый текст.
Поддерживает JS-рендеринг через playwright (опционально).
"""
import logging
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

MAX_CONTENT_LENGTH = 500_000   # 500 KB лимит на HTML


class WebParser:
    def __init__(self, timeout: int = 15):
        self.timeout = aiohttp.ClientTimeout(total=timeout)

    async def fetch(self, url: str) -> str:
        """Скачивает страницу и возвращает чистый текст или сообщение об ошибке."""
        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        parsed = urlparse(url)
        if not parsed.netloc:
            return "❌ Некорректный URL."

        try:
            async with aiohttp.ClientSession(
                headers=HEADERS,
                timeout=self.timeout,
                connector=aiohttp.TCPConnector(ssl=False)
            ) as session:
                async with session.get(url, max_redirects=5) as resp:
                    if resp.status != 200:
                        return f"❌ Сайт вернул код {resp.status}."

                    content_type = resp.headers.get("Content-Type", "")
                    if "text/html" not in content_type and "text/plain" not in content_type:
                        return f"❌ Неподдерживаемый тип: {content_type}"

                    raw_html = await resp.text(errors="replace")

            return self._extract_text(raw_html, url)

        except aiohttp.ClientConnectorError:
            return "❌ Не удалось подключиться к сайту."
        except asyncio.TimeoutError:
            return "❌ Сайт не ответил вовремя (таймаут)."
        except Exception as e:
            logger.error(f"Parser error [{url}]: {e}")
            return f"❌ Ошибка парсинга: {e}"

    def _extract_text(self, html: str, url: str) -> str:
        """Извлекает читаемый текст из HTML."""
        soup = BeautifulSoup(html[:MAX_CONTENT_LENGTH], "lxml")

        # Удаляем мусор
        for tag in soup(["script", "style", "nav", "footer",
                          "header", "aside", "form", "noscript",
                          "iframe", "svg", "img"]):
            tag.decompose()

        # Пробуем получить основной контент
        main = (
            soup.find("main") or
            soup.find("article") or
            soup.find(id="content") or
            soup.find(class_="content") or
            soup.find("body")
        )

        if not main:
            return "❌ Не удалось извлечь текст из страницы."

        lines = [
            line.strip()
            for line in main.get_text(separator="\n").splitlines()
            if line.strip() and len(line.strip()) > 3
        ]

        text = "\n".join(lines)

        if len(text) < 50:
            return "❌ Страница содержит слишком мало текста (возможно, требует JS)."

        # Мета-заголовок
        title_tag = soup.find("title")
        title = title_tag.get_text(strip=True) if title_tag else parsed_domain(url)

        return f"[{title}]\n\n{text[:4000]}"


def parsed_domain(url: str) -> str:
    try:
        return urlparse(url).netloc
    except Exception:
        return url
