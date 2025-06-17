"""
CRC for Data Link implementation for Network Simulator
Equivalent to CRCforDataLink.java in the Java implementation
"""

class CRCforDataLink:
    def __init__(self):
        """Initialize CRC for Data Link with binary data and divisor"""
        self.binary_data = ""
        self.recvd_data = ""
        self.divisor = "100000111"  # Generator polynomial
        self.rem = ""
        self.sxt_copy = ""
    
    def sender_code(self, sxt_bit):
        """
        Generate CRC code for sender
        
        Args:
            sxt_bit (str): Binary data to transmit
            
        Returns:
            str: Data with CRC appended
        """
        self.sxt_copy = sxt_bit
        sxt_bit += "00000000"  # Append zeros for calculation
        self.rem = self.binary_xor_division(sxt_bit, self.divisor)
        self.sxt_copy += self.rem
        print(f"The remainder is {self.rem}")
        print(f"The sender codeword is {self.sxt_copy}")
        return self.sxt_copy
    
    def receiver_code(self, sxt_bit, probability):
        """
        Process received code and introduce random bit error
        
        Args:
            sxt_bit (str): Binary data received
            probability (float): Probability for bit flipping
            
        Returns:
            str: Possibly modified data
        """
        import random
        import math
        
        # Convert string to array of integers
        arr = [int(sxt_bit[i]) for i in range(24)]
        
        # Randomly flip bits based on probability
        bit_to_flip = math.ceil(random.random() * 23)
        rand_prob = random.random()
        
        if rand_prob < 0.5:
            arr[bit_to_flip] = 1 - arr[bit_to_flip]  # Flip bit (0->1 or 1->0)
        
        # Convert back to string
        sxt_bit = ''.join([str(bit) for bit in arr])
        print("The received codeword is", sxt_bit)
        
        self.recvd_data = sxt_bit
        return sxt_bit
    
    @staticmethod
    def is_correct(d):
        """
        Check if received data has errors
        
        Args:
            d (str): Data to check
            
        Returns:
            bool: True if error detected, False otherwise
        """
        rem = CRCforDataLink.binary_xor_division(d, "100000111")
        if rem != "00000000":
            print("Discard")
            return True
        else:
            print("No error")
            print(f"The received data is {d}")
            return False
    
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
        temp = dividend[:len(divisor) - 1]
        
        for i in range(len(divisor) - 1, len(dividend)):
            temp += dividend[i]
            if temp[0] == '1':
                temp = CRCforDataLink.xor_op(temp, divisor)
            else:
                temp = CRCforDataLink.xor_op(temp, "0" * len(divisor))
            temp = temp[1:]
        
        return temp
    
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
