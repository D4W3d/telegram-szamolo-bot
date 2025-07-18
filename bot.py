import telebot
from telebot import types
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
import os

TOKEN = os.getenv("TOKEN")  # Railway/Render környezeti változó
bot = telebot.TeleBot(TOKEN)

ser_data = {}  # ide mentjük a felhasználói adatokat

# 1-es gomb funkciója (számoló)
def calc(message):
    try:
        data = message.text.strip().split()
        dolgozottnap = int(data[0])
        tav = int(data[1])        # int
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
        bot.reply_to(message, "Hibás adatbevitel. Kérlek így add meg az adatokat, minden adatot külön sorba írva:\n\nLedolgozott napok száma:\nTelephely oda-vissza:\nFogyasztás:\nGázolaj ára:")

# 2-es gomb funkciója (túlóra kérdezés)
def ask_location(message):
    chat_id = message.chat.id
    user_data[chat_id] = {}
    user_data[chat_id]['helyszin'] = message.text.strip()
    bot.send_message(chat_id, "Melyik nap és hány órát dolgoztál? Add meg szóközzel elválasztva (pl. '15 1'), több napot új sorba írva is adhatsz meg.")
    bot.register_next_step_handler(message, ask_hours)

def ask_hours(message):
    chat_id = message.chat.id
    lines = message.text.strip().split('\n')
    napok = []
    ossz_orak = 0
    hibas_sorok = []
    
    for line in lines:
        parts = line.strip().split()
        if len(parts) != 2:
            hibas_sorok.append(line)
            continue
        try:
            nap = int(parts[0])
            mennyi = float(parts[1])
            napok.append((nap, mennyi))
            ossz_orak += mennyi
        except:
            hibas_sorok.append(line)
            
    if hibas_sorok:
        bot.send_message(chat_id, f"Hibás formátum a következő sor(ok)ban:\n" + "\n".join(hibas_sorok) + "\nKérlek, próbáld újra.")
        bot.register_next_step_handler(message, ask_hours)
        return
    
    user_data[chat_id]['napok'] = napok
    
    helyszin = user_data[chat_id].get('helyszin', 'Ismeretlen hely')
    szoveg = f"Túlórák helyszíne: {helyszin}\nRögzített napok és órák:\n"
    for nap, mennyi in napok:
        szoveg += f" - {nap}. nap: {mennyi} óra\n"
    szoveg += f"Összes túlóra: {ossz_orak} óra"
    
    bot.send_message(chat_id, szoveg)

# /start parancs - megjeleníti az inline gombokat
@bot.message_handler(commands=['start'])
def start(message):
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("⛽️", callback_data="run_calc"),  # 1-es gomb
        InlineKeyboardButton("🕰️", callback_data="run_other")  # 2-es gomb
    )
    bot.send_message(message.chat.id, "Válassz az alábbi lehetőségek közül:", reply_markup=keyboard)

# Callback query handler az inline gombokhoz
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "run_calc":
        bot.send_message(call.message.chat.id,
                         "Add meg az adatokat minden adatot külön sorba írva, így:\n\nLedolgozott napok száma:\nTelephely oda-vissza:\nFogyasztás:\nGázolaj ára:")
        bot.register_next_step_handler(call.message, calc)
    elif call.data == "run_other":
        bot.send_message(call.message.chat.id, "Hol túlóráztál?")
        bot.register_next_step_handler(call.message, ask_location)

# Ha üzenetet küldenek, amit nem tud kezelni, indítsa el az /start-ot
@bot.message_handler(func=lambda m: True)
def default_handler(message):
    bot.send_message(message.chat.id, "Kérlek, használd a /start parancsot a menühöz.")

# Bot indítása
bot.infinity_polling()
