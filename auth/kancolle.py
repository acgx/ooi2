import re
import time
from urllib.parse import urlencode, urlparse, parse_qs
from tornado.gen import coroutine

from tornado.escape import native_str, json_decode
from tornado.curl_httpclient import CurlError
from tornado.httpclient import HTTPError
from utils.httpclient import AsyncHTTPClient

from config import proxy_host, proxy_port
from auth.exceptions import OoiAuthError
from auth import dmm


class KanColleAuth:
    user_agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko'
    connect_timeout = 30
    request_timeout = 60
    dmm_token_pattern = re.compile(r'"DMM_TOKEN", "([\d|\w]+)"')
    token_pattern = re.compile(r'"token": "([\d|\w]+)"')
    sesid_pattern = re.compile(r'INT_SESID=([^;]+);')
    osapi_url_pattern = re.compile(r'URL\W+:\W+"(.*)",')

    def __init__(self, login_id, password):
        self.login_id = login_id
        self.password = password
        self.http_client = AsyncHTTPClient()
        self.headers = {'User-Agent': self.user_agent}
        self.owner = 0

    @coroutine
    def _get_dmm_token(self):
        try:
            req = yield self.http_client.fetch(dmm.LOGIN_URL, headers=self.headers,
                                               connect_timeout=self.connect_timeout,
                                               request_timeout=self.request_timeout,
                                               proxy_host=proxy_host, proxy_port=proxy_port)
        except (CurlError, HTTPError):
            raise OoiAuthError('连接DMM网站失败')

        body = native_str(req.body)
        m = self.dmm_token_pattern.search(body)
        if m:
            dmm_token = m.group(1)
        else:
            raise OoiAuthError('获取DMM token失败')
        m = self.token_pattern.search(body)
        if m:
            token = m.group(1)
        else:
            raise OoiAuthError('获取token失败')

        return dmm_token, token

    @coroutine
    def _get_ajax_token(self, dmm_token, token):
        self.headers.update({'Origin': 'https://www.dmm.com',
                             'Referer': dmm.LOGIN_URL,
                             'Cookie': 'ckcy=1; check_open_login=1; check_down_login=1',
                             'DMM_TOKEN': dmm_token,
                             'X-Requested-With': 'XMLHttpRequest'})
        body = urlencode({'token': token})
        try:
            req = yield self.http_client.fetch(dmm.AJAX_TOKEN_URL, method='POST', headers=self.headers, body=body,
                                               connect_timeout=self.connect_timeout,
                                               request_timeout=self.request_timeout,
                                               proxy_host=proxy_host, proxy_port=proxy_port)
        except (CurlError, HTTPError):
            raise OoiAuthError('DMM网站AJAX请求失败')
        j = json_decode(native_str(req.body))
        return j['token'], j['login_id'], j['password']

    @coroutine
    def _get_osapi_url(self, ajax_token, login_id_key, password_key):
        del self.headers['DMM_TOKEN']
        del self.headers['X-Requested-With']
        body = urlencode({'login_id': self.login_id,
                          'password': self.password,
                          'token': ajax_token,
                          login_id_key: self.login_id,
                          password_key: self.password})
        req = yield self.http_client.fetch(dmm.AUTH_URL, method='POST', headers=self.headers, body=body,
                                           connect_timeout=self.connect_timeout, request_timeout=self.request_timeout,
                                           follow_redirects=False, raise_error=False,
                                           proxy_host=proxy_host, proxy_port=proxy_port)
        if req.code == 302:
            raw_cookie = req.headers.get('Set-Cookie')
            m = self.sesid_pattern.search(raw_cookie)
            if m:
                sesid = m.group(1)
            else:
                raise OoiAuthError('DMM用户session获取失败')
        elif req.code == 200:
            raise OoiAuthError('DMM用户认证失败，用户名或密码错误' if native_str(req.body).find(dmm.AJAX_TOKEN_URL) > 0 else 'DMM强制要求用户修改密码')
        else:
            raise OoiAuthError('连接DMM认证服务器失败')

        self.headers.update({'Cookie': 'ckcy=1; check_open_login=1; check_down_login=1; INT_SESID='+sesid,
                             'Referer': dmm.AUTH_URL})
        try:
            req = yield self.http_client.fetch(dmm.GAME_URL, headers=self.headers,
                                               connect_timeout=self.connect_timeout,
                                               request_timeout=self.request_timeout,
                                               proxy_host=proxy_host, proxy_port=proxy_port)
        except (CurlError, HTTPError):
            raise OoiAuthError('连接游戏服务器失败')
        m = self.osapi_url_pattern.search(native_str(req.body))
        if m:
            osapi_url = m.group(1)
        else:
            raise OoiAuthError('DMM强制要求用户修改密码')
        return osapi_url

    @coroutine
    def _get_world(self, osapi_url):
        qs = parse_qs(urlparse(osapi_url).query)
        owner = qs['owner'][0]
        self.owner = owner
        st = qs['st'][0]
        url = dmm.GET_WORLD_URL % (owner, int(time.time()*1000))
        self.headers['Referer'] = osapi_url
        try:
            req = yield self.http_client.fetch(url, headers=self.headers,
                                               connect_timeout=self.connect_timeout,
                                               request_timeout=self.request_timeout,
                                               proxy_host=proxy_host, proxy_port=proxy_port)
        except (CurlError, HTTPError):
            raise OoiAuthError('获取服务器ID失败')
        svdata = json_decode(native_str(req.body)[7:])
        if svdata['api_result'] == 1:
            world_id = svdata['api_data']['api_world_id']
        else:
            raise OoiAuthError('服务器ID错误')
        return world_id, st


    @coroutine
    def _get_api_token(self, world_id, st):
        world_ip = dmm.WORLD_IP[world_id-1]
        url = dmm.GET_FLASH_URL % (world_ip, self.owner, int(time.time()*1000))
        body = urlencode({'url': url,
                          'httpMethod': 'GET',
                          'authz': 'signed',
                          'st': st,
                          'contentType': 'JSON',
                          'numEntries': '3',
                          'getSummaries': 'false',
                          'signOwner': 'true',
                          'signViewer': 'true',
                          'gadget': 'http://203.104.209.7/gadget.xml',
                          'container': 'dmm'})
        try:
            req = yield self.http_client.fetch(dmm.MAKE_REQUEST_URL, method='POST', headers=self.headers, body=body,
                                               connect_timeout=self.connect_timeout,
                                               request_timeout=self.request_timeout,
                                               proxy_host=proxy_host, proxy_port=proxy_port)
        except (CurlError, HTTPError):
            raise OoiAuthError('连接api_token服务器失败')
        svdata = json_decode(native_str(req.body)[27:])
        if svdata[url]['rc'] != 200:
            raise OoiAuthError('获取api_token失败')
        svdata = json_decode(svdata[url]['body'][7:])
        if svdata['api_result'] != 1:
            raise OoiAuthError('获取api_token失败')
        return world_ip, svdata['api_token'], svdata['api_starttime']

    @coroutine
    def get_osapi(self):
        dmm_token, token = yield self._get_dmm_token()
        ajax_token, login_id_key, password_key = yield self._get_ajax_token(dmm_token, token)
        osapi_url = yield self._get_osapi_url(ajax_token, login_id_key, password_key)
        return osapi_url

    @coroutine
    def get_flash(self):
        osapi_url = yield self.get_osapi()
        world_id, st = yield self._get_world(osapi_url)
        world_ip, token, starttime = yield self._get_api_token(world_id, st)
        flash_url = dmm.FLASH_URL % (world_ip, token, starttime)
        return flash_url, world_ip, token, str(starttime), self.owner
