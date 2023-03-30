#!/usr/bin/python3
import os

#local import
from main import web
from search import Search, SEARCH_URL
from edit import edit_web
from constant import *
from user import User

#test
from support import extracter

#foreign import
import telebot
from gtts import gTTS
from io import BytesIO

import sys
#import traceback

from flask import Flask, request
from pypinyin import pinyin
import requests
#import json

#constants
LANGUAGES = ['ru', 'en', 'cn']

#telebot.apihelper.proxy = {'https':PROXY}
server = Flask(__name__)

# Init Search class
srch = Search()

#bot = telebot.TeleBot(TOKEN,parse_mode='markdown')
bot = telebot.TeleBot(TOKEN, parse_mode='html')

# Setup proxy
if PROXY not in ('', ' '): telebot.apihelper.proxy = {'https': PROXY}

usr = User()

print('It started')


def query_lines():
	pass


# Retrieve translation
def get_text(user_id, text_message, mode=False):

	srch.whatlan(text_message)

	lan = usr.get_info(user_id, usr.lan)
	print(lan)
	#Return russion Translation
	if srch.language == "ru":
		webb = web(text_message)
		return webb.main()[:]

	# If language is not one of supported return not found
	if lan in LANGUAGES: result = srch.main(text_message, lan, mode)
	else: result = (None, None)

	if result[0] != None: text = "\n\n".join(result[0])
	else:
		text = LOCALIZATION[lan]['error'].format(SEARCH_URL + text_message,
		                                         text_message)

	return text, result[0]


def bt_assemble(text, date):
	return telebot.types.InlineKeyboardButton(text=text, callback_data=date)


# Admin Keyboard
def define_keyboard(char, lan='', admin=False):

	# button assemble
	create_button = lambda text, date: telebot.types.InlineKeyboardButton(
	 text=text, callback_data=date)

	buttons = []
	if admin:
		buttons.append(create_button('Edit', 'edit'))

	if lan != 'ru': buttons.append(create_button('Русский', f"{char}#ru"))
	if lan != 'en': buttons.append(create_button('English', f"{char}#en"))
	if lan != 'cn': buttons.append(create_button('中文', f"{char}#cn"))

	keyboard = telebot.types.InlineKeyboardMarkup(row_width=len(buttons))
	keyboard.add(*buttons)
	return keyboard


# Change language keyboard
def define_language_keyboard():
	buttons = []

	buttons.append(bt_assemble('Русский', 'ru'))
	buttons.append(bt_assemble('English', "en"))
	buttons.append(bt_assemble('中文', 'cn'))

	keyboard = telebot.types.InlineKeyboardMarkup(row_width=len(buttons))
	keyboard.add(*buttons)

	return keyboard


# Change language keyboard
def define_full_keyboard(char, page):
	print(f"{char}@{page}")
	keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
	button = telebot.types.InlineKeyboardButton(text='Expend',
	                                            callback_data=f"{char}@{page}")

	keyboard.add(*[button])

	return keyboard


# Change language keyboard
def define_back_keyboard(char, page):

	keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
	button = telebot.types.InlineKeyboardButton(text='Back',
	                                            callback_data=f"{char}&{page}")

	keyboard.add(*[button])

	return keyboard


# Change language init message
def change_language(message):
	keyboard = define_language_keyboard()
	message = long_message_request(message.from_user.id, "Choose your language",
	                               keyboard)


# Send a message request
def long_message_request(chat_id, text, keyboard=None):
	if len(text) > 4095:
		for x in range(0, len(text), 4095):
			bot.send_message(chat_id, text[x:x + 4095], disable_web_page_preview=True)
			print(text[x:x + 4095])
	else:
		return bot.send_message(chat_id,
		                        text,
		                        disable_web_page_preview=True,
		                        reply_markup=keyboard)


# Start command Handler
@bot.message_handler(commands=['start'])
def handle_start_tags(message):
	user_id = str(message.from_user.id)
	user_lan = message.from_user.language_code

	lan = user_lan if user_lan in ['en', 'ru'] else "en"
	usr.add_user(user_id, message.from_user.username,
	             message.from_user.first_name, lan)

	bot.send_message(message.chat.id,
	                 LOCALIZATION[usr.get_info(user_id, usr.lan)]['welcome'])
	pass


# Language command Handler
@bot.message_handler(commands=['language'])
def handle_language_tags(message):
	change_language(message)


#[word,pinyin,translation]
def fetchin(i):
	print(i)
	keyboard = None
	#keyboard=define_full_keyboard(i[0],i[3])
	return telebot.types.InlineQueryResultArticle(
	 i[3],
	 i[0],
	 description=i[1] + " " + i[2],
	 input_message_content=telebot.types.InputTextMessageContent(i[0] + "-" +
	                                                             i[1] + '-' +
	                                                             i[2] + "\n\n" +
	                                                             i[4]),
	 reply_markup=keyboard)


def inline_fetch(query_str, page=-2):
	exctar = extracter()
	result = exctar.main(query_str)
	pinyin_str = ''.join([i[0] for i in pinyin(query_str)])
	output = []
	print(result)
	n = 0
	for t in result[:]:
		for i in t['all_definitions'][:3]:
			n += 1
			definition = t['type'] + "| " + i['definition'] if t[
			 'type'] != None else str(n) + "| " + i['definition']
			if i['examples'] != None: examples = "\n".join(i['examples'][:3])
			else: examples = ''

			# for backwards function
			#if (page+1) == n:return [query_str, pinyin_str, definition,n,examples]

			output.append(fetchin([query_str, pinyin_str, definition, n, examples]))
	print(output)
	return output


def edit_message_back(call, char, page):
	user_id = str(call.from_user.id)
	chat_id = call.message.chat.id
	message_id = call.message.message_id

	result = inline_fetch(char, page)

	keyboard = define_full_keyboard(result[0], result[3])
	output = result[0] + "-" + result[1] + '-' + result[2] + "\n\n" + result[4]

	bot.edit_message_text(chat_id=chat_id,
	                      message_id=message_id,
	                      text=output,
	                      reply_markup=keyboard)


# Inline Handler
@bot.inline_handler(lambda query: len(query.query) != 0)
def query_text(inline_query):
	query_str = inline_query.query
	try:
		bot.answer_inline_query(inline_query.id, inline_fetch(query_str))
	except:
		print(sys.exc_info())

	pinyin_str = ''.join([i[0] for i in pinyin(query_str)])
	try:
		r = telebot.types.InlineQueryResultArticle(
		 '1',
		 query_str,
		 description=pinyin_str,
		 input_message_content=telebot.types.InputTextMessageContent(query_str +
		                                                             " " +
		                                                             pinyin_str))

		bot.answer_inline_query(inline_query.id, [r])
	except Exception as e:
		print(e)


# Handle all incomming text
@bot.message_handler(
 func=lambda q: q.from_user.is_bot == False and q.via_bot == None,
 content_types=['text'])
def handle_text_request(message):
	# Extract user main info
	user_id = str(message.from_user.id)
	text_message = message.text
	user_lan = usr.get_info(user_id, usr.lan)
	# define keyboard
	keyboard = None
	# Get message languge
	srch.whatlan(text_message)

	# Debbuging information
	print("User id", user_id, message.from_user.username, text_message, sep="\n")

	# Check if user in database
	if not usr.check_user(user_id): return change_language(message)

	# Admin and testers
	if user_id in TESTERS and srch.language not in ('en', 'ru'):
		keyboard = define_keyboard(message.text, user_lan)
		result = get_text(user_id, text_message, True)
	else:
		# Get text output
		result = get_text(user_id, text_message)

	print(result)

	# Print message to a user
	long_message_request(message.chat.id, result[0], keyboard)

	# Cancel audio generation in message language is not chinese
	if srch.language != 'cn': return
	if result[1] == None:
		fp = BytesIO()
		generated = gTTS(text_message, lang='zh')
		generated.write_to_fp(fp)
		fp.seek(0)
	else:
		fp = requests.get(result[1], headers=HEADER).content
	bot.send_voice(message.chat.id, fp)


# Handle call back: Change language
@bot.callback_query_handler(func=lambda call: call.data in ('en', 'ru', 'cn'))
def handle_Language_callback(call):
	try:
		user_id = str(call.from_user.id)
		chat_id = call.message.chat.id
		lan_code = call.from_user.language_code

		lan = lan_code if lan_code in ('ru', 'en', 'cn') else "en"

		usr.add_user(user_id, call.from_user.username, call.from_user.first_name,
		             lan)
		if usr.edit_info(user_id, usr.lan, call.data):
			print("Success")
			bot.edit_message_text(chat_id=call.message.chat.id,
			                      message_id=call.message.message_id,
			                      text="Language is updated")
			return

		long_message_request(chat_id, "Laguage is already set to " + call.data)
	except Exception as e:
		print(e)


# Handle call back: Switch message for other language source
@bot.callback_query_handler(func=lambda call: "#" in call.data)
def handle_edit_callback(call):
	#switch_lang = {'ru':'en','en':'ru'}

	user_id = str(call.from_user.id)
	chat_id = call.message.chat.id
	message_text = call.message.text

	char, lan = call.data.split('#')
	result = get_text(user_id, char, lan)
	keyboard = define_keyboard(char, lan)

	bot.edit_message_text(chat_id=chat_id,
	                      message_id=call.message.message_id,
	                      text=result[0],
	                      reply_markup=keyboard)


# Handle call back: Switch message for other language source
@bot.callback_query_handler(func=lambda call: "@" in call.data)
def handle_full_callback(call):

	user_id = str(call.from_user.id)

	#TODO solve this issue
	print(call)
	return
	chat_id = call.message.chat.id

	message_id = call.message.message_id

	print(call.data)

	char, page = call.data.split('@')
	result = get_text(user_id, char)
	print(result)
	keyboard = define_back_keyboard(char, page)

	bot.edit_message_text(chat_id=chat_id,
	                      message_id=message_id,
	                      text=result[0],
	                      reply_markup=keyboard)


# Handle call back: Switch message for other language source
@bot.callback_query_handler(func=lambda call: "&" in call.data)
def handle_full_callback(call):
	user_id = str(call.from_user.id)
	chat_id = call.message.chat.id
	char, page = call.data.split('&')
	edit_message_back(call, char, int(page))


# Handle call back: Edit message on a website
@bot.callback_query_handler(func=lambda call: "edit")
def handle_callback(call):
	chat_id = call.message.chat.id
	if str(chat_id) != ADMIN: return

	message = long_message_request(chat_id, "Write your message:")

	bot.register_next_step_handler(message=message, callback=next_message)


# Start message editing
def next_message(message):
	text = message.text
	lines = text.split('\n\n')
	if len(lines) != 3: return
	edit_web(lines[0], lines[1], lines[2])
	print(text)


# Flask accept
@server.route('/' + TOKEN, methods=['POST'])
def getMessage():
	json_string = request.get_data().decode('utf-8')
	update = telebot.types.Update.de_json(json_string)
	bot.process_new_updates([update])
	return "!", 200


# Flask setup hook
@server.route("/")
def webhook():
	print('debug')
	bot.remove_webhook()
	url = HOOK + TOKEN if HOOK[-1] == '/' else HOOK + "/" + TOKEN
	print(url)
	bot.set_webhook(url=url)
	return "!", 200


@server.teardown_appcontext
def teardown_appcontext(exception=None):
	usr.save()


if __name__ == "__main__":
	webhook()
	server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
	#bot.infinity_polling(interval=0, timeout=20)
