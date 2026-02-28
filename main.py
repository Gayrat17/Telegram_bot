import asyncio
import logging
import sys
from csv import DictReader

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.filters import CommandStart
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, InlineKeyboardButton, BotCommand, \
    BotCommandScopeAllPrivateChats
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import settings
from models.regions import Region, District


dp = Dispatcher()
ADMIN_ID = 1318702560


class Form(StatesGroup):
    first_name = State()
    birthday = State()
    image = State()


@dp.message(CommandStart())
async def command_start(message: Message) -> None:
    ikm = InlineKeyboardBuilder()
    text = Region.get_all()
    for region in text:
        ikm.add(InlineKeyboardButton(text=region.name, callback_data=f"region:{region.id}"))
    ikm.adjust(1)
    await message.answer('Xush kelibsiz')
    await message.answer('Viloyatlar', reply_markup=ikm.as_markup())


@dp.message(Command("migrate"))
async def migrate_command_handler(message: Message):
    with open('districts.csv', encoding='utf-8-sig') as d_file, open('regions.csv', encoding='utf-8-sig') as r_file:
        regions = DictReader(r_file)
        district = DictReader(d_file)
        for i in regions:
            data = {
                "id": int(i['id']),
                "name": i['name']
            }
            Region.create(**data)
        for i in district:
            data = {
                "id": int(i['id']),
                "name": i['name'],
                "region_id": i["region_id"]
            }
            District.create(**data)
    await message.answer("Viloyat va tumanlar muvaffaqiyatli qo'shildi!✅")


@dp.message(Command('del'))
async def command_start_handler(message: Message, bot: Bot) -> None:
    try:
        await bot.delete_messages(message.chat.id, list(range(message.message_id, 0, -1))[:99])
    except Exception as e:
        await message.answer(str(e))
    ikm = InlineKeyboardBuilder()
    ikm.add(InlineKeyboardButton(text='btn1', callback_data='123'))
    await message.answer('<b>Barcha</b> <i>xabarlar</i> <u>ochirildi</u>', reply_markup=ikm.as_markup())


@dp.message(Command('edit'))
async def command_start_handler(message: Message, bot: Bot) -> None:
    ikm = InlineKeyboardBuilder()
    ikm.add(InlineKeyboardButton(text='yangisi', callback_data='123'))

    await bot.edit_message_reply_markup(chat_id=message.chat.id, message_id=message.message_id - 1,
                                        reply_markup=ikm.as_markup())


async def startup(bot: Bot) -> None:
    await bot.set_my_commands([
        BotCommand(command='start', description='Boshlash'),
        BotCommand(command='migrate', description='Databasega yozish'),
        BotCommand(command='del', description='Ochirish uchun'),
        BotCommand(command='edit', description='ozgartirish uchun')
    ], scope=BotCommandScopeAllPrivateChats())
    await bot.send_message(ADMIN_ID, 'bot started!')


async def shutdown(bot: Bot) -> None:
    await bot.send_message(ADMIN_ID, 'bot stopped!')


async def main() -> None:
    bot = Bot(settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp.startup.register(startup)
    dp.shutdown.register(shutdown)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
