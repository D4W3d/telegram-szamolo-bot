import os
import telebot

TOKEN = os.getenv('TOKEN')
bot = telebot.TeleBot(TOKEN)

user_data = {}

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Add meg a ledolgozott napok számát:")
    bot.register_next_step_handler(message, get_dolgozottnap)

def get_dolgozottnap(message):
    try:
        user_data['dolgozottnap'] = int(message.text)
        bot.reply_to(message, "Add meg a telephely oda-vissza távot (km):")
        bot.register_next_step_handler(message, get_tav)
    except:
        bot.reply_to(message, "Kérlek számot adj meg. Próbáld újra.")
        bot.register_next_step_handler(message, get_dolgozottnap)

def get_tav(message):
    try:
        user_data['tav'] = float(message.text)
        bot.reply_to(message, "Add meg a fogyasztást (l/100km):")
        bot.register_next_step_handler(message, get_fogy)
    except:
        bot.reply_to(message, "Kérlek számot adj meg. Próbáld újra.")
        bot.register_next_step_handler(message, get_tav)

def get_fogy(message):
    try:
        user_data['fogy'] = float(message.text)
        bot.reply_to(message, "Add meg a gázolaj árát (Ft/l):")
        bot.register_next_step_handler(message, get_ar)
    except:
        bot.reply_to(message, "Kérlek számot adj meg. Próbáld újra.")
        bot.register_next_step_handler(message, get_fogy)

def get_ar(message):
    try:
        user_data['ar'] = int(message.text)

        dolgozottnap = user_data['dolgozottnap']
        tav = user_data['tav']
        fogy = user_data['fogy']
        ar = user_data['ar']

        ossz_tav = dolgozottnap * tav
        uzemanyag_koltseg = (ossz_tav / 100) * fogy * ar

        szoveg = (
            f"Ledolgozott napok száma: {dolgozottnap}\\n"
            f"Telephely oda-vissza: {tav:.2f} km\\n"
            f"Összesen: {ossz_tav:.2f} km\\n"
            f"Fogyasztás: {fogy:.2f} l/100km\\n"
            f"Gázolaj ára: {ar} Ft/l\\n"
            f"Üzemanyag költség összesen: {uzemanyag_koltseg:.0f} Ft"
        )

        bot.send_message(message.chat.id, szoveg)

    except Exception as e:
        bot.reply_to(message, "Hiba történt, próbáld újra.")
        print(e)

bot.polling()
