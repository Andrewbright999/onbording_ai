from aiogram.dispatcher.middlewares.base import BaseMiddleware
from aiogram.fsm.context import FSMContext

class PrintStateMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        # Попытка получить FSMContext из словаря data
        state: FSMContext = data.get("state")
        if state:
            current_state = await state.get_state()
            user_id = data.get("event_from_user")  # или data.get("user_id")
            print(f"[Middleware] Current FSM state for user {user_id}: {current_state}")
        else:
            print("[Middleware] No FSM state available.")
        return await handler(event, data)

# class DebugUpdateMiddleware(BaseMiddleware):
#     async def __call__(
#         self,
#         handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
#         event: Update,
#         data: Dict[str, Any]
#     ) -> Any:
#         print(">>> RAW UPDATE:", event.dict())
#         return await handler(event, data)
