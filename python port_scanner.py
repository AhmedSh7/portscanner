import socket
import threading
import time
from datetime import datetime
import argparse
import json
import csv
import os

# ------------------- CLI Argument Parser ------------------- #
parser = argparse.ArgumentParser(description="Multi-IP Port Scanner")

parser.add_argument("--targets", required=True, help="Path to file with list of IP addresses")
parser.add_argument("--start", type=int, help="Start port (required if --ports is not provided)")
parser.add_argument("--end", type=int, help="End port (required if --ports is not provided)")
parser.add_argument("--ports", help="Path to file with specific ports to scan (optional)")
parser.add_argument("--threads", type=int, default=100, help="Max concurrent threads per IP (default: 100)")
parser.add_argument("--format", choices=["txt", "json", "csv"], default="txt", help="Output format (default: txt)")

args = parser.parse_args()

# ------------------- Load Targets ------------------- #
with open(args.targets, "r") as file:
    targets = [line.strip() for line in file if line.strip()]

# ------------------- Determine Ports to Scan ------------------- #
if args.ports:
    with open(args.ports, "r") as f:
        ports = set()
        for line in f:
            for item in line.strip().split(","):
                if item.strip().isdigit():
                    ports.add(int(item.strip()))
    port_list = sorted(ports)
elif args.start is not None and args.end is not None:
    port_list = list(range(args.start, args.end + 1))
else:
    parser.error("You must provide either --ports or both --start and --end.")

max_threads = args.threads
print_lock = threading.Lock()

# ------------------- Scanner Function ------------------- #
def scan_ip(target):
    try:
        hostname = socket.gethostbyaddr(target)[0]
    except socket.herror:
        hostname = "Unknown"

    print(f"\n[+] Scanning {target} ({hostname}) on {len(port_list)} port(s)...\n")

    start_time = time.time()
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    base_filename = f"scan_results_{target.replace('.', '_')}_{timestamp}"

    results = []

    def scan_port(port):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.5)
        try:
            result = s.connect_ex((target, port))
            if result == 0:
                try:
                    service = socket.getservbyport(port)
                except:
                    service = "unknown"
                try:
                    banner = s.recv(1024).decode().strip()
                except:
                    banner = "No banner"

                result_data = {
                    "port": port,
                    "service": service,
                    "banner": banner
                }

                with print_lock:
                    print(f"Port {port} is OPEN ({service}) - Banner: {banner}")
                    results.append(result_data)
        finally:
            s.close()

    threads = []
    for port in port_list:
        thread = threading.Thread(target=scan_port, args=(port,))
        threads.append(thread)
        thread.start()

        if len(threads) >= max_threads:
            for t in threads:
                t.join()
            threads = []

    for t in threads:
        t.join()

    # ------------------- Save Results ------------------- #
    if args.format == "txt":
        filename = f"{base_filename}.txt"
        with open(filename, "w") as f:
            for r in results:
                f.write(f"Port {r['port']} is OPEN ({r['service']}) - Banner: {r['banner']}\n")
    elif args.format == "json":
        filename = f"{base_filename}.json"
        with open(filename, "w") as f:
            json.dump(results, f, indent=2)
    elif args.format == "csv":
        filename = f"{base_filename}.csv"
        with open(filename, "w", newline='') as f:
            writer = csv.DictWriter(f, fieldnames=["port", "service", "banner"])
            writer.writeheader()
            writer.writerows(results)

    end_time = time.time()
    elapsed = end_time - start_time
    minutes = int(elapsed // 60)
    seconds = int(elapsed % 60)

    print(f"[+] Scan of {target} complete. Results saved to {filename}")
    print(f"[+] Time elapsed: {minutes} minutes {seconds} seconds")

# ------------------- Run Scanner ------------------- #
for target in targets:
    scan_ip(target)
