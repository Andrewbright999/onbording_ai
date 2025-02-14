import aioschedule, asyncio
from aiogram.types import Message

async def scheduler():
    aioschedule.every().day.at("23:04").do(sheduler_msg)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)

async def on_startup(dp):
    asyncio.create_task(scheduler())
    
async def sheduler_msg(message: Message, ):
    for user in [message.user.id]:
        await message.bot.send_message(chat_id = user, text = "отложенное сообщение")
        
        
