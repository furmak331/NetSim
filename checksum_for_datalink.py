"""
Checksum for Data Link implementation for Network Simulator
Replaces CRC with a simpler checksum implementation
"""

class ChecksumForDataLink:
    def __init__(self):
        """Initialize Checksum for Data Link"""
        self.original_text = ""
        self.checksum_value = ""
        self.sent_copy = ""
        self.sequence_number = 0  # Current sequence number for sending
        self.expected_sequence = 0  # Next expected sequence number for receiving
        self.window_size = 4  # Window size for Go-Back-N
        self.frame_buffer = {}  # Buffer for frames waiting for ACK
        self.window_base = 0  # Base of the sliding window
    
    def text_to_binary(self, text):
        """
        Convert text to binary string
        
        Args:
            text (str): Text to convert
            
        Returns:
            str: Binary representation
        """
        binary = ""
        for char in text:
            # Convert each character to its ASCII value, then to binary
            # Remove '0b' prefix and pad to 8 bits
            binary += format(ord(char), '08b')
        return binary
    
    def binary_to_text(self, binary):
        """
        Convert binary string to text
        
        Args:
            binary (str): Binary data to convert
            
        Returns:
            str: Text representation
        """
        text = ""
        # Process 8 bits at a time
        for i in range(0, len(binary), 8):
            if i + 8 <= len(binary):
                byte = binary[i:i+8]
                text += chr(int(byte, 2))
        return text
    
    def calculate_checksum(self, text):
        """
        Calculate a simple checksum for the given text
        
        Args:
            text (str): Text to calculate checksum for
            
        Returns:
            str: Binary checksum (16 bits)
        """
        # Convert to binary
        binary = self.text_to_binary(text)
        
        # Pad to multiple of 16 bits
        while len(binary) % 16 != 0:
            binary += '0'
        
        # Calculate one's complement sum
        checksum = 0
        for i in range(0, len(binary), 16):
            if i + 16 <= len(binary):
                chunk = binary[i:i+16]
                chunk_value = int(chunk, 2)
                checksum = (checksum + chunk_value) & 0xFFFF  # Keep it 16 bits
        
        # One's complement of the sum
        checksum = checksum ^ 0xFFFF
        
        # Convert to binary (16 bits)
        return format(checksum, '016b')
    
    def create_frame(self, data, seq_num):
        """
        Create a frame with sequence number and checksum
        
        Args:
            data (str): Data to send
            seq_num (int): Sequence number
            
        Returns:
            str: Framed data with checksum
        """
        # Format: SEQ|data|CHECKSUM where SEQ is a single digit (0-9)
        frame_data = f"{seq_num % 10}|{data}"
        checksum = self.calculate_checksum(frame_data)
        framed_data = f"{frame_data}|CHECKSUM|{checksum}"
        return framed_data
    
    def sender_code(self, text, seq_num=None):
        """
        Generate frame with checksum for sender
        
        Args:
            text (str): Text data to transmit
            seq_num (int, optional): Sequence number override
            
        Returns:
            str: Data with checksum appended
        """
        self.original_text = text
        
        if seq_num is None:
            seq_num = self.sequence_number
            
        # Check if we can send this frame (within window)
        window_end = (self.window_base + self.window_size) % 10
        can_send = False
        
        # Check if sequence number is within window
        if self.window_base <= window_end:
            # Normal case (window doesn't wrap around)
            can_send = self.window_base <= seq_num < window_end
        else:
            # Window wraps around (e.g., base=8, end=2)
            can_send = seq_num >= self.window_base or seq_num < window_end
        
        if not can_send:
            print(f"\n[DATA LINK] ⚠ Cannot send frame {seq_num} - outside window {self.window_base}-{window_end}")
            return None
        
        print(f"\n[DATA LINK] ▶ Creating frame {seq_num} with data: {text}")
        
        # Calculate checksum
        frame = self.create_frame(text, seq_num)
        self.sent_copy = frame
        
        # Store the frame in the buffer for possible retransmission
        self.frame_buffer[seq_num] = frame
        
        # Advance sequence number for next frame
        if seq_num == self.sequence_number:
            self.sequence_number = (self.sequence_number + 1) % 10
        
        # Get the checksum part for logging
        checksum = frame.split("|CHECKSUM|")[1]
        
        print(f"[DATA LINK] ▶ Frame {seq_num}: {text}")
        print(f"[DATA LINK] ▶ Checksum: {checksum}")
        print(f"[DATA LINK] ▶ Window: base={self.window_base}, size={self.window_size}, next={self.sequence_number}")
        
        return frame
    
    def verify_frame(self, frame):
        """
        Verify if a frame's checksum is valid
        
        Args:
            frame (str): Frame to verify
            
        Returns:
            tuple: (is_valid, seq_num, data)
        """
        try:
            # Parse the frame: SEQ|data|CHECKSUM|value
            parts = frame.split("|")
            if len(parts) < 4 or parts[2] != "CHECKSUM":
                print("[DATA LINK] ⚠ ERROR: Invalid frame format")
                return False, -1, None
            
            seq_num = int(parts[0])
            data = parts[1]
            received_checksum = parts[3]
            
            # Re-calculate the checksum
            calculated_checksum = self.calculate_checksum(f"{seq_num}|{data}")
            
            # Compare checksums
            is_valid = (calculated_checksum == received_checksum)
            
            if not is_valid:
                print(f"[DATA LINK] ❌ CHECKSUM ERROR: Received {received_checksum}, calculated {calculated_checksum}")
                print(f"[DATA LINK] ❌ Frame {seq_num} is corrupt")
            else:
                print(f"[DATA LINK] ✓ Checksum verified for frame {seq_num}")
            
            return is_valid, seq_num, data
            
        except Exception as e:
            print(f"[DATA LINK] ⚠ ERROR processing frame: {e}")
            return False, -1, None
    
    def receiver_code(self, frame, error_probability):
        """
        Process received frame and introduce random bit error based on probability
        
        Args:
            frame (str): Frame received
            error_probability (float): Probability for bit flipping (0-1)
            
        Returns:
            str: Possibly modified frame
        """
        import random
        
        # Create a copy of original frame
        modified_frame = frame
        
        try:
            # Parse the frame parts
            seq_part = frame.split("|")[0]
            data_part = frame.split("|")[1]
            checksum_keyword = frame.split("|")[2]
            checksum_part = frame.split("|")[3]
            
            print(f"\n[DATA LINK] ▶ Received frame: {seq_part}|{data_part}")
            print(f"[DATA LINK] ▶ Frame checksum: {checksum_part}")
            
            # With a certain probability, introduce an error
            error_chance = random.random()
            print(f"[DATA LINK] ▶ Error probability: {error_probability:.2f}, Random value: {error_chance:.2f}")
            
            if error_chance < error_probability:
                # Convert data part to binary for bit flipping
                binary_data = self.text_to_binary(data_part)
                binary_list = list(binary_data)
                
                # Randomly select a bit to flip
                bit_to_flip = random.randint(0, len(binary_list) - 1)
                
                # Flip the bit (0->1 or 1->0)
                original_bit = binary_list[bit_to_flip]
                binary_list[bit_to_flip] = '1' if original_bit == '0' else '0'
                
                # Convert back to string
                modified_binary = ''.join(binary_list)
                modified_text = self.binary_to_text(modified_binary)
                
                # Create modified frame
                modified_frame = f"{seq_part}|{modified_text}|{checksum_keyword}|{checksum_part}"
                
                # Calculate position information for better logging
                byte_position = bit_to_flip // 8
                bit_in_byte = bit_to_flip % 8
                affected_char = data_part[byte_position:byte_position+1] if byte_position < len(data_part) else "?"
                
                print(f"[DATA LINK] ⚠ BIT ERROR: Bit flipped at position {bit_to_flip}")
                print(f"[DATA LINK] ⚠ Affected byte {byte_position}, bit {bit_in_byte} in character '{affected_char}'")
                print(f"[DATA LINK] ⚠ Original: {data_part}, Modified: {modified_text}")
            else:
                print(f"[DATA LINK] ✓ No transmission errors introduced")
                
        except Exception as e:
            print(f"[DATA LINK] ⚠ ERROR: Frame format incorrect: {e}")
            
        return modified_frame
    
    def process_ack(self, ack):
        """
        Process an acknowledgment and update the send window
        
        Args:
            ack (str): Acknowledgment string (e.g., "ACK3")
            
        Returns:
            list: Sequence numbers that were ACKed
        """
        if not ack.startswith("ACK"):
            print(f"[DATA LINK] ⚠ Invalid ACK format: {ack}")
            return []
            
        try:
            # Extract the ACK number
            ack_num = int(ack[3:])
            acked_frames = []
            
            print(f"[DATA LINK] ▶ Received ACK for frame {ack_num}")
            print(f"[DATA LINK] ▶ Current window base: {self.window_base}")
            print(f"[DATA LINK] ▶ Current frame buffer: {list(self.frame_buffer.keys())}")
            
            # Go-Back-N uses cumulative ACKs
            # Move the window base to ack_num + 1
            # Need to handle sequence number wrap-around
            if ack_num >= self.window_base:
                # Normal case
                for seq in range(self.window_base, ack_num + 1):
                    if seq in self.frame_buffer:
                        del self.frame_buffer[seq]
                        acked_frames.append(seq)
                        print(f"[DATA LINK] ✓ Frame {seq} acknowledged and removed from buffer")
            else:
                # Wrap-around case
                # First, remove frames from window_base to 9
                for seq in range(self.window_base, 10):
                    if seq in self.frame_buffer:
                        del self.frame_buffer[seq]
                        acked_frames.append(seq)
                        print(f"[DATA LINK] ✓ Frame {seq} acknowledged and removed from buffer")
                
                # Then remove frames from 0 to ack_num
                for seq in range(0, ack_num + 1):
                    if seq in self.frame_buffer:
                        del self.frame_buffer[seq]
                        acked_frames.append(seq)
                        print(f"[DATA LINK] ✓ Frame {seq} acknowledged and removed from buffer")
            
            # Update window base
            self.window_base = (ack_num + 1) % 10
            print(f"[DATA LINK] ▶ New window base: {self.window_base}")
            print(f"[DATA LINK] ▶ Updated frame buffer: {list(self.frame_buffer.keys())}")
            
            return acked_frames
            
        except Exception as e:
            print(f"[DATA LINK] ⚠ ERROR processing ACK: {e}")
            return []
    
    def handle_nak(self, nak):
        """
        Handle a NAK by preparing to resend from the NAKed sequence
        
        Args:
            nak (str): NAK string (e.g., "NAK3")
            
        Returns:
            list: Sequence numbers to resend
        """
        if not nak.startswith("NAK"):
            print(f"[DATA LINK] ⚠ Invalid NAK format: {nak}")
            return []
            
        try:
            # Extract the NAK number
            nak_num = int(nak[3:])
            
            print(f"[DATA LINK] ▶ Received NAK for frame {nak_num}")
            print(f"[DATA LINK] ▶ Current frame buffer: {list(self.frame_buffer.keys())}")
            
            # Go-Back-N: resend all frames from NAK sequence onward that are in the buffer
            to_resend = []
            for seq in sorted(self.frame_buffer.keys()):
                if (seq >= nak_num and seq < (nak_num + self.window_size) % 10) or \
                   (nak_num + self.window_size >= 10 and seq < (nak_num + self.window_size) % 10):
                    to_resend.append(seq)
            
            print(f"[DATA LINK] ▶ Will resend frames: {to_resend}")
            return to_resend
            
        except Exception as e:
            print(f"[DATA LINK] ⚠ ERROR processing NAK: {e}")
            return []
    
    def get_next_frames_to_send(self):
        """
        Get the next frames to send based on the current window
        
        Returns:
            list: List of sequence numbers to send
        """
        # Calculate the end of the window, handling wrap-around
        window_end = (self.window_base + self.window_size) % 10
        to_send = []
        
        # Check if we can send each frame within the window
        for seq in range(10):  # Check all possible sequence numbers
            if self.window_base <= window_end:
                # Normal case (window doesn't wrap around)
                if self.window_base <= seq < window_end:
                    to_send.append(seq)
            else:
                # Window wraps around (e.g., base=8, end=2)
                if seq >= self.window_base or seq < window_end:
                    to_send.append(seq)
        
        print(f"[DATA LINK] ▶ Available frames to send within window: {to_send}")
        return to_send
        
    def print_window_status(self):
        """Print the current status of the sliding window"""
        print(f"[DATA LINK] === GO-BACK-N WINDOW STATUS ===")
        print(f"[DATA LINK] ▶ Window base: {self.window_base}")
        print(f"[DATA LINK] ▶ Window size: {self.window_size}")
        print(f"[DATA LINK] ▶ Window end: {(self.window_base + self.window_size) % 10}")
        print(f"[DATA LINK] ▶ Next sequence number: {self.sequence_number}")
        print(f"[DATA LINK] ▶ Frames in buffer: {list(self.frame_buffer.keys())}")
        
        # Visual representation of the window
        window_repr = []
        for i in range(10):
            if i == self.window_base:
                marker = "[Base→ "
            elif i == (self.window_base + self.window_size - 1) % 10:
                marker = " ←End]"
            elif self.window_base <= i < (self.window_base + self.window_size) % 10:
                marker = "      "
            else:
                marker = "      "
                
            status = "✓" if i in self.frame_buffer else " "
            window_repr.append(f"{marker}{i}{status}")
            
        print(f"[DATA LINK] ▶ Window: {''.join(window_repr)}")
