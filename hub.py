"""
Hub implementation for Network Simulator
Equivalent to Hub.java in the Java implementation
"""

class Hub:
    def __init__(self, hub_number):
        """
        Initialize hub with a hub number
        
        Args:
            hub_number (int): Hub identification number
        """
        self.sender_address = None
        self.receiver_address = None
        self.hub_number = hub_number
        self.data = None
        self.devices_connected = None
        self.channel_busy = False
        self.collision_detected = False
        self.transmission_in_progress = False
        self.active_senders = set()  # Track devices currently sending data
        self.backoff_times = {}      # Store backoff times for devices after collisions
    
    def receive_data_from_sender(self, d):
        """
        Receive data from a sender
        
        Args:
            d (str): Data received from a sender device
        """
        self.data = d
        print(f"\n[HUB {self.hub_number}] ▶ PHYSICAL LAYER: Received data from source")
        # Display truncated data to keep logs clean
        display_data = d[:20] + "..." if len(d) > 20 else d
        print(f"[HUB {self.hub_number}] ▶ Data content: '{display_data}'")
    
    def send_data_to_receiver(self, receiver_device):
        """
        Send data to a receiver device
        
        Args:
            receiver_device (EndDevices): The receiver device
        """
        self.receiver_address = receiver_device.get_mac()
        
        # In physical layer, we don't do CRC validation - that happens at the data link layer
        print(f"[HUB {self.hub_number}] ▶ PHYSICAL LAYER: Forwarding data to {receiver_device.get_device_name()}")
        print(f"[HUB {self.hub_number}] ▶ Destination MAC: {receiver_device.get_mac()}")
        
        # Pass the data to the receiver - receiver will handle CRC at data link layer
        receiver_device.set_receiver_data(self.data)
        print(f"[HUB {self.hub_number}] ✓ Data transmitted to {receiver_device.get_device_name()}")
    
    def get_hub_number(self):
        """Get hub number"""
        return self.hub_number
    
    def get_receiver_address(self):
        """Get receiver address"""
        return self.receiver_address
    
    def get_sender_address(self):
        """Get sender address"""
        return self.sender_address
    
    def store_devices_connected(self, dev):
        """
        Store connected devices
        
        Args:
            dev (list): List of connected devices
        """
        self.devices_connected = dev
        print(f"[HUB {self.hub_number}] Connected {len(dev)} device(s) to hub")
    
    def get_connected_devices(self):
        """Get connected devices"""
        return self.devices_connected
    
    def send_data_to_switch(self, switch_new, sender_hub, receiver_hub, sender, receiver):
        """
        Send data through a switch if needed
        
        Args:
            switch_new (Switch): Switch to use
            sender_hub (Hub): Sender's hub
            receiver_hub (Hub): Receiver's hub
            sender (EndDevices): Sender device
            receiver (EndDevices): Receiver device
        """
        print(f"\n[HUB {sender_hub.get_hub_number()}] === HUB BROADCASTING OPERATION ===")
        print(f"[HUB {sender_hub.get_hub_number()}] ▶ Source: {sender.get_device_name()} (MAC: {sender.get_mac()})")
        print(f"[HUB {sender_hub.get_hub_number()}] ▶ Target: {receiver.get_device_name()} (MAC: {receiver.get_mac()})")
        
        # Try to send data using CSMA/CD protocol
        if not self.send_with_csma_cd(sender_hub, sender, receiver):
            print(f"[HUB {sender_hub.get_hub_number()}] ❌ Data transmission failed after multiple attempts")
            return
            
        # If we're here, transmission succeeded
        # If receiver is in a different hub, forward to switch
        if sender_hub.get_hub_number() != receiver_hub.get_hub_number():
            print(f"\n[HUB {sender_hub.get_hub_number()}] ⚠ Intended receiver not found in this hub")
            print(f"[HUB {sender_hub.get_hub_number()}] → Forwarding data to switch {switch_new.switch_number}")
            switch_new.send_data_via_hub(sender_hub, receiver_hub, sender, receiver)
            print(f"[HUB {sender_hub.get_hub_number()}] ✓ Data forwarded to switch for further routing")
    
    def send_ACK_or_NAK(self, receiver_device):
        """
        Send ACK or NAK to a receiver device
        
        Args:
            receiver_device (EndDevices): The receiver device
        """
        print(f"[HUB {self.hub_number}] ▶ PHYSICAL LAYER: Sending ACK to {receiver_device.get_device_name()}")
        receiver_device.receive_ACK_or_NAK("ACK")
    
    def receive_ACK_or_NAK(self, ack_or_nak):
        """
        Receive ACK or NAK
        
        Args:
            ack_or_nak (str): ACK or NAK string
        """
        print(f"[HUB {self.hub_number}] ▶ PHYSICAL LAYER: Received {ack_or_nak}")
    
    def check_channel_status(self):
        """
        Check if the channel is busy
        
        Returns:
            bool: True if channel is busy, False otherwise
        """
        return self.channel_busy
    
    def detect_collision(self):
        """
        Detect if there's a collision in the channel
        
        Returns:
            bool: True if collision is detected, False otherwise
        """
        return self.collision_detected
    
    def set_collision(self, status):
        """
        Set collision status
        
        Args:
            status (bool): Collision status
        """
        self.collision_detected = status
        if status:
            print(f"[HUB {self.hub_number}] ⚠ COLLISION DETECTED: Multiple devices transmitting simultaneously")
    
    def set_channel_busy(self, status):
        """
        Set channel busy status
        
        Args:
            status (bool): Channel busy status
        """
        self.channel_busy = status
        if status:
            print(f"[HUB {self.hub_number}] ▶ Channel is now busy")
        else:
            print(f"[HUB {self.hub_number}] ▶ Channel is now free")
    
    def broadcast_physical_layer(self, sender_device):
        """
        Broadcast data to all connected devices at the physical layer (no data link layer logic).
        
        Args:
            sender_device (EndDevices): The device that sent the data (will not receive its own data)
        """
        if not self.devices_connected:
            print(f"[HUB {self.hub_number}] ⚠ No devices connected to hub for broadcast.")
            return
        print(f"[HUB {self.hub_number}] === PHYSICAL LAYER BROADCAST ===")
        for device in self.devices_connected:
            if device == sender_device:
                continue
            print(f"[HUB {self.hub_number}] ▶ Broadcasting to {device.get_device_name()} (MAC: {device.get_mac()})")
            # Set raw_data at physical layer only (no data link layer processing)
            device.raw_data = self.data  
            print(f"[DEVICE {device.get_device_name()}] ▶ PHYSICAL LAYER: Received bits '{self.data[:20]}{'...' if len(self.data) > 20 else ''}' from hub {self.hub_number}")
            # Note that in a physical broadcast, all devices receive the signal, but only the intended recipient processes it further
            # Other devices would discard it at the data link layer (MAC filtering)
        print(f"[HUB {self.hub_number}] ✓ Broadcast complete at physical layer.")

    def send_with_csma_cd_physical(self, sender_device, data, max_attempts=5):
        """
        Simulate CSMA/CD protocol at the physical layer for demonstration.
        
        Args:
            sender_device (EndDevices): The device attempting to send
            data (str): Data to send
            max_attempts (int): Maximum number of retransmission attempts
        
        Returns:
            bool: True if transmission succeeded, False if failed after retries
        """
        import random
        import time
        attempt = 0
        while attempt < max_attempts:
            print(f"[HUB {self.hub_number}] ▶ [CSMA/CD] Attempt {attempt+1}: Checking if channel is busy...")
            if self.channel_busy:
                print(f"[HUB {self.hub_number}] ▶ [CSMA/CD] Channel busy. Waiting...")
                time.sleep(0.5)
                continue
            # Channel is free, start transmission
            self.set_channel_busy(True)
            print(f"[HUB {self.hub_number}] ▶ [CSMA/CD] Channel is free. {sender_device.get_device_name()} starts transmitting...")
            # Simulate possible collision (random chance)
            collision_happened = random.random() < 0.3  # 30% chance
            if collision_happened:
                self.set_collision(True)
                print(f"[HUB {self.hub_number}] ▶ [CSMA/CD] Collision detected! Sending jamming signal...")
                self.set_channel_busy(False)
                backoff = random.randint(1, 2 ** (attempt + 1))
                print(f"[HUB {self.hub_number}] ▶ [CSMA/CD] Backing off for {backoff} time units...")
                time.sleep(0.2 * backoff)
                self.set_collision(False)
                attempt += 1
                continue
            # No collision, broadcast
            self.data = data
            self.broadcast_physical_layer(sender_device)
            self.set_channel_busy(False)
            print(f"[HUB {self.hub_number}] ▶ [CSMA/CD] Transmission successful at physical layer.")
            return True
        print(f"[HUB {self.hub_number}] ❌ [CSMA/CD] Transmission failed after {max_attempts} attempts.")
        return False
    
    def send_with_csma_cd(self, sender_hub, sender_device, receiver_device):
        """
        Send data using CSMA/CD protocol
        
        Args:
            sender_hub (Hub): The hub that the sender is connected to
            sender_device (EndDevices): The device that is sending data
            receiver_device (EndDevices): The device that will receive data
        
        Returns:
            bool: True if transmission succeeded, False if failed after retries
        """
        print(f"[HUB {sender_hub.get_hub_number()}] ▶ CSMA/CD: Beginning transmission process")
        
        # Use sender's data
        data = sender_device.data
        
        # Call the physical layer implementation of CSMA/CD
        return self.send_with_csma_cd_physical(sender_device, data)
