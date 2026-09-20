from dns_utils.cname import get_cname
from checker import requester, checker


def scan(target, config, fingerprint):
    cname = get_cname(target)

    if not cname:
        return {
            "target": target,
            "cname": None,
            "potential": False,
            "provider": None,
            "confidence": None,
        }

    tasks = [{"url": f"https://{target}", "cname": cname,}]

    responses = requester(config, tasks)
    result = responses.get()

    return checker(target=target, cname=cname, response=result["response"], fingerprint=fingerprint,)