from ninja_extra import NinjaExtraAPI
from ninja_jwt.controller import NinjaJWTDefaultController

from users.api import router as users_router
from todo.api import router as todo_router
from llm_chat.api import router as chat_router
from notifications.api import router as notifications_router

api = NinjaExtraAPI()

api.add_router("/users/", users_router)
api.add_router("/todo/", todo_router)
api.add_router("/chat/", chat_router)
api.add_router("/notifications/", notifications_router)

api.register_controllers(NinjaJWTDefaultController)