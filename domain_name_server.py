"""
Domain Name Server implementation for Network Simulator
Equivalent to DomainNameServer.java in the Java implementation
"""

class DomainNameServer:
    @staticmethod
    def store_DNS_for_email(receiver_IP):
        """
        Store DNS mappings for email addresses
        
        Args:
            receiver_IP (str): IP address of receiver
        """
        emails = ["akansha08agarwal@gmail.com", "akansha26agarwal@gmail.com", 
                  "bhartitak11@gmail.com", "zakiakmal13@gmail.com"]
        mail_names = []
        
        # Extract usernames from email addresses
        for email in emails:
            mail_names.append(email[:email.find('@')])
        
        # Extract IP parts
        IP_parts = [None] * 4
        IP_parts[0] = receiver_IP[:receiver_IP.find('.')]
        IP_parts[1] = "0"
        IP_parts[2] = receiver_IP[receiver_IP.rindex('.')+1:]
        
        # Create DNS mappings
        dns = {}
        dns["com"] = IP_parts[2]
        dns["gmail"] = IP_parts[1]
        dns["@"] = IP_parts[1]
        
        for i in range(len(emails)):
            dns[mail_names[i]] = IP_parts[0]
        
        # Print DNS mappings
        print("\nThe DNS mappings for g-mail are as follows:")
        for key, value in dns.items():
            print(f"{key} -> {value}")
        print()
    
    @staticmethod
    def store_DNS_for_search_engines(receiver_IP):
        """
        Store DNS mappings for search engines
        
        Args:
            receiver_IP (str): IP address of receiver
        """
        websites = ["www.google.com", "www.duckduckgo.com", "www.bing.com"]
        website_names = []
        
        # Extract domain names from websites
        for website in websites:
            # Extract domain name (e.g., "google" from "www.google.com")
            start = website.find('.') + 1
            end = website.rindex('.')
            website_names.append(website[start:end])
        
        # Extract IP parts
        IP_parts = [None] * 4
        IP_parts[0] = receiver_IP[:receiver_IP.find('.')]
        IP_parts[1] = "0"
        IP_parts[2] = receiver_IP[receiver_IP.rindex('.')+1:]
        
        # Create DNS mappings
        dns = {}
        dns["."] = IP_parts[1]
        dns["com"] = IP_parts[2]
        dns["www"] = IP_parts[1]
        
        for i in range(len(websites)):
            dns[website_names[i]] = IP_parts[0]
        
        # Print DNS mappings
        print("\nThe DNS mappings for search engine are as follows:")
        for key, value in dns.items():
            print(f"{key} -> {value}")
        print()
