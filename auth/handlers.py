from tornado.gen import coroutine
from tornado.escape import json_encode
from tornado.web import RequestHandler
from .kancolle import KanColleAuth
from .exceptions import OoiAuthError


class OsapiHandler(RequestHandler):
    @coroutine
    def post(self):
        login_id = self.get_argument('login_id')
        password = self.get_argument('password')
        if login_id and password:
            auth = KanColleAuth(login_id, password)
            try:
                osapi_url = yield auth.get_osapi()
                result = {'status': 1, 'osapi_url': osapi_url}
            except OoiAuthError as e:
                result = {'status': 0, 'message': e.message}
            self.set_header('Content-Type', 'application/json')
            self.write(json_encode(result))

        else:
            self.send_error(400)


class TokenHandler(RequestHandler):
    @coroutine
    def post(self):
        login_id = self.get_argument('login_id')
        password = self.get_argument('password')
        if login_id and password:
            auth = KanColleAuth(login_id, password)
            try:
                flash_url, world_ip, token, starttime, owner = yield auth.get_flash()
                result = {'status': 1,
                          'world_ip': world_ip,
                          'token': token,
                          'starttime': starttime,
                          'owner': owner}
            except OoiAuthError as e:
                result = {'status': 0, 'message': e.message}
            self.set_header('Content-Type', 'application/json')
            self.write(json_encode(result))

        else:
            self.send_error(400)
