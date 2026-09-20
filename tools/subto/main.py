#!/usr/bin/env python3

from pathlib import Path
import argparse
import re
from urllib.parse import urlparse
import yaml

from scanner import scan
from display import banner, frame


def parse_args():
    parser = argparse.ArgumentParser(
        prog="subto",
        description="An automated subdomain takeover detection tool for faster testing",
        add_help=True,
        formatter_class=lambda prog: argparse.RawDescriptionHelpFormatter(
            prog,
            max_help_position=50,
            width=150,
        ),
    )

    target = parser.add_argument_group("TARGET")
    target.add_argument("-u", "--url", dest="url", type=str, help="Scan a single subdomain")
    target.add_argument("-l", "--list", dest="target_list", type=str, help="Scan subdomains from a file")

    performance = parser.add_argument_group("PERFORMANCE")
    performance.add_argument("-t", "--thread", dest="thread", type=int, default=5, help="Number of concurrent workers (default: 5)")
    performance.add_argument("--delay", "--delay", dest="delay", type=float, default=0.0, help="Delay between requests in milliseconds")
    performance.add_argument("--timeout", dest="timeout", type=int, default=6, help="Request timeout in seconds (default: 6)")

    fingerprint = parser.add_argument_group("FINGERPRINT")
    fingerprint.add_argument("--provider", dest="provider", type=str, help="Scan only a specific provider")
    fingerprint.add_argument("--list-providers", dest="list_providers", type=str, help="List supported providers")

    network = parser.add_argument_group("NETWORK")
    network.add_argument("--http", dest="http", action="store_true", help="Check HTTP")
    network.add_argument("--https", dest="https", action="store_true", help="Check HTTPS")
    network.add_argument("--dns-only", dest="dns_only", action="store_true", help="DNS checks only")

    args = parser.parse_args()

    if not args.url and not args.target_list:
        parser.print_help()
        raise SystemExit

    return args


def normalize_url(url):
    url = url.strip()

    if not re.match(r"^https?://", url, re.IGNORECASE):
        url = "https://" + url

    try:
        parsed = urlparse(url)

        if parsed.scheme not in ("http", "https") or not parsed.hostname:
            return None

        normalized = f"{parsed.scheme}://{parsed.hostname}"

        if parsed.port:
            normalized += f":{parsed.port}"

        return normalized

    except ValueError:
        return None


def extract_target(line):
    line = line.strip()

    if not line:
        return None

    return line.split()[0]

    
def build_config(args):
    return {
        "url": args.url,
        "target_list": args.target_list,
        "thread": args.thread,
        "delay": args.delay,
        "timeout": args.timeout,
        "http": args.http,
        "https": args.https,
        "dns_only": args.dns_only,
        "provider": args.provider,
        "list_providers": args.list_providers
    }


BASE_DIR = Path(__file__).resolve().parent


def load_fingerprint(path):
    with open(path, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def main():
    try:
        print(banner())

        args = parse_args()
        config = build_config(args)

        fingerprint = load_fingerprint(BASE_DIR / "db" / "cname_fingerprint.yaml")
        total = len(fingerprint["services"])

        # Print total services
        print(f"[*] Loaded {total} fingerprints")

        if config["url"]:
            target = normalize_url(config["url"])

            if not target:
                print(f"[!] Invalid target: {config['url']}")
                return

            result = scan(target, config, fingerprint)
            frame(result)

        elif config["target_list"]:
            try:
                with open(config["target_list"], "r", encoding="utf-8") as file:
                    targets = [
                        line.strip()
                        for line in file
                        if line.strip()
                    ]

            except FileNotFoundError:
                print(f"[!] Target list not found: {config['target_list']}")
                return

            print(f"[*] Scanning {len(targets)} subdomains")

            for target in targets:
                target = extract_target(target)

                if not target:
                    print("[!] Invalid target")
                    continue

                target = normalize_url(target)

                if not target:
                    print(f"[!] Invalid target: {target}")
                    continue

                result = scan(target, config)
                frame(result)

    except KeyboardInterrupt:
        print("\n[!] Scan interrupted.")


if __name__ == "__main__":
    main()