from flask import Blueprint

admin_bp = Blueprint(
    "admin",
    __name__,
    template_folder="../templates/admin",
    url_prefix="/admin"
)

# IMPORTANT: import routes AFTER blueprint creation
from admin import routes
from admin import dashboard
from admin import appointments
from admin import services
from admin import categories
from admin import analytics
from admin import booking
from admin import payments
from admin import products