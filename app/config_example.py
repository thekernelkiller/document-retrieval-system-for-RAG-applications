import redis

class Config:
    MONGO_URI = " "
    REDIS_HOST = " "
    REDIS_PORT = 19867
    REDIS_PASSWORD = " "
    NEWS_API_KEY = " "

    @staticmethod
    def get_redis_client():
        return redis.Redis(
            host=Config.REDIS_HOST,
            port=Config.REDIS_PORT,
            password=Config.REDIS_PASSWORD
        )
    
