# db_fsm_storage.py
from typing import Any, Dict, Optional
from aiogram.fsm.storage.base import BaseStorage, StorageKey
from database import async_session, get_user, update_user_state
from handlers import Registration, Feedback, Questions  # импортируем ваши FSM группы

class DBFSMStorage(BaseStorage):
    async def close(self) -> None:
        pass

    async def wait_closed(self) -> None:
        pass

    async def get_state(self, key: StorageKey) -> Optional[str]:
        async with async_session() as session:
            user = await get_user(session=session, user_id=key.user_id)
            if user and user.state and user.state != "Fine State":
                stored = user.state  # например, "Registration:waiting_for_name"
                # Преобразуем сохранённую строку в нужное состояние:
                if stored == str(Registration.waiting_for_name):
                    return Registration.waiting_for_name
                elif stored == str(Feedback.waiting_for_feedback):
                    return Feedback.waiting_for_feedback
                elif stored == str(Questions.waiting_for_question):
                    return Questions.waiting_for_question
                return stored  # на случай, если состояние не распознано
            return None

    async def set_state(self, key: StorageKey, state: Optional[str]) -> None:
        async with async_session() as session:
            # Приводим состояние к строке, если оно задано
            await update_user_state(session=session, user_id=key.user_id, new_state = str(state) if state is not None else None)

    async def get_data(self, key: StorageKey) -> Dict[str, Any]:
        return {}

    async def update_data(self, key: StorageKey, data: Dict[str, Any]) -> None:
        pass

    async def set_data(self, key: StorageKey, data: Dict[str, Any]) -> None:
        pass

    async def reset_state(self, key: StorageKey, with_data: bool = True) -> None:
        await self.set_state(key, None)
