import tornado.httpserver
import tornado.ioloop
import tornado.web
from auth.handlers import OsapiHandler, AuthHandler
from config import template_path, static_path, cookie_secret, debug

application = tornado.web.Application(
    handlers=[('/osapi', OsapiHandler),
              ('/auth', AuthHandler), ],
    template_path=template_path,
    static_path=static_path,
    cookie_secret=cookie_secret,
    debug=debug
)

if __name__ == "__main__":
    application.listen(8000)
    tornado.ioloop.IOLoop.current().start()
