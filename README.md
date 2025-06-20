#  Python Port Scanner CLI Tool

This is a multithreaded Python-based port scanner that supports scanning multiple IP addresses and ports, with optional banner grabbing and output in TXT, JSON, or CSV formats.

##  Features

- Scan single or multiple target IPs
- Specify port range or provide a list of ports
- Banner grabbing for open ports
- Multithreading support for faster scanning
- Export scan results to `.txt`, `.json`, or `.csv`
- CLI usage with `argparse`

##  Requirements

- Python 3.6+
- No external dependencies (uses standard libraries)

## ️ Usage

```bash
python port_scanner.py --targets targets.txt --start 1 --end 1024 --format txt

Optional Flags
--ports ports.txt – Scan specific ports listed in a file instead of a range

--threads 50 – Set max threads (default: 100)

--format – Output format (txt, json, or csv)
python port_scanner.py --targets targets.txt --ports ports.txt --threads 50 --format json

Example
python port_scanner.py --targets targets.txt --ports ports.txt --threads 50 --format json

File Structure 
 project/
├── port_scanner.py
├── targets.txt
├── ports.txt
├── README.md
└── scan_results_*.{txt,json,csv}

Example Output
Port 22 is OPEN (ssh) - Banner: SSH-2.0-OpenSSH_9.9

Author
Ahmed Shammout