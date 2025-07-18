import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from telebot import types
import os

TOKEN = os.getenv("TOKEN")  # Railway/Render környezeti változó
bot = telebot.TeleBot(TOKEN)

user_states = {}
user_data = {}

auto_lista = [
    ("Név1", "ABC-123"),
    ("Név2", "XYZ-789"),
    ("Név3", "DEF-456"),
]

# Kezdő üzenet, inline gombokkal
def send_welcome(chat_id):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("⛽ Üzemanyag", callback_data="option_1"))
    markup.add(InlineKeyboardButton("🕰️ Túlóra", callback_data="option_2"))
    bot.send_message(chat_id, "Válassz egy opciót:", reply_markup=markup)
    user_states[chat_id] = "waiting_for_option"

@bot.message_handler(commands=['start'])
def start_handler(message):
    send_welcome(message.chat.id)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    chat_id = call.message.chat.id

    if call.data == "option_1":
        user_states[chat_id] = "waiting_for_calc_data"
        bot.send_message(chat_id, "Add meg az adatokat szóközzel elválasztva (pl. 14 20 7 718):")
        bot.answer_callback_query(call.id)
    elif call.data == "option_2":
        user_states[chat_id] = "waiting_for_location"
        user_data[chat_id] = {}
        bot.send_message(chat_id, "Hol túlóráztál?")
        bot.answer_callback_query(call.id)

    elif call.data.startswith("car_select_"):
        if chat_id not in user_data or 'napok' not in user_data[chat_id]:
            bot.send_message(chat_id, "Valami hiba történt, kérlek indítsd újra a folyamatot /start parancsal.")
            return
        idx = int(call.data.split("_")[-1])
        if idx < 0 or idx >= len(auto_lista):
            bot.send_message(chat_id, "Érvénytelen autó választás.")
            return

        rendszam = auto_lista[idx][1]
        helyszin = user_data[chat_id].get("helyszin", "Ismeretlen helyszín")
        napok = user_data[chat_id]['napok']
        osszes_ora = sum(ora for _, ora in napok)

        # Formázott napok szöveg: pl. 15 (2h), 16 (1h)
        napok_szoveg = ", ".join(f"{nap} ({ora}h)" for nap, ora in napok)

        szoveg = (
            f"{helyszin}\n"
            f"Napok: {napok_szoveg}\n"
            f"Összesen: {osszes_ora} óra\n"
            f"Autó: {rendszam}"
        )
        bot.send_message(chat_id, szoveg)
        # Vége a folyamatnak, töröljük az állapotot
        user_states.pop(chat_id, None)
        user_data.pop(chat_id, None)
        bot.answer_callback_query(call.id)

@bot.message_handler(func=lambda message: True)
def message_handler(message):
    chat_id = message.chat.id
    state = user_states.get(chat_id)

    if state == "waiting_for_calc_data":
        try:
            data = message.text.strip().split()
            if len(data) != 4:
                raise ValueError
            dolgozottnap = int(data[0])
            tav = int(data[1])
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
        except:
            bot.reply_to(message, "Hibás adatbevitel. Kérlek így add meg:\nLedolgozott napok száma:\nTelephely oda-vissza:\nFogyasztás:\nGázolaj ára:")
        user_states.pop(chat_id, None)

    elif state == "waiting_for_location":
        helyszin = message.text.strip()
        if not helyszin:
            bot.send_message(chat_id, "Kérlek, írd be hol túlóráztál!")
            return
        user_data[chat_id]['helyszin'] = helyszin
        user_states[chat_id] = "waiting_for_hours"
        bot.send_message(chat_id, "Add meg a napokat és az órákat szóközzel elválasztva, soronként! Például:\n15 1\n16 2\n")

    elif state == "waiting_for_hours":
        lines = message.text.strip().split('\n')
        napok = []
        hibas_sorok = []

        for line in lines:
            parts = line.strip().split()
            if len(parts) != 2:
                hibas_sorok.append(line)
                continue
            try:
                nap = int(parts[0])
                mennyi = int(parts[1])  # egész szám
                napok.append((nap, mennyi))
            except:
                hibas_sorok.append(line)

        if hibas_sorok:
            bot.send_message(chat_id, f"Hibás formátum a következő sor(ok)ban:\n" + "\n".join(hibas_sorok) + "\nKérlek, próbáld újra.")
            return

        user_data[chat_id]['napok'] = napok
        user_states[chat_id] = "waiting_for_car"

        # Autók listája inline gombokkal
        markup = InlineKeyboardMarkup()
        for i, (nev, rendszam) in enumerate(auto_lista):
            szoveg = f"{i+1} {nev} {rendszam}"
            markup.add(InlineKeyboardButton(szoveg, callback_data=f"car_select_{i}"))

        bot.send_message(chat_id, "Melyik autóval voltál ott?", reply_markup=markup)

    else:
        send_welcome(chat_id)

if __name__ == '__main__':
    print("Bot fut...")
    bot.infinity_polling()
