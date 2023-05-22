# FirewallPython

This code is an example of a simple firewall implementation in Python. It utilizes the pydivert library to capture and filter network packets on a specific port. The firewall is designed to block certain packets based on their content, block IP addresses that exceed a certain packet rate or number of blocked packets, and monitor and restart a specified process if it is not running.

The necessary libraries are imported: pydivert for capturing packets, threading for running packet capture and process monitoring concurrently, subprocess for restarting processes, time for time-related operations, psutil for process-related operations, ctypes for setting the console window title, and json for handling JSON file operations.

Several constants are defined:

BAN_DURATION: The duration in seconds for which an IP address will be banned.
BANNED_IPS_FILE: The file name to store the banned IP addresses.
MAX_PACKETS_PER_SECOND: The maximum allowed packets per second for each IP address.
BLOCKED_PACKET_THRESHOLD: The number of blocked packets that trigger an IP ban.
The console window title is set using ctypes.windll.kernel32.SetConsoleTitleW().

Two dictionaries are initialized:

banned_ips: Stores the banned IP addresses as keys and the ban start time as values.
packet_count: Keeps track of the packet count for each source IP address.
Two helper functions are defined:

load_banned_ips(): Loads the banned IPs from the banned_ips.json file and returns them as a dictionary.
save_banned_ips(banned_ips): Saves the provided banned IPs dictionary to the banned_ips.json file.
The block_packet(packet, w) function is defined. It is responsible for processing each captured packet and deciding whether to block it or allow it to pass through.

The function checks if the packet is destined for port 4000 and has a payload with specific content (based on the condition packet.tcp.dst_port == 4000 and ...).
If the packet meets the criteria, the source IP address is extracted from the packet.
It checks if the source IP address is already banned. If so, it checks if the ban duration has elapsed. If not, the packet is not sent, effectively blocking it.
It then checks if the source IP has exceeded the maximum packet rate. If it has, the IP address is banned, and the packet count is reset. The ban is stored in banned_ips with the ban start time.
The blocked packet and source IP information are printed, and if the number of blocked packets exceeds the threshold, the IP address is banned.
If the packet doesn't meet the blocking criteria, it is allowed to pass through using w.send(packet).
The packet_capture() function is defined. It captures packets on port 4000 with a non-zero payload length using the pydivert.WinDivert context manager. It iterates over the captured packets and calls the block_packet() function for each packet.

The restart_process(process_name, process_path) function is defined. It attempts to restart a process with the given name and path using subprocess.Popen(). If the process fails to restart, an error message is printed.

The process_monitor() function is defined. It continuously checks if Diablo 2 Gameserver "D2GS.exe" is running using psutil.process_iter(). If the process is not running, it restarts it by calling restart_process().

The priority of the current process is set to real-time using psutil.Process().nice().

Two threads are created:

packet_capture_thread: Runs the packet_capture() function.
process_monitor_thread: Runs the process_monitor() function.
The threads are started using thread.start().

A message is printed indicating that the script is scanning packets on port 4000.
