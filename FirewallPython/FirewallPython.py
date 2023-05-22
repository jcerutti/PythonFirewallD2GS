import pydivert
import threading
import subprocess
import time
import psutil
import ctypes
import json

ban_duration = 300  # Ban duration in seconds
banned_ips_file = "banned_ips.json"  # File to store banned IPs
max_packets_per_second = 1000  # Maximum allowed packets per second

# Set the window title
ctypes.windll.kernel32.SetConsoleTitleW("Revenge Firewall")

# Load banned IPs from file
def load_banned_ips():
    try:
        with open(banned_ips_file, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

# Save banned IPs to file
def save_banned_ips(banned_ips):
    with open(banned_ips_file, "w") as f:
        json.dump(banned_ips, f)

# Initialize banned IPs dictionary
banned_ips = load_banned_ips()

# Initialize packet count dictionary
packet_count = {}

def block_packet(packet, w):
    payload = bytes(packet.tcp.payload)
    if packet.tcp.dst_port == 4000 and (payload.startswith(b'\xFF\x01') or payload == b'\xFF\x01\xFF\x01\xAA\xA1\xB1\x00\xAA\xA1\xB1\x00\xAA\xA1\xB1\x00\xAA\xA1\xB1\x00\xAA\xA1\xB1\x00\xAA\xA1\xB1\x00\xAA\xA1\xB1\x00\xAA\xA1\xB1\x00\xAA\xA1\xB1\x00'):
        source_ip = packet.src_addr

        # Check if the source IP is banned
        if source_ip in banned_ips:
            ban_start_time = banned_ips[source_ip]
            ban_elapsed_time = time.time() - ban_start_time
            if ban_elapsed_time < ban_duration:
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
            if packet_count[source_ip] > max_packets_per_second:
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
        if packet_count[source_ip] > 10:
            print(f"Banned IP due to excessive blocked packets: {source_ip}", flush=True)
            banned_ips[source_ip] = current_time
            save_banned_ips(banned_ips)

        # Do not send the packet to effectively block it

    else:
        # Allow the packet to pass through
        w.send(packet)

def packet_capture():
    print("Starting packet capture...")
    with pydivert.WinDivert("tcp.DstPort == 4000 and tcp.PayloadLength > 0") as w:
        for packet in w:
            block_packet(packet, w)

def process_monitor():
    while True:
        process_name = "D2GS.exe"

        # Check if the process is running
        process_running = any(
            proc.name() == process_name for proc in psutil.process_iter()
        )

        if not process_running:
            # Restart the process
            process_path = r"C:\Users\Mantenimiento\Desktop\Server\D2GS\D2GS.exe"
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

        # Wait for a few seconds before checking again
        time.sleep(5)

# Set the process priority to real-time
current_process = psutil.Process()
current_process.nice(psutil.REALTIME_PRIORITY_CLASS)

# Start packet capture and process monitor in separate threads
packet_capture_thread = threading.Thread(target=packet_capture)
process_monitor_thread = threading.Thread(target=process_monitor)

packet_capture_thread.start()
process_monitor_thread.start()

print("Scanning packets on port 4000...")
