import redis

from config import redis_host, redis_port, redis_db, redis_password

OoiRedis = redis.StrictRedis(redis_host, redis_port, redis_db, redis_password)
