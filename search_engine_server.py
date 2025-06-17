"""
Search Engine Server implementation for Network Simulator
Equivalent to SearchEngineServer.java in the Java implementation
"""

class SearchEngineServer:
    @staticmethod
    def return_key_search(key):
        """
        Return search result for a given key
        
        Args:
            key (str): Search key
            
        Returns:
            str: Search result
        """
        search_results = {
            "apple": "red, apple shaped, keeps doctor away",
            "boy": "special kind of species who disguise themselves as humans",
            "cat": "small, long, colour varies, soft and funny,says meow",
            "dog": "medium size, cute, colour varies, barks, scares some people",
            "egg": "oval, white, may or may not be eaten",
            "fish": "lives in water, breathes in water, colourful, wide variety",
            "girl": "intelligent human being, sweet and nice",
            "house": "where humans live, animals may also live here"
        }
        
        return search_results.get(key, "Sorry, no search result available")
