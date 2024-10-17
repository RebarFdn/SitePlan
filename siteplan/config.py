# Config file
import os
from pathlib import Path
from starlette.config import Config
from starlette.datastructures import CommaSeparatedStrings, Secret
from starlette.templating import Jinja2Templates
from modules.utils import convert_timestamp, to_dollars


# Directory Paths

PARENT_PATH = Path(__file__).parent.parent.parent
BASE_PATH = Path(__file__).parent.parent
HOME_PATH = Path(__file__).parent
STATIC_PATH = Path.joinpath(BASE_PATH, 'static')
TEMPLATE_PATH = Path.joinpath(BASE_PATH, 'templates')
DOCUMENT_PATH = Path.joinpath(STATIC_PATH, 'docs')
IMAGES_PATH = Path.joinpath(STATIC_PATH, 'imgs')
PROFILES_PATH = Path.joinpath(IMAGES_PATH, 'workers')

DATA_PATH = Path.joinpath(PARENT_PATH, 'siteplanData')

# File Paths
ENV_PATH = Path.joinpath(BASE_PATH, '.env') 

__config = Config(ENV_PATH)

# Application Specific Settings

DEBUG = True
DATABASE_URL = 'http://localhost:5984/'
SECRET_KEY = __config('SECRET_KEY',  cast=Secret)
DB_ADMIN  = __config('DB_ACCESS',  cast=Secret)
ADMIN_ACCESS  = __config('DB_SECRET',  cast=Secret)
APITALLY_CLIENT_TOKEN = __config('APITALLY_CLIENT_TOKEN')


# Network
ALLOWED_HOSTS = ['127.0.0.1', 'localhost']
PORT = 8004
HOST = '0.0.0.0'

# Templates Engine
TEMPLATES = Jinja2Templates(TEMPLATE_PATH)

# Logs
LOG_PATH = Path.joinpath(BASE_PATH, 'logs')
SYSTEM_LOG_PATH = Path.joinpath(LOG_PATH, 'system.log')
SERVER_LOG_PATH = Path.joinpath(LOG_PATH, 'server.log')
APP_LOG_PATH = Path.joinpath(LOG_PATH, 'app.log')


env = TEMPLATES.env
env.filters['to_dollars'] = to_dollars
env.filters['convert_timestamp'] = convert_timestamp