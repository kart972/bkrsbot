#!/usr/bin/python3
import os

#local import
from main import web
from search import Search, SEARCH_URL
from edit import edit_web
from constant import TOKEN, ADMIN, WELCOME, HEADER, HOOK
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
LANGUAGES = ['ru','en']


#telebot.apihelper.proxy = {'https':PROXY}
server = Flask(__name__)

# Init Search class
srch = Search()

#bot = telebot.TeleBot(TOKEN,parse_mode='markdown')
bot = telebot.TeleBot(TOKEN, parse_mode='html')

usr = User()

print('It started')
print(usr.flush)


def query_lines():
	pass


# Retrieve translation
def get_text(user_id, text_message, language=''):

	srch.whatlan(text_message)
	print(text_message)

	lan = usr.get_info(user_id, usr.lan) if language == '' else language
	#Return russion Translation
	if srch.language == "ru":
		webb = web(text_message)
		return webb.main()[:]

	# Admin or other user testing
	if lan == "en":
		result = srch.main(text_message, 'en')

	else:
		result = srch.main(text_message)

	print(result)

	# if there is no word found
	if result[0] == None:
		outmessage = f'Слово <a href="{SEARCH_URL+text_message}">{text_message}</a> не найдено'
		print(outmessage)
		return outmessage, None

	outmessage = "\n\n".join(result[0])

	return outmessage, result[1]


# Admin Keyboard
def define_keyboard(char,lan='',admin=True):
	
	# button assemble
	create_button = lambda text,date : telebot.types.InlineKeyboardButton(text=text, callback_data=date)
	
	
	buttons = []
	if admin:
		buttons.append(create_button('Edit','edit'))
	
	if lan == 'ru':
		buttons.append(create_button('English',f"{char}#en"))
	else:
		buttons.append(create_button('Russian',f"{char}#ru"))
		
	
	keyboard = telebot.types.InlineKeyboardMarkup(row_width=len(buttons))
	keyboard.add(*buttons)
	print('keyboard')
	return keyboard


# Change language keyboard
def define_language_keyboard():

	keyboard = telebot.types.InlineKeyboardMarkup(row_width=2)
	button = telebot.types.InlineKeyboardButton(text='Englist',
	                                            callback_data="en")

	button1 = telebot.types.InlineKeyboardButton(text='Русский',
	                                             callback_data="ru")
	keyboard.add(*[button, button1])

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
	lan = message.from_user.language_code if 'en' in message.from_user.language_code or 'ru' in message.from_user.language_code else "en"
	usr.add_user(user_id, message.from_user.username,
	             message.from_user.first_name, lan)
	bot.send_message(message.chat.id, WELCOME)
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
@bot.message_handler(content_types=['text'])
def handle_text_request(message):
	print("User id",
	      message.from_user.id,
	      message.from_user.username,
	      message.text,
	      sep="\n")
	# define keyboard
	user_id = str(message.from_user.id)
	text = message.text
	keyboard = None
	if not usr.check_user(user_id): return change_language(message)

	if message.from_user.id == int(ADMIN):
		keyboard = define_keyboard(message.text,usr.get_info(user_id,usr.lan))

	result = get_text(user_id, text)

	print(result)
	long_message_request(message.chat.id, result[0], keyboard)
	if result[1] != None:
		try:
			fp = BytesIO()
			generated = gTTS(text, lang='zh')
			generated.write_to_fp(fp)
			fp.seek(0)
			#audio = requests.get(result[1], headers=HEADER).content
			bot.send_voice(message.chat.id, fp)
		except Exception as e:
			print(e)


# Handle call back: Change language
@bot.callback_query_handler(
 func=lambda call: call.data == "en" or call.data == 'ru')
def handle_Language_callback(call):
	try:

		user_id = str(call.from_user.id)
		chat_id = call.message.chat.id

		lan = call.from_user.language_code if 'en' == call.from_user.language_code or 'ru' == call.from_user.language_code else "en"

		usr.add_user(user_id, call.from_user.username, call.from_user.first_name,
		             lan)
		print(usr.flush())
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
	keyboard = define_keyboard(char,lan)

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
	bot.remove_webhook()
	bot.set_webhook(url=HOOK + TOKEN)
	return "!", 200


@server.teardown_appcontext
def teardown_appcontext(exception=None):
	usr.save()


if __name__ == "__main__":
	server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
	#bot.remove_webhook()
	#bot.infinity_polling(interval=0, timeout=20)
