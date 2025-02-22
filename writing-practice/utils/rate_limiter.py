import time
from collections import defaultdict
from functools import wraps
import logging

logger = logging.getLogger(__name__)

class RateLimiter:
    def __init__(self, max_requests=10, time_window=60):
        """Initialize rate limiter.
        
        Args:
            max_requests: Maximum number of requests allowed in time window
            time_window: Time window in seconds
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = defaultdict(list)
    
    def is_allowed(self, user_id):
        """Check if request is allowed for user."""
        current_time = time.time()
        user_requests = self.requests[user_id]
        
        # Remove old requests outside time window
        while user_requests and user_requests[0] < current_time - self.time_window:
            user_requests.pop(0)
        
        # Check if under limit
        if len(user_requests) < self.max_requests:
            user_requests.append(current_time)
            return True
        
        return False

rate_limiter = RateLimiter()

def rate_limit(f):
    """Decorator to apply rate limiting to functions."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = kwargs.get('user_id', 'anonymous')
        
        if not rate_limiter.is_allowed(user_id):
            logger.warning(f"Rate limit exceeded for user {user_id}")
            return "Rate limit exceeded. Please wait before trying again."
        
        return f(*args, **kwargs)
    return decorated_function