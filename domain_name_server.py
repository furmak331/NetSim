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
        
        print("\n[DNS] === EMAIL DNS MAPPINGS ===")
        print(f"[DNS] ▶ Setting up DNS for email server at IP: {receiver_IP}")
        
        # Extract usernames from email addresses
        for email in emails:
            username = email[:email.find('@')]
            mail_names.append(username)
            print(f"[DNS] ▶ Extracted username: {username} from {email}")
        
        # Extract IP parts - Fixed the logic here
        IP_parts = [None] * 4
        
        # Parse the IP address properly
        try:
            ip_segments = receiver_IP.split('.')
            if len(ip_segments) == 4:
                IP_parts = ip_segments
                print(f"[DNS] ▶ Parsed IP segments: {IP_parts}")
            else:
                print(f"[DNS] ⚠ Warning: IP address format incorrect. Expected 4 segments, got {len(ip_segments)}")
                # Use default values
                IP_parts = [receiver_IP[:receiver_IP.find('.')], "0", "0", receiver_IP[receiver_IP.rindex('.')+1:]]
        except Exception as e:
            print(f"[DNS] ❌ Error parsing IP address: {str(e)}")
            # Fallback to simple parsing
            IP_parts[0] = receiver_IP[:receiver_IP.find('.')]
            IP_parts[1] = "0"
            IP_parts[2] = "0"
            IP_parts[3] = receiver_IP[receiver_IP.rindex('.')+1:]
        
        # Create DNS mappings
        dns = {}
        dns["com"] = IP_parts[2]
        dns["gmail"] = IP_parts[1]
        dns["@"] = IP_parts[1]
        
        for i in range(len(emails)):
            dns[mail_names[i]] = IP_parts[0]
        
        # Print DNS mappings
        print("\n[DNS] === DNS MAPPINGS FOR EMAIL ===")
        for key, value in dns.items():
            print(f"[DNS] {key:<20} → {value}")
        print()
        
        return dns
    
    @staticmethod
    def store_DNS_for_search_engines(receiver_IP):
        """
        Store DNS mappings for search engines
        
        Args:
            receiver_IP (str): IP address of receiver
            
        Returns:
            dict: DNS mappings
        """
        websites = ["www.google.com", "www.duckduckgo.com", "www.bing.com"]
        website_names = []
        
        print("\n[DNS] === SEARCH ENGINE DNS MAPPINGS ===")
        print(f"[DNS] ▶ Setting up DNS for search engine server at IP: {receiver_IP}")
        
        # Extract domain names from websites
        for website in websites:
            # Extract domain name (e.g., "google" from "www.google.com")
            try:
                start = website.find('.') + 1
                end = website.rindex('.')
                domain = website[start:end]
                website_names.append(domain)
                print(f"[DNS] ▶ Extracted domain: {domain} from {website}")
            except Exception as e:
                print(f"[DNS] ❌ Error parsing website {website}: {str(e)}")
                website_names.append("unknown")
        
        # Extract IP parts
        IP_parts = [None] * 4
        
        # Parse the IP address properly
        try:
            ip_segments = receiver_IP.split('.')
            if len(ip_segments) == 4:
                IP_parts = ip_segments
                print(f"[DNS] ▶ Parsed IP segments: {IP_parts}")
            else:
                print(f"[DNS] ⚠ Warning: IP address format incorrect. Expected 4 segments, got {len(ip_segments)}")
                # Use default values
                IP_parts = [receiver_IP[:receiver_IP.find('.')], "0", "0", receiver_IP[receiver_IP.rindex('.')+1:]]
        except Exception as e:
            print(f"[DNS] ❌ Error parsing IP address: {str(e)}")
            # Fallback to simple parsing
            IP_parts[0] = receiver_IP[:receiver_IP.find('.')]
            IP_parts[1] = "0"
            IP_parts[2] = "0"
            IP_parts[3] = receiver_IP[receiver_IP.rindex('.')+1:]
        
        # Create DNS mappings
        dns = {}
        dns["."] = IP_parts[1]
        dns["com"] = IP_parts[2]
        dns["www"] = IP_parts[1]
        
        for i in range(len(websites)):
            dns[website_names[i]] = IP_parts[0]
        
        # Print DNS mappings
        print("\n[DNS] === DNS MAPPINGS FOR SEARCH ENGINES ===")
        for key, value in dns.items():
            print(f"[DNS] {key:<20} → {value}")
        print()
        
        return dns
