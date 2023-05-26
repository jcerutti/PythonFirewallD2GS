import pydivert
import threading
import subprocess
import time
import psutil
import ctypes
import json

# Read the configuration from the JSON file
with open("config.json", "r") as config_file:
    config = json.load(config_file)

# Read the payloads from the JSON file
with open("payloads.json", "r") as payloads_file:
    payloads = json.load(payloads_file)

# Extract the configuration values
BAN_DURATION = config.get("BAN_DURATION", 300)
BANNED_IPS_FILE = config.get("BANNED_IPS_FILE", "banned_ips.json")
MAX_PACKETS_PER_SECOND = config.get("MAX_PACKETS_PER_SECOND", 1000)
BLOCKED_PACKET_THRESHOLD = config.get("BLOCKED_PACKET_THRESHOLD", 10)
PROCESS_PATH = config.get("PROCESS_PATH", r"C:\Users\Mantenimiento\Desktop\Server\D2GS\D2GS.exe")
BLOCKED_PORT = config.get("BLOCKED_PORT", 4000)
PROCESS_NAME = config.get("PROCESS_NAME", "D2GS.exe")

# Set the window title
ctypes.windll.kernel32.SetConsoleTitleW("Revenge Firewall")

# Initialize banned IPs dictionary
banned_ips = {}

# Initialize packet count dictionary
packet_count = {}

def load_banned_ips():
    try:
        with open(BANNED_IPS_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_banned_ips(banned_ips):
    with open(BANNED_IPS_FILE, "w") as f:
        json.dump(banned_ips, f)

def block_packet(packet, w):
    payload = bytes(packet.tcp.payload)
    if packet.tcp.dst_port == BLOCKED_PORT and (payload.startswith(tuple(bytes.fromhex(p) for p in payloads["starting_with"])) or payload == bytes.fromhex(payloads["fixed"])):
        source_ip = packet.src_addr

        # Check if the source IP is banned
        if source_ip in banned_ips:
            ban_start_time = banned_ips[source_ip]
            ban_elapsed_time = time.time() - ban_start_time
            if ban_elapsed_time < BAN_DURATION:
                # IP is still banned, don't send the packet
                return
            else:
                # Ban duration has elapsed, remove the IP from the banned list
                del banned_ips[source_ip]
                save_banned_ips(banned_ips)

        # Check if the source IP has exceeded the maximum packet rate
        current_time = time.time()
        if source_ip in packet_count:
            packet_count[source_ip] += 1
            if packet_count[source_ip] > MAX_PACKETS_PER_SECOND:
                # IP has exceeded the maximum packet rate, ban the IP
                print(f"Banned IP due to excessive packet rate: {source_ip}", flush=True)
                banned_ips[source_ip] = current_time
                save_banned_ips(banned_ips)
                del packet_count[source_ip]
                return
        else:
            packet_count[source_ip] = 1

        # Display blocked packet and source IP
        print(f"Blocked packet: {payload}\nSource IP: {source_ip}\n", flush=True)

        # Ban the source IP if it exceeds a certain threshold of blocked packets
        if packet_count[source_ip] > BLOCKED_PACKET_THRESHOLD:
            print(f"Banned IP due to excessive blocked packets: {source_ip}", flush=True)
            banned_ips[source_ip] = current_time
            save_banned_ips(banned_ips)

        # Do not send the packet to effectively block it

    else:
        # Allow the packet to pass through
        w.send(packet)

def packet_capture():
    print("Starting packet capture...")
    with pydivert.WinDivert(f"tcp.DstPort == {BLOCKED_PORT} and tcp.PayloadLength > 0") as win_divert:
        for packet in win_divert:
            block_packet(packet, win_divert)

def restart_process(process_name, process_path):
    try:
        subprocess.Popen(
            process_path,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NEW_CONSOLE,
        )
        print(f"Process '{process_name}' restarted.")
    except subprocess.CalledProcessError:
        print(f"Failed to restart process '{process_name}'.")

def process_monitor():
    while True:
        process_running = any(proc.name() == PROCESS_NAME for proc in psutil.process_iter())

        if not process_running:
            restart_process(PROCESS_NAME, PROCESS_PATH)

        time.sleep(5)

# Set the process priority to real-time
current_process = psutil.Process()
current_process.nice(psutil.REALTIME_PRIORITY_CLASS)

# Start packet capture and process monitor in separate threads
packet_capture_thread = threading.Thread(target=packet_capture)
process_monitor_thread = threading.Thread(target=process_monitor)

packet_capture_thread.start()
process_monitor_thread.start()

print(f"Scanning packets on port {BLOCKED_PORT}...")
