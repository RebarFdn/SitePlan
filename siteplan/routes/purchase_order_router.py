# project_inventory_router.py
from starlette.responses import HTMLResponse, RedirectResponse
from starlette_login.decorator import login_required
from starlette.background import BackgroundTask
from decoRouter import Router
from modules.project import get_project, update_project
from modules.inventory import InventoryItem, Supplier, stock_material, get_material_inventory, get_material_usage
from modules.utils import timestamp, exception_message
from config import TEMPLATES

router = Router()
