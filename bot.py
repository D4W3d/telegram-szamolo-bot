import telebot
from telebot import types
import os

TOKEN = os.getenv("TOKEN")  # Állítsd be Render/Railway-en környezeti változóként
bot = telebot.TeleBot(TOKEN)

# /start parancs
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton("1️⃣ Számolás", callback_data="run_calc")
    btn2 = types.InlineKeyboardButton("2️⃣ Másik funkció", callback_data="run_other")
    markup.add(btn1, btn2)
    bot.send_message(message.chat.id, "Mit szeretnél futtatni?", reply_markup=markup)

# Callback kezelése
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "run_calc":
        bot.send_message(call.message.chat.id, "Add meg az adatokat szóközzel elválasztva az alábbi formátumban:\n\n14 20 7 718")
        bot.register_next_step_handler(call.message, calc)
    elif call.data == "run_other":
        bot.send_message(call.message.chat.id, "Jelenleg nem elérhető funkció.")

# Számolás funkció
def calc(message):
    try:
        data = message.text.strip().split()
        dolgozottnap = int(data[0])
        tav = int(data[1])        # int-re javítva
        fogy = float(data[2])
        ar = int(data[3])

        ossz_tav = dolgozottnap * tav * 2
        uzemanyag_koltseg = ossz_tav / 100 * fogy * ar

        szoveg = (
            f"Ledolgozott napok száma: {dolgozottnap}\n"
            f"Telephely oda-vissza: {tav*2} km\n"
            f"Összesen: {ossz_tav} km\n"
            f"Fogyasztás: {fogy} l/100km\n"
            f"Gázolaj ára: {ar} Ft/l\n"
            f"Üzemanyag költség összesen: {round(uzemanyag_koltseg)} Ft"
        )
        bot.reply_to(message, szoveg)
    except Exception as e:
        bot.reply_to(message, "Hibás adatbevitel. Kérlek így add meg:\n14 20 7 718")

bot.polling()
