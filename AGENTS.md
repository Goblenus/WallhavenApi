# WallhavenApi

## Project Overview

Python wrapper for the [Wallhaven API](https://wallhaven.cc/help/api). Single-file library with minimal dependencies (`requests` only).

## Project Structure

```
WallhavenApi/
├── wallhavenapi.py    # Main library (enums, exceptions, WallhavenApiV1 class)
├── tests.py           # Integration tests (unittest)
├── requirements.txt   # Dependencies
├── readme.md          # User documentation
├── .gitlab-ci.yml     # CI/CD pipeline
└── .gitignore
```

## Setup

```bash
pip install -r requirements.txt
```

## Running Tests

```bash
python tests.py
```

Optionally set `APIKEY` environment variable to test authenticated endpoints:

```bash
APIKEY=your_key python tests.py
```

## Code Conventions

- **No comments** in code unless explicitly requested
- Use `Enum` classes for API constants: `Category`, `Purity`, `Sorting`, `Order`, `TopRange`, `Color`, `Type`
- Private methods prefixed with `_` (`_request`, `_url_format`, `_category`, `_purity`)
- Custom exceptions at module level: `RequestsLimitError`, `ApiKeyError`, `UnhandledException`, `NoWallpaperError`

## Architecture

- Single class `WallhavenApiV1` handles all API operations
- `_request()` is the central HTTP method — handles auth, timeouts, proxies, 429 retries
- All public methods delegate to `_request()` or `requests.get()` directly (for downloads)
- API key injected automatically into request params when set

## Known Quirks

- Legacy typo methods `is_walpaper_exists` and `download_walpaper` still exist (deprecated — use `wallpaper` variants)
- 429 retry logic uses tuple `(retries, delay_seconds)` via `requestslimit_timeout`
- `download_wallpaper` returns file path if `file_path` provided, otherwise returns raw bytes

## CI/CD

- GitLab CI runs on `master` branch only
- Coverage reported to both [coveralls.io](https://coveralls.io) and [codecov.io](https://codecov.io)
- Triggered via `.gitlab-ci.yml`
