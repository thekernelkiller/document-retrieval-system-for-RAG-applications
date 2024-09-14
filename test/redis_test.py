from app.config import Config
import redis

def test_redis_connection():
    try:
        # Get Redis client
        redis_client = Config.get_redis_client()

        # Set a test key
        redis_client.set('test_key', 'Hello, Redis!')

        # Get the value
        value = redis_client.get('test_key')
        print(f"Retrieved value: {value.decode('utf-8')}")

        # Delete the test key
        redis_client.delete('test_key')

        print("Redis connection test successful!")
    except redis.exceptions.ConnectionError as e:
        print(f"Connection Error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    test_redis_connection()