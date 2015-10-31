import os

# Tornado settings
base_dir = os.path.abspath(os.path.dirname(__file__))
template_path = os.path.join(base_dir, 'templates')
static_path = os.path.join(base_dir, 'static')
cookie_secret = os.environ.get('OOI_SECRET', 'DEFAULT COOKIE SECRET FOR DEVELOPING')

# Redis setting
redis_host = os.environ.get('OOI_REDIS_HOST', '127.0.0.1')
redis_port = int(os.environ.get('OOI_REDIS_PORT', 6379))
redis_db = int(os.environ.get('OOI_REDIS_DB', 0))
redis_password = os.environ.get('OOI_REDIS_PASSWORD', None)

# Proxy settings
proxy_host = os.environ.get('OOI_PROXY_HOST', None)
proxy_port = int(os.environ.get('OOI_PROXY_PORT')) if os.environ.get('OOI_PROXY_PORT') else None

# Customized settings
customize_dir = os.path.join(base_dir, 'customize')

# result of api_start2
api_start2_path = '/srv/_kcs/api_start2.json'

# CDN
try:
    from customize.cdn import cdn_domains
except ImportError:
    cdn_domains = None
