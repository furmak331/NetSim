"""
Main Network Simulator implementation in Python
Equivalent to functionality in Main.java and SampleMain.java
"""

import random
from end_devices import EndDevices
from hub import Hub
from switch import Switch
from router import Router
from domain_name_server import DomainNameServer
from search_engine_server import SearchEngineServer
from email_service import SenderEmail, ReceiverEmail
from search_service import SenderSearch, ReceiverSearch
from crc_for_datalink import CRCforDataLink

class NetworkSimulator:
    def __init__(self):
        """Initialize the network simulator with all necessary components"""
        self.hubs = []
        self.switches = []
        self.routers = []
        self.devices = []
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
    
    def create_network_topology(self):
        """Create network topology with routers, switches, hubs and end devices"""
        print("Setting up network topology...")
        
        # Get user input for number of routers
        num_routers = int(input("Enter the number of routers you want in your network: "))
        
        # Create routers
        for r in range(num_routers):
            router = Router(r, f"{(r+1)*10}.0.0.0")
            self.routers.append(router)
            
            # Create switches for each router
            num_switches = int(input(f"Enter the number of switches in ROUTER {r}: "))
            router_switches = []
            
            # If no switches are created, create default devices connected directly to router
            if num_switches == 0:
                # Create at least two devices connected directly to router
                num_direct_devices = 2
                if num_routers == 1:  # If there's only one router, ask for the number of devices
                    num_direct_devices = int(input(f"Enter the number of devices directly connected to ROUTER {r}: "))
                
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
                num_hubs = int(input(f"Enter the number of hubs in SWITCH {s} of ROUTER {r}: "))
                switch_hubs = []
                
                for h in range(num_hubs):
                    hub = Hub(h)
                    switch_hubs.append(hub)
                    self.hubs.append(hub)
                    
                    # Create end devices for each hub
                    num_devices = int(input(f"Enter the number of devices in HUB {h} of SWITCH {s} of ROUTER {r}: "))
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
        
        print("\nDevices:")
        for device in self.devices:
            print(f"Device {device.get_device_name()}: MAC={device.get_mac()}, IP={device.IP}")
    
    def select_sender_and_receiver(self):
        """Select sender and receiver devices"""
        print("\n--- SELECT SENDER AND RECEIVER ---")
        
        # Check if there are devices available
        if not self.devices:
            print("ERROR: No devices available in the network.")
            print("Please create some devices first by configuring the network topology.")
            return False
        
        if len(self.devices) < 2:
            print("ERROR: Need at least 2 devices to select sender and receiver.")
            print("Please create more devices in the network topology.")
            return False
        
        # Display available devices
        print("Available devices:")
        for i, device in enumerate(self.devices):
            print(f"{i+1}. Device {device.get_device_name()}: IP={device.IP}")
        
        try:
            # Get user selection for sender
            sender_index = int(input("Select sender device (number): ")) - 1
            if sender_index < 0 or sender_index >= len(self.devices):
                print(f"ERROR: Invalid device number. Please select a number between 1 and {len(self.devices)}")
                return False
                
            self.sender_device = self.devices[sender_index]
            self.sender_IP = self.sender_device.IP
            
            # Get user selection for receiver
            receiver_index = int(input("Select receiver device (number): ")) - 1
            if receiver_index < 0 or receiver_index >= len(self.devices):
                print(f"ERROR: Invalid device number. Please select a number between 1 and {len(self.devices)}")
                return False
                
            self.receiver_device = self.devices[receiver_index]
            self.receiver_IP = self.receiver_device.IP
            
            # Check if sender and receiver are different
            if sender_index == receiver_index:
                print("ERROR: Sender and receiver cannot be the same device.")
                return False
            
            # Find sender and receiver hubs
            self.sender_hub = None
            self.receiver_hub = None
            for hub in self.hubs:
                connected_devices = hub.get_connected_devices()
                if connected_devices and self.sender_device in connected_devices:
                    self.sender_hub = hub
                if connected_devices and self.receiver_device in connected_devices:
                    self.receiver_hub = hub
            
            # Check if we found hubs for both devices
            if not self.sender_hub or not self.receiver_hub:
                print("ERROR: Could not find hubs for sender and receiver devices.")
                return False
            
            print(f"Selected sender: Device {self.sender_device.get_device_name()} ({self.sender_IP})")
            print(f"Selected receiver: Device {self.receiver_device.get_device_name()} ({self.receiver_IP})")
            
            return True
            
        except ValueError:
            print("ERROR: Please enter a valid number.")
            return False
    
    def data_transfer_test(self):
        """Test data transfer between devices"""
        print("\n--- DATA TRANSFER TEST ---")
        
        if self.sender_device is None or self.receiver_device is None:
            success = self.select_sender_and_receiver()
            if not success:
                return
        
        # Get data from user
        self.data_to_be_sent = input("Enter data to be sent: ")
        
        # Apply CRC for error detection
        crc = CRCforDataLink()
        encoded_data = crc.sender_code(self.data_to_be_sent)
        self.sender_device.set_data(encoded_data)
        
        print(f"\nTransferring data from Device {self.sender_device.get_device_name()} to Device {self.receiver_device.get_device_name()}")
        
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
                return
        
        # Check for errors in received data
        self.check_error = CRCforDataLink.is_correct(self.receiver_device.get_data())
        
        # Send ACK or NAK
        self.receiver_device.send_ACK_or_NAK(self.check_error, self.sender_device)
        self.ACK_or_NAK = self.sender_device.ACKorNAK
        
        print(f"ACK/NAK from receiver: {self.ACK_or_NAK}")
        
        if self.ACK_or_NAK == "ACK":
            print("Data transferred successfully")
        else:
            print("Error in data transfer, retransmission needed")
    
    def email_service_test(self):
        """Test email service between devices"""
        print("\n--- EMAIL SERVICE TEST ---")
        
        if self.sender_device is None or self.receiver_device is None:
            success = self.select_sender_and_receiver()
            if not success:
                return
        
        # Get email addresses
        sender_email = input("Enter sender email address: ")
        receiver_email = input("Enter receiver email address: ")
        
        # Set up DNS mappings
        DomainNameServer.store_DNS_for_email(self.receiver_IP)
        
        # Create email sender and get content
        email_sender = SenderEmail(sender_email, receiver_email)
        email_content = email_sender.email_to_be_sent
        
        # Set the data to be sent
        self.data_to_be_sent = email_content
        
        # Similar data transfer as in data_transfer_test
        self.sender_device.set_data(self.data_to_be_sent)
        
        print(f"\nTransferring email from Device {self.sender_device.get_device_name()} to Device {self.receiver_device.get_device_name()}")
        
        # Transfer data between devices
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
        
        # Create email receiver and show the received email
        email_receiver = ReceiverEmail(sender_email, receiver_email, self.receiver_device.get_data())
    
    def search_service_test(self):
        """Test search engine service"""
        print("\n--- SEARCH ENGINE SERVICE TEST ---")
        
        if self.sender_device is None or self.receiver_device is None:
            success = self.select_sender_and_receiver()
            if not success:
                return
        
        # Get search engine website
        search_website = input("Enter search engine website (www.google.com, www.bing.com, www.duckduckgo.com): ")
        
        # Set up DNS mappings for search engines
        DomainNameServer.store_DNS_for_search_engines(self.receiver_IP)
        
        # Create search sender and get search key
        search_sender = SenderSearch(search_website)
        search_key = search_sender.key_to_be_sent
        
        # Set the data to be sent
        self.data_to_be_sent = search_key
        
        # Similar data transfer as in data_transfer_test
        self.sender_device.set_data(self.data_to_be_sent)
        
        print(f"\nTransferring search request from Device {self.sender_device.get_device_name()} to Device {self.receiver_device.get_device_name()}")
        
        # Transfer data between devices
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
        
        # Process search key to get meaning
        search_meaning = SearchEngineServer.return_key_search(search_key)
        
        # Create search receiver and show the search results
        search_receiver = ReceiverSearch(search_website, search_key, search_meaning)
    
    def run_simulator(self):
        """Run the network simulator with a menu"""
        print("\n===== NETWORK SIMULATOR =====")
        
        # Create network topology first
        self.create_network_topology()
        
        while True:
            print("\n--- MAIN MENU ---")
            print("1. Test Data Transfer (Physical & Data Link Layer)")
            print("2. Test Email Service (Application Layer)")
            print("3. Test Search Engine (Application Layer)")
            print("4. Show Network Topology")
            print("5. Select Sender and Receiver")
            print("6. Exit")
            
            choice = input("Enter your choice: ")
            
            if choice == '1':
                self.data_transfer_test()
            elif choice == '2':
                self.email_service_test()
            elif choice == '3':
                self.search_service_test()
            elif choice == '4':
                self.print_network_topology()
            elif choice == '5':
                self.select_sender_and_receiver()
            elif choice == '6':
                print("Exiting simulator...")
                break
            else:
                print("Invalid choice. Please try again.")
