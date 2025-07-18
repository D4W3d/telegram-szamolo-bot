import telebot
import os

TOKEN = os.getenv("TOKEN")
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Kérlek add meg az adatokat az alábbi formában:\n\n"
                           "dolgozottnap tav fogy ar\n\n"
                           "Példa:\n14 20 7 718")

@bot.message_handler(func=lambda m: True)
def calc(message):
    try:
        data = message.text.strip().split()
        dolgozottnap = int(data[0])
        tav = int(data[1])
        fogy = float(data[2])
        ar = int(data[3])

        ossz_tav = dolgozottnap * tav * 2
        uzemanyag_koltseg = ossz_tav / 100 * fogy * ar

        szoveg = (
            f"Ledolgozott napok száma: {dolgozottnap}"\n
            f"Telephely oda-vissza: {tav*2} km"\n
            f"Összesen: {ossz_tav} km"\n
            f"Fogyasztás: {fogy} l/100km"\n
            f"Gázolaj ára: {ar} Ft/l"\n
            f"Üzemanyag költség összesen: {round(uzemanyag_koltseg)} Ft"
        )
        bot.send_message(message.chat.id, szoveg)
    except Exception as e:
        bot.reply_to(message, "Hibás adatbevitel. Kérlek így add meg:\n14 20 7 718")

bot.polling()
