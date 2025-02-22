import unittest
import time
from utils.rate_limiter import RateLimiter

class TestRateLimiter(unittest.TestCase):
    def setUp(self):
        self.rate_limiter = RateLimiter(max_requests=2, time_window=1)
    
    def test_within_limit(self):
        """Test requests within rate limit"""
        self.assertTrue(self.rate_limiter.is_allowed("test_user"))
        self.assertTrue(self.rate_limiter.is_allowed("test_user"))
        
    def test_exceeds_limit(self):
        """Test requests exceeding rate limit"""
        self.assertTrue(self.rate_limiter.is_allowed("test_user"))
        self.assertTrue(self.rate_limiter.is_allowed("test_user"))
        self.assertFalse(self.rate_limiter.is_allowed("test_user"))
        
    def test_window_reset(self):
        """Test rate limit reset after time window"""
        self.assertTrue(self.rate_limiter.is_allowed("test_user"))
        self.assertTrue(self.rate_limiter.is_allowed("test_user"))
        self.assertFalse(self.rate_limiter.is_allowed("test_user"))
        
        # Wait for window to reset
        time.sleep(1)
        self.assertTrue(self.rate_limiter.is_allowed("test_user"))

if __name__ == '__main__':
    unittest.main()