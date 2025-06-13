from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, Update
from ..utils.user_manager import user_manager

class AuthMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery | Update,
        data: Dict[str, Any]
    ) -> Any:
        # Get user_id based on event type
        user_id = None
        if isinstance(event, Message):
            user_id = event.from_user.id
        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id
        elif isinstance(event, Update):
            # For Update objects, we need to check what type of update it is
            if event.message:
                user_id = event.message.from_user.id
            elif event.callback_query:
                user_id = event.callback_query.from_user.id
            else:
                # If it's not a message or callback query, allow it
                return await handler(event, data)
        
        # If we couldn't get a user_id, allow the event
        if not user_id:
            return await handler(event, data)
        
        # Allow /start command for everyone
        if isinstance(event, Message) and event.text == "/start":
            return await handler(event, data)
        
        # Check authorization for all other commands
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

def register_middleware(dp):
    """Register the auth middleware with the dispatcher"""
    dp.update.middleware(AuthMiddleware()) 