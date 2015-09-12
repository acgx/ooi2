import tornado.httpserver
import tornado.ioloop
import tornado.web
from ooi.handlers import MainHandler, NormalGameHandler, iFrameGameHandler, iFrameFlashHandler, PoiGameHandler
from auth.handlers import OsapiHandler, AuthHandler
from config import template_path, static_path, cookie_secret, debug
from ui import modules

application = tornado.web.Application(
    handlers=[('/', MainHandler),
              ('/kancolle', NormalGameHandler),
              ('/iframe', iFrameGameHandler),
              ('/flash', iFrameFlashHandler),
              ('/poi', PoiGameHandler),
              ('/osapi', OsapiHandler),
              ('/auth', AuthHandler), ],
    template_path=template_path,
    static_path=static_path,
    cookie_secret=cookie_secret,
    ui_modules=modules,
    debug=debug
)

if __name__ == "__main__":
    application.listen(80)
    tornado.ioloop.IOLoop.current().start()
