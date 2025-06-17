"""
Email Sender implementation for Network Simulator
Equivalent to Sender_email.java in the Java implementation
"""

class SenderEmail:
    def __init__(self, sender_email, receiver_email):
        """
        Initialize email sender
        
        Args:
            sender_email (str): Sender's email address
            receiver_email (str): Receiver's email address
        """
        self.sender_email = sender_email
        self.receiver_email = receiver_email
        self.email_to_be_sent = ""
        
        # Since we're not implementing GUI, we'll simulate user input
        print(f"\n--- EMAIL SENDER ---")
        print(f"Sender: {sender_email}")
        print(f"Receiver: {receiver_email}")
        
        # Simulate getting user input for email content
        self.email_to_be_sent = self.get_email_content()
    
    def get_email_content(self):
        """
        Simulate getting email content from user
        
        Returns:
            str: Email content
        """
        content = input("Enter your email content: ")
        print("Email content saved.")
        return content


class ReceiverEmail:
    def __init__(self, sender_email, receiver_email, data):
        """
        Initialize email receiver
        
        Args:
            sender_email (str): Sender's email address
            receiver_email (str): Receiver's email address
            data (str): Email content
        """
        self.email_to_be_received = data
        
        # Since we're not implementing GUI, we'll display the email in console
        print("\n--- EMAIL RECEIVER ---")
        print(f"Sender: {sender_email}")
        print(f"Receiver: {receiver_email}")
        print(f"Content: {self.email_to_be_received}")
        print("Email received successfully.")
