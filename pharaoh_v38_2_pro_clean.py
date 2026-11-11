#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
👑 PHARAOH V38.2 PRO - CLEAN ARCHITECTURE
Author: ADEL89 - Fixes: REAL DNS, Clean OOP, Accurate Scans
"""

import os, sys, socket, ssl, json, requests
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

VERSION = "38.2 PRO CLEAN"
TIMEOUT = 8
THREADS = 20

class Colors:
    GREEN = "\033[92m"; RED = "\033[91m"; YELLOW = "\033[93m"
    CYAN = "\033[96m"; RESET = "\033[0m"; BOLD = "\033[1m"

class DNSFixer:
    TERMUX_RESOLV = Path("/data/data/com.termux/files/usr/etc/resolv.conf")
    def __init__(self):
        self.log_file = Path("pharaoh_dns_proof.log")
        self.fixed = False; self.method = None
    def log(self, msg):
        ts = datetime.now().isoformat()
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(f"[{ts}] {msg}\n")
        print(f"{Colors.CYAN}[DNS-FIX]{Colors.RESET} {msg}")
    def try_termux_resolv(self):
        try:
            self.TERMUX_RESOLV.parent.mkdir(parents=True, exist_ok=True)
            self.TERMUX_RESOLV.write_text("nameserver 8.8.8.8\nnameserver 1.1.1.1\n")
            self.log(f"WROTE Termux resolv.conf: {self.TERMUX_RESOLV}")
            self.method = "termux_resolv_write"; self.fixed = True
            return True
        except Exception as e:
            self.log(f"Failed: {e}"); return False
    def test_resolution(self):
        for host in ["google.com","cloudflare.com","github.com"]:
            try:
                ip = socket.gethostbyname(host)
                self.log(f"RESOLUTION OK: {host} -> {ip}")
                self.method = self.method or "socket_default"
                self.fixed = True
                return host, ip
            except: continue
        return None, None
    def fix(self):
        print(f"\n{Colors.BOLD}--- PHARAOH DNS FIXER v38.2 (Android 15) ---{Colors.RESET}")
        self.log("=== START DNS FIX v38.2 ===")
        self.try_termux_resolv()
        host, ip = self.test_resolution()
        if self.fixed and ip:
            print(f"{Colors.GREEN}[OK] DNS FIXED: {host} -> {ip} | Method: {self.method}{Colors.RESET}")
            return True
        else:
            print(f"{Colors.RED}[FAIL] DNS FAILED{Colors.RESET}"); return False

class PharaohEngine:
    def __init__(self, target):
        self.target = target.strip().lower().replace("https://","").replace("http://","").split("/")[0]
        self.ip = None
        print(f"\n{Colors.BOLD}PHARAOH {VERSION} - TARGET: {self.target}{Colors.RESET}")
    def resolve_target(self):
        try:
            self.ip = socket.gethostbyname(self.target)
            print(f"{Colors.GREEN}[*] IP: {self.target} => {self.ip}{Colors.RESET}"); return True
        except Exception as e:
            print(f"{Colors.RED}[!] Cannot resolve {self.target}: {e}{Colors.RESET}"); return False
    def tool_dns(self):
        print(f"\n{Colors.YELLOW}[1/8] DNS LOOKUP{Colors.RESET}")
        try:
            a = socket.gethostbyname(self.target)
            print(f"  A Record: {a}")
        except Exception as e: print(f"  Error: {e}")
    def tool_whois(self):
        print(f"\n{Colors.YELLOW}[2/8] WHOIS (Port 43 Real){Colors.RESET}")
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(TIMEOUT); s.connect(("whois.iana.org", 43))
            s.sendall((self.target + "\r\n").encode())
            data = b""
            while True:
                chunk = s.recv(4096)
                if not chunk: break
                data += chunk
            s.close()
            text = data.decode(errors="ignore")
            for line in text.splitlines()[:20]: print(f"  {line}")
        except Exception as e: print(f"  WHOIS Error: {e}")
    def tool_subdomains(self):
        print(f"\n{Colors.YELLOW}[3/8] SUBDOMAIN ENUM (crt.sh){Colors.RESET}")
        found = set()
        try:
            url = f"https://crt.sh/?q=%25.{self.target}&output=json"
            r = requests.get(url, timeout=15, headers={"User-Agent":"Pharaoh"})
            if r.status_code == 200:
                data = r.json()
                for entry in data[:50]:
                    for n in entry.get('name_value','').split('\n'):
                        n = n.strip().lower()
                        if self.target in n and '*' not in n: found.add(n)
                print(f"  crt.sh found: {len(found)}")
                for f in list(found)[:10]: print(f"    - {f}")
        except Exception as e: print(f"  crt.sh error: {e}")
    def tool_ports(self):
        print(f"\n{Colors.YELLOW}[4/8] PORT SCAN (Threaded){Colors.RESET}")
        common_ports = {80:"http",443:"https",22:"ssh",21:"ftp",3306:"mysql",8080:"http-alt"}
        def scan_one(port):
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(1.5); res = s.connect_ex((self.ip, port)); s.close()
                if res == 0: return port
            except: pass
            return None
        with ThreadPoolExecutor(max_workers=THREADS) as ex:
            futures = [ex.submit(scan_one, p) for p in common_ports]
            for fut in as_completed(futures):
                p = fut.result()
                if p: print(f"  {Colors.GREEN}OPEN {p}/{common_ports.get(p,'unknown')}{Colors.RESET}")
    def tool_ssl(self):
        print(f"\n{Colors.YELLOW}[5/8] SSL HUNTER{Colors.RESET}")
        try:
            ctx = ssl.create_default_context()
            with ctx.wrap_socket(socket.socket(), server_hostname=self.target) as s:
                s.settimeout(TIMEOUT); s.connect((self.target, 443))
                cert = s.getpeercert()
                print(f"  Issuer: {cert.get('issuer')}"); print(f"  Valid: {cert.get('notAfter')}")
        except Exception as e: print(f"  SSL Error: {e}")
    def tool_headers(self):
        print(f"\n{Colors.YELLOW}[6/8] SECURITY HEADERS{Colors.RESET}")
        try:
            r = requests.get(f"https://{self.target}", timeout=TIMEOUT, headers={"User-Agent":"Pharaoh"})
            for h in ["Strict-Transport-Security","Content-Security-Policy","X-Frame-Options"]:
                print(f"  {'✅' if h in r.headers else '❌'} {h}")
        except Exception as e: print(f"  Error: {e}")
    def tool_cors(self):
        print(f"\n{Colors.YELLOW}[7/8] CORS TESTER{Colors.RESET}")
        try:
            r = requests.get(f"https://{self.target}", headers={"Origin":"https://evil.com"}, timeout=TIME
