"""
Search functionality implementation for Network Simulator
Equivalent to Sender_search.java and Receiver_search.java in the Java implementation
"""

from search_engine_server import SearchEngineServer

class SenderSearch:
    def __init__(self, search_website):
        """
        Initialize search sender
        
        Args:
            search_website (str): Website URL to search on
        """
        self.search_website = search_website
        self.key_to_be_sent = ""
        
        # Since we're not implementing GUI, we'll simulate user input
        print(f"\n--- SEARCH ENGINE ---")
        print(f"URL: {search_website}")
        print("Better to choose words like:")
        print("apple, boy, cat, dog, egg, fish, girl, house.")
        print("If not, it is your choice, but a result may be unavailable.")
        
        # Simulate getting search key from user
        self.key_to_be_sent = self.get_search_key()
    
    def get_search_key(self):
        """
        Simulate getting search key from user
        
        Returns:
            str: Search key
        """
        key = input("Enter search key: ")
        print(f"Searching for: {key}")
        return key


class ReceiverSearch:
    def __init__(self, search_website, key, meaning):
        """
        Initialize search receiver
        
        Args:
            search_website (str): Website URL used for search
            key (str): Search key
            meaning (str): Search result/meaning
        """
        # Since we're not implementing GUI, we'll display the search results in console
        print("\n--- SEARCH RESULTS ---")
        print(f"URL: {search_website}")
        print(f"Key: {key}")
        print(f"Meaning: {meaning}")
        print("Search result received successfully.")
