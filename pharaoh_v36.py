# PHARAOH V36 - ULTIMATE - ANDROID 15 GOD
# by ADEL89 - ALL IN ONE
import socket, requests, threading, dns.resolver
from datetime import datetime

GOLD="\033[33m";GREEN="\033[32m";CYAN="\033[36m";RED="\033[31m";RESET="\033[0m";BOLD="\033[1m"

# FIX ANDROID 15
resolver=dns.resolver.Resolver(configure=False)
resolver.nameservers=['8.8.8.8','1.1.1.1']
resolver.timeout=2

def banner():
    print(f"{GOLD}{BOLD}╔══════════════════════════════╗")
    print(f"║  PHARAOH V36 ULTIMATE        ║")
    print(f"║  ANDROID 15 EDITION          ║")
    print(f"╚══════════════════════════════╝{RESET}")

def dns_info(target):
    print(f"\n{GOLD}[1] DNS INFO:{RESET}")
    try:
        ip=socket.gethostbyname(target)
        print(f"{GREEN}IP: {ip}{RESET}")
        return ip
    except Exception as e:
        print(f"{RED}{e}{RESET}")
        return None

def subdomains(target):
    print(f"\n{GOLD}[2] SUBDOMAIN HUNTER:{RESET}")
    subs=["www","mail","api","admin","dev","test","app","drive","docs","map","m","vpn","ftp","blog","shop","support","portal","secure","cloud","cdn","auth","login","sso","beta","staging","dashboard"]
    found=[]
    def check(s):
        full=f"{s}.{target}"
        try:
            ans=resolver.resolve(full,'A')
            ip=str(ans[0])
            print(f"{GREEN}[FOUND] {full} -> {ip}{RESET}")
            found.append(full)
        except: pass
    threads=[]
    for s in subs:
        t=threading.Thread(target=check, args=(s,))
        t.start()
        threads.append(t)
    for t in threads: t.join()
    print(f"{CYAN}Total: {len(found)}{RESET}")
    return found

def tech_detect(target):
    print(f"\n{GOLD}[3] TECH DETECTOR:{RESET}")
    try:
        r=requests.get(f"https://{target}", timeout=5)
        if 'Server' in r.headers: print(f"{CYAN}Server: {r.headers['Server']}{RESET}")
        if 'cf-ray' in r.headers: print(f"{CYAN}WAF: Cloudflare{RESET}")
        if 'gws' in str(r.headers).lower(): print(f"{CYAN}Google Web Server{RESET}")
        print(f"{GREEN}Status: {r.status_code} | Size: {len(r.text)}{RESET}")
        
        print(f"\n{GOLD}[4] INTERESTING PATHS:{RESET}")
        for p in ["/robots.txt","/sitemap.xml","/admin","/api","/.env","/login"]:
            try:
                rr=requests.get(f"https://{target}{p}", timeout=3)
                if rr.status_code!=404:
                    print(f"{GREEN}[{rr.status_code}] {p}{RESET}")
            except: pass
    except Exception as e:
        print(e)

# MAIN
banner()
target=input(f"{GOLD}Target: {RESET}").strip()
if not target: exit()

start=datetime.now()
ip=dns_info(target)
subs=subdomains(target)
tech_detect(target)

filename=f"PHARAOH_V36_{target}_{datetime.now().strftime('%H%M')}.txt"
with open(filename,"w") as f:
    f.write(f"TARGET: {target} IP: {ip}\n")
    f.write(f"SUBS: {subs}\n")
    f.write(f"DATE: {start}\n")

print(f"\n{GOLD}{BOLD}SAVED {filename}{RESET}")
print(f"{GREEN}{BOLD}PHARAOH V36 ULTIMATE DONE - ANDROID 15 KING 👑🔱{RESET}")
