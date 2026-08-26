"""v1 API package."""
from admin.api.v1 import auth, health
from admin.api.v1.org import departments, roles, users

__all = ["auth", "health", "departments", "roles", "users"]