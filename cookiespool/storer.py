# -*- coding: utf-8 -*-

import redis
from cookiespool import settings
import random


class RedisClient(object):
    def __init__(self, type_, website, host=settings.REDIS_HOST,
                 port=settings.REDIS_PORT, pwd=settings.REDIS_PWD):
        self.redis = redis.Redis(host=host, port=port, password=pwd)
        self.type = type_
        self.website = website
        self.hash_name = self.get_hash_name()

    def get_hash_name(self):
        name = '{type}:{website}'.format(type=self.type, website=self.website)
        print("hash名字为: {name}".format(name=name))
        return name

    def set_value(self, user_name, value):
        return self.redis.hset(self.hash_name, name=user_name, value=value)

    def get_value(self, user_name):
        return self.redis.hget(self.hash_name, name=user_name)

    def del_key_value(self, user_name):
        return self.redis.hdel(self.hash_name, name=user_name)

    def get_hash_lens(self):
        return self.redis.hlen(self.hash_name)

    def get_cookies_random(self):
        if 'cookies' in self.get_hash_name():
            return random.choice(self.redis.hvals(self.hash_name))
        else:
            print("非获取cookies对象")
            return None

    def get_all_user_name(self):
        return self.redis.hkeys(self.hash_name)

    def get_all_key_value(self):
        return self.redis.hgetall(self.hash_name)

