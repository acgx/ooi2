import os
from tornado.web import UIModule
from config import customize_dir


class Customize(UIModule):
    def render(self, name, default=''):
        mod_path = os.path.join(customize_dir, name+'.html')
        if os.path.exists(mod_path):
            f = open(mod_path, encoding='utf-8')
            content = f.read()
            f.close()
            return content
        else:
            return default
