"""v1 API package."""
from admin.api.v1 import auth, health
from admin.api.v1.org import departments, roles, users
from admin.api.v1.knowledge import import_router, units

__all = ["auth", "health", "departments", "roles", "users", "import_router", "units"]