import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from telebot import types
import os

TOKEN = os.getenv("TOKEN")  # Railway/Render környezeti változó
bot = telebot.TeleBot(TOKEN)

user_states = {}  # chat_id -> állapot pl. "waiting_for_location", "waiting_for_hours"
user_data = {}    # chat_id -> adatokat tárol (pl. helyszin, napok)

# Menü gombok emojival
def send_menu(chat_id):
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton("⛽️", callback_data="run_calc"),
        InlineKeyboardButton("🕰️", callback_data="run_other")
    )
    bot.send_message(chat_id, "Válassz egy opciót:", reply_markup=markup)

@bot.message_handler(commands=['start'])
def start_handler(message):
    send_menu(message.chat.id)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    chat_id = call.message.chat.id
    if call.data == "run_calc":
        bot.send_message(chat_id, "Add meg az adatokat egy sorban szóközzel elválasztva:\n"
                                  "Ledolgozott napok száma:\n"
                                  "Telephely oda-vissza:\n"
                                  "Fogyasztás:\n"
                                  "Gázolaj ára:")
        user_states[chat_id] = "waiting_for_calc_input"

    elif call.data == "run_other":
        user_states[chat_id] = "waiting_for_location"
        bot.send_message(chat_id, "Hol túlóráztál?")

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    chat_id = message.chat.id
    state = user_states.get(chat_id, None)

    if state == "waiting_for_calc_input":
        try:
            data = message.text.strip().split()
            if len(data) != 4:
                raise ValueError("Nem 4 adat van.")
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
            bot.send_message(chat_id, szoveg)
        except Exception:
            bot.send_message(chat_id, "Hibás adatbevitel. Kérlek, próbáld újra így:\n"
                                      "Ledolgozott napok száma:\n"
                                      "Telephely oda-vissza:\n"
                                      "Fogyasztás:\n"
                                      "Gázolaj ára:")
        finally:
            user_states.pop(chat_id, None)

    elif state == "waiting_for_location":
        user_data[chat_id] = {}
        user_data[chat_id]['helyszin'] = message.text.strip()
        user_states[chat_id] = "waiting_for_hours"
        bot.send_message(chat_id, "Melyik nap és hány órát dolgoztál? Add meg szóközzel elválasztva (pl. '15 1'), több napot új sorba írva is adhatsz meg.")

    elif state == "waiting_for_hours":
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
            return

        user_data[chat_id]['napok'] = napok
        helyszin = user_data[chat_id].get('helyszin', 'Ismeretlen hely')

        szoveg = f"Túlórák helyszíne: {helyszin}\nRögzített napok és órák:\n"
        for nap, mennyi in napok:
            szoveg += f" - {nap}. nap: {mennyi} óra\n"
        szoveg += f"Összes túlóra: {ossz_orak} óra"

        bot.send_message(chat_id, szoveg)

        # állapot törlése, mert kész vagyunk
        user_states.pop(chat_id, None)
        user_data.pop(chat_id, None)

    else:
        # Ha nincs állapot, ajánld fel újra a menüt
        send_menu(chat_id)


bot.infinity_polling()
