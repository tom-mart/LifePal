from ninja_extra import NinjaExtraAPI
from ninja_jwt.controller import NinjaJWTDefaultController
from ninja_jwt.authentication import JWTAuth

from chat.api import router as chat_router

api = NinjaExtraAPI()

api.register_controllers(NinjaJWTDefaultController)

api.add_router("/chat/", chat_router, auth=JWTAuth())