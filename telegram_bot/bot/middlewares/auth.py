from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from ..utils.user_manager import user_manager

class AuthMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        # Allow /start command for everyone
        if isinstance(event, Message) and event.text == "/start":
            return await handler(event, data)
        
        # Check authorization for all other commands
        user_id = event.from_user.id
        if not user_manager.is_authorized(user_id):
            if isinstance(event, Message):
                await event.answer(
                    "⚠️ You are not authorized. Please use /start and enter the password.",
                    show_alert=True
                )
            elif isinstance(event, CallbackQuery):
                await event.answer(
                    "⚠️ You are not authorized. Please use /start and enter the password.",
                    show_alert=True
                )
            return
        
        return await handler(event, data) 