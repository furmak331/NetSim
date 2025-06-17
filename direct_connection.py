"""
Direct connection implementation for Network Simulator
This handles connections directly between end devices
"""

class DirectConnection:
    def __init__(self, device1, device2):
        """
        Initialize a direct connection between two devices
        
        Args:
            device1 (EndDevices): First device in the connection
            device2 (EndDevices): Second device in the connection
        """
        self.device1 = device1
        self.device2 = device2
        self.connection_active = True
        self.connection_quality = 1.0  # 1.0 means perfect connection (no errors)
        
        print(f"\n[DIRECT] === DIRECT CONNECTION ESTABLISHED ===")
        print(f"[DIRECT] ▶ Device 1: {device1.get_device_name()} (MAC: {device1.get_mac()}, IP: {device1.IP})")
        print(f"[DIRECT] ▶ Device 2: {device2.get_device_name()} (MAC: {device2.get_mac()}, IP: {device2.IP})")
        print(f"[DIRECT] ✓ Connection status: Active")
    
    def get_connected_devices(self):
        """Get the devices connected by this connection"""
        return [self.device1, self.device2]
    
    def set_connection_quality(self, quality):
        """
        Set the connection quality which affects error rate
        
        Args:
            quality (float): Connection quality from 0.0 (worst) to 1.0 (best)
        """
        if quality < 0.0 or quality > 1.0:
            print(f"[DIRECT] ⚠ Invalid connection quality value: {quality}. Using default value.")
            return
            
        self.connection_quality = quality
        error_rate = (1.0 - quality) * 100
        print(f"[DIRECT] ▶ Connection quality set to: {quality:.2f}")
        print(f"[DIRECT] ▶ Estimated error rate: {error_rate:.1f}%")
    
    def send_data(self, sender, receiver, data):
        """
        Send data from sender to receiver
        
        Args:
            sender (EndDevices): Sender device
            receiver (EndDevices): Receiver device
            data (str): Data to send
        
        Returns:
            bool: True if transmission was successful, False otherwise
        """
        if not self.connection_active:
            print(f"[DIRECT] ❌ Connection is not active. Cannot transmit data.")
            return False
        
        # Verify that sender and receiver are the devices in this connection
        if (sender == self.device1 and receiver == self.device2) or (sender == self.device2 and receiver == self.device1):
            print(f"\n[DIRECT] === DIRECT DATA TRANSMISSION ===")
            print(f"[DIRECT] ▶ Source: {sender.get_device_name()} (MAC: {sender.get_mac()})")
            print(f"[DIRECT] ▶ Destination: {receiver.get_device_name()} (MAC: {receiver.get_mac()})")
            print(f"[DIRECT] ▶ Data: {data[:30]}{'...' if len(data) > 30 else ''}")
            
            # Calculate error probability based on connection quality
            error_probability = 1.0 - self.connection_quality
            
            # Set data in sender (with CRC applied at data link layer)
            sender.set_data(data)
            
            # Simulate transmission
            print(f"[DIRECT] ▶ Physical layer transmission in progress...")
            print(f"[DIRECT] ▶ Connection quality: {self.connection_quality:.2f}")
            print(f"[DIRECT] ▶ Error probability: {error_probability:.2f}")
            
            # Send data to receiver
            sender.send_data_to_receiver(receiver)
            
            # Check if transmission was acknowledged
            if receiver.ACKorNAK == "ACK":
                print(f"[DIRECT] ✓ Transmission successful: Received ACK")
                return True
            else:
                print(f"[DIRECT] ❌ Transmission failed: Received NAK")
                print(f"[DIRECT] ⚠ Retransmission required")
                return False
        else:
            print(f"[DIRECT] ❌ Error: These devices are not connected via this connection")
            print(f"[DIRECT] ⓘ Connected devices are: {self.device1.get_device_name()} and {self.device2.get_device_name()}")
            return False
    
    def disable_connection(self):
        """Disable this connection"""
        self.connection_active = False
        print(f"[DIRECT] ⚠ Connection between {self.device1.get_device_name()} and {self.device2.get_device_name()} disabled")
    
    def enable_connection(self):
        """Enable this connection"""
        self.connection_active = True
        print(f"[DIRECT] ✓ Connection between {self.device1.get_device_name()} and {self.device2.get_device_name()} enabled")
