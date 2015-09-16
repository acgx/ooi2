from session.redis import OoiRedis
from utils.convert import to_str


class OoiSession:
    redis = OoiRedis

    def _get_name(self, owner):
        return 'kcu:%s' % owner

    def _get_user(self, owner):
        return self.redis.hgetall(self._get_name(owner))

    def create_user(self, owner, token, starttime, world_ip, member_id=None, nickname=None):
        self.redis.hmset(self._get_name(owner), {'token': token,
                                                 'starttime': starttime,
                                                 'world_ip': world_ip,
                                                 'member_id': member_id,
                                                 'nickname': nickname})
        return True

    def get_user(self, owner, token, starttime):
        user = self._get_user(owner)
        if user and token == to_str(user.get(b'token')) and starttime == to_str(user.get(b'starttime')):
            return user
        else:
            return None

    def update_user(self, owner, member_id, nickname):
        user = self._get_user(owner)
        if user:
            self.redis.hmset(self._get_name(owner), {'member_id': member_id, 'nickname': nickname})
            return True
        else:
            return False

    def delete_user(self, owner, token, starttime):
        user = self.get_user(owner, token, starttime)
        if user:
            self.redis.delete(self._get_name(owner))
            return True
        else:
            return False
