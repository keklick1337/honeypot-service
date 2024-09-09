# Honeypot Service Simulator

This project implements a lightweight honeypot using Python and `asyncio` to simulate various network services. It listens on a range of ports and logs connections, making it useful for detecting potential unauthorized activity on a network.

## Features

- Simulates network services based on configurable banners.
- Logs incoming connections, including the received data (optionally in hex format).
- Allows dynamic assignment of ports, excluding specific reserved ports (e.g., 22, 80, 443).
- Multi-service support using asynchronous I/O for handling many connections simultaneously.

## Requirements

- Python 3.7+
- `asyncio` module (standard with Python 3.7+)
- JSON configuration file for the banners

## Installation

1. Clone the repository:
```bash
git clone https://github.com/keklick1337/honeypot-service.git
cd honeypot-service
```

2. Create the `logs/` directory for connection logs:
```bash
mkdir logs
```

3. Prepare a `banners_list.json` file. This JSON file should contain the banner information for each service. Example content:
```json
{
    "http": {
        "banner": "HTTP/1.1 200 OK\r\nServer: FakeHTTP\r\n\r\n",
        "echo_data": false
    },
    "ssh": {
        "banner": "SSH-2.0-OpenSSH_8.2p1\r\n",
        "echo_data": false
    },
    "echo": {
        "banner": "",
        "echo_data": true
    }
}
```

4. Ensure you have the necessary dependencies installed (Python 3.7+).

## Usage

To start the honeypot, use the following command:

```bash
python3 honeypot.py --start <START_PORT> --end <END_PORT> --ip <BIND_IP> [--exclude <PORTS_TO_EXCLUDE>]
```

### Command-Line Arguments

- `--start`: The start of the port range to listen on (default: `1`).
- `--end`: The end of the port range to listen on (default: `65535`).
- `--ip`: The IP address to bind the ports (default: `0.0.0.0`, listens on all interfaces).
- `--exclude`: List of ports to exclude from the honeypot simulation (default: `[22, 80, 443]`).

Example:

```bash
python3 honeypot.py --start 1000 --end 2000 --ip 192.168.1.100 --exclude 22 80 443
```

This will simulate services on ports 1000–2000 on IP `192.168.1.100`, excluding ports 22, 80, and 443.

## Banners Configuration

The banners for different services are configured using the `banners_list.json` file, which should be placed in the `templates/` directory.

Example `templates/banners_list.json` content:

```json
{
    "http": {
        "banner": "HTTP/1.1 200 OK\r\nServer: FakeHTTP\r\n\r\n",
        "echo_data": false
    },
    "ssh": {
        "banner": "SSH-2.0-OpenSSH_8.2p1\r\n",
        "echo_data": false
    },
    "echo": {
        "banner": "",
        "echo_data": true
    }
}
```

Make sure that the `banners_list.json` file is available in the `templates/` directory before running the honeypot.

## Logging

Logs of incoming connections are stored in the `logs/` directory. Each connection is logged in JSONL format, where each line is a JSON object describing the event.

Example log entry:

```json
{
    "service_id": "Jenkins",
    "event_time": "2024-09-09 08:16:33",
    "remote_address": "10.10.10.55",
    "remote_port": 52200,
    "local_address": "10.10.10.125",
    "local_port": 5552,
    "received_data_is_hex": false,
    "received_data": "GET / HTTP/1.1\r\nHost: testhost:5552\r\nConnection: keep-alive\r\nsec-ch-ua: \"Chromium\";v=\"128\", \"Not;A=Brand\";v=\"24\", \"Google Chrome\";v=\"128\"\r\nsec-ch-ua-mobile: ?0\r\nsec-ch-ua-platform: \"macOS\"\r\nUpgrade-Insecure-Requests: 1\r\nUser-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)\r\nAccept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7\r\nSec-Fetch-Site: none\r\nSec-Fetch-Mode: navigate\r\nSec-Fetch-User: ?1\r\nSec-Fetch-Dest: document\r\nAccept-Encoding: gzip, deflate, br, zstd\r\nAccept-Language: en-US\r\n\r\n"
}
```

## License

This project is open-source and available under the MIT License.