# FirewallPython

This code is an example of a simple firewall implementation in Python. It utilizes the pydivert library to capture and filter network packets on a specific port. The firewall is designed to block certain packets based on their content, block IP addresses that exceed a certain packet rate or number of blocked packets, and monitor and restart a specified process if it is not running.

The necessary libraries are imported: pydivert for capturing packets, threading for running packet capture and process monitoring concurrently, subprocess for restarting processes, time for time-related operations, psutil for process-related operations, ctypes for setting the console window title, and json for handling JSON file operations.

to run the script under windows install python 3.11 (is the one i used for this code)
and from a CMD or powershell install the dependencies:

pip install pydivert

pip install psutil

for running it i used a CMD windows with admin rights, locate the FirewallPython.py file, and just write
FirewallPython.py and the firewall should start running without any problems
![startingfirew](https://github.com/jcerutti/PythonFirewallD2GS/assets/20859048/29a06d48-d69d-4b8a-b4ef-a5429ed92664)


Blocking Hex packets:

![pack1](https://github.com/jcerutti/PythonFirewallD2GS/assets/20859048/e60a2b1e-ab7e-46ee-9aa9-b6686d2c2968)

![pack2](https://github.com/jcerutti/PythonFirewallD2GS/assets/20859048/d4f73b0f-5678-44c4-81de-aac4c9bde0b8)

