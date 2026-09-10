#!/usr/bin/env python3

from queue import Queue, Empty
from threading import Thread, Lock
import time
import sys
import requests
import re
import argparse
from urllib.parse import urlparse


VERSION = "0.1.0"
AUTHOR = "Hunter"

def banner():
    return fr"""
  ____  ___    ___  ___ ____ ___  ___
    \   \  \ \ \ _\ \     \  \  \ \ _\
    _\__ \  \ \ \___ \___  \  \__\ \ \  v{VERSION}
             __\
    
Built by: {AUTHOR}
    """


def build_flags():
    parser = argparse.ArgumentParser(
        prog="Injector",
        description=(
            "A generic injection testing tool using custom payload wordlists.\n\n"
            "** IMPORTANT: **\n"
            "  Target URL or request body MUST contain the INJECT placeholder."
        ),
        add_help=True,
        formatter_class=lambda prog: argparse.RawDescriptionHelpFormatter(
            prog,
            max_help_position=50,
            width=150,
        ),
    )

    parser.add_argument("-u", "--url", dest="url", type=str, help="Target URL to test.")
    parser.add_argument("--rate", dest="rate", type=int, default=0, help="Maximum requests per second (default: unlimited).")
    parser.add_argument("-w", "--wordlist", dest="wordlist", type=str, help="Path to the custom injection payload wordlist.")
    parser.add_argument("-H", "--header", dest="header", type=str, help="Custom HTTP header to include in requests.")
    parser.add_argument("-X", "--method", dest="method", type=str, default="GET", help="HTTP method to use for requests (default: GET).")
    parser.add_argument("-t", "--thread", dest="thread", type=int, default=5, help="Number of concurrent threads (default: 5).")
    parser.add_argument("-c", "--cookie", dest="cookie", type=str, help="Add custom cookies to the request.")
    parser.add_argument("-d", "--data", dest="data", type=str, help="Request body containing the INJECT placeholder.")
    parser.add_argument("--timeout", dest="timeout", type=int, default=10, help="Request timeout in seconds (default: 10).")
    parser.add_argument("--retry", dest="retry", type=int, default=0, help="Number of times to retry failed requests (default: 0).")
    parser.add_argument("--request", dest="request", action="store_true", help="Show the HTTP request.")

    if len(sys.argv) == 1:
        sys.argv.append("-h")

    args = parser.parse_args()
    return args


def get_header(args):
    headers = {
        "User-Agent": "Injector/0.1.0"
    }
    if args.header:
        name, value = args.header.split(":", 1)
        headers[name.strip()] = value.strip()

    return headers

def get_cookie(args, headers):
    if not args.cookie:
        return

    cookies = {}

    if "Cookie" in headers:
        for cookie in headers["Cookie"].split(";"):
            name, value = cookie.split("=", 1)
            cookies[name.strip()] = value.strip()

    for cookie in args.cookie.split(";"):
        name, value = cookie.split("=", 1)
        cookies[name.strip()] = value.strip()

    headers["Cookie"] = "; ".join(f"{name}={value}" for name, value in cookies.items())


def load_payloads(args):
    if not args.wordlist:
        raise ValueError("A payload wordlist is required.")

    with open(args.wordlist, "r", encoding="utf-8") as f:
        payloads = [line.strip() for line in f if line.strip()]

    return payloads


def show_request(args, headers):
    if not args.request:
        return

    parsed = urlparse(args.url)

    print("\n--- HTTP Request ---")
    print(f"{args.method} {parsed.path or '/'}")

    if parsed.query:
        print(f"Query: {parsed.query}")

    print(f"Host: {parsed.netloc}")

    for name, value in headers.items():
        print(f"{name}: {value}")

    if args.data:
        print()
        print(args.data)

    print()


def target_normalize(args):
    target = args.url.strip()

    if not target:
        raise ValueError("Target is required.")

    domain_regex = (
        r'^(?:https?://)?'
        r'(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+'
        r'[a-zA-Z]{2,63}'
        r'(?::\d{1,5})?'
        r'(?:/.*)?$'
    )

    ip_regex = (
        r'^(?:https?://)?'
        r'(?:(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\.){3}'
        r'(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)'
        r'(?::\d{1,5})?'
        r'(?:/.*)?$'
    )

    if (not re.fullmatch(domain_regex, target) and not re.fullmatch(ip_regex, target)):
        raise ValueError(f"Invalid target: {target}")
    if not re.match(r'^https?://', target, re.IGNORECASE):
        target = f"http://{target}"

    return target


def fuzz_location(args):
    locations = []

    if args.url and "INJECT" in args.url:
        locations.append("url")

    if args.data and "INJECT" in args.data:
        locations.append("data")

    if not locations:
        raise ValueError("The target must contain an 'INJECT' placeholder in the URL or data.")

    return locations


def fuzzer(args, payloads):
    headers = get_header(args)
    get_cookie(args, headers)
    show_request(args, headers)
    q = Queue()

    for payload in payloads:
        q.put(payload)

    rate_lock = Lock()
    last_request = 0.0

    def wait_for_rate():
        nonlocal last_request

        if args.rate <= 0:
            return

        interval = 1 / args.rate

        with rate_lock:
            now = time.monotonic()
            wait = interval - (now - last_request)

            if wait > 0:
                time.sleep(wait)

            last_request = time.monotonic()

    def worker():
        while True:
            try:
                payload = q.get_nowait()
            except Empty:
                break

            url = args.url
            if url:
                url = url.replace("INJECT", payload)

            data = None
            if args.data:
                data = args.data.replace("INJECT", payload)

            attempts = 0

            while True:
                start_time = time.perf_counter()

                try:
                    wait_for_rate()
                    response = requests.request(method=args.method, url=url, data=data, timeout=args.timeout, headers=headers)
                    elapsed = time.perf_counter() - start_time
                    redirect = bool(response.history)

                    if redirect:
                        print(f"Status code: {response.status_code} | Url: {url} | Payload: {payload} | Time: {elapsed:.3f}s | Redirect [YES]")
                    else:
                        print(f"Status code: {response.status_code} | Time: {elapsed:.3f}s | Payload: {payload}")
                    break

                except requests.Timeout:
                    print(f"Url: {url} | Payload: {payload} | Request timed out (Will retry if --retry is enabled)")
                    if attempts >= args.retry:
                        break

                    attempts += 1

                except requests.RequestException as e:
                    error = str(e)

                    if "Failed to resolve" in error:
                        short_error = "Failed to resolve host"
                    elif "Connection refused" in error:
                        short_error = "Connection refused"
                    elif "Max retries exceeded" in error:
                        short_error = "Max retries exceeded"
                    else:
                        short_error = error.split(" (Caused by")[0]

                    print(f"Url: {url} | Payload: {payload} | Request Error: {short_error}")
                    if attempts >= args.retry:
                        break

                    attempts += 1
                except Exception as e:
                    print(f"Url: {url} | Payload: {payload} | Python Error: {e}")
                    break

            q.task_done()

    threads = []
    for _ in range(args.thread):
        thread = Thread(target=worker, daemon=True)
        thread.start()
        threads.append(thread)

    q.join()
    for thread in threads:
        thread.join()


def display(
    url,
    payload,
    status_code=None,
    elapsed=None,
    redirect=False,
    error=None,
    timeout=False,
    retry=None,
):
    if timeout:
        message = (f"Url: {url} | Payload: {payload} | Request timed out")

    elif error:
        if "Failed to resolve" in error:
            short_error = "Failed to resolve host"
        elif "Connection refused" in error:
            short_error = "Connection refused"
        elif "Connection timed out" in error:
            short_error = "Connection timed out"
        elif "Max retries exceeded" in error:
            short_error = "Max retries exceeded"
        else:
            short_error = error.split(" (Caused by")[0]

        message = (f"Url: {url} | Payload: {payload} | Request Error: {short_error}")

    else:
        if redirect:
            message = (f"Status code: {status_code} | Url: {url} | Payload: {payload} | Time: {elapsed:.3f}s | Redirect [YES]")
        else:
            message = (f"Status code: {status_code} | Time: {elapsed:.3f}s |Payload: {payload}")

    if retry:
        message += f" | Request will be retried ({retry})"

    print(message)

    
def main():
    print(banner())

    try:
        args = build_flags()
        # Normalize target before fuzzing.
        args.url = target_normalize(args)

        if args.rate < 0:
            raise ValueError("--rate must be >= 0.")
        if args.thread <= 0:
            raise ValueError("--thread must be greater than 0.")
        if args.timeout <= 0:
            raise ValueError("--timeout must be greater than 0.")
        if args.retry < 0:
            raise ValueError("--retry must be >= 0.")

        locations = fuzz_location(args)
        print(f"[+] Injection locations: {', '.join(locations)}")
        payloads = load_payloads(args)
        if not payloads:
            raise ValueError("Payload wordlist is empty.")

        print(f"[+] Loaded {len(payloads)} payloads")
        fuzzer(args, payloads)

    except KeyboardInterrupt:
        print("\n[!] Interrupted by user. Exiting...")
        raise SystemExit(130)

    except FileNotFoundError:
        print(f"[ERROR] Wordlist not found: {args.wordlist}")
        raise SystemExit(1)

    except ValueError as e:
        print(f"[ERROR] {e}")
        raise SystemExit(1)

    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()