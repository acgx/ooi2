import os

# Tornado directories
base_dir = os.path.abspath(os.path.dirname(__file__))
template_path = os.path.join(base_dir, 'templates')
static_path = os.path.join(base_dir, 'static')

# Tornado Settings
cookie_secret = os.environ.get('OOI_SECRET', 'DEFAULT COOKIE SECRET FOR DEVELOPING')
debug = bool(os.environ.get('OOI_DEBUG', False))

# Proxy settings
proxy_host = os.environ.get('OOI_AUTH_PROXY_HOST', None)
proxy_port = int(os.environ.get('OOI_AUTH_PROXY_PORT')) if os.environ.get('OOI_AUTH_PROXY_PORT') else None
