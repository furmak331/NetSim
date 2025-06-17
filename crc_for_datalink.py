"""
CRC for Data Link implementation for Network Simulator
Equivalent to CRCforDataLink.java in the Java implementation
"""

class CRCforDataLink:
    def __init__(self):
        """Initialize CRC for Data Link with binary data and divisor"""
        self.binary_data = ""
        self.recvd_data = ""
        self.divisor = "100000111"  # Generator polynomial CRC-8
        self.rem = ""
        self.sxt_copy = ""
        self.original_text = ""
    
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
    
    def sender_code(self, text):
        """
        Generate CRC code for sender
        
        Args:
            text (str): Text data to transmit
            
        Returns:
            str: Data with CRC appended (with special separator)
        """
        self.original_text = text
        # Convert text to binary
        binary_data = self.text_to_binary(text)
        print(f"\n[DATA LINK] ▶ Computing CRC for message: {text}")
        print(f"[DATA LINK] ▶ Binary representation: {binary_data}")
        
        # Calculate CRC
        # Append zeros equal to divisor length minus 1
        padding_size = len(self.divisor) - 1
        binary_with_padding = binary_data + ("0" * padding_size)
        self.rem = self.binary_xor_division(binary_with_padding, self.divisor)
        
        # Store the complete codeword
        self.sxt_copy = text + "|CRC|" + self.rem
        
        print(f"[DATA LINK] ▶ CRC calculation: {self.divisor} (polynomial)")
        print(f"[DATA LINK] ▶ CRC remainder: {self.rem}")
        print(f"[DATA LINK] ✓ Message with CRC: {text}|CRC|{self.rem}")
        return self.sxt_copy
    
    def receiver_code(self, data, probability):
        """
        Process received code and introduce random bit error based on probability
        
        Args:
            data (str): Data received (text with CRC)
            probability (float): Probability for bit flipping (0-1)
            
        Returns:
            str: Possibly modified data
        """
        import random
        
        # Split the data into text and CRC parts
        if "|CRC|" not in data:
            print("[DATA LINK] ⚠ ERROR: Invalid data format: CRC separator not found")
            return data
            
        text_part, crc_part = data.split("|CRC|")
        binary_data = self.text_to_binary(text_part)
        
        # Create a copy of original data
        modified_data = text_part + "|CRC|" + crc_part
        print(f"\n[DATA LINK] ▶ Received frame: {text_part}")
        print(f"[DATA LINK] ▶ Frame CRC: {crc_part}")
        
        # With a certain probability, introduce an error
        error_chance = random.random()
        print(f"[DATA LINK] ▶ Error probability: {probability:.2f}, Random value: {error_chance:.2f}")
        
        if error_chance < probability:
            # Convert text part to binary array for manipulation
            binary_list = list(binary_data)
            
            # Randomly select a bit to flip
            bit_to_flip = random.randint(0, len(binary_list) - 1)
            
            # Flip the bit (0->1 or 1->0)
            original_bit = binary_list[bit_to_flip]
            binary_list[bit_to_flip] = '1' if original_bit == '0' else '0'
            
            # Convert back to string
            modified_binary = ''.join(binary_list)
            modified_text = self.binary_to_text(modified_binary)
            
            # Create modified data with original CRC
            modified_data = modified_text + "|CRC|" + crc_part
            
            # Calculate position information for better logging
            bit_position = bit_to_flip
            byte_position = bit_to_flip // 8
            bit_in_byte = bit_to_flip % 8
            affected_char = text_part[byte_position:byte_position+1]
            
            print(f"[DATA LINK] ⚠ BIT ERROR: Bit flipped at position {bit_position}")
            print(f"[DATA LINK] ⚠ Affected byte {byte_position}, bit {bit_in_byte} in character '{affected_char}'")
            print(f"[DATA LINK] ⚠ Original bit value: {original_bit}, New value: {binary_list[bit_to_flip]}")
            print(f"[DATA LINK] ⚠ Modified text: {modified_text}")
        else:
            print(f"[DATA LINK] ✓ No transmission errors introduced")
        
        return modified_data
    
    @staticmethod
    def is_correct(data):
        """
        Check if received data has errors using CRC check
        
        Args:
            data (str): Data to check (text|CRC|checksum format)
            
        Returns:
            bool: True if error detected, False otherwise
        """
        if "|CRC|" not in data:
            print("[DATA LINK] ⚠ ERROR: Invalid data format: missing CRC separator")
            return True  # Consider invalid format as an error
        
        text_part, crc_part = data.split("|CRC|")
        
        # Convert text to binary and append the received CRC
        crc = CRCforDataLink()
        binary_data = crc.text_to_binary(text_part) + crc_part
        
        # Do CRC check - remainder should be all zeros if no errors
        print(f"[DATA LINK] ▶ Verifying data integrity with CRC check")
        rem = CRCforDataLink.binary_xor_division(binary_data, "100000111")
        
        if "1" in rem:  # Check if there's any 1 in the remainder
            print(f"[DATA LINK] ❌ ERROR DETECTED: CRC check failed!")
            print(f"[DATA LINK] ❌ Remainder: {rem} (should be all zeros)")
            print(f"[DATA LINK] ❌ Frame will be discarded, retransmission required")
            return True  # Error detected
        else:
            print(f"[DATA LINK] ✓ Data integrity verified: CRC check passed")
            print(f"[DATA LINK] ✓ Data verified: {text_part}")
            return False  # No errors
    
    @staticmethod
    def binary_xor_division(dividend, divisor):
        """
        Perform binary XOR division for CRC
        
        Args:
            dividend (str): The dividend
            divisor (str): The divisor
            
        Returns:
            str: The remainder
        """
        # Copy first n-1 bits from dividend
        n = len(divisor)
        pick = dividend[:n]
        
        # Perform XOR division
        while n < len(dividend):
            if pick[0] == '1':
                pick = CRCforDataLink.xor_op(pick, divisor) + dividend[n]
            else:
                # If first bit is 0, XOR with all zeros
                zeros = '0' * len(divisor)
                pick = CRCforDataLink.xor_op(pick, zeros) + dividend[n]
            pick = pick[1:]  # Remove the first bit
            n += 1
        
        # Final step
        if pick[0] == '1':
            pick = CRCforDataLink.xor_op(pick, divisor)
        else:
            zeros = '0' * len(divisor)
            pick = CRCforDataLink.xor_op(pick, zeros)
        
        return pick[1:]  # Return remainder
    
    @staticmethod
    def xor_op(str1, str2):
        """
        Perform XOR operation on two binary strings
        
        Args:
            str1 (str): First binary string
            str2 (str): Second binary string
            
        Returns:
            str: XOR result
        """
        result = ""
        for i in range(len(str1)):
            if str1[i] == str2[i]:
                result += "0"
            else:
                result += "1"
        return result
