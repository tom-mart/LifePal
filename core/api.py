from ninja_extra import NinjaExtraAPI
from ninja_jwt.controller import NinjaJWTDefaultController
from ninja_jwt.authentication import JWTAuth

from chat.api import router as chat_router
from notifications.api import router as notifications_router

api = NinjaExtraAPI()

api.register_controllers(NinjaJWTDefaultController)

api.add_router("/chat/", chat_router, auth=JWTAuth())
api.add_router("/notifications/", notifications_router, auth=JWTAuth())