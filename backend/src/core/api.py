from ninja_extra import NinjaExtraAPI
from ninja_jwt.controller import NinjaJWTDefaultController

from users.api import router as users_router

api = NinjaExtraAPI()

api.add_router("/users/", users_router)

api.register_controllers(NinjaJWTDefaultController)