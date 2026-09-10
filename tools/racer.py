#!/usr/bin/env python3

from threading import Thread, Barrier, Lock
import argparse
import requests
import sys
import time
from urllib.parse import urlparse


VERSION = "0.1.0"
AUTHOR = "Hunter"


def banner():
    return fr"""
     ___   ___   ___  ___   ___
    | . | | . | |    |   | | . |
    |  _| |___| |    |___| |  _|
    |  \  |   | |___ |___  |  \  v{VERSION}

Built by: {AUTHOR}
    """


def build_flags():
    parser = argparse.ArgumentParser(
        prog="Racer",
        description=(
            "Send concurrent HTTP requests.\n\n"
            "** IMPORTANT: **\n"
            "  Use --burst to send multiple requests simultaneously."
        ),
        add_help=True,
        formatter_class=lambda prog: argparse.RawDescriptionHelpFormatter(
            prog,
            max_help_position=50,
            width=150,
        ),
    )

    parser.add_argument("-H", "--header", dest="header", action="append", help="Custom HTTP header. Can be specified multiple times.")
    parser.add_argument("-b", "--cookie", dest="cookie", type=str, help="Custom cookies, e.g. 'a=1; b=2'.")
    parser.add_argument("-X", "--method", dest="method", type=str, default="GET", help="HTTP method (default: GET).")
    parser.add_argument("-d", "--data", dest="data", type=str, help="Request body.")
    parser.add_argument("-u", "--url", dest="url", type=str, help="Target URL.")
    parser.add_argument("-r", "--burst", dest="burst", type=int, default=1, help="Number of requests to send simultaneously (default: 1).")
    parser.add_argument("--payload", dest="payload", type=str, help="Payload(s) to replace INJ with, e.g. '1,2'.")
    parser.add_argument("--request", dest="request", action="store_true", help="Show the HTTP request before sending.")

    if len(sys.argv) == 1:
        sys.argv.append("-h")

    return parser.parse_args()


def get_header(args):
    headers = {
        "User-Agent": f"Racer/{VERSION}"
    }

    if not args.header:
        return headers

    for value in args.header:
        if ":" not in value:
            raise ValueError(f"Invalid header: {value}")

        name, content = value.split(":", 1)
        headers[name.strip()] = content.strip()

    return headers


def get_cookie(args, headers):
    if not args.cookie:
        return

    cookies = {}

    if "Cookie" in headers:
        for cookie in headers["Cookie"].split(";"):
            cookie = cookie.strip()

            if not cookie or "=" not in cookie:
                continue

            name, value = cookie.split("=", 1)
            cookies[name.strip()] = value.strip()

    for cookie in args.cookie.split(";"):
        cookie = cookie.strip()

        if not cookie:
            continue

        if "=" not in cookie:
            raise ValueError(f"Invalid cookie: {cookie}")

        name, value = cookie.split("=", 1)
        cookies[name.strip()] = value.strip()

    headers["Cookie"] = "; ".join(f"{name}={value}" for name, value in cookies.items())


def build_payloads(value, burst):
    if not value:
        return [None] * burst

    payloads = [payload.strip() for payload in value.split(",")]

    if not payloads:
        return [None] * burst

    if len(payloads) < burst:
        payloads = (payloads * burst)[:burst]

    return payloads[:burst]


def build_request(args, payload):
    url = args.url
    data = args.data

    if payload is not None:
        if "INJ" not in url and (not data or "INJ" not in data):
            raise ValueError("--payload requires INJ placeholder in the URL or request body.")

        url = url.replace("INJ", payload)

        if data:
            data = data.replace("INJ", payload)

    return url, data


def show_request(args, headers):
    if not args.request:
        return

    parsed = urlparse(args.url)

    print("\n--- HTTP Request ---")
    print(f"{args.method.upper()} {parsed.path or '/'}")

    if parsed.query:
        print(f"Query: {parsed.query}")

    print(f"Host: {parsed.netloc}")

    for name, value in headers.items():
        print(f"{name}: {value}")

    if args.data:
        print()
        print(args.data)

    print()


def display(url, payload, status_code=None, elapsed=None, error=None):
    if error:
        print(f"[ERROR] Url: {url} | Payload: {payload} | Request Error: {error}")
        return

    print(f"[{status_code}] Url: {url} | Payload: {payload} | Time: {elapsed:.3f}s")


def worker(args, payload, headers, barrier, result_lock):
    try:
        url, data = build_request(args, payload)

        barrier.wait()

        start_time = time.perf_counter()

        response = requests.request(
            method=args.method,
            url=url,
            headers=headers,
            data=data,
            timeout=10,
            allow_redirects=False,
        )

        elapsed = time.perf_counter() - start_time

        with result_lock:
            display(url=url, payload=payload, status_code=response.status_code, elapsed=elapsed)

    except requests.RequestException as e:
        with result_lock:
            display(url=url, payload=payload, error=str(e))


def racer(args, payloads):
    headers = get_header(args)
    get_cookie(args, headers)
    show_request(args, headers)

    result_lock = Lock()
    barrier = Barrier(len(payloads))
    threads = []

    for payload in payloads:
        thread = Thread(
            target=worker,
            args=(args, payload, headers, barrier, result_lock),
            daemon=True,
        )
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()


def main():
    print(banner())

    try:
        args = build_flags()

        if not args.url:
            raise ValueError("Target URL is required.")

        if args.burst <= 0:
            raise ValueError("--burst must be greater than 0.")

        payloads = build_payloads(args.payload, args.burst)

        racer(args, payloads)

    except KeyboardInterrupt:
        print("\n[!] Interrupted by user. Exiting...")
        raise SystemExit(130)

    except ValueError as e:
        print(f"[ERROR] {e}")
        raise SystemExit(1)

    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()