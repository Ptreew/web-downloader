# Web File Downloader

Ten program służy do pobierania plików o określonych rozszerzeniach z podanej strony internetowej. Wspiera dynamiczne renderowanie za pomocą Selenium oraz obsługę ciasteczek przeglądarek.

## Wymagania

- Python 3.8 lub nowszy
- Firefox (lub inna wspierana przeglądarka)

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

### Obsługa programu

Uruchomienie programu wymaga podania kilku argumentów wejściowych:

### Przykład podstawowy:
```bash
python web_downloader.py <URL> "<Rozszerzenia plików>" <Ścieżka wyjściowa>
```
- <URL>: Adres URL strony do przetworzenia, `http://` lub `https://` jest wymagane.
- <Rozszerzenia plików>: Rozszerzenia plików do pobrania (np. `"*.jpg|*.png"`).
- <Ścieżka wyjściowa>: Katalog, w którym będą zapisywane pliki.
  - Przykład:

```bash
python web_downloader.py "https://archlinux.org" "*.jpg|*.png" "~/Downloads/ArchLinux"
```

### Opcjonalne argumenty:

- --cookies-from-browser: Pobierz ciasteczka z przeglądarki (firefox, chrome, librewolf).

    - Przykład:
    ```bash
    python web_downloader.py "https://archlinux.org" "*.jpg|*.png" "~/Downloads/ArchLinux" --cookies-from-browser librewolf
    ```

- --max-depth: Maksymalna głębokość przetwarzania strony (domyślnie: 3).
- --max-workers: Maksymalna liczba jednoczesnych połączeń (domyślnie: 5).

### Zatrzymanie programu

Możesz przerwać działanie programu w dowolnym momencie, naciskając `Ctrl+C`

## Dodatkowe informacje

- Obsługiwane typy plików to: `png`, `jpg`, `jpeg`, `gif`, `bmp`, `webp`, `svg`, `json`, `html`, `css`, `js`, `ts`, `py`, `java`, `mp3`, `wav`, `webm`, `mp4`, `pdf`, `docx`, `xlsx`, `zip`, `rar`, `tar.gz`, `txt`, `yaml`, `xml`, `ico`, `tiff`.

