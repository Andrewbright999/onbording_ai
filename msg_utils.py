from aiogram.types import InlineKeyboardButton, FSInputFile, CallbackQuery, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.media_group import MediaGroupBuilder

from Callbackfactory import InterestsCallbackFactory


# Сделать кнопку на клавиатуре с вызовом и удалением старого меню
# Сделать функцию редактирования и добавления рецептов

back_button = "🔙 Назад"
menu_button = "🔙 В меню"   
close_button = "❌Закрыть❌"


def get_callback_buttons_pref(btns: dict[str, str] | str, prefix: str = None):
    keyboard = InlineKeyboardBuilder()
    for data, text in btns.items():
        print(text)
        keyboard.add(InlineKeyboardButton(text=text,callback_data=prefix+"_"+data))
    # keyboard.add(InlineKeyboardButton(text=text,callback_data=prefix+back_button))
    return keyboard.adjust(1).as_markup()



def get_callback_buttons(btns: dict[str, str] | str):
    keyboard = InlineKeyboardBuilder()
    for text, data in btns.items():
        print(text)
        keyboard.add(InlineKeyboardButton(text=data,callback_data=text))
    keyboard.add(InlineKeyboardButton(text="Done ✅",callback_data="done_btn"))
    return keyboard.adjust(1).as_markup()


def get_callback_factory_buttons(btns: dict[str, dict] | str):
    keyboard = InlineKeyboardBuilder()
    for data, prop in btns.items():
        state = prop["state"]
        text = prop["text"]
        if state == 'on':
            text = "✔️ " + text
        keyboard.add(InlineKeyboardButton(text=text,
                             callback_data=InterestsCallbackFactory(interest = data, state=prop["state"]).pack()
                             ))
    keyboard.add(InlineKeyboardButton(text="Done ✅",callback_data="done_btn"))
    return keyboard.adjust(1).as_markup()




def get_album(photo_list: list[str] | str, caption: str):
    album_builder = MediaGroupBuilder(caption=caption)
    for photo in photo_list[:10]:
        album_builder.add_photo(media=FSInputFile(photo))
    return album_builder
 

    # photo_list = [
    #     FSInputFile("images/image1.png"),
    #     FSInputFile("images/image2.png")
    # ]

    # album_caption = "Добро пожаловать в наше сообщество! Вам зачислено 10 токенов."

    # if not photo_list:
    #     await message.answer(album_caption)
    # else:
    #     album_builder = MediaGroupBuilder(caption=album_caption)
    #     for photo in photo_list[:10]:
    #         album_builder.add_photo(media=photo)
    #     await message.answer_media_group(media=album_builder.build())
