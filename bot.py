import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from telebot import types
import os

TOKEN = os.getenv("TOKEN")  # Railway/Render környezeti változó
bot = telebot.TeleBot(TOKEN)

user_states = {}  # chat_id -> állapot ("waiting_for_calc_input", "waiting_for_location", "waiting_for_hours", "waiting_for_car")
user_data = {}    # chat_id -> tárolt adatok: helyszin, napok, autok, kiválasztott rendszam

# Példa autók listája név + rendszám
auto_lista = [
    ("Audi", "ABC-123"),
    ("BMW", "XYZ-987"),
    ("Skoda", "QWE-456"),
]

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
    data = call.data

    if data == "run_calc":
        bot.send_message(chat_id, "Add meg az adatokat egy sorban szóközzel elválasztva:\n"
                                  "Ledolgozott napok száma:\n"
                                  "Telephely oda-vissza:\n"
                                  "Fogyasztás:\n"
                                  "Gázolaj ára:")
        user_states[chat_id] = "waiting_for_calc_input"

    elif data == "run_other":
        user_states[chat_id] = "waiting_for_location"
        bot.send_message(chat_id, "Hol túlóráztál?")

    elif data.startswith("car_select_") and user_states.get(chat_id) == "waiting_for_car":
        # pl: car_select_0, car_select_1 ...
        idx = int(data.split("_")[-1])
        if 0 <= idx < len(auto_lista):
            rendszam = auto_lista[idx][1]
            user_data[chat_id]['rendszam'] = rendszam

            helyszin = user_data[chat_id].get('helyszin', 'Ismeretlen hely')
            napok = user_data[chat_id].get('napok', [])
            ossz_orak = sum(ora for _, ora in napok)

            # formázzuk a napokat a megadott formában: 15 (2h), 16 (1h)
            napok_str = ", ".join(f"{nap} ({ora}h)" for nap, ora in napok)

            vegso_uzenet = (
                f"{helyszin}\n"
                f"{napok_str}\n"
                f"Összesen: {ossz_orak} óra\n"
                f"Autó: {rendszam}"
            )
            bot.send_message(chat_id, vegso_uzenet)

            # állapot törlése
            user_states.pop(chat_id, None)
            user_data.pop(chat_id, None)

        else:
            bot.send_message(chat_id, "Érvénytelen választás, kérlek válassz újra.")

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
        hibas_sorok = []

        for line in lines:
            parts = line.strip().split()
            if len(parts) != 2:
                hibas_sorok.append(line)
                continue
            try:
                nap = int(parts[0])
                mennyi = int(parts[1])
                napok.append((nap, mennyi))
            except:
                hibas_sorok.append(line)

        if hibas_sorok:
            bot.send_message(chat_id, f"Hibás formátum a következő sor(ok)ban:\n" + "\n".join(hibas_sorok) + "\nKérlek, próbáld újra.")
            return

        user_data[chat_id]['napok'] = napok
        user_states[chat_id] = "waiting_for_car"

        # Küldd el az autók listáját inline gombokkal (számokkal)
        markup = InlineKeyboardMarkup()
        for i, (nev, rendszam) in enumerate(auto_lista):
            szoveg = f"{i+1} {nev} {rendszam}"
            markup.add(InlineKeyboardButton(szoveg, callback_data=f"car_select_{i}"))

        bot.send_message(chat_id, "Melyik autóval voltál ott? Válassz az alábbi listából:", reply_markup=markup)

    else:
        send_menu(chat_id)

bot.infinity_polling()
