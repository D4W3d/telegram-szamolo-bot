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
        user_data = {}

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
            nap = int(parts[0])       # hónap hányadik napja
            mennyi = float(parts[1])  # hány órát
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
    szoveg = f"Túlórák helyszíne: {helyszin}\n"
    szoveg += "Rögzített napok és órák:\n"
    for nap, mennyi in napok:
        szoveg += f" - {nap}. nap: {mennyi} óra\n"
    szoveg += f"Összes túlóra: {ossz_orak} óra"
    
    bot.send_message(chat_id, szoveg)

# A callback handler résznél (a 2-es gombhoz):

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "run_calc":
        # Itt az 1-es gombhoz tartozó kódod (számoló funkció)
        pass  # vagy tedd be a kódod ide
    
    elif call.data == "run_other":
        chat_id = call.message.chat.id
        bot.send_message(chat_id, "Hol túlóráztál?")
        bot.register_next_step_handler(call.message, ask_location)


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
