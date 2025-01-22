# Web File Downloader

Ten program służy do pobierania plików o określonych rozszerzeniach z podanej strony internetowej. Wspiera dynamiczne renderowanie za pomocą Selenium oraz obsługę ciasteczek przeglądarek.

## Dokumentacja

Dokumentacja projektu znajduje się w pliku [Dokumentacja.md](Dokumentacja/Dokumentacja.md) i [Dokumentacja.pdf](Dokumentacja/Dokumentacja.pdf)

## Wymagania

- Python 3.8 lub nowszy
- Przeglądarka bazująca na chromium (np. chrome lub brave), lub inna wspierana przeglądarka
- [Chromedriver](https://googlechromelabs.github.io/chrome-for-testing/) w wersji 132.0.6834.83 lub nowszy umieszczony w katalogu głównym programu.

---

## Instalacja i konfiguracja

### 1. Utwórz wirtualne środowisko

Aby oddzielić zależności projektu, utwórz wirtualne środowisko:
```bash
python -m venv venv
```

Aktywuj środowisko:
- Na systemie Windows:
```bash
.\venv\Scripts\activate
```
- Na systemie Linux/Mac:
```bash
source venv/bin/activate
```

### 2. Zainstaluj wymagane pakiety

Upewnij się, że plik `requirements.txt` znajduje się w katalogu projektu.
Następnie zainstaluj zależności:
```bash
pip install -r requirements.txt
```

---

## Obsługa programu

Uruchomienie programu wymaga podania kilku argumentów wejściowych:

### Przykład podstawowy:
```bash
python web_downloader.py <URL> "<Rozszerzenia plików>" <Ścieżka wyjściowa>
```
- --url <URL>: Adres URL strony do przetworzenia, `http://` lub `https://` jest wymagane.
- --extensions <Rozszerzenia plików>: Rozszerzenia plików do pobrania (np. `"*.jpg|*.png"`).
- --output <Ścieżka wyjściowa>: Katalog, w którym będą zapisywane pliki.
  - Przykład:

```bash
python web_downloader.py --url "https://archlinux.org" --extensions "*.jpg|*.png" --output "~/Downloads/ArchLinux"
```

### Opcjonalne argumenty:

- --cookies-from-browser: Pobierz ciasteczka z przeglądarki (firefox, chrome, librewolf).

    - Przykład:
    ```bash
    python web_downloader.py --url "https://archlinux.org" --extensions "*.jpg|*.png" --output "~/Downloads/ArchLinux" --cookies-from-browser librewolf
    ```

- --max-depth: Maksymalna głębokość przetwarzania strony (domyślnie: 3).
- --max-workers: Maksymalna liczba jednoczesnych połączeń (domyślnie: 5).

### Zatrzymanie programu

Możesz przerwać działanie programu w dowolnym momencie, naciskając `Ctrl+C`

---

## Dodatkowe informacje

- Obsługiwane typy plików to: `png`, `jpg`, `jpeg`, `gif`, `bmp`, `webp`, `svg`, `json`, `html`, `css`, `js`, `ts`, `py`, `java`, `mp3`, `wav`, `webm`, `mp4`, `pdf`, `docx`, `xlsx`, `zip`, `rar`, `tar.gz`, `txt`, `yaml`, `xml`, `ico`, `tiff`.

---

## Środowisko Testowe

Środowisko testowe jest zbudowane na maszynie wirtualnej Alpine Linux uruchomionej w VirtualBoxie. System działa w trybie tekstowym (bez GUI) i jest w pełni skonfigurowany oraz gotowy do użycia.

### Dane dostępowe

- **Konto root**
  - Login: `root`
  - Hasło: `Zaq1@WSX`
- **Konto piotr**
  - Login: `piotr-131483`
  - Hasło: `131483`
