import telebot
from telebot import types
import os

TOKEN = os.getenv("TOKEN")  # Állítsd be környezeti változóként Render/Railway-en
bot = telebot.TeleBot(TOKEN)

# /start parancs
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton("⛽️", callback_data="run_calc")
    btn2 = types.InlineKeyboardButton("🕓", callback_data="run_other")
    markup.add(btn1, btn2)
    bot.send_message(message.chat.id, "Mit szeretnél futtatni?", reply_markup=markup)

# Callback kezelése
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "run_calc":
        bot.send_message(
            call.message.chat.id,
            "Kérlek, add meg az adatokat az alábbi sablon szerint, minden adatot **k**
