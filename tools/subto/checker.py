import threading
from queue import Queue
import requests
import time
import yaml


def delay(config):
    if config["delay"] > 0.0:
        time.sleep(config["delay"])


def requester(config, tasks):
    q = Queue()
    done = Queue()

    for task in tasks:
        q.put(task)

    stop = False

    def worker():
        while True:
            task = q.get()

            if task is None:
                q.task_done()
                break

            try:
                response = requests.get(url=task["url"], timeout=config["timeout"],)

                done.put({"task": task, "response": response, "error": None,})

            except requests.exceptions.RequestException as error:
                done.put({"task": task, "response": None, "error": error,})

            finally:
                delay(config)
                q.task_done()

    threads = []

    for _ in range(config["thread"]):
        t = threading.Thread(target=worker)
        t.start()
        threads.append(t)

    try:
        q.join()

    except KeyboardInterrupt:
        stop = True

    finally:
        for _ in threads:
            q.put(None)

        for t in threads:
            t.join()

    if stop:
        raise KeyboardInterrupt

    return done


def checker(target, cname, response, fingerprint):
    cname = cname.rstrip(".").lower()

    for service in fingerprint["services"]:
        # Check CNAME
        cname_patterns = service.get("cname", [])
        matched = False

        for pattern in cname_patterns:
            pattern = pattern.rstrip(".").lower()

            if cname == pattern or cname.endswith("." + pattern):
                matched = True
                break

        if not matched:
            continue

        # HTTP request failed
        if response is None:
            return {
                "target": target,
                "cname": cname,
                "potential": False,
                "provider": service["name"],
                "confidence": service["confidence"],
            }

        fingerprints = service.get("fingerprints", {})

        # Check status code
        statuses = service.get("status", [])

        status_match = (
            not statuses
            or response.status_code in statuses
        )

        if not status_match:
            return {
                "target": target,
                "cname": cname,
                "potential": False,
                "provider": service["name"],
                "confidence": service["confidence"],
            }

        # Check response body
        body = response.text.lower()

        for fingerprint_text in fingerprints.get("body", []):
            if fingerprint_text.lower() in body:
                return {
                    "target": target,
                    "cname": cname,
                    "potential": True,
                    "provider": service["name"],
                    "confidence": service["confidence"],
                }

        # Check response headers
        headers = "\n".join(
            f"{key}: {value}"
            for key, value in response.headers.items()
        ).lower()

        for fingerprint_text in fingerprints.get("header", []):
            if fingerprint_text.lower() in headers:
                return {
                    "target": target,
                    "cname": cname,
                    "potential": True,
                    "provider": service["name"],
                    "confidence": service["confidence"],
                }

        # CNAME matched, but no takeover fingerprint
        return {
            "target": target,
            "cname": cname,
            "potential": False,
            "provider": service["name"],
            "confidence": service["confidence"],
        }

    # No CNAME fingerprint matched
    return {
        "target": target,
        "cname": cname,
        "potential": False,
        "provider": None,
        "confidence": None,
    }