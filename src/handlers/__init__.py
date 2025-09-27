from handlers.v1.admin import admin
from handlers.v1.admin.categories import add, delete, update
from handlers.v1.main_menu import router

routers = (router, admin.router, update.router, add.router, delete.router)
