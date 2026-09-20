import dns.resolver


""" This file is just simply like this. no need to change """
def get_cname(target):
    target = target.strip()

    try:
        answers = dns.resolver.resolve(target, "CNAME")
        return str(answers[0].target).rstrip(".")

    except (
        dns.resolver.NoAnswer,
        dns.resolver.NXDOMAIN,
        dns.resolver.NoNameservers,
        dns.resolver.Timeout,
        dns.resolver.LifetimeTimeout,
        dns.name.LabelTooLong,
        dns.name.EmptyLabel,
    ):
        return None