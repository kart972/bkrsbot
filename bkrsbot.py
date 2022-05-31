#!/usr/bin/python3
import os

import telebot
from constant import TOKEN, PROXY
from main import web
from flask import Flask, request


#telebot.apihelper.proxy = {'https':PROXY}

server = Flask(__name__)
bot = telebot.TeleBot(TOKEN,parse_mode='HTML')

print('It started')


@bot.message_handler(commands=['start'])
def handle_tags(message):
	pass

@bot.message_handler(content_types=['text'])
def handle_docs_text(message):
	webb = web(message.text)
	print(webb.url)
	localmsg = webb.main()
	bot.send_message(message.chat.id,localmsg,disable_web_page_preview=True)

@server.route('/' + TOKEN, methods=['POST'])
def getMessage():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200


@server.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url='https://peaceful-bastion-48701.herokuapp.com/' + TOKEN)
    return "!", 200


if __name__ == "__main__":
    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
