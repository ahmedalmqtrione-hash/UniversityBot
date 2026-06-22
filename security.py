import random
import string
import time

class SecurityEngine:
    def __init__(self):
        self.master_pass = "2026"
        self.active_tokens = {}
    
    def generate_token(self, link, duration=300):
        token = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
        self.active_tokens[token] = {"link": link, "expiry": time.time() + duration}
        return token
    
    def access_token(self, token):
        if token in self.active_tokens:
            if time.time() < self.active_tokens[token]["expiry"]:
                return self.active_tokens[token]["link"]
            else:
                del self.active_tokens[token]
                return None
        return None

security = SecurityEngine()
