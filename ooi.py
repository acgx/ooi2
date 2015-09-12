import tornado.httpserver
import tornado.ioloop
import tornado.web
from tornado.options import define, options
from ooi.handlers import MainHandler, NormalGameHandler, iFrameGameHandler, iFrameFlashHandler, \
    PoiGameHandler, ReloginHandler
from api.handlers import ApiHandler, MainSwfHandler, WorldImageHandler
from config import template_path, static_path, cookie_secret, debug
from ui import modules

application = tornado.web.Application(
    handlers=[('/', MainHandler),
              ('/kancolle', NormalGameHandler),
              ('/iframe', iFrameGameHandler),
              ('/flash', iFrameFlashHandler),
              ('/poi', PoiGameHandler),
              (r'/kcsapi/(.*)', ApiHandler),
              ('/kcs/mainD2.swf', MainSwfHandler),
              (r'/kcs/resources/image/world/.*(l|s)\.png', WorldImageHandler),
              ('/relogin', ReloginHandler), ],
    template_path=template_path,
    static_path=static_path,
    cookie_secret=cookie_secret,
    ui_modules=modules,
    debug=debug
)

define('port', type=int, default=8000)

if __name__ == "__main__":
    application.listen(options.port)
    tornado.ioloop.IOLoop.current().start()
