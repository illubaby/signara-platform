#!/usr/bin/env python3

import argparse
import base64
import http.cookiejar
import os
import re
import sys
import time
from pathlib import Path
from typing import Iterable, List, Optional, Set, Tuple
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

import requests


DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36"
)
LOGIN_MARKERS = (
    "sign in",
    "access denied",
    "login.microsoftonline.com",
    "guestaccess.aspx",
)


class DownloadError(RuntimeError):
    pass


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Download a SharePoint file from a sharing link."
    )
    parser.add_argument("url", nargs="?", default=None, help="SharePoint sharing URL (positional)")
    parser.add_argument(
        "--url",
        dest="url_named",
        help="SharePoint sharing URL (named alternative, avoids shell escaping issues).",
    )
    parser.add_argument(
        "--url-base64",
        help="Base64-encoded URL (use when shell can't handle & in URLs, e.g. csh).",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Output file path or output directory. Defaults to current directory.",
    )
    parser.add_argument(
        "--browser",
        choices=("auto", "chrome", "edge", "firefox", "none"),
        default="auto",
        help="Load cookies from a browser profile if direct access fails.",
    )
    parser.add_argument(
        "--cookie-header",
        help="Raw Cookie header copied from an authenticated browser session.",
    )
    parser.add_argument(
        "--cookies-file",
        help="Path to a Netscape-format cookies.txt file.",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=10,
        help="Request timeout in seconds.",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Print redirect and response details.",
    )
    parser.add_argument(
        "--selenium",
        action="store_true",
        help="Use Selenium with Chrome's authenticated profile to download.",
    )
    parser.add_argument(
        "--device-login",
        action="store_true",
        help="Authenticate via Azure AD device code flow (for headless/SSH servers).",
    )
    return parser


def add_or_replace_query_param(url: str, key: str, value: str) -> str:
    parsed = urlparse(url)
    pairs = [(current_key, current_value) for current_key, current_value in parse_qsl(parsed.query, keep_blank_values=True) if current_key != key]
    pairs.append((key, value))
    return urlunparse(parsed._replace(query=urlencode(pairs)))


def _build_sharepoint_download_url(raw_url: str) -> str:
    """Convert a SharePoint sharing/viewer URL into a direct download URL.

    For Doc.aspx URLs with a sourcedoc GUID, use the download.aspx endpoint
    which reliably triggers a file download instead of opening the viewer.
    """
    parsed = urlparse(raw_url)
    params = dict(parse_qsl(parsed.query, keep_blank_values=True))

    # Doc.aspx with sourcedoc -> use download.aspx?UniqueId=<guid>
    if "Doc.aspx" in parsed.path and "sourcedoc" in params:
        # Strip braces from the GUID if present
        guid = params["sourcedoc"].strip("{}")
        # Build the site base from the path (everything before _layouts)
        site_path = parsed.path.split("_layouts")[0].rstrip("/")
        download_path = f"{site_path}/_layouts/15/download.aspx"
        download_url = urlunparse(parsed._replace(
            path=download_path,
            query=urlencode({"UniqueId": guid}),
        ))
        return download_url

    # Fallback: append download=1
    return add_or_replace_query_param(raw_url, "download", "1")


def candidate_urls(url: str) -> List[str]:
    candidates = []
    # Try the proper download.aspx endpoint first (most reliable)
    download_url = _build_sharepoint_download_url(url.strip())
    candidates.append(download_url)
    candidates.append(url.strip())
    candidates.append(add_or_replace_query_param(url, "download", "1"))

    unique_candidates = []
    seen = set()
    for candidate in candidates:
        if candidate not in seen:
            seen.add(candidate)
            unique_candidates.append(candidate)
    return unique_candidates


def browser_order(mode: str) -> List[str]:
    if mode == "auto":
        return ["chrome", "edge", "firefox"]
    if mode == "none":
        return []
    return [mode]


def load_cookie_file(path: str) -> requests.cookies.RequestsCookieJar:
    jar = http.cookiejar.MozillaCookieJar(path)
    jar.load(ignore_discard=True, ignore_expires=True)
    requests_jar = requests.cookies.RequestsCookieJar()
    for cookie in jar:
        requests_jar.set_cookie(cookie)
    return requests_jar


def load_browser_cookies(hostname: str, mode: str) -> Tuple[Optional[requests.cookies.RequestsCookieJar], Optional[str], List[str]]:
    errors = []
    names = browser_order(mode)
    if not names:
        return None, None, errors

    try:
        import browser_cookie3
    except ImportError:
        errors.append("browser-cookie3 is not installed")
        return None, None, errors

    for browser_name in names:
        try:
            loader = getattr(browser_cookie3, browser_name)
            jar = loader(domain_name=hostname)
            requests_jar = requests.cookies.RequestsCookieJar()
            loaded_count = 0
            for cookie in jar:
                requests_jar.set_cookie(cookie)
                loaded_count += 1
            if loaded_count:
                return requests_jar, f"{browser_name} cookies ({loaded_count})", errors
            errors.append(f"{browser_name}: no cookies for {hostname}")
        except Exception as exc:
            errors.append(f"{browser_name}: {exc}")

    return None, None, errors


def build_session(user_agent: str = DEFAULT_USER_AGENT) -> requests.Session:
    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": user_agent,
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.9",
        }
    )
    return session


def response_preview(response: requests.Response, max_bytes: int = 4096) -> Tuple[bytes, str]:
    chunk = b""
    iterator = response.iter_content(chunk_size=max_bytes)
    try:
        chunk = next(iterator)
    except StopIteration:
        return b"", ""
    preview_text = chunk[:max_bytes].decode("utf-8", errors="ignore")
    response._copilot_remaining_iterator = iterator
    return chunk, preview_text


def looks_like_login(response: requests.Response, preview_text: str) -> bool:
    final_host = urlparse(response.url).netloc.lower()
    content_type = response.headers.get("Content-Type", "").lower()
    if response.status_code in {401, 403}:
        return True
    if "login.microsoftonline.com" in final_host:
        return True
    if response.headers.get("X-Forms_Based_Auth_Required"):
        return True
    if "text/html" in content_type or "text/plain" in content_type:
        lowered = preview_text.lower()
        return any(marker in lowered for marker in LOGIN_MARKERS)
    return False


def content_disposition_filename(header_value: Optional[str]) -> Optional[str]:
    if not header_value:
        return None

    utf8_match = re.search(r"filename\*=UTF-8''([^;]+)", header_value, flags=re.IGNORECASE)
    if utf8_match:
        return requests.utils.unquote(utf8_match.group(1)).strip()

    plain_match = re.search(r'filename="?([^";]+)"?', header_value, flags=re.IGNORECASE)
    if plain_match:
        return plain_match.group(1).strip()
    return None


def fallback_extension(url: str) -> str:
    path = urlparse(url).path.lower()
    if "/:x:/" in path:
        return ".xlsx"
    if "/:w:/" in path:
        return ".docx"
    if "/:p:/" in path:
        return ".pptx"
    if "/:b:/" in path:
        return ".pdf"
    return ".bin"


def resolve_output_path(output: Optional[str], response: requests.Response, source_url: str) -> Path:
    derived_name = content_disposition_filename(response.headers.get("Content-Disposition"))
    if not derived_name:
        derived_name = Path(urlparse(response.url).path).name or f"sharepoint_download{fallback_extension(source_url)}"

    if not output:
        return Path.cwd() / derived_name

    output_path = Path(output)
    if output_path.exists() and output_path.is_dir():
        return output_path / derived_name
    if not output_path.exists() and output_path.suffix == "":
        output_path.mkdir(parents=True, exist_ok=True)
        return output_path / derived_name
    output_path.parent.mkdir(parents=True, exist_ok=True)
    return output_path


def write_response_to_file(response: requests.Response, output_path: Path, first_chunk: bytes) -> int:
    bytes_written = 0
    with output_path.open("wb") as file_handle:
        if first_chunk:
            file_handle.write(first_chunk)
            bytes_written += len(first_chunk)
        iterator: Iterable[bytes] = getattr(response, "_copilot_remaining_iterator", response.iter_content(chunk_size=1024 * 1024))
        for chunk in iterator:
            if not chunk:
                continue
            file_handle.write(chunk)
            bytes_written += len(chunk)
    return bytes_written


def describe_attempt(label: str, debug: bool, errors: List[str]) -> None:
    if label:
        print(f"Using authentication: {label}")
    if debug and errors:
        for error in errors:
            print(f"Cookie source skipped: {error}")


# Microsoft Office public client ID (first-party, supports device code flow)
_MS_OFFICE_CLIENT_ID = "d3590ed6-52b3-4102-aeff-aad2292ab01c"


def _discover_tenant_id(sharepoint_host: str, debug: bool = False) -> Optional[str]:
    """Discover the Azure AD tenant ID from a SharePoint host."""
    try:
        # Use the SharePoint REST API endpoint which returns tenant ID in WWW-Authenticate
        resp = requests.get(
            f"https://{sharepoint_host}/_vti_bin/client.svc",
            allow_redirects=False,
            timeout=10,
            headers={"Authorization": "Bearer"},
        )
        auth_header = resp.headers.get("WWW-Authenticate", "")
        realm_match = re.search(r'realm="([a-f0-9-]{36})"', auth_header)
        if realm_match:
            return realm_match.group(1)
        # Fallback: follow redirects and extract from login URL
        resp2 = requests.get(
            f"https://{sharepoint_host}/",
            allow_redirects=True,
            timeout=10,
            headers={"User-Agent": DEFAULT_USER_AGENT},
        )
        url_match = re.search(r"login\.microsoftonline\.com[:/]+([a-f0-9-]{36})/", resp2.url)
        if url_match:
            return url_match.group(1)
    except Exception as exc:
        if debug:
            print(f"Tenant discovery error: {exc}", file=sys.stderr)
    return None


def device_code_auth(sharepoint_host: str, debug: bool = False) -> Optional[str]:
    """Authenticate using OAuth2 device code flow. Returns an access token."""
    tenant_id = _discover_tenant_id(sharepoint_host, debug)
    if not tenant_id:
        print("Could not discover Azure AD tenant ID.", file=sys.stderr)
        return None

    if debug:
        print(f"Tenant ID: {tenant_id}")

    scope = f"https://{sharepoint_host}/.default offline_access"

    # Step 1: Request device code
    resp = requests.post(
        f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/devicecode",
        data={"client_id": _MS_OFFICE_CLIENT_ID, "scope": scope},
        timeout=10,
    )
    if resp.status_code != 200:
        if debug:
            print(f"Device code request failed: {resp.status_code} {resp.text}", file=sys.stderr)
        return None

    data = resp.json()
    device_code = data["device_code"]
    user_code = data["user_code"]
    verification_uri = data.get("verification_uri", "https://microsoft.com/devicelogin")
    interval = data.get("interval", 5)
    expires_in = data.get("expires_in", 900)

    print(f"\n{'=' * 60}")
    print(f"  DEVICE LOGIN REQUIRED")
    print(f"{'=' * 60}")
    print(f"  Open:  {verification_uri}")
    print(f"  Code:  {user_code}")
    print(f"{'=' * 60}")
    print(f"  Waiting for you to authenticate (up to {expires_in}s)...\n")

    # Step 2: Poll for token
    token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    deadline = time.time() + expires_in

    while time.time() < deadline:
        time.sleep(interval)
        resp = requests.post(token_url, data={
            "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
            "client_id": _MS_OFFICE_CLIENT_ID,
            "device_code": device_code,
        }, timeout=10)

        if resp.status_code == 200:
            token_data = resp.json()
            access_token = token_data.get("access_token")
            if access_token:
                print("Authentication successful!")
                return access_token

        error = resp.json().get("error", "")
        if error == "authorization_pending":
            continue
        elif error == "slow_down":
            interval += 5
            continue
        elif error == "authorization_declined":
            print("Authorization was declined.", file=sys.stderr)
            return None
        elif error == "expired_token":
            print("Device code expired. Please try again.", file=sys.stderr)
            return None
        else:
            if debug:
                print(f"Token poll error: {resp.json()}", file=sys.stderr)
            return None

    print("Authentication timed out.", file=sys.stderr)
    return None


def download_once(session: requests.Session, url: str, output: Optional[str], timeout: int, debug: bool) -> Tuple[Path, int, str]:
    response = session.get(url, allow_redirects=True, stream=True, timeout=timeout)
    if debug:
        print(f"Tried URL: {url}")
        print(f"Final URL: {response.url}")
        print(f"Status: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type', '')}")

    first_chunk, preview_text = response_preview(response)
    if looks_like_login(response, preview_text):
        response.close()
        raise DownloadError(
            "SharePoint requested authentication instead of returning the file. "
            "Use --browser, --cookie-header, or --cookies-file with an authenticated session."
        )
    if response.status_code >= 400:
        message = preview_text.strip() or response.reason or "HTTP error"
        response.close()
        raise DownloadError(f"HTTP {response.status_code}: {message}")

    output_path = resolve_output_path(output, response, url)
    bytes_written = write_response_to_file(response, output_path, first_chunk)
    response.close()
    return output_path, bytes_written, response.url


def selenium_download(url: str, output: Optional[str], timeout: int, debug: bool) -> int:
    """Launch Chrome with the user's authenticated profile to download the file."""
    import glob
    import shutil
    import subprocess
    import time

    # Resolve output directory
    if output:
        out_path = Path(output)
        if out_path.suffix:
            out_path.parent.mkdir(parents=True, exist_ok=True)
            download_dir = str(out_path.parent.resolve())
        else:
            out_path.mkdir(parents=True, exist_ok=True)
            download_dir = str(out_path.resolve())
    else:
        download_dir = str(Path.cwd())

    # Find Chrome executable (Windows and Linux)
    chrome_exe = None
    candidates_list = [
        # Windows
        Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
        Path(r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"),
        Path.home() / "AppData" / "Local" / "Google" / "Chrome" / "Application" / "chrome.exe",
        # Linux
        Path("/usr/bin/google-chrome"),
        Path("/usr/bin/google-chrome-stable"),
        Path("/usr/bin/chromium"),
        Path("/usr/bin/chromium-browser"),
        Path("/snap/bin/chromium"),
    ]
    for candidate in candidates_list:
        if candidate.exists():
            chrome_exe = str(candidate)
            break
    if not chrome_exe:
        # Try 'which' on Linux
        import shutil as _shutil
        for name in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser"):
            found = _shutil.which(name)
            if found:
                chrome_exe = found
                break
    if not chrome_exe:
        print("Chrome/Chromium executable not found. On Linux, install google-chrome or chromium.", file=sys.stderr)
        print("Alternatively, use the non-selenium mode with --cookie-header or --cookies-file.", file=sys.stderr)
        return 1

    is_windows = sys.platform == "win32"

    if is_windows:
        chrome_user_data = Path.home() / "AppData" / "Local" / "Google" / "Chrome" / "User Data"
    else:
        chrome_user_data = Path.home() / ".config" / "google-chrome"
    # Monitor Chrome's ACTUAL default Downloads folder, not our output dir
    chrome_downloads = Path.home() / "Downloads"

    # Check if Chrome is already running (DON'T kill it - we need its auth session)
    if is_windows:
        result = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq chrome.exe", "/NH"],
            capture_output=True, text=True
        )
        chrome_running = "chrome.exe" in result.stdout.lower()
    else:
        result = subprocess.run(
            ["pgrep", "-x", "chrome|chromium"],
            capture_output=True, text=True
        )
        chrome_running = result.returncode == 0

    # Snapshot files in Chrome's default download folder
    pre_files_downloads = set(glob.glob(os.path.join(str(chrome_downloads), "*")))
    pre_files_output = set(glob.glob(os.path.join(download_dir, "*")))

    # Build download URL - handle different SharePoint URL patterns
    raw_url = url.strip()
    download_url = _build_sharepoint_download_url(raw_url)
    if debug:
        print(f"Chrome exe: {chrome_exe}")
        print(f"Chrome already running: {chrome_running}")
        print(f"Monitoring: {chrome_downloads} AND {download_dir}")
        print(f"Download URL: {download_url}")

    if chrome_running:
        # Open URL in existing Chrome instance - preserves authenticated session
        chrome_proc = subprocess.Popen([chrome_exe, download_url])
        print("Opened URL in existing Chrome (preserving auth session). Waiting for download...")
    else:
        # Chrome not running - launch with user profile
        chrome_proc = subprocess.Popen([
            chrome_exe,
            f"--user-data-dir={chrome_user_data}",
            "--profile-directory=Default",
            "--no-first-run",
            "--no-default-browser-check",
            download_url,
        ])
        print(f"Launched Chrome (PID {chrome_proc.pid}). Waiting for download...")

    # Poll for new file in Downloads folder AND output dir
    deadline = time.time() + timeout
    downloaded_file = None
    while time.time() < deadline:
        # Check both Chrome's Downloads and the output directory
        for pre_files, search_dir in [
            (pre_files_downloads, str(chrome_downloads)),
            (pre_files_output, download_dir),
        ]:
            all_files = set(glob.glob(os.path.join(search_dir, "*")))
            new_files = all_files - pre_files
            crdownloads = {f for f in new_files if f.endswith(".crdownload")}
            completed = new_files - crdownloads
            if completed:
                downloaded_file = max(completed, key=os.path.getmtime)
                break
        if downloaded_file:
            break
        time.sleep(2)

    if not downloaded_file:
        print(f"No new file detected in {chrome_downloads} within {timeout}s.", file=sys.stderr)
        print("If SharePoint asked you to log in, please sign in and the download should proceed.", file=sys.stderr)
        return 1

    # Move to the requested output location
    final_path = downloaded_file
    if output:
        out_path = Path(output)
        if out_path.suffix:
            out_path.parent.mkdir(parents=True, exist_ok=True)
            dest = str(out_path)
        else:
            out_path.mkdir(parents=True, exist_ok=True)
            dest = str(out_path / Path(downloaded_file).name)
        shutil.move(downloaded_file, dest)
        final_path = dest

    size = os.path.getsize(final_path)
    print(f"Downloaded to: {final_path}")
    print(f"Bytes written: {size}")
    return 0


def main() -> int:
    if len(sys.argv) > 1 and sys.argv[1] == "-help":
        sys.argv[1] = "--help"

    args = build_parser().parse_args()

    # Resolve URL from named --url, positional url, or --url-base64
    if args.url_named:
        args.url = args.url_named
    if args.url_base64:
        try:
            args.url = base64.b64decode(args.url_base64).decode("utf-8")
        except Exception as exc:
            print("Failed to decode --url-base64: {}".format(exc), file=sys.stderr)
            return 1
    if not args.url:
        print("Error: must provide url, --url, or --url-base64", file=sys.stderr)
        return 1

    parsed = urlparse(args.url)
    if not parsed.scheme or not parsed.netloc:
        print("Invalid URL", file=sys.stderr)
        return 1

    if args.selenium:
        return selenium_download(args.url, args.output, args.timeout, args.debug)

    session = build_session()
    auth_label = "direct link only"
    cookie_errors = []
    used_device_login = False

    if args.device_login:
        token = device_code_auth(parsed.netloc, args.debug)
        if not token:
            print("Device code authentication failed.", file=sys.stderr)
            return 1
        session.headers["Authorization"] = f"Bearer {token}"
        auth_label = "device code login"
        used_device_login = True
    elif args.cookie_header:
        session.headers["Cookie"] = args.cookie_header
        auth_label = "manual Cookie header"
    elif args.cookies_file:
        session.cookies.update(load_cookie_file(args.cookies_file))
        auth_label = f"cookies file: {args.cookies_file}"
    else:
        cookies, loaded_label, cookie_errors = load_browser_cookies(parsed.netloc, args.browser)
        if cookies is not None:
            session.cookies.update(cookies)
            auth_label = loaded_label or auth_label

    describe_attempt(auth_label, args.debug, cookie_errors)

    errors = []
    for url in candidate_urls(args.url):
        try:
            output_path, bytes_written, final_url = download_once(
                session=session,
                url=url,
                output=args.output,
                timeout=args.timeout,
                debug=args.debug,
            )
            print(f"Downloaded to: {output_path}")
            print(f"Bytes written: {bytes_written}")
            if args.debug:
                print(f"Resolved file URL: {final_url}")
            return 0
        except DownloadError as exc:
            errors.append(f"{url}: {exc}")
        except requests.RequestException as exc:
            errors.append(f"{url}: network error: {exc}")

    # If download failed and we haven't tried device login, suggest it
    if not used_device_login:
        print("\nDownload failed — authentication required.", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        print("\nTip: On headless/SSH servers, use --device-login to authenticate:", file=sys.stderr)
        print(f"  {sys.argv[0]} --device-login --url '<URL>' -o <output>", file=sys.stderr)
        return 1

    print("Download failed.", file=sys.stderr)
    for error in errors:
        print(f"- {error}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())