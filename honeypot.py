#!/usr/bin/env python3
import asyncio
import datetime
import random
import os
import json
import socket
import argparse
from asyncio import Semaphore

_file_blocker = Semaphore()

def is_port_open(port, bind_ip):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(1)
        try:
            s.bind((bind_ip, port))
            return True
        except:
            return False

async def handle_client(reader, writer, banner_config, bind_ip, bind_port):
    addr = writer.get_extra_info('peername')
    timestamp = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%d %H:%M:%S")
    print(f"Accepted connection from {addr} on port {banner_config['port']}")

    data = b''
    try:
        while True:
            part = await reader.read(100)
            if not part:
                break
            data += part
    except asyncio.IncompleteReadError as e:
        data += e.partial
    except ConnectionResetError:
        print(f"Connection reset by peer: {addr}")
    
    data_is_hex = False
    if banner_config.get("echo_data", False):
        log_data = data.decode('utf-8', 'ignore')
    else:
        log_data = data.hex()
        data_is_hex = True

    try:
        writer.write(banner_config["banner"].encode())
        await writer.drain()
    except ConnectionResetError:
        print(f"Connection reset while sending banner to: {addr}")
    finally:
        writer.close()

    global _file_blocker
    async with _file_blocker:
        with open(f"logs/{banner_config['port']}_connections.jsonl", "a") as log_file:
            jsonl_data = json.dumps(
                {
                    "service_id": banner_config['banner_key'],
                    "event_time": timestamp,
                    "remote_address": addr[0],
                    "remote_port": addr[1],
                    "local_address": bind_ip,
                    "local_port": bind_port,
                    "received_data_is_hex": data_is_hex,
                    "received_data": log_data
                },
                ensure_ascii=False)
            log_file.write(jsonl_data + '\n')

async def start_server(port, banner_config, bind_ip):
    server = await asyncio.start_server(lambda r, w: handle_client(r, w, banner_config, bind_ip, port), bind_ip, port)
    print(f"Serving on port {port}")
    async with server:
        await server.serve_forever()

def generate_services(start_port, end_port, excluded_ports, bind_ip):
    services = []
    for port in range(start_port, end_port + 1):
        if port not in excluded_ports and is_port_open(port, bind_ip):
            banner_key = random.choice(list(banner_configs.keys()))
            services.append({
                **banner_configs[banner_key],
                "banner_key": banner_key,
                "port": port,
            })
    return services

async def main(start_port, end_port, excluded_ports, bind_ip):
    services = generate_services(start_port, end_port, excluded_ports, bind_ip)

    await asyncio.gather(*(start_server(service['port'], service, bind_ip) for service in services))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run fake services on specified ports.")
    parser.add_argument("--start", type=int, default=1, help="Start of port range")
    parser.add_argument("--end", type=int, default=65535, help="End of port range")
    parser.add_argument("--ip", type=str, default="0.0.0.0", help="IP to bind ports")
    parser.add_argument("--exclude", nargs="*", type=int, default=[22, 80, 443], help="Ports to exclude")

    args = parser.parse_args()

    if not os.path.exists('./logs/'):
        os.makedirs('./logs/', exist_ok=True)
    
    with open('templates/banners_list.json', 'r') as fban:
        banner_configs = json.load(fban)
    
    print(f'Loaded {len(banner_configs)} banners')

    asyncio.run(main(args.start, args.end, args.exclude, args.ip))
