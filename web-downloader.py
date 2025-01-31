import os
import re
import aiohttp
import asyncio
from urllib.parse import urljoin, urlparse
import hashlib
import uuid
import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import lxml.html
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service

CHROMEDRIVER_PATH = "chromedriver"  # Ścieżka do sterownika Chrome w wersji 132.0.6834.83
chrome_service = Service(CHROMEDRIVER_PATH)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36"
}

# Nadawanie rozszerzenia na podstawie MIME
extension_map = {
            'image/png': '.png',
            'image/jpeg': '.jpg',
            'image/gif': '.gif',
            'image/bmp': '.bmp',
            'image/webp': '.webp',
            'image/svg+xml': '.svg',
            'application/json': '.json',
            'text/html': '.html',
            'text/css': '.css',
            'application/javascript': '.js',
            'application/typescript': '.ts',
            'text/x-python': '.py',
            'text/x-java-source': '.java',
            'audio/mpeg': '.mp3',
            'audio/wav': '.wav',
            'video/webm': '.webm',
            'video/mp4': '.mp4',
            'application/pdf': '.pdf',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '.docx',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': '.xlsx',
            'application/zip': '.zip',
            'application/x-rar-compressed': '.rar',
            'application/gzip': '.tar.gz',
            'text/plain': '.txt',
            'application/x-yaml': '.yaml',
            'application/xml': '.xml',
            'image/vnd.microsoft.icon': '.ico',
            'image/tiff': '.tiff',
            'application/octet-stream': '.iso'
}

# Pobranie ciasteczek z przeglądarki (testowane na systemie Linux)
def get_cookies_from_browser(browser, domain):
    try:
        if browser == "librewolf":
            import browser_cookie3
            cookies = browser_cookie3.librewolf(domain_name=domain)
        elif browser == "firefox":
            import browser_cookie3
            cookies = browser_cookie3.firefox(domain_name=domain)
        elif browser == "chrome":
            import browser_cookie3
            cookies = browser_cookie3.chrome(domain_name=domain)
        else:
            print(f"Nieobsługiwana przeglądarka: {browser}")
            return {}

        cookie_dict = {cookie.name: cookie.value for cookie in cookies}
        if not cookie_dict:
            print(f"Brak ciasteczek dla domeny {domain} w przeglądarce {browser}.")
        else:
            print(f"Pobrano ciasteczka z {browser} dla domeny {domain}: {cookie_dict}")
        return cookie_dict
    except Exception as e:
        print(f"Błąd przy pobieraniu ciasteczek z {browser}: {e}")
        return {}

# Tworzenie katalogu, jeśli nie istnieje
def ensure_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)

# Funkcja zapisująca wbudowane SVG do pliku
def extract_and_save_svgs(html_content, output_directory, extensions):
    try:
        # Sprawdzenie, czy 'svg' znajduje się w podanych rozszerzeniach
        if 'svg' not in extensions:
            print("Pomijanie osadzonych SVG - rozszerzenie 'svg' nie zostało uwzględnione.")
            return

        # Parsowanie HTML
        tree = lxml.html.fromstring(html_content)

        # Znajdowanie elementów <svg>
        svg_elements = tree.xpath('//svg')

        for i, svg in enumerate(svg_elements):
            # Konwersja elementu <svg> do stringa
            svg_code = lxml.html.tostring(svg, pretty_print=True, encoding='unicode')

            # Tworzenie pełnej ścieżki zapisu pliku
            filename = f"embedded_svg_{i}.svg"
            output_path = os.path.join(output_directory, filename)

           # Zapis pliku SVG
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(svg_code)
            print(f"Zapisano osadzone SVG do {output_path}")

    except Exception as e:
        print(f"Błąd przy ekstrakcji SVG: {e}")


# Mechanizm ponowienia próby
async def download_with_retry(url, retries=3, delay=3, cookies=None):
    for i in range(retries):
        try:
            async with aiohttp.ClientSession(headers=HEADERS, cookies=cookies) as session:
                async with session.get(url, timeout=10) as response:
                    response.raise_for_status()
                    return await response.read()
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            if i < retries - 1:
                print(f"Błąd {e}, ponawiam próbę ({i + 1}/{retries})...")
                await asyncio.sleep(delay)
            else:
                print(f"Nie udało się pobrać pliku {url} po {retries} próbach.")
                raise



# Pobieranie pliku z danego URL
async def download_file(url, output_directory, downloaded_files, cookies):
    try:
        parsed_url = urlparse(url)

        relative_path = parsed_url.path.lstrip('/')

        # Sprawdzanie, czy plik został już pobrany
        url_hash = hashlib.md5(url.encode('utf-8')).hexdigest()
        if url_hash in downloaded_files:
            print(f"Pominięto {url} (plik już pobrany).")
            return

        # Pobranie danych pliku
        file_data = await download_with_retry(url, cookies=cookies)

        # Pobranie MIME typu pliku
        mime_type = await get_mime_type(url)
        if not mime_type:
            # print(f"Pominięto plik {url} - nie udało się określić typu MIME.")
            return

        # Pobranie rzeczywistego rozszerzenia pliku
        file_extension = os.path.splitext(parsed_url.path)[1].lstrip('.').lower()

        if not file_extension:  # Jeśli plik nie ma rozszerzenia, nadanie go na podstawie MIME
            file_extension = extension_map.get(mime_type, '').lstrip('.')

        if file_extension not in extensions:
            # print(f"Pominięto {url} - rozszerzenie .{file_extension} lub MIME {mime_type} nie pasuje do wybranych.")
            return


        # Parsowanie URL
        path = parsed_url.path.lstrip('/')  # Usuwamy początkowy '/', aby nie tworzyć katalogu głównego

        # Jeśli URL kończy się "/", traktujemy go jako katalog i nadajemy domyślną nazwę pliku
        if path.endswith('/'):
            path += "index" + file_extension

        # Tworzenie pełnej ścieżki katalogu, w którym zapisany będzie plik
        file_directory = os.path.join(output_directory, os.path.dirname(path))
        ensure_directory(file_directory)  # Tworzenie katalogu, jeśli nie istnieje

        # Nazwa pliku
        filename = os.path.basename(path)
        if not filename:  # Jeśli nie ma nazwy pliku, generujemy ją losowo
            filename = f"{uuid.uuid4().hex}{file_extension}"

        # Finalna ścieżka zapisu pliku
        output_path = os.path.join(file_directory, filename)

        # Sprawdzanie, czy plik już istnieje
        if os.path.exists(output_path):
            print(f"Plik {filename} już istnieje, pomijam.")
        else:
            # Zapis pliku
            with open(output_path, 'wb') as f:
                f.write(file_data)
            downloaded_files.add(url_hash)
            print(f"Pobrano: {url} do {output_path}")
    except Exception as e:
        print(f"Błąd przy pobieraniu pliku {url}: {e}")




# Użycie Selenium do dynamicznego renderowania strony
def get_dynamic_page_content(url, extensions):
    try:
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        with webdriver.Chrome(service=chrome_service, options=options) as driver:
            driver.get(url)
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            driver.set_page_load_timeout(15)
            page_source = driver.page_source

            # Pobranie dynamicznie załadowanych linków i obrazów
            links = set()
            for element in driver.find_elements(By.XPATH, '//a[@href] | //img[@src]'):
                if element.tag_name == "a":
                    href = element.get_attribute("href")
                    if href:
                        links.add(href)
                elif element.tag_name == "img":
                    src = element.get_attribute("src")
                    if src:
                        links.add(src)

            print(f"Znaleziono {len(links)} linków dynamicznych na stronie.")
            return page_source, links
    except Exception as e:
        print(f"Błąd w Selenium: {e}")
        return "", set()


# Sprawdzanie typu MIME pliku
async def get_mime_type(url):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.head(url, allow_redirects=True, timeout=10) as response:
                response.raise_for_status()
                mime_type = response.headers.get('Content-Type', 'application/octet-stream').lower()

                # Usuwanie parametru charset, jeśli istnieje
                if ';' in mime_type:
                    mime_type = mime_type.split(';')[0]

                # print(f"[DEBUG] MIME dla {url}: {mime_type}")
                return mime_type
    except Exception as e:
        print(f"Błąd przy sprawdzaniu MIME dla {url}: {e}")
        return 'application/octet-stream'


def is_symlink_loop(url, visited_symlinks):
    try:
        real_path = os.path.realpath(url)  # Pobieramy rzeczywistą ścieżkę
        if real_path in visited_symlinks:
            print(f"🛑 Wykryto zapętlony symlink: {url} → {real_path}")
            return True
        visited_symlinks.add(real_path)
    except Exception as e:
        print(f"Błąd przy sprawdzaniu symlinków dla {url}: {e}")
    return False

"""def has_repeating_segments(url):
    parsed = urlparse(url)
    path_segments = parsed.path.strip('/').split('/')
    if len(path_segments) > len(set(path_segments)):
        print(f"Wykryto powtarzające się segmenty w URL: {url}")
        return True
    return False"""

# Przetwarzanie strony rekurencyjnie
async def process_page(url, extensions, visited, downloaded_files, output_directory, semaphore, depth=0, max_depth=3, cookies=None, session=None, visited_symlinks=None):
    if visited_symlinks is None:
        visited_symlinks = set()

    if is_symlink_loop(url, visited_symlinks):
        return

    # Jeśli strona została już odwiedzona, pomiń
    if url in visited:
        return

    # Dodaj stronę do odwiedzonych
    visited.add(url)

    # Jeśli przekroczono maksymalną głębokość, nie przetwarzaj linków wewnętrznych
    if depth > max_depth:
        print(f"Pominięto {url} - osiągnięto maksymalną głębokość {max_depth}.")
        return

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as response:
                response.raise_for_status()

                # Sprawdź typ MIME, aby upewnić się, że to HTML
                content_type = response.headers.get('Content-Type', '').lower()
                if 'text/html' in content_type:
                    html_content = await response.text()
                else:
                    print(f"Pominięto {url} - typ MIME to {content_type}, nie jest to strona HTML.")
                    return

        # Wykrywanie i zapisywanie wbudowanych SVG
        extract_and_save_svgs(html_content, output_directory, extensions)

        print(f"Przetwarzanie: {url} na głębokości {depth}")

        # Pobierz treść dynamicznie za pomocą Selenium
        html_content, dynamic_links = get_dynamic_page_content(url, extensions)

        # Połącz linki z DOM dynamicznym i statycznym
        """all_links = set(re.findall(r'href=["\'](.*?)["\']|src=["\'](.*?)["\']', html_content))
        all_links.update(dynamic_links)
        all_links = {urljoin(url, link[0] or link[1]) for link in all_links}"""

        all_links = set()
        for match in re.findall(r'href=["\'](.*?)["\']|src=["\'](.*?)["\']', html_content):
            all_links.add(urljoin(url, match[0] or match[1]))


        # Iteruj po znalezionych linkach
        async with semaphore:  # Kontrola równoległych zadań
            for file_url in all_links:
                try:
                    # Pobieranie MIME i nadawanie rozszerzenia na podstawie MIME
                    mime_type = await get_mime_type(file_url)

                    parsed_url = urlparse(file_url)
                    file_extension = os.path.splitext(parsed_url.path)[1].lstrip('.').lower()

                    # Sprawdź, czy plik ma rozszerzenie pasujące do podanych przez użytkownika
                    if file_extension in extensions:
                        await download_file(file_url, output_directory, downloaded_files, cookies)
                    elif not file_extension:  # Jeśli plik nie ma rozszerzenia, sprawdź MIME
                        mime_type = await get_mime_type(file_url)
                        expected_extension = extension_map.get(mime_type, '').lstrip('.')

                        if expected_extension in extensions:
                            await download_file(file_url, output_directory, downloaded_files, cookies)
                        else:
                            print(f"Pominięto {file_url} - MIME {mime_type} nie pasuje do wybranych rozszerzeń.")
                    else:
                        print(f"Pominięto {file_url} - rozszerzenie .{file_extension} nie pasuje do wybranych rozszerzeń.")


                    # Wywołaj rekurencyjnie `process_page` dla znalezionych linków, zwiększając głębokość
                    try:
                        await process_page(file_url, extensions, visited, downloaded_files, output_directory, semaphore, depth=depth + 1, max_depth=max_depth, cookies=cookies)
                    except Exception as e:
                        print(f"Error processing {file_url}: {e}")


                except Exception as e:
                    print(f"Błąd przy przetwarzaniu linku {file_url}: {e}")

    except Exception as e:
        print(f"Błąd przy przetwarzaniu strony {url}: {e}")



if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Pobieranie plików o wskazanych rozszerzeniach ze strony internetowej.")
    parser.add_argument("--url", required=True, help="URL strony internetowej do przetworzenia")
    parser.add_argument("--extensions", required=True, help="Rozszerzenia plików do pobrania, oddzielone '|' (np. *.jpg|*.png)")
    parser.add_argument("--output", default="download", help="Katalog, w którym będą zapisywane pliki")
    parser.add_argument("--cookies-from-browser", default=None, help="Nazwa przeglądarki do pobrania ciasteczek (np. firefox, chrome, librewolf) - testowane jedynie w systemie Linux")
    parser.add_argument("--max-depth", type=int, default=3, help="Maksymalna głębokość rekursji (domyślnie 3)")
    parser.add_argument("--max-workers", type=int, default=5, help="Maksymalna liczba jednoczesnych połączeń (domyślnie 5)")

    args = parser.parse_args()

    if not args.url.endswith('/'):
        args.url += '/'

    extensions = [ext.strip().lower().lstrip('*.') for ext in args.extensions.split('|')]
    domain = urlparse(args.url).netloc.replace('.', '_')

    # Tworzenie domyślnego katalogu wyjściowego, jeśli nie został podany
    output_directory = os.path.join(args.output, domain)
    ensure_directory(output_directory)

    visited = set()
    downloaded_files = set()
    semaphore = asyncio.Semaphore(args.max_workers)  # Ograniczenie równoległych zadań

    cookies = None
    if args.cookies_from_browser:
        cookies = get_cookies_from_browser(args.cookies_from_browser, urlparse(args.url).netloc)
        if not cookies:
            print(f"Nie udało się pobrać ciasteczek z przeglądarki {args.cookies_from_browser}. Kontynuuję bez ciasteczek.")

    try:
        asyncio.run(process_page(args.url, extensions, visited, downloaded_files, output_directory, semaphore, max_depth=args.max_depth, cookies=cookies))
    except KeyboardInterrupt:
        print("\nProgram został zatrzymany przez użytkownika.")
