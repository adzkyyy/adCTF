import redis
import json
import os
from datetime import datetime, timedelta
from functools import wraps

class ScoreboardCache:
    def __init__(self):
        redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
        self.redis_client = redis.from_url(redis_url, decode_responses=True)
        self.cache_duration = 60  # Cache for 60 seconds
        self.scoreboard_key = "scoreboard:latest"
        self.last_update_key = "scoreboard:last_update"
        
    def get_cached_scoreboard(self):
        """Get cached scoreboard data"""
        try:
            # Check if cache exists and is still valid
            last_update = self.redis_client.get(self.last_update_key)
            if last_update:
                last_update_time = datetime.fromisoformat(last_update)
                if datetime.now() - last_update_time < timedelta(seconds=self.cache_duration):
                    cached_data = self.redis_client.get(self.scoreboard_key)
                    if cached_data:
                        return json.loads(cached_data)
            return None
        except Exception as e:
            print(f"Redis cache get error: {e}")
            return None
    
    def set_cached_scoreboard(self, scoreboard_data):
        """Cache scoreboard data"""
        try:
            # Set the scoreboard data
            self.redis_client.setex(
                self.scoreboard_key, 
                self.cache_duration + 10,  # Add 10 seconds buffer
                json.dumps(scoreboard_data)
            )
            
            # Set the last update timestamp
            self.redis_client.setex(
                self.last_update_key,
                self.cache_duration + 10,
                datetime.now().isoformat()
            )
            print(f"Scoreboard cached at {datetime.now()}")
        except Exception as e:
            print(f"Redis cache set error: {e}")
    
    def invalidate_scoreboard_cache(self):
        """Manually invalidate the scoreboard cache"""
        try:
            self.redis_client.delete(self.scoreboard_key)
            self.redis_client.delete(self.last_update_key)
            print("Scoreboard cache invalidated")
        except Exception as e:
            print(f"Redis cache invalidation error: {e}")
    
    def is_connected(self):
        """Check if Redis is connected"""
        try:
            self.redis_client.ping()
            return True
        except:
            return False

# Global cache instance
scoreboard_cache = ScoreboardCache()

def cache_scoreboard(func):
    """Decorator to cache scoreboard function"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Check if Redis is available
        if not scoreboard_cache.is_connected():
            print("Redis not available, executing function directly")
            return func(*args, **kwargs)
        
        # Try to get cached data
        cached_data = scoreboard_cache.get_cached_scoreboard()
        if cached_data is not None:
            print("Returning cached scoreboard data")
            return cached_data, 200
        
        # Execute function and cache result
        print("Generating fresh scoreboard data")
        result, status_code = func(*args, **kwargs)
        
        # Cache the result if successful
        if status_code == 200:
            scoreboard_cache.set_cached_scoreboard(result.get_json() if hasattr(result, 'get_json') else result)
        
        return result, status_code
    
    return wrapper