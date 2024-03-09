import os

IS_PRODUCTION = os.environ.get('IS_PRODUCTION')

if IS_PRODUCTION:
    from .conf.prod.settings import *
else:
    from .conf.dev.settings import *
