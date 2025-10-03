from handlers.v1.admin import admin
from handlers.v1.admin.categories import add, delete, update
from handlers.v1.admin.products import add as add_product
from handlers.v1.admin.products import delete as delete_product
from handlers.v1.admin.products import update as update_product
from handlers.v1.cart import router as baskets
from handlers.v1.catalogs import router as catalogs
from handlers.v1.main_menu import router
from handlers.v1.orders import router as orders

routers = (
    router,
    admin.router,
    update.router,
    add.router,
    delete.router,
    add_product.router,
    delete_product.router,
    update_product.router,
    catalogs,
    baskets,
    orders,
)
