import telebot
from telebot import types
import os

TOKEN = os.getenv("TOKEN")  # Railway/Render környezeti változó
bot = telebot.TeleBot(TOKEN)

# /start parancs
@bot.message_handler(func=lambda message: True)
def start(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton("⛽️", callback_data="run_calc")
    btn2 = types.InlineKeyboardButton("⏰", callback_data="run_other")
    markup.add(btn1, btn2)
    bot.send_message(message.chat.id, "Mit szeretnél futtatni?", reply_markup=markup)

# Callback kezelése
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "run_calc":
        bot.send_message(
            call.message.chat.id,
            "Kérlek, add meg az adatokat az alábbi sablon szerint, minden adatot **külön sorba írva**:\n\n"
            "Ledolgozott napok száma:\n"
            "Telephely oda-vissza:\n"
            "Fogyasztás:\n"
            "Gázolaj ára:"
        )
        bot.register_next_step_handler(call.message, calc)
    elif call.data == "run_other":
        bot.send_message(call.message.chat.id, "Jelenleg nem elérhető funkció.")

# Számolás funkció
def calc(message):
    try:
        data = message.text.strip().split('\n')
        if len(data) < 4:
            bot.reply_to(message, "Hibás adatbevitel. Kérlek pontosan 4 adatot adj meg, mindegyiket új sorba írva.")
            return

        dolgozottnap = int(data[0])
        tav = int(data[1])        # int marad
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
        bot.reply_to(message, "Hibás adatbevitel. Kérlek így add meg, minden adatot új sorba írva:\n\n"
                              "14\n20\n7\n718")

bot.polling()
