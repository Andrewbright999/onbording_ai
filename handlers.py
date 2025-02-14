import asyncio
from enum import Enum
from copy import deepcopy

from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import InlineKeyboardButton, Message, CallbackQuery, InlineKeyboardButton

from Callbackfactory import InterestsCallbackFactory

from database import (
    async_session,
    add_user,
    get_user_without_session,
    # update_user_state,
    # update_user_balance,
    # update_user_interests,
    # update_user_feedback
)

from msg_utils import get_album, get_callback_factory_buttons
from gpt_manager import validate_name, analyze_feedback, answer_question, get_context
from config import CHAT_LINK, BOT_TOKEN

router = Router()

# FSM состояния для регистрации
class Registration(StatesGroup):
    waiting_for_name = State()

# FSM состояния для обратной связи
class Feedback(StatesGroup):
    waiting_for_feedback = State()

# FSM состояния для вопросов
class Questions(StatesGroup):
    waiting_for_question = State()

# Пример enum для интересов
class InterestsEnum(Enum):
    WEB3 = "Web3"
    SAFE_TECHNOLOGY = "SAFE Technologies"
    DAO = "DAOs"
    TRADING = "Trading"
    AI = "AI"
    SMART_CONTRACTS = "Smart Contracts"
    FOOD = "Еда"
    GAMING = "Игры"
    SCIENCE = "Наука"



# Фабрика callback_data для интересов
intersts_dict = {i.name: {"text": i.value, 'state':'off'} for i in InterestsEnum}

hello_photo_list = ["images/image1.png","images/image2.png"]


@router.message(Command("start"))
async def start_handler(message: types.Message, state: FSMContext):
    user = await get_user_without_session(message.from_user.id)
    if not user:
        await add_user(
            message.from_user.id,
            message.from_user.username,
            message.from_user.first_name,
            message.from_user.last_name
        )
    
    album_caption = """```welcome
in our web3 community```

*This bot will help you:*
- Create and configure your wallet and accounts
- Understand smart contracts and blockchain
- It's better to join our community
- To answer your questions about web3

```But let's begin with an introduction. Can you tell me your name?```
"""

    # Отправляем альбом с фотографиями (или текст, если фотографий нет)
    if not hello_photo_list:
        await message.answer(album_caption)
    else:
        album = get_album(hello_photo_list, album_caption)
        await message.answer_media_group(media=album.build())

    # Устанавливаем FSM‑состояние
    await state.set_state(Registration.waiting_for_name)


@router.message(Registration.waiting_for_name)
async def process_name(message: types.Message, state: FSMContext):
    name = message.text.strip()
    is_valid = await validate_name(name)
    if not is_valid:
        await message.answer(
            "It doesn't seem like the right name. Please specify another name"
        )
        return
    
    user = await get_user_without_session(message.from_user.id)
    if user:
        user.first_name = name
    # Пример «логического» статуса в user.state (не путать с fsm_state):
    user.state = "Registered"
    user.balance += 10

    # Отправляем клавиатуру для перехода в чат
    button = InlineKeyboardButton(text="Join the chat", url=CHAT_LINK)
    keyboard = types.InlineKeyboardMarkup(row_width=2, inline_keyboard=[[button]])

    await message.answer(
        """*Nice to meet you!*
        
        ```click
on the button to join the chat.```""",
        reply_markup=keyboard
    )
    await state.clear()
    asyncio.create_task(schedule_interests(message))
    await state.set_state(Questions.waiting_for_question)


async def schedule_interests(message: Message):
    chat_id  = message.chat.id
    await asyncio.sleep(5)  # Через 5 сек
    # await asyncio.sleep(86400)  # Через сутки
    
    keyboard = get_callback_factory_buttons(intersts_dict)

    await message.bot.send_message(
        chat_id,
        """<pre class="language-welcome">
in our web3 community"""
        "Добрый день!\n\nУкажите ваши интересы:",
        reply_markup=keyboard
    )


@router.callback_query(InterestsCallbackFactory.filter())
async def interest_toggle(callback: CallbackQuery, callback_data: InterestsCallbackFactory, state: FSMContext):
    # Получаем текущее состояние интересов пользователя
    user_data = await state.get_data()
    person_intersts = user_data.get("interests", deepcopy(intersts_dict))

    # Обновляем состояние для текущего интереса
    interest = callback_data.interest
    current_state = callback_data.state
    if current_state == "off":
        new_state = 'on'
    else:
        new_state = "off"
    print(f"""BTN:{interest} OLD {current_state}, NEW {new_state}""")
    person_intersts[interest]["state"] = new_state
    keyboard = callback.message.reply_markup
    for row in keyboard.inline_keyboard:
        for button in row:
            data = button.callback_data.split(':')
            if len(data) == 3:
                state = data[-1]
                enum_interest = button.callback_data.split(':')[1]
                if (state == "on") & (enum_interest != interest):
                    person_intersts[enum_interest]["state"] = state

    # Создаем новую клавиатуру с обновленным состоянием
    new_keyboard = get_callback_factory_buttons(person_intersts)

    # Обновляем сообщение с новыми кнопками
    await callback.message.edit_text("Добрый день!\n\nУкажите ваши интересы:", reply_markup=new_keyboard)
    await callback.answer()


@router.callback_query(lambda c: c.data == "done_btn")
async def interests_done(callback: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    person_intersts = user_data.get("interests", deepcopy(intersts_dict))
    keyboard = callback.message.reply_markup
    for row in keyboard.inline_keyboard:
        for button in row:
            data = button.callback_data.split(':')
            if len(data) == 3:
                state = data[-1]
                enum_interest = button.callback_data.split(':')[1]
    # async with async_session() as session:
    #     user = await get_user_without_session(callback.from_user.id)
    #     if user:
    #         user.interests = interests_str
    #         user.balance += 10
    #         await session.commit()

    # Завершаем выбор интересов
    await callback.message.edit_reply_markup()
    await callback.message.answer("Отлично! Мы разделяем ваши увлечения. Вам зачислено 10 токенов.")


@router.message(Command("feedback"))
async def feedback_initiate(message: types.Message, state: FSMContext):
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        types.InlineKeyboardButton(text="Да", callback_data="feedback_yes"),
        types.InlineKeyboardButton(text="Нет", callback_data="feedback_no"),
    )
    await message.answer(
        "Хотим получить вашу обратную связь. Вам нравится в нашем сообществе?",
        reply_markup=keyboard
    )
    

@router.callback_query(lambda c: c.data in ["feedback_yes", "feedback_no"])
async def feedback_choice(callback: types.CallbackQuery, state: FSMContext):
    if callback.data == "feedback_yes":
        await callback.message.answer("Прекрасно! Расскажите, что именно понравилось.")
    else:
        await callback.message.answer("Давайте это исправим! Расскажите, что не понравилось.")
    await state.set_state(Feedback.waiting_for_feedback)
    await callback.answer()


@router.message(Feedback.waiting_for_feedback)
async def process_feedback(message: types.Message, state: FSMContext):
    feedback_text = message.text
    sentiment = await analyze_feedback(feedback_text)
    # async with async_session() as session:
        # await update_user_feedback(message.from_user.id, feedback_text, sentiment)
    await message.answer("Спасибо за ваш отзыв!")
    await state.clear()
    

# ---- Вопросы / GPT
@router.message(Command("ask"))
async def ask_command(message: types.Message, state: FSMContext):
    await message.answer("Задайте ваш вопрос:")
    await state.set_state(Questions.waiting_for_question)


@router.message(Questions.waiting_for_question)
async def process_question(message: types.Message, state: FSMContext):
    context = get_context()
    conversation_file = f"conversation_{message.from_user.id}.txt"
    try:
        with open(conversation_file, "r", encoding="utf-8") as f:
            conversation_context = f.read()
    except FileNotFoundError:
        conversation_context = ""
    conversation_context += f"\nUser: {message.text}"
    answer = await answer_question(message.text, context, conversation_context)
    with open(conversation_file, "w", encoding="utf-8") as f:
        f.write(conversation_context + f"\nBot: {answer}\n")
    await message.answer(answer)
    # await state.clear()
