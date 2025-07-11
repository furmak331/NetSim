"""
Switch implementation for Network Simulator
Equivalent to Switch.java in the Java implementation
"""

class Switch:
    def __init__(self, num):
        """
        Initialize switch with a number
        
        Args:
            num (int): Switch identification number
        """
        self.switch_number = num
        self.hubs = []
        self.devices_directly_connected = None
        self.connected_direct = []
        self.connected_via_hub = {}  # Maps MAC address to Hub for faster lookup
        self.mac_table = {}  # Maps MAC address to a port (for MAC learning demonstration)
        self.data = None
        print(f"[SWITCH {num}] ▶ Switch initialized")
    
    def get_data(self, data):
        """
        Get data for this switch
        
        Args:
            data (str): Data to store
        """
        self.data = data
        print(f"[SWITCH {self.switch_number}] ▶ Received data for forwarding")
    
    def store_directly_connected_devices(self, devices):
        """
        Store directly connected devices
        
        Args:
            devices (list): List of directly connected devices
        """
        self.devices_directly_connected = devices
        print(f"[SWITCH {self.switch_number}] ▶ Added {len(devices)} directly connected devices")
    
    def store_connected_hubs(self, hubs):
        """
        Store connected hubs
        
        Args:
            hubs (list): List of connected hubs
        """
        self.hubs = hubs
        hub_numbers = [hub.get_hub_number() for hub in hubs]
        print(f"[SWITCH {self.switch_number}] ▶ Connected to Hubs: {hub_numbers}")
    
    def add_to_direct_connection_table(self, device):
        """
        Add device to direct connection table
        
        Args:
            device (EndDevices): Device to add
        """
        self.connected_direct.append(device)
        print(f"[SWITCH {self.switch_number}] ▶ Added device {device.get_device_name()} (MAC: {device.get_mac()}) to direct connections")
    
    def add_to_hub_connected_table(self, hub, device):
        """
        Add device to hub connection table
        
        Args:
            hub (Hub): Hub the device is connected to
            device (EndDevices): Device to add
        """
        # Use MAC address as the key for faster lookups
        self.connected_via_hub[device.get_mac()] = hub
        print(f"[SWITCH {self.switch_number}] ⓘ MAC Table Update: {device.get_mac()} → Hub {hub.get_hub_number()}")
    
    def display_mac_table(self):
        """Display the current MAC address table"""
        print(f"\n[SWITCH {self.switch_number}] === MAC ADDRESS TABLE ===")
        
        # Consolidate all entries into a single table
        has_entries = False
        entries = []
        
        # Add entries from MAC table
        if self.mac_table:
            has_entries = True
            for mac, port in self.mac_table.items():
                entries.append((mac, port, "Dynamic"))
        
        # Add entries from devices connected via hubs
        if self.connected_via_hub:
            has_entries = True
            for mac, hub in self.connected_via_hub.items():
                # Calculate the port number for this hub
                if self.hubs:
                    try:
                        hub_index = self.hubs.index(hub)
                        port_num = len(self.connected_direct) + hub_index + 1
                        entries.append((mac, f"PORT {port_num} (Hub {hub.get_hub_number()})", "Dynamic"))
                    except ValueError:
                        entries.append((mac, f"Hub {hub.get_hub_number()}", "Dynamic"))
        
        # Add entries from directly connected devices that aren't yet in the MAC table
        if self.connected_direct:
            has_entries = True
            for device in self.connected_direct:
                mac = device.get_mac()
                # Only add if not already in the MAC table
                if not self.mac_table or mac not in self.mac_table:
                    port_num = self.connected_direct.index(device) + 1
                    entries.append((mac, f"PORT {port_num}", "Static"))
        
        # Display the consolidated table
        if has_entries:
            print(f"[SWITCH {self.switch_number}] {'MAC Address':<15} | {'Port':<20} | {'Type'}")
            print(f"[SWITCH {self.switch_number}] {'-'*15} | {'-'*20} | {'-'*10}")
            
            # Sort entries for better display
            entries.sort(key=lambda x: x[0])  # Sort by MAC address
            
            for mac, port, entry_type in entries:
                print(f"[SWITCH {self.switch_number}] {mac:<15} | {port:<20} | {entry_type}")
        else:
            print(f"[SWITCH {self.switch_number}] MAC address table is empty.")
    
    def send_direct_data(self, sender_device, receiver_device):
        """
        Send data directly between devices with CSMA/CD protocol
        
        Args:
            sender_device (EndDevices): Sender device
            receiver_device (EndDevices): Receiver device
        """
        import random
        import time
        
        data = sender_device.get_data()
        print(f"\n[SWITCH {self.switch_number}] === DIRECT SWITCHING ===")
        print(f"[SWITCH {self.switch_number}] ▶ Source: {sender_device.get_device_name()} (MAC: {sender_device.get_mac()})")
        print(f"[SWITCH {self.switch_number}] ▶ Destination: {receiver_device.get_device_name()} (MAC: {receiver_device.get_mac()})")
        
        # Initialize CSMA/CD variables
        channel_busy = False
        max_attempts = 5
        attempt = 0
        
        # Check if switch ports are busy (randomly)
        # This simulates CSMA/CD medium sensing
        print(f"[SWITCH {self.switch_number}] === PHYSICAL LAYER: CSMA/CD PROTOCOL ===")
        
        # Randomly determine if channel is busy (30% chance)
        channel_busy = random.random() < 0.3
        
        while attempt < max_attempts:
            print(f"[SWITCH {self.switch_number}] ▶ [CSMA/CD] Attempt {attempt+1}: Checking if channel is busy...")
            
            if channel_busy:
                print(f"[SWITCH {self.switch_number}] ▶ [CSMA/CD] Channel busy. Waiting...")
                time.sleep(0.5)  # Wait before retrying
                # After waiting, check again with 50% chance of still being busy
                channel_busy = random.random() < 0.5
                attempt += 1
                continue
                
            # Channel is free, start transmission
            print(f"[SWITCH {self.switch_number}] ▶ [CSMA/CD] Channel is free. {sender_device.get_device_name()} starts transmitting...")
            
            # Simulate possible collision (random chance)
            collision_happened = random.random() < 0.2  # 20% chance of collision
            
            if collision_happened:
                print(f"[SWITCH {self.switch_number}] ⚠ [CSMA/CD] COLLISION DETECTED during transmission!")
                print(f"[SWITCH {self.switch_number}] ▶ [CSMA/CD] Sending jamming signal...")
                
                # Calculate backoff time using exponential backoff algorithm
                backoff = random.randint(1, 2 ** min(attempt, 10))  # Limit exponent to avoid overflow
                print(f"[SWITCH {self.switch_number}] ▶ [CSMA/CD] Backing off for {backoff} time units...")
                
                time.sleep(0.2 * backoff)  # Wait according to backoff algorithm
                attempt += 1
                continue
                
            # No collision, proceed with switching
            print(f"[SWITCH {self.switch_number}] ✓ [CSMA/CD] Transmission successful at physical layer")
            print(f"[SWITCH {self.switch_number}] === DATA LINK LAYER: MAC LEARNING & FORWARDING ===")
            
            # Check if we know this MAC address yet (MAC Table lookup)
            known_receiver = False
            if hasattr(self, 'mac_table') and receiver_device.get_mac() in self.mac_table:
                known_receiver = True
                print(f"[SWITCH {self.switch_number}] ✓ MAC address found in table: {receiver_device.get_mac()} → {self.mac_table[receiver_device.get_mac()]}")
            elif receiver_device in self.connected_direct:
                known_receiver = True
                port_num = self.connected_direct.index(receiver_device) + 1
                print(f"[SWITCH {self.switch_number}] ✓ Device connected directly: {receiver_device.get_device_name()} on Port {port_num}")
                
                # Add to MAC table for future reference
                if hasattr(self, 'mac_table'):
                    self.mac_table[receiver_device.get_mac()] = f"PORT {port_num}"
                    print(f"[SWITCH {self.switch_number}] ⓘ MAC Table Updated: {receiver_device.get_mac()} → PORT {port_num}")
                    
            # Learn the sender's MAC if needed
            if hasattr(self, 'mac_table') and sender_device.get_mac() not in self.mac_table:
                if sender_device in self.connected_direct:
                    port_num = self.connected_direct.index(sender_device) + 1
                    self.mac_table[sender_device.get_mac()] = f"PORT {port_num}"
                    print(f"[SWITCH {self.switch_number}] ⓘ MAC Table Updated: {sender_device.get_mac()} → PORT {port_num}")
            
            # Unlike a hub, a switch only forwards to the specific destination
            if known_receiver:
                print(f"[SWITCH {self.switch_number}] ▶ Forwarding frame directly to destination")
            else:
                print(f"[SWITCH {self.switch_number}] ⚠ Unknown destination MAC, flooding frame to all ports")
                
            # Send the data to the receiver
            print(f"[SWITCH {self.switch_number}] === NETWORK LAYER: PASSING DATA UPWARD ===")
            receiver_device.set_receiver_data(data)
            print(f"[SWITCH {self.switch_number}] ✓ Frame forwarded to destination")
            return
            
        # If we reach here, max attempts were exceeded
        print(f"[SWITCH {self.switch_number}] ❌ [CSMA/CD] Transmission failed after {max_attempts} attempts")
    
    def send_data_via_hub(self, sender_hub, receiver_hub, sender, receiver):
        """
        Send data between hubs via switch
        
        Args:
            sender_hub (Hub): Sender's hub
            receiver_hub (Hub): Receiver's hub
            sender (EndDevices): Sender device
            receiver (EndDevices): Receiver device
        """
        print(f"\n[SWITCH {self.switch_number}] === INTER-HUB SWITCHING ===")
        print(f"[SWITCH {self.switch_number}] ▶ Source: Hub {sender_hub.get_hub_number()}")
        print(f"[SWITCH {self.switch_number}] ▶ Source device: {sender.get_device_name()} (MAC: {sender.get_mac()})")
        print(f"[SWITCH {self.switch_number}] ▶ Destination device: {receiver.get_device_name()} (MAC: {receiver.get_mac()})")
        
        # Learn sender's MAC address and hub (building MAC address table)
        self.add_to_hub_connected_table(sender_hub, sender)
        
        # Check if the switch knows which hub the receiver is connected to
        receiver_hub_from_table = self.connected_via_hub.get(receiver.get_mac())
        
        if receiver_hub_from_table is not None:
            print(f"[SWITCH {self.switch_number}] ✓ MAC table lookup successful: {receiver.get_mac()} → Hub {receiver_hub_from_table.get_hub_number()}")
            
            # Verify if our knowledge is correct
            if receiver_hub_from_table.get_hub_number() != receiver_hub.get_hub_number():
                print(f"[SWITCH {self.switch_number}] ⚠ MAC table outdated! Updating: {receiver.get_mac()} is now at Hub {receiver_hub.get_hub_number()}")
                self.add_to_hub_connected_table(receiver_hub, receiver)
        else:
            print(f"[SWITCH {self.switch_number}] ⓘ MAC {receiver.get_mac()} not in table, learning it's at Hub {receiver_hub.get_hub_number()}")
            self.add_to_hub_connected_table(receiver_hub, receiver)
            
        # Display the current MAC table
        self.display_mac_table()
        
        # Forward data to the receiver's hub
        print(f"[SWITCH {self.switch_number}] ▶ Forwarding frame from Hub {sender_hub.get_hub_number()} to Hub {receiver_hub.get_hub_number()}")
        receiver_hub.receive_data_from_sender(sender_hub.data)
        print(f"[SWITCH {self.switch_number}] ✓ Frame forwarded to Hub {receiver_hub.get_hub_number()}")
        
        # The receiver hub will broadcast to its connected devices
        # When a hub receives data, it broadcasts to all connected devices
        receiver_hub.send_data_to_receiver(receiver)
        print(f"[SWITCH {self.switch_number}] ✓ Transfer complete")
    
    def send_ACK_or_NAK(self):
        """Send ACK or NAK (placeholder)"""
        pass
    
    def broadcast_arp(self, sender_device, target_ip):
        """
        ARP logic should not be in Switch. This method is deprecated and will be removed.
        """
        print(f"[SWITCH {self.switch_number}] ARP logic is now handled by the Router (Layer 3 device). No action taken.")
        return None
    
    def find_device_by_ip(self, ip_address):
        """
        Find a device connected to this switch by IP address
        Useful for ARP lookups
        
        Args:
            ip_address (str): IP address to find
            
        Returns:
            EndDevices or None: Device with the IP if found, None otherwise
        """
        print(f"[SWITCH {self.switch_number}] ▶ Looking for device with IP {ip_address}")
        
        # Check directly connected devices
        for device in self.connected_direct:
            if device.IP == ip_address:
                print(f"[SWITCH {self.switch_number}] ✓ Found device with IP {ip_address}: MAC {device.get_mac()}")
                return device
        
        # Check devices connected via hubs
        for hub in self.hubs:
            for device in hub.get_connected_devices():
                if device.IP == ip_address:
                    print(f"[SWITCH {self.switch_number}] ✓ Found device with IP {ip_address} via Hub {hub.get_hub_number()}: MAC {device.get_mac()}")
                    return device
        
        print(f"[SWITCH {self.switch_number}] ⚠ No device with IP {ip_address} found")
        return None
