from aiogram.filters.callback_data import CallbackData

class InterestsCallbackFactory(CallbackData, prefix="interest"):
    interest: str
    state: str