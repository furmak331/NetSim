"""
Main Network Simulator implementation in Python
Equivalent to functionality in Main.java and SampleMain.java
"""

import random
import time
from end_devices import EndDevices
from hub import Hub
from switch import Switch
from router import Router
from domain_name_server import DomainNameServer
from search_engine_server import SearchEngineServer
from email_service import SenderEmail, ReceiverEmail
from search_service import SenderSearch, ReceiverSearch
from checksum_for_datalink import ChecksumForDataLink
from direct_connection import DirectConnection
from cli_utils import CLIUtils

class NetworkSimulator:
    def __init__(self):
        """Initialize the network simulator with all necessary components"""
        self.hubs = []
        self.switches = []
        self.routers = []
        self.devices = []
        self.direct_connections = []  # Store direct connections between devices
        self.sender_device = None
        self.receiver_device = None
        self.sender_hub = None
        self.receiver_hub = None
        self.sender_switch = None
        self.receiver_switch = None
        self.sender_router = None
        self.receiver_router = None
        self.data_to_be_sent = ""
        self.check_error = False
        self.ACK_or_NAK = ""
        self.sender_IP = ""
        self.receiver_IP = ""
        self.device_counter = 0  # Counter for device IDs
        
        # Go-Back-N protocol parameters
        self.window_size = 4
        self.timeout = 2.0  # seconds
        self.max_retries = 3
    
    def create_network_topology(self):
        """Create network topology with routers, switches, hubs and end devices"""
        print("Setting up network topology...")
        
        # Get user input for number of routers
        while True:
            try:
                num_routers = int(input("Enter the number of routers you want in your network (0 or more): "))
                if num_routers < 0:
                    print("Please enter a non-negative number.")
                else:
                    break
            except ValueError:
                print("Please enter a valid number.")
        
        # If no routers, offer to create a simple network
        if num_routers == 0:
            print("\nZero routers selected. Creating a network without routers.")
            print("You can choose from these topology options:")
            print("1. Create direct connections between devices")
            print("2. Create a star topology with hub (multiple devices connected to a single hub)")
            print("3. Create a custom network with switches and hubs (no routers)")
            print("4. Return to main menu")
            
            choice = input("Enter your choice (1-4): ")
            if choice == '1':
                return self.create_direct_connection()
            elif choice == '2':
                return self.create_star_topology()
            elif choice == '3':
                # Create a custom network with switches and hubs but no routers
                print("\n--- CREATE CUSTOM NETWORK (NO ROUTERS) ---")
                # Ask for number of switches
                while True:
                    try:
                        num_switches = int(input("Enter the number of switches you want in your network: "))
                        if num_switches < 0:
                            print("Please enter a non-negative number.")
                        else:
                            break
                    except ValueError:
                        print("Please enter a valid number.")
                
                # Create switches
                switches = []
                for s in range(num_switches):
                    switch = Switch(s)
                    switches.append(switch)
                    self.switches.append(switch)
                    
                    # Create hubs for each switch
                    while True:
                        try:
                            num_hubs = int(input(f"Enter the number of hubs in SWITCH {s} (0 or more): "))
                            if num_hubs < 0:
                                print("Please enter a non-negative number.")
                            else:
                                break
                        except ValueError:
                            print("Please enter a valid number.")
                    
                    switch_hubs = []
                    
                    for h in range(num_hubs):
                        hub = Hub(h)
                        switch_hubs.append(hub)
                        self.hubs.append(hub)
                        
                        # Create end devices for each hub
                        while True:
                            try:
                                num_devices = int(input(f"Enter the number of devices in HUB {h} of SWITCH {s} (0 or more): "))
                                if num_devices < 0:
                                    print("Please enter a non-negative number.")
                                else:
                                    break
                            except ValueError:
                                print("Please enter a valid number.")
                        
                        hub_devices = []
                        
                        for d in range(num_devices):
                            device_name = chr(65 + len(self.devices))  # Generate name as letter (A, B, C...)
                            mac_address = len(self.devices) + 1
                            ip_address = f"192.168.{s+1}.{d+1}"
                            
                            device = EndDevices(mac_address, device_name, ip_address)
                            hub_devices.append(device)
                            self.devices.append(device)
                            print(f"Created device {device_name} with IP {ip_address} and MAC {mac_address}")
                        
                        # Connect devices to hub
                        hub.store_devices_connected(hub_devices)
                    
                    # Connect hubs to switch
                    switch.store_connected_hubs(switch_hubs)
                
                print("Custom network created successfully.")
                self.print_network_topology()
                return
            else:
                print("Returning to main menu.")
                return
        
        # Create routers
        for r in range(num_routers):
            router = Router(r, f"{(r+1)*10}.0.0.0")
            self.routers.append(router)
            
            # Create switches for each router
            while True:
                try:
                    num_switches = int(input(f"Enter the number of switches in ROUTER {r} (0 or more): "))
                    if num_switches < 0:
                        print("Please enter a non-negative number.")
                    else:
                        break
                except ValueError:
                    print("Please enter a valid number.")
            
            router_switches = []
            
            # If no switches are created, create default devices connected directly to router
            if num_switches == 0:
                # Create devices connected directly to router
                while True:
                    try:
                        num_direct_devices = int(input(f"Enter the number of devices directly connected to ROUTER {r} (0 or more): "))
                        if num_direct_devices < 0:
                            print("Please enter a non-negative number.")
                        else:
                            break
                    except ValueError:
                        print("Please enter a valid number.")
                
                for d in range(num_direct_devices):
                    device_name = chr(65 + len(self.devices))  # Generate name as letter (A, B, C...)
                    mac_address = len(self.devices) + 1
                    ip_address = f"{(r+1)*10}.0.0.{d+1}"
                    
                    device = EndDevices(mac_address, device_name, ip_address)
                    self.devices.append(device)
                    print(f"Created device {device_name} with IP {ip_address} and MAC {mac_address}")
                
                # Create a virtual hub for these devices just for simulation purposes
                if num_direct_devices > 0:
                    direct_hub = Hub(-1)  # Special ID for direct hub
                    direct_hub.store_devices_connected(self.devices)
                    self.hubs.append(direct_hub)
                
                continue  # Skip to next router
            
            for s in range(num_switches):
                switch = Switch(s)
                router_switches.append(switch)
                self.switches.append(switch)
                
                # Create hubs for each switch
                while True:
                    try:
                        num_hubs = int(input(f"Enter the number of hubs in SWITCH {s} of ROUTER {r} (0 or more): "))
                        if num_hubs < 0:
                            print("Please enter a non-negative number.")
                        else:
                            break
                    except ValueError:
                        print("Please enter a valid number.")
                
                switch_hubs = []
                
                for h in range(num_hubs):
                    hub = Hub(h)
                    switch_hubs.append(hub)
                    self.hubs.append(hub)
                    
                    # Create end devices for each hub
                    while True:
                        try:
                            num_devices = int(input(f"Enter the number of devices in HUB {h} of SWITCH {s} of ROUTER {r} (0 or more): "))
                            if num_devices < 0:
                                print("Please enter a non-negative number.")
                            else:
                                break
                        except ValueError:
                            print("Please enter a valid number.")
                    
                    hub_devices = []
                    
                    for d in range(num_devices):
                        device_name = chr(65 + len(self.devices))  # Generate name as letter (A, B, C...)
                        mac_address = len(self.devices) + 1
                        ip_address = f"{(r+1)*10}.{s+1}.{h+1}.{d+1}"
                        
                        device = EndDevices(mac_address, device_name, ip_address)
                        hub_devices.append(device)
                        self.devices.append(device)
                        print(f"Created device {device_name} with IP {ip_address} and MAC {mac_address}")
                    
                    # Connect devices to hub
                    hub.store_devices_connected(hub_devices)
                
                # Connect hubs to switch
                switch.store_connected_hubs(switch_hubs)
            
            # Connect switches to router
            router.store_connected_switches(router_switches)
        
        print("Network topology created successfully.")
        self.print_network_topology()
    
    def print_network_topology(self):
        """Print the current network topology"""
        print("\n--- NETWORK TOPOLOGY ---")
        print(f"Number of Routers: {len(self.routers)}")
        print(f"Number of Switches: {len(self.switches)}")
        print(f"Number of Hubs: {len(self.hubs)}")
        print(f"Number of End Devices: {len(self.devices)}")
        print(f"Number of Direct Connections: {len(self.direct_connections)}")
        
        print("\nDevices:")
        for device in self.devices:
            print(f"Device {device.get_device_name()}: MAC={device.get_mac()}, IP={device.IP}")
            
        if self.direct_connections:
            print("\nDirect Connections:")
            for i, conn in enumerate(self.direct_connections):
                devices = conn.get_connected_devices()
                print(f"Connection {i+1}: {devices[0].get_device_name()} <--> {devices[1].get_device_name()}")
        
        print("\nHubs and Connected Devices:")
        for hub in self.hubs:
            if hub.hub_number == -1:
                continue  # Skip virtual hubs for direct connections
                
            devices = hub.get_connected_devices()
            if devices:
                print(f"Hub {hub.get_hub_number()}: Connected to {len(devices)} devices")
                for device in devices:
                    print(f"  - Device {device.get_device_name()}: MAC={device.get_mac()}, IP={device.IP}")
    
    def select_sender_and_receiver(self):
        """Select sender and receiver devices"""
        print("\n--- SELECT SENDER AND RECEIVER ---")
        
        if not self.devices:
            print("No devices available. Please create some devices first.")
            return False
        
        # Show available devices
        print("Available devices:")
        for i, device in enumerate(self.devices):
            print(f"{i+1}. Device {device.get_device_name()}: IP={device.IP}")
        
        while True:
            try:
                sender_idx = int(input("Select sender device (number): ")) - 1
                if sender_idx < 0 or sender_idx >= len(self.devices):
                    print("Invalid selection. Please try again.")
                    continue
                
                receiver_idx = int(input("Select receiver device (number): ")) - 1
                if receiver_idx < 0 or receiver_idx >= len(self.devices) or receiver_idx == sender_idx:
                    print("Invalid selection. Please try again.")
                    continue
                
                break
            except ValueError:
                print("Please enter a valid number.")
        
        self.sender_device = self.devices[sender_idx]
        self.sender_IP = self.sender_device.IP
        self.receiver_device = self.devices[receiver_idx]
        self.receiver_IP = self.receiver_device.IP
        
        print(f"Selected sender: Device {self.sender_device.get_device_name()} (IP: {self.sender_IP})")
        print(f"Selected receiver: Device {self.receiver_device.get_device_name()} (IP: {self.receiver_IP})")
        
        # Find the hubs for these devices
        for hub in self.hubs:
            devices = hub.get_connected_devices()
            if devices and self.sender_device in devices:
                self.sender_hub = hub
            if devices and self.receiver_device in devices:
                self.receiver_hub = hub
        
        if self.sender_hub:
            print(f"Sender is connected to Hub {self.sender_hub.get_hub_number()}")
        if self.receiver_hub:
            print(f"Receiver is connected to Hub {self.receiver_hub.get_hub_number()}")
        
        return True
    
    def data_transfer_test(self):
        """Test data transfer between devices"""
        print("\n--- DATA TRANSFER TEST ---")
        
        if self.sender_device is None or self.receiver_device is None:
            success = self.select_sender_and_receiver()
            if not success:
                return
        
        # Get data from user
        self.data_to_be_sent = input("Enter data to be sent: ")
        
        # Demo of Go-Back-N protocol with multiple frames
        print("\n--- GO-BACK-N PROTOCOL DEMONSTRATION ---")
        print(f"Window size: {self.window_size}")
        print(f"Using checksum for error detection")
        
        # Split the message into multiple frames if it's long enough
        frames = []
        frame_size = 5  # characters per frame
        
        for i in range(0, len(self.data_to_be_sent), frame_size):
            frame_data = self.data_to_be_sent[i:i+frame_size]
            frames.append(frame_data)
            
        print(f"Message split into {len(frames)} frames")
        
        # Set up our checksum handler
        checksum_handler = ChecksumForDataLink()
        
        # Simulate sending frames with Go-Back-N
        current_seq = 0
        frames_sent = 0
        buffer = {}  # Buffer for unacknowledged frames
        
        while frames_sent < len(frames):
            # Send frames within the window
            while frames_sent < len(frames) and len(buffer) < self.window_size:
                # Create frame with checksum
                frame_data = frames[frames_sent]
                frame = checksum_handler.sender_code(frame_data, current_seq)
                
                # Store in buffer
                buffer[current_seq] = frame
                
                # Send frame to receiver
                print(f"\n[SENDER] ▶ Sending frame {current_seq}: {frame_data}")
                self.sender_device.data = frame
                
                # Special case: if the hub is a virtual hub (direct connection to router)
                if self.sender_hub.hub_number == -1 or self.receiver_hub.hub_number == -1:
                    print("Direct connection devices (no switch involved)")
                    self.sender_device.send_data_to_receiver(self.receiver_device)
                # Check if sender and receiver are in the same hub
                elif self.sender_hub == self.receiver_hub:
                    print("Sender and receiver are in the same hub")
                    self.sender_device.send_data_and_address_to_hub(self.sender_hub)
                    self.sender_hub.send_data_to_receiver(self.receiver_device)
                else:
                    print("Sender and receiver are in different hubs")
                    # Find a switch connecting both hubs
                    self.sender_switch = None
                    for s in self.switches:
                        if self.sender_hub in s.hubs and self.receiver_hub in s.hubs:
                            self.sender_switch = self.receiver_switch = s
                            break
                    
                    if self.sender_switch is not None:
                        self.sender_device.send_data_and_address_to_hub(self.sender_hub)
                        self.sender_hub.send_data_to_switch(self.sender_switch, self.sender_hub, self.receiver_hub, 
                                                          self.sender_device, self.receiver_device)
                    else:
                        print("ERROR: Could not find a path between sender and receiver")
                        print("Direct connection will be used instead")
                        self.sender_device.send_data_to_receiver(self.receiver_device)
                
                # Move to next sequence number
                current_seq = (current_seq + 1) % 10
                frames_sent += 1
            
            # Wait for ACK or NAK
            print(f"\n[SENDER] ▶ Waiting for acknowledgment...")
            time.sleep(0.5)  # Simulate network delay
            
            # Check ACK/NAK from receiver
            response = self.receiver_device.ACKorNAK
            
            if response.startswith("ACK"):
                # Extract the ACK sequence number
                ack_seq = int(response[3:])
                print(f"[SENDER] ✓ Received ACK for frame {ack_seq}")
                
                # Handle cumulative acknowledgment
                to_remove = []
                for seq in buffer:
                    if (seq <= ack_seq and ack_seq - seq < 5) or (seq > ack_seq and seq - ack_seq > 5):
                        to_remove.append(seq)
                
                for seq in to_remove:
                    del buffer[seq]
                    print(f"[SENDER] ✓ Frame {seq} acknowledged")
                
                print(f"[SENDER] ▶ Current window: {list(buffer.keys())}")
                
            elif response.startswith("NAK"):
                # Extract NAK sequence number
                nak_seq = int(response[3:])
                print(f"[SENDER] ❌ Received NAK for frame {nak_seq}")
                
                # Go-Back-N: Resend all frames from NAK onwards
                print(f"[SENDER] ⚠ Retransmitting from frame {nak_seq}")
                
                # Reset frames_sent to force retransmission
                for seq in list(buffer.keys()):
                    if seq >= nak_seq:
                        frames_sent = frames_sent - (current_seq - seq)
                        current_seq = seq
                        break
        
        print("\n[SENDER] ✓ All frames transmitted and acknowledged")
        print("[SENDER] ✓ Data transfer completed successfully")
    
    def email_service_test(self):
        """Test email service between devices"""
        print("\n--- EMAIL SERVICE TEST ---")
        
        if not self.devices:
            print("No devices available. Please create some devices first.")
            return
        
        # Select sender and receiver if not already selected
        if self.sender_device is None or self.receiver_device is None:
            success = self.select_sender_and_receiver()
            if not success:
                return
        
        # Set up DNS for email
        print("Setting up DNS for email service...")
        dns_mappings = DomainNameServer.store_DNS_for_email(self.receiver_IP)
        
        # Create email sender and receiver
        sender_email = SenderEmail(f"user@{self.sender_IP}", f"user@{self.receiver_IP}")
        
        # Get the email content
        email_content = sender_email.email_to_be_sent
        
        # Apply checksum for data link layer
        print("\nApplying data link layer processing...")
        checksum = ChecksumForDataLink()
        encoded_email = checksum.sender_code(email_content)
        
        # Send the email data
        print("\nSending email data...")
        self.sender_device.set_data(encoded_email)
        
        # Determine how to send based on network topology
        if self.sender_hub == self.receiver_hub:
            print("Sender and receiver are in the same hub")
            self.sender_device.send_data_and_address_to_hub(self.sender_hub)
            self.sender_hub.send_data_to_receiver(self.receiver_device)
        elif self.sender_switch and self.receiver_switch and self.sender_switch == self.receiver_switch:
            print("Sender and receiver are connected to the same switch")
            self.sender_device.send_data_and_address_to_hub(self.sender_hub)
            self.sender_hub.send_data_to_switch(self.sender_switch, self.sender_hub, 
                                             self.receiver_hub, self.sender_device, self.receiver_device)
        else:
            print("Using direct connection")
            self.sender_device.send_data_to_receiver(self.receiver_device)
        
        # Check for errors
        is_valid, seq_num, data = checksum.verify_frame(self.receiver_device.get_data())
        
        if is_valid:
            print("\nEmail received successfully!")
            receiver_email = ReceiverEmail(f"user@{self.sender_IP}", f"user@{self.receiver_IP}", data)
        else:
            print("\nError in email transmission. Email could not be delivered.")
    
    def search_service_test(self):
        """Test search engine service"""
        print("\n--- SEARCH ENGINE SERVICE TEST ---")
        
        if not self.devices:
            print("No devices available. Please create some devices first.")
            return
        
        # Select sender and receiver if not already selected
        if self.sender_device is None or self.receiver_device is None:
            success = self.select_sender_and_receiver()
            if not success:
                return
                
        # Set up DNS for search engines
        print("Setting up DNS for search engine service...")
        dns_mappings = DomainNameServer.store_DNS_for_search_engines(self.receiver_IP)
        
        # List available search engines
        search_engines = ["www.google.com", "www.duckduckgo.com", "www.bing.com"]
        print("\nAvailable search engines:")
        for i, engine in enumerate(search_engines):
            print(f"{i+1}. {engine}")
        
        # Let user select a search engine
        selection = int(input("Select a search engine (number): ")) - 1
        search_engine = search_engines[selection]
        
        # Create search sender
        sender_search = SenderSearch(search_engine)
        search_key = sender_search.key_to_be_sent
        
        # Apply checksum for data link layer
        print("\nApplying data link layer processing...")
        checksum = ChecksumForDataLink()
        encoded_search = checksum.sender_code(search_key)
        
        # Send the search data
        print("\nSending search request...")
        self.sender_device.set_data(encoded_search)
        
        # Determine how to send based on network topology
        if self.sender_hub == self.receiver_hub:
            print("Sender and receiver are in the same hub")
            self.sender_device.send_data_and_address_to_hub(self.sender_hub)
            self.sender_hub.send_data_to_receiver(self.receiver_device)
        elif self.sender_switch and self.receiver_switch and self.sender_switch == self.receiver_switch:
            print("Sender and receiver are connected to the same switch")
            self.sender_device.send_data_and_address_to_hub(self.sender_hub)
            self.sender_hub.send_data_to_switch(self.sender_switch, self.sender_hub, 
                                             self.receiver_hub, self.sender_device, self.receiver_device)
        else:
            print("Using direct connection")
            self.sender_device.send_data_to_receiver(self.receiver_device)
            
        # Check for errors
        is_valid, seq_num, data = checksum.verify_frame(self.receiver_device.get_data())
        
        if is_valid:
            print("\nSearch request received successfully!")
            # Get search result from search engine server
            search_result = SearchEngineServer.return_key_search(data)
            
            # Create receiver search
            receiver_search = ReceiverSearch(search_engine, data, search_result)
        else:
            print("\nError in search request transmission. Search could not be completed.")
    
    def create_device(self, ip_prefix="192.168.1"):
        """
        Create a new device with a unique ID
        
        Args:
            ip_prefix (str): IP prefix for the device
            
        Returns:
            EndDevices: The created device
        """
        device_name = chr(65 + len(self.devices))  # Generate name as letter (A, B, C...)
        mac_address = len(self.devices) + 1
        ip_address = f"{ip_prefix}.{len(self.devices) + 1}"
        
        device = EndDevices(mac_address, device_name, ip_address)
        self.devices.append(device)
        print(f"Created device {device_name} with IP {ip_address} and MAC {mac_address}")
        
        return device
    
    def create_direct_connection(self):
        """Create a direct connection between two devices"""
        print("\n--- CREATE DIRECT CONNECTION ---")
        
        # Create two devices if needed
        if len(self.devices) < 2:
            print("Creating devices for direct connection...")
            device1 = self.create_device()
            device2 = self.create_device()
        else:
            # Let user select existing devices or create new ones
            print("Use existing devices or create new ones?")
            print("1. Use existing devices")
            print("2. Create new devices")
            
            choice = input("Enter your choice (1 or 2): ")
            
            if choice == '2':
                # Create new devices
                device1 = self.create_device()
                device2 = self.create_device()
            else:
                # Show available devices
                print("\nAvailable devices:")
                for i, device in enumerate(self.devices):
                    print(f"{i+1}. Device {device.get_device_name()}: IP={device.IP}")
                
                # Select first device
                idx1 = int(input("Select first device (number): ")) - 1
                device1 = self.devices[idx1]
                
                # Select second device
                print("\nSelect second device:")
                for i, device in enumerate(self.devices):
                    if i != idx1:
                        print(f"{i+1}. Device {device.get_device_name()}: IP={device.IP}")
                
                idx2 = int(input("Select second device (number): ")) - 1
                device2 = self.devices[idx2]
        
        # Create the direct connection
        connection = DirectConnection(device1, device2)
        self.direct_connections.append(connection)
        
        # Set sender and receiver for convenience
        self.sender_device = device1
        self.sender_IP = device1.IP
        self.receiver_device = device2
        self.receiver_IP = device2.IP
        
        # Create a virtual hub for simulation purposes
        virtual_hub = Hub(-1)  # -1 indicates a virtual hub
        virtual_hub.store_devices_connected([device1, device2])
        self.hubs.append(virtual_hub)
        self.sender_hub = virtual_hub
        self.receiver_hub = virtual_hub
        
        print(f"\nDirect connection created between Device {device1.get_device_name()} and Device {device2.get_device_name()}")
        return connection
    
    def create_star_topology(self):
        """Create a star topology with a hub and multiple devices"""
        print("\n--- CREATE STAR TOPOLOGY ---")
        
        # Get number of devices
        while True:
            try:
                num_devices = int(input("Enter number of devices for star topology (min 3, recommended 5): "))
                if num_devices < 3:
                    print("Star topology should have at least 3 devices. Please try again.")
                else:
                    break
            except ValueError:
                print("Please enter a valid number.")
        
        # Create a hub
        hub_number = len(self.hubs)
        hub = Hub(hub_number)
        self.hubs.append(hub)
        print(f"Created Hub {hub_number} for star topology")
        
        # Create devices and connect them to hub
        devices = []
        ip_prefix = f"192.168.{hub_number + 2}"
        
        for i in range(num_devices):
            device = self.create_device(ip_prefix)
            devices.append(device)
        
        # Connect devices to hub
        hub.store_devices_connected(devices)
        print(f"Connected {num_devices} devices to Hub {hub_number} in star topology")
        
        # Automatically set first two devices as sender and receiver for convenience
        self.sender_device = devices[0]
        self.sender_IP = devices[0].IP
        self.receiver_device = devices[1]
        self.receiver_IP = devices[1].IP
        self.sender_hub = hub
        self.receiver_hub = hub
        
        return hub, devices
    
    def test_direct_connection(self):
        """Test data transfer over a direct connection"""
        print("\n--- DIRECT CONNECTION TEST ---")
        
        # Check if we have direct connections
        if not self.direct_connections:
            print("No direct connections available. Creating one...")
            self.create_direct_connection()
        
        # Let user select a direct connection
        if len(self.direct_connections) > 1:
            print("Available direct connections:")
            for i, conn in enumerate(self.direct_connections):
                devices = conn.get_connected_devices()
                print(f"{i+1}. {devices[0].get_device_name()} <--> {devices[1].get_device_name()}")
            
            selection = int(input("Select a connection to test (number): ")) - 1
            conn = self.direct_connections[selection]
            devices = conn.get_connected_devices()
            
            # Set sender and receiver
            self.sender_device = devices[0]
            self.sender_IP = devices[0].IP
            self.receiver_device = devices[1]
            self.receiver_IP = devices[1].IP
            
            # Find the hub (virtual) for these devices
            for h in self.hubs:
                if h.hub_number == -1 and self.sender_device in h.get_connected_devices():
                    self.sender_hub = h
                    self.receiver_hub = h
                    break
        
        # Get data to send
        data = input("Enter data to send: ")
        
        # Split the data into frames for Go-Back-N
        frames = [data[i:i+10] for i in range(0, len(data), 10)]
        print(f"\n[DATA LINK] ▶ Splitting data into {len(frames)} frames")
        
        # Send each frame using Go-Back-N
        from checksum_for_datalink import ChecksumForDataLink
        from cli_utils import CLIUtils
        
        # Send the frames one by one
        for i, frame_data in enumerate(frames):
            print(f"\n[DIRECT] === SENDING FRAME {i} ===")
            print(f"[DIRECT] ▶ Frame data: '{frame_data}'")
            
            # Set the data in the sender device
            self.sender_device.set_data(frame_data)
            
            # Send the data directly
            CLIUtils.print_transmission_animation(
                f"Device {self.sender_device.get_device_name()}", 
                f"Device {self.receiver_device.get_device_name()}"
            )
            self.sender_device.send_data_to_receiver(self.receiver_device)
            
            # Process any retransmissions needed
            retransmission_count = 0
            max_retransmissions = 3
            
            while self.sender_device.ACKorNAK.startswith("NAK") and retransmission_count < max_retransmissions:
                retransmission_count += 1
                print(f"\n[DIRECT] === RETRANSMISSION ATTEMPT {retransmission_count} ===")
                
                # Get frames to retransmit
                frames_to_retransmit = self.sender_device.process_acknowledgment()
                
                if frames_to_retransmit:
                    # Retransmit frames
                    self.sender_device.retransmit_frames(frames_to_retransmit)
                    CLIUtils.print_transmission_animation(
                        f"Device {self.sender_device.get_device_name()} (RETRY)", 
                        f"Device {self.receiver_device.get_device_name()}"
                    )
                    self.sender_device.send_data_to_receiver(self.receiver_device)
            
            if retransmission_count >= max_retransmissions:
                print(f"\n[DIRECT] ❌ Max retransmissions reached, some data may be lost")
            
            # Small delay between frames
            import time
            time.sleep(0.5)
        
        self.ACK_or_NAK = self.sender_device.ACKorNAK
        
        print(f"ACK/NAK from receiver: {self.ACK_or_NAK}")
        
        if self.ACK_or_NAK.startswith("ACK"):
            print("Data transferred successfully")
        else:
            print("Error in data transfer, retransmission needed")
    
    def test_star_topology(self):
        """Test data transfer in a star topology"""
        print("\n--- STAR TOPOLOGY TEST ---")
        
        # Check if we have any hubs with multiple devices (not virtual hubs)
        star_hubs = [h for h in self.hubs if h.hub_number != -1 and h.get_connected_devices() 
                   and len(h.get_connected_devices()) >= 3]
        
        if not star_hubs:
            print("No star topologies available. Creating one...")
            self.create_star_topology()
            # The star topology creation already sets sender and receiver
        else:
            # Let user select a hub
            print("Available star topologies (hubs with multiple devices):")
            for i, hub in enumerate(star_hubs):
                devices = hub.get_connected_devices()
                print(f"{i+1}. Hub {hub.get_hub_number()} with {len(devices)} devices")
            
            selection = int(input("Select a star topology to test (number): ")) - 1
            hub = star_hubs[selection]
            devices = hub.get_connected_devices()
            
            # Let user select sender and receiver
            print("\nAvailable devices in this hub:")
            for i, device in enumerate(devices):
                print(f"{i+1}. Device {device.get_device_name()}: IP={device.IP}")
            
            sender_index = int(input("Select sender device (number): ")) - 1
            self.sender_device = devices[sender_index]
            self.sender_IP = self.sender_device.IP
            
            receiver_index = int(input("Select receiver device (number): ")) - 1
            self.receiver_device = devices[receiver_index]
            self.receiver_IP = self.receiver_device.IP
            
            self.sender_hub = hub
            self.receiver_hub = hub
        
        # Get data to send
        data = input("Enter data to send: ")
        self.data_to_be_sent = data
        
        # Split the data into frames for Go-Back-N
        frames = [data[i:i+10] for i in range(0, len(data), 10)]
        print(f"\n[DATA LINK] ▶ Splitting data into {len(frames)} frames")
        
        # Import required modules
        from checksum_for_datalink import ChecksumForDataLink
        from cli_utils import CLIUtils
        
        # Send each frame using Go-Back-N
        for i, frame_data in enumerate(frames):
            print(f"\n[HUB] === SENDING FRAME {i} ===")
            print(f"[HUB] ▶ Frame data: '{frame_data}'")
            
            # Set the data in the sender device
            self.sender_device.set_data(frame_data)
            
            # Send the data via hub
            print(f"\nTransferring frame {i} from Device {self.sender_device.get_device_name()} to Device {self.receiver_device.get_device_name()} via Hub {self.sender_hub.get_hub_number()}")
            
            # Demonstrate CSMA/CD protocol and hub broadcasting behavior
            print("\nHUB BROADCAST BEHAVIOR:")
            
            # Use CSMA/CD protocol for transmission
            print(f"\n[HUB {self.sender_hub.get_hub_number()}] === HUB BROADCASTING OPERATION ===")
            print(f"[HUB {self.sender_hub.get_hub_number()}] ▶ Source: {self.sender_device.get_device_name()} (MAC: {self.sender_device.get_mac()})")
            print(f"[HUB {self.sender_hub.get_hub_number()}] ▶ Target: {self.receiver_device.get_device_name()} (MAC: {self.receiver_device.get_mac()})")
            
            # Try to send data using CSMA/CD protocol
            if not self.sender_hub.send_with_csma_cd(self.sender_hub, self.sender_device, self.receiver_device):
                print(f"[HUB {self.sender_hub.get_hub_number()}] ❌ Data transmission failed after multiple attempts")
                continue  # Skip to next frame
            
            # If we didn't use CSMA/CD, this would be the traditional way to send data
            # self.sender_device.send_data_and_address_to_hub(self.sender_hub)
            
            # Get all devices in the hub except sender
            broadcast_devices = self.sender_hub.get_connected_devices()
            for device in broadcast_devices:
                if device == self.sender_device:
                    continue  # Skip the sender
                    
                if device == self.receiver_device:
                    print(f"Hub sends data to intended receiver {device.get_device_name()}")
                    self.sender_hub.send_data_to_receiver(device)
                else:
                    print(f"Hub sends data to {device.get_device_name()} (not intended receiver)")
                    print(f"Device {device.get_device_name()} discards the data")
            
            # Process any retransmissions needed
            retransmission_count = 0
            max_retransmissions = 3
            
            while self.sender_device.ACKorNAK.startswith("NAK") and retransmission_count < max_retransmissions:
                retransmission_count += 1
                print(f"\n[HUB] === RETRANSMISSION ATTEMPT {retransmission_count} ===")
                
                # Get frames to retransmit
                frames_to_retransmit = self.sender_device.process_acknowledgment()
                
                if frames_to_retransmit:
                    # Retransmit frames
                    retransmitted_frame = self.sender_device.retransmit_frames(frames_to_retransmit)
                    if retransmitted_frame:
                        print(f"\nRetransmitting frame via Hub {self.sender_hub.get_hub_number()}")
                        self.sender_device.send_data_and_address_to_hub(self.sender_hub)
                        
                        # Broadcast to all devices
                        for device in broadcast_devices:
                            if device == self.sender_device:
                                continue  # Skip the sender
                                
                            if device == self.receiver_device:
                                print(f"Hub resends data to intended receiver {device.get_device_name()}")
                                self.sender_hub.send_data_to_receiver(device)
                            else:
                                print(f"Hub resends data to {device.get_device_name()} (not intended receiver)")
                                print(f"Device {device.get_device_name()} discards the data")
            
            if retransmission_count >= max_retransmissions:
                print(f"\n[HUB] ❌ Max retransmissions reached for frame {i}, data may be lost")
            
            # Small delay between frames
            import time
            time.sleep(0.5)
        
        self.ACK_or_NAK = self.sender_device.ACKorNAK
        
        print(f"ACK/NAK from receiver: {self.ACK_or_NAK}")
        
        if self.ACK_or_NAK.startswith("ACK"):
            print("Data transferred successfully")
        else:
            print("Error in data transfer, retransmission needed")
    
    def run_simulator(self):
        """Run the network simulator with a menu"""
        print("\n===== NETWORK SIMULATOR =====")
        
        # Ask user if they want to create a complete network topology or start with simpler options
        print("Select how to start the simulator:")
        print("1. Create a complete network topology (routers, switches, hubs, devices)")
        print("2. Start with a simple setup (direct connections or star topology)")
        
        topology_choice = input("Enter your choice (1 or 2): ")
        
        if topology_choice == '1':
            # Create complete network topology
            self.create_network_topology()
        
        while True:
            print("\n--- MAIN MENU ---")
            print("PHYSICAL LAYER:")
            print("1. Create Direct Connection Between Two Devices")
            print("2. Create Star Topology With Hub")
            print("3. Test Direct Connection")
            print("4. Test Star Topology (Hub Broadcasting)")
            print("\nOTHER OPTIONS:")
            print("5. Test Data Transfer (via existing topology)")
            print("6. Test Email Service (Application Layer)")
            print("7. Test Search Engine (Application Layer)")
            print("8. Show Network Topology")
            print("9. Select Sender and Receiver")
            print("10. Create Complex Network Topology")  
            print("0. Exit")
            
            choice = input("Enter your choice: ")
            
            if choice == '1':
                self.create_direct_connection()
            elif choice == '2':
                self.create_star_topology()
            elif choice == '3':
                self.test_direct_connection()
            elif choice == '4':
                self.test_star_topology()
            elif choice == '5':
                self.data_transfer_test()
            elif choice == '6':
                self.email_service_test()
            elif choice == '7':
                self.search_service_test()
            elif choice == '8':
                self.print_network_topology()
            elif choice == '9':
                self.select_sender_and_receiver()
            elif choice == '10':
                self.create_network_topology()
            elif choice == '0':
                print("\nExiting Network Simulator. Goodbye!")
                break
            else:
                print("Invalid choice. Please try again.")
