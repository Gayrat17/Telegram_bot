import asyncio
import logging
import sys
from csv import DictReader

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, InlineKeyboardButton, BotCommand, \
    BotCommandScopeAllPrivateChats, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import settings
from models.regions import Region, District

dp = Dispatcher()


class Form(StatesGroup):
    name = State()


def regions_btn():
    ikm = InlineKeyboardBuilder()
    text = Region.get_all()
    for region in text:
        ikm.add(InlineKeyboardButton(text=region.name, callback_data=f"region:{region.id}"))
    ikm.adjust(1)
    return ikm


def districts_btn(_id):
    districts = District.filter(region_id=_id)
    ikm = InlineKeyboardBuilder()
    for d in districts:
        ikm.row(InlineKeyboardButton(text=f"📍{d.name}", callback_data=f"district:{d.name}"),
                InlineKeyboardButton(text="✏️", callback_data=f"change_districts:{d.id}"),
                InlineKeyboardButton(text="❌", callback_data=f"remove_districts:{d.id}"))
    ikm.row(InlineKeyboardButton(text="⬅️ back", callback_data="back"))
    return ikm


@dp.message(CommandStart())
async def command_start(message: Message) -> None:
    ikm = regions_btn()
    await message.answer('Xush kelibsiz')
    await message.answer('Viloyatlar', reply_markup=ikm.as_markup())


@dp.callback_query(F.data.startswith("district:"))
async def callback_query_handler(callback: CallbackQuery):
    name = callback.data.removeprefix("district:")
    await callback.message.answer(f"{name}ni tanladingiz!")



@dp.callback_query(F.data.startswith("region:"))
async def region_handler(callback: CallbackQuery) -> None:
    _id = callback.data.removeprefix("region:")
    ikm = districts_btn(_id)
    await callback.message.edit_text("Tumanlardan birini tanlang:", reply_markup=ikm.as_markup())


@dp.callback_query(F.data == "back")
async def back_handler(callback: CallbackQuery):
    ikm = regions_btn()
    await callback.message.edit_text('Viloyatlar', reply_markup=ikm.as_markup())


@dp.callback_query(F.data.startswith("change_districts:"))
async def back_handler(callback: CallbackQuery, state: FSMContext):
    _id = callback.data.removeprefix("change_districts:")
    await state.update_data(districts_id=_id)
    await state.set_state(Form.name)
    await callback.message.answer("Yangi nom kiriting: ")


@dp.message(Form.name)
async def change_name_handler(message: Message, state: FSMContext):
    data = await state.get_data()
    District.update(data['districts_id'], name=message.text)
    await state.clear()
    await message.answer("Nomi o'zgardi", show_alert=True)


@dp.callback_query(F.data.startswith("remove_districts:"))
async def back_handler(callback: CallbackQuery):
    _id = callback.data.removeprefix("remove_districts:")
    district = District.delete(_id)
    await callback.answer(f"{district.name} bazadan o'chirildi", show_alert=True)
    ikm = districts_btn(district.region_id)
    await callback.message.edit_text('Tumanlar', reply_markup=ikm.as_markup())

@dp.message()
async def forward_to_admin(message: Message):
    user = message.from_user

    text = (
        f"📩 Yangi xabar!\n\n"
        f"👤 Ism: {user.full_name}\n"
        f"🆔 ID: {user.id}\n"
        f"📨 Xabar:\n{message.text}"
    )

    await message.bot.send_message(settings.ADMIN_ID, text)
    await message.forward(settings.ADMIN_ID)


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
    # await bot.set_my_description("🤖 My first bot!\n©️ Xushboqov G'ayratjon")
    await bot.set_my_commands([
        BotCommand(command='start', description='Boshlash'),
        BotCommand(command='migrate', description='Databasega yozish'),
        BotCommand(command='del', description='Ochirish uchun'),
        BotCommand(command='edit', description='ozgartirish uchun')
    ], scope=BotCommandScopeAllPrivateChats())
    await bot.send_message(settings.ADMIN_ID, 'bot started!')


async def shutdown(bot: Bot) -> None:
    await bot.send_message(settings.ADMIN_ID, 'bot stopped!')


async def main() -> None:
    bot = Bot(settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp.startup.register(startup)
    dp.shutdown.register(shutdown)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())