"""
End Devices implementation for Network Simulator
Equivalent to EndDevices.java in the Java implementation
"""

class EndDevices:
    def __init__(self, MAC, name, IP):
        """
        Initialize an end device with MAC address, name and IP
        
        Args:
            MAC (int): MAC address of the device
            name (str): Single character name of the device
            IP (str): IP address of the device
        """
        self.MAC = MAC
        self.device_name = name
        self.data = ""
        self.raw_data = ""  # Data at physical layer (without processing)
        self.ACKorNAK = "ACK0"  # Default ACK
        self.IP = IP
        self.ARP_cache = {MAC: IP}  # Store own MAC and IP in ARP cache
        
        # Go-Back-N protocol variables
        self.window_size = 4
        self.current_seq_num = 0  # Current sequence number for sending
        self.expected_seq_num = 0  # Next expected sequence number for receiving
        self.last_received_seq = -1  # Last correctly received frame
        
        # Buffer for frames and retransmission
        self.frame_buffer = {}  # Buffer for frames waiting for ACK
        self.received_frames = {}  # Frames successfully received
        
        # Create checksum handler as an instance variable
        from checksum_for_datalink import ChecksumForDataLink
        self.checksum_handler = ChecksumForDataLink()
        
        # Transmission status
        self.transmission_complete = False
        self.retransmission_count = 0
        self.max_retransmissions = 3
    
    def send_ARP_request(self, receiver):
        """
        Send ARP request to a receiver device
        
        Args:
            receiver (EndDevices): The receiver device
        """
        self.ARP_cache[receiver.get_mac()] = receiver.IP
    
    def get_mac(self):
        """Get MAC address of this device"""
        return self.MAC
    
    def set_data(self, d):
        """
        Set data for this device (used for the application layer)
        
        Args:
            d (str): Data for the device
        """
        print(f"[DEVICE {self.device_name}] ▶ Application layer: Setting data")
        self.raw_data = d
        
        # Apply data link layer processing (checksum)
        print(f"[DEVICE {self.device_name}] ▶ Data link layer: Applying checksum with Go-Back-N protocol")
        
        # Generate frame with correct sequence number
        self.data = self.checksum_handler.sender_code(d, self.current_seq_num)
        
        # Store the frame in buffer for possible retransmission
        self.frame_buffer[self.current_seq_num] = d
        
        # Advance sequence number for next frame
        self.current_seq_num = (self.current_seq_num + 1) % 10
        
        print(f"[DEVICE {self.device_name}] ✓ Frame ready for transmission")
        self.checksum_handler.print_window_status()
    
    def get_data(self):
        """Get data from this device (with checksum applied)"""
        return self.data
    
    def set_receiver_data(self, d):
        """
        Set data for receiving at physical layer, then process at data link layer
        
        Args:
            d (str): Data to be received
        """
        # PHYSICAL LAYER - Just receives the raw bits, no checking
        print(f"\n[DEVICE {self.device_name}] === RECEIVING DATA THROUGH NETWORK LAYERS ===")
        print(f"[DEVICE {self.device_name}] ▶ PHYSICAL LAYER: Received frame")
        self.raw_data = d
        
        # DATA LINK LAYER - Apply error detection
        print(f"[DEVICE {self.device_name}] ▶ DATA LINK LAYER: Processing frame with Go-Back-N protocol")
        
        # Use a controlled probability for bit flipping (e.g., 30% chance)
        error_probability = 0.3
        
        # Possibly modify the data (simulate transmission errors)
        modified_data = self.checksum_handler.receiver_code(d, error_probability)
        
        # Verify the checksum and extract sequence number and data
        is_valid, seq_num, frame_data = self.checksum_handler.verify_frame(modified_data)
        
        if not is_valid or seq_num == -1:
            print(f"[DEVICE {self.device_name}] ❌ DATA LINK LAYER: Checksum verification failed")
            if seq_num != -1:
                print(f"[DEVICE {self.device_name}] ❌ Frame {seq_num} will be discarded")
                # In Go-Back-N, we send NAK for the expected frame
                self.ACKorNAK = f"NAK{self.expected_seq_num}"
                print(f"[DEVICE {self.device_name}] ❌ Sending NAK{self.expected_seq_num}")
            else:
                print(f"[DEVICE {self.device_name}] ❌ Invalid frame format, cannot identify sequence number")
                self.ACKorNAK = f"NAK{self.expected_seq_num}"  # NAK with expected sequence number
        else:
            print(f"[DEVICE {self.device_name}] ✓ DATA LINK LAYER: Checksum verification passed")
            
            # Go-Back-N protocol implementation
            if seq_num == self.expected_seq_num:
                print(f"[DEVICE {self.device_name}] ✓ Received expected frame {seq_num}")
                
                # Store the valid data
                self.received_frames[seq_num] = frame_data
                self.last_received_seq = seq_num
                
                # Update expected sequence number
                self.expected_seq_num = (self.expected_seq_num + 1) % 10
                self.ACKorNAK = f"ACK{seq_num}"
                
                print(f"[DEVICE {self.device_name}] ✓ Sending ACK{seq_num}")
                print(f"[DEVICE {self.device_name}] ✓ Next expecting frame {self.expected_seq_num}")
            else:
                print(f"[DEVICE {self.device_name}] ⚠ Received out-of-order frame {seq_num}, expected {self.expected_seq_num}")
                # In Go-Back-N, we discard out-of-order frames and send ACK for the last in-order frame received
                if self.last_received_seq >= 0:
                    self.ACKorNAK = f"ACK{self.last_received_seq}"
                    print(f"[DEVICE {self.device_name}] ⚠ Sending cumulative ACK{self.last_received_seq}")
                else:
                    self.ACKorNAK = f"NAK{self.expected_seq_num}"
                    print(f"[DEVICE {self.device_name}] ⚠ No frames received yet, sending NAK{self.expected_seq_num}")
        
        # Store the data regardless of validity - upper layer will handle errors
        self.data = modified_data
        
        # Extract actual message to pass to the network layer
        if is_valid and seq_num == self.expected_seq_num - 1 or (self.expected_seq_num == 0 and seq_num == 9):
            print(f"[DEVICE {self.device_name}] ▶ NETWORK LAYER: Processing message: {frame_data}")
        else:
            print(f"[DEVICE {self.device_name}] ⚠ NETWORK LAYER: Frame not passed to network layer")
    
    def process_acknowledgment(self):
        """
        Process acknowledgment and update the sending window
        
        Returns:
            list: Frames to retransmit if any
        """
        to_retransmit = []
        
        if self.ACKorNAK.startswith("ACK"):
            # Process ACK
            acked_frames = self.checksum_handler.process_ack(self.ACKorNAK)
            print(f"[DEVICE {self.device_name}] ✓ Processed ACK: {self.ACKorNAK}")
            self.checksum_handler.print_window_status()
            self.retransmission_count = 0  # Reset retransmission counter
            
            # Check if transmission is complete
            if len(self.frame_buffer) == 0:
                self.transmission_complete = True
                print(f"[DEVICE {self.device_name}] ✓ All frames acknowledged, transmission complete")
                
        elif self.ACKorNAK.startswith("NAK"):
            # Process NAK
            to_retransmit = self.checksum_handler.handle_nak(self.ACKorNAK)
            print(f"[DEVICE {self.device_name}] ⚠ Processed NAK: {self.ACKorNAK}")
            print(f"[DEVICE {self.device_name}] ⚠ Will retransmit frames: {to_retransmit}")
            
            # Increment retransmission counter
            self.retransmission_count += 1
            print(f"[DEVICE {self.device_name}] ⚠ Retransmission attempt {self.retransmission_count} of {self.max_retransmissions}")
            
            # Check if we've reached max retransmissions
            if self.retransmission_count >= self.max_retransmissions:
                print(f"[DEVICE {self.device_name}] ❌ Max retransmissions reached, transmission failed")
                self.transmission_complete = True  # Mark as complete even though it failed
            
        return to_retransmit
    
    def retransmit_frames(self, seq_nums_to_retransmit):
        """
        Retransmit frames with specified sequence numbers
        
        Args:
            seq_nums_to_retransmit (list): List of sequence numbers to retransmit
            
        Returns:
            str: The first retransmitted frame (for simulation purposes)
        """
        if not seq_nums_to_retransmit:
            print(f"[DEVICE {self.device_name}] ⚠ No frames to retransmit")
            return None
        
        # For simulation purposes, we'll just retransmit the first frame in the list
        seq_num = seq_nums_to_retransmit[0]
        if seq_num not in self.frame_buffer:
            print(f"[DEVICE {self.device_name}] ⚠ Cannot retransmit frame {seq_num} - not in buffer")
            return None
            
        data = self.frame_buffer[seq_num]
        print(f"[DEVICE {self.device_name}] ▶ Retransmitting frame {seq_num}")
        
        # Regenerate the frame with the sequence number
        retransmitted_frame = self.checksum_handler.sender_code(data, seq_num)
        self.data = retransmitted_frame
        
        print(f"[DEVICE {self.device_name}] ▶ Frame {seq_num} ready for retransmission")
        return retransmitted_frame
    
    def send_data_and_address_to_hub(self, hub):
        """
        Send data and address to hub
        
        Args:
            hub (Hub): The hub to send data to
        """
        hub.sender_address = self.MAC
        hub.receive_data_from_sender(self.data)
        print(f"[DEVICE {self.device_name}] ▶ Sending data to Hub {hub.get_hub_number()}")
    
    def send_data_to_receiver(self, receiver):
        """
        Send data directly to receiver
        
        Args:
            receiver (EndDevices): The receiver device
        """
        # APPLICATION LAYER - Data originates here (already set in self.data)
        # TRANSPORT LAYER - Would handle segmentation, flow control (not implemented)
        # NETWORK LAYER - Would handle routing (not fully implemented)
        # DATA LINK LAYER - Already handled by set_data() for the sender
        # PHYSICAL LAYER - Raw bit transmission
        
        print(f"[DEVICE {self.device_name}] === SENDING DATA THROUGH NETWORK LAYERS ===")
        print(f"[DEVICE {self.device_name}] ▶ APPLICATION LAYER: Data ready for transmission")
        print(f"[DEVICE {self.device_name}] ▶ TRANSPORT LAYER: Preparing segments")
        print(f"[DEVICE {self.device_name}] ▶ NETWORK LAYER: Preparing datagram with destination IP {receiver.IP}")
        print(f"[DEVICE {self.device_name}] ▶ DATA LINK LAYER: Framing with destination MAC {receiver.get_mac()}")
        print(f"[DEVICE {self.device_name}] ▶ PHYSICAL LAYER: Sending bits to {receiver.get_device_name()}")
        
        # Send the physical layer bits to the receiver
        receiver.set_receiver_data(self.data)
        
        # In a real implementation, we'd wait for ACK here
        print(f"[DEVICE {self.device_name}] ▶ Waiting for acknowledgment...")
        ack = receiver.ACKorNAK
        print(f"[DEVICE {self.device_name}] ▶ Received: {ack}")
        self.ACKorNAK = ack  # Store the received ACK/NAK
        
        # Process the acknowledgment and get frames to retransmit
        frames_to_retransmit = self.process_acknowledgment()
        
        # If we need to retransmit frames, do so
        if frames_to_retransmit:
            retransmitted_frame = self.retransmit_frames(frames_to_retransmit)
            if retransmitted_frame:
                print(f"[DEVICE {self.device_name}] ▶ Retransmitting to {receiver.get_device_name()}")
                self.send_data_to_receiver(receiver)
        
        print(f"[DEVICE {self.device_name}] ✓ Data transmission process completed")
    
    def get_device_name(self):
        """Get the name of this device"""
        return self.device_name
    
    def send_ACK_or_NAK(self, check_error, sender_device):
        """
        Send ACK or NAK based on error check
        
        Args:
            check_error (bool): Whether error was detected
            sender_device (EndDevices): The sender device
        """
        if check_error:
            print(f"[DEVICE {self.device_name}] ❌ Sending NAK{self.expected_seq_num} to {sender_device.get_device_name()}")
            sender_device.ACKorNAK = f"NAK{self.expected_seq_num}"
        else:
            print(f"[DEVICE {self.device_name}] ✓ Sending ACK{self.last_received_seq} to {sender_device.get_device_name()}")
            sender_device.ACKorNAK = f"ACK{self.last_received_seq}"
            
    def is_transmission_complete(self):
        """
        Check if transmission is complete
        
        Returns:
            bool: True if transmission is complete
        """
        return self.transmission_complete
