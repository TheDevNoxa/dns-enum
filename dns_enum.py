#!/usr/bin/env python3
"""
dns-enum — DNS enumeration & subdomain discovery
Author : Noxa (Valentin Lagarde)
Usage  : python3 dns_enum.py -d example.com -w wordlist.txt
"""

import argparse
import socket
import concurrent.futures
import dns.resolver
import dns.zone
import dns.query
import dns.exception
from dataclasses import dataclass, field

DNS_RECORD_TYPES = ["A", "AAAA", "MX", "NS", "TXT", "SOA", "CNAME", "PTR"]

DEFAULT_WORDLIST = [
    "www", "mail", "ftp", "localhost", "webmail", "smtp", "pop", "ns1", "ns2",
    "admin", "vpn", "api", "dev", "staging", "test", "app", "portal",
    "remote", "server", "cdn", "git", "gitlab", "jenkins", "jira",
    "monitoring", "grafana", "dashboard", "internal", "intranet", "db",
    "backup", "files", "static", "blog", "shop", "store", "forum",
]


@dataclass
class DNSResult:
    domain: str
    records: dict = field(default_factory=dict)
    subdomains: list = field(default_factory=list)
    zone_transfer: bool = False


def query_records(domain: str, resolver: dns.resolver.Resolver) -> dict:
    records = {}
    for rtype in DNS_RECORD_TYPES:
        try:
            answers = resolver.resolve(domain, rtype, raise_on_no_answer=False)
            if answers.rrset:
                records[rtype] = [str(r) for r in answers.rrset]
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer,
                dns.exception.Timeout, dns.resolver.NoNameservers):
            pass
        except Exception:
            pass
    return records


def check_zone_transfer(domain: str, nameservers: list[str]) -> list[str]:
    """Attempt AXFR zone transfer against each nameserver."""
    found = []
    for ns in nameservers:
        ns_ip = ns.rstrip(".")
        try:
            ns_ip = socket.gethostbyname(ns_ip)
            zone = dns.zone.from_xfr(dns.query.xfr(ns_ip, domain, timeout=5))
            names = [str(n) for n in zone.nodes.keys()]
            found.extend(names)
            print(f"  [!] Zone transfer SUCCESS on {ns} — {len(names)} records leaked!")
        except Exception:
            pass
    return found


def resolve_subdomain(sub: str, domain: str) -> dict | None:
    fqdn = f"{sub}.{domain}"
    try:
        ip = socket.gethostbyname(fqdn)
        return {"fqdn": fqdn, "ip": ip}
    except socket.gaierror:
        return None


def bruteforce_subdomains(domain: str, wordlist: list[str], threads: int = 50) -> list[dict]:
    found = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as ex:
        futures = {ex.submit(resolve_subdomain, sub, domain): sub for sub in wordlist}
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result:
                found.append(result)
                print(f"  [+] {result['fqdn']:<45} {result['ip']}")
    return sorted(found, key=lambda x: x["fqdn"])


def load_wordlist(path: str | None) -> list[str]:
    if path:
        try:
            with open(path) as f:
                return [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            print(f"[!] Wordlist not found: {path} — using built-in list")
    return DEFAULT_WORDLIST


COLORS = {"A": "\033[92m", "MX": "\033[94m", "NS": "\033[96m",
          "TXT": "\033[93m", "SOA": "\033[37m"}
RESET = "\033[0m"


def print_results(result: DNSResult) -> None:
    print(f"\n{'=' * 65}")
    print(f"  DNS ENUMERATION — {result.domain}")
    print(f"{'=' * 65}")

    print("\n  [ DNS Records ]\n")
    for rtype, values in result.records.items():
        color = COLORS.get(rtype, "")
        for v in values:
            print(f"  {color}{rtype:<8}{RESET} {v}")

    if result.zone_transfer:
        print("\n  [!] ZONE TRANSFER SUCCESSFUL — full DNS zone exposed!")

    if result.subdomains:
        print(f"\n  [ Subdomains found: {len(result.subdomains)} ]\n")
        for s in result.subdomains:
            print(f"  {s['fqdn']:<45} → {s['ip']}")

    print(f"\n{'=' * 65}\n")


def main():
    parser = argparse.ArgumentParser(description="DNS enumeration tool (educational)")
    parser.add_argument("-d", "--domain",   required=True, help="Target domain")
    parser.add_argument("-w", "--wordlist", default=None,  help="Subdomain wordlist file")
    parser.add_argument("--no-bruteforce", action="store_true", help="Skip subdomain bruteforce")
    parser.add_argument("--no-axfr",       action="store_true", help="Skip zone transfer attempt")
    parser.add_argument("--threads", type=int, default=50, help="Threads for subdomain scan")
    args = parser.parse_args()

    result = DNSResult(domain=args.domain)
    resolver = dns.resolver.Resolver()
    resolver.timeout = 3
    resolver.lifetime = 5

    print(f"[*] Enumerating DNS records for {args.domain} ...")
    result.records = query_records(args.domain, resolver)

    if not args.no_axfr and "NS" in result.records:
        print("[*] Attempting zone transfer ...")
        zt_records = check_zone_transfer(args.domain, result.records["NS"])
        if zt_records:
            result.zone_transfer = True

    if not args.no_bruteforce:
        wordlist = load_wordlist(args.wordlist)
        print(f"[*] Bruteforcing subdomains ({len(wordlist)} words, {args.threads} threads) ...")
        result.subdomains = bruteforce_subdomains(args.domain, wordlist, args.threads)

    print_results(result)


if __name__ == "__main__":
    main()
