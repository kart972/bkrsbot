#!/usr/bin/python3
import os

#local import
from main import web
from search import Search, SEARCH_URL
from edit import edit_web
from constant import *
from user import User, Logs

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
# Supported Languages
LANGUAGES = ['ru', 'en', 'zh']
LANGUAGES_DIC = {'ru': 'Русский', 'en': 'English', 'zh': '中文'}

#telebot.apihelper.proxy = {'https':PROXY}
server = Flask(__name__)

# Init Search class
srch = Search()
usr = User()
logs = Logs()

#bot = telebot.TeleBot(TOKEN,parse_mode='markdown')
bot = telebot.TeleBot(TOKEN, parse_mode='html')

# Setup proxy
if PROXY not in ('', ' '): telebot.apihelper.proxy = {'https': PROXY}

print('It started')


# Edit message
def edit_message(chat_id, message_id, text, keyboard=None):
	bot.edit_message_text(text,
	                      chat_id,
	                      message_id,
	                      reply_markup=keyboard,
	                      disable_web_page_preview=True)


# Send a message request
def long_message_request(chat_id, text, keyboard=None):
	if len(text) < 4095:
		return bot.send_message(chat_id,
		                        text,
		                        disable_web_page_preview=True,
		                        reply_markup=keyboard)
	#[for x in range(0, len(text), 4095)]
	for x in range(0, len(text), 4095):
		bot.send_message(chat_id, text[x:x + 4095], disable_web_page_preview=True)


# Generate audio from google as and IOBytes
def get_audio(text, language='zh'):
	fp = BytesIO()
	generated = gTTS(text, lang=language, lang_check=False)
	generated.write_to_fp(fp)
	fp.seek(0)
	return fp


# Retrieve translation
# If language is speficy it
def get_text(user_id, text_message, language=None, mode=False):

	srch.whatlan(text_message)

	if language == None: lan = usr.get_info(user_id, usr.lan)
	else: lan = language

	#Return russion Translation
	if srch.language == "ru":
		webb = web(text_message)
		return webb.main()[:]

	# If language is not one of supported return not found
	if lan in LANGUAGES: result = srch.main(text_message, lan, mode)
	else: result = (None, None)

	if result[0] != None:
		logs.add([user_id, usr.get_info(user_id, "nick"), text_message, lan, "TRUE"])
		text = "\n\n".join(result[0])
	else:
		logs.add([
		 user_id,
		 usr.get_info(user_id, "nick"), text_message, lan,
		 usr.get_info(user_id, "nick"), "ERROR"
		])
		text = LOCALIZATION[lan]['error'].format(SEARCH_URL + text_message,
		                                         text_message)
	return text, result[1]


# Buttons Assembler
def create_button(text, date):
	return telebot.types.InlineKeyboardButton(text=text, callback_data=date)


# New keyboard
def new_keyboard(tags, callbacks, length=0):
	print(tags, callbacks)
	#print([i for i in range(len(tags))])
	buttons = [create_button(tags[i], callbacks[i]) for i in range(len(tags))]
	keyboard_len = len(buttons) if length == 0 else length
	keyboard = telebot.types.InlineKeyboardMarkup(row_width=keyboard_len)
	keyboard.add(*buttons)
	return keyboard


# Admin Keyboard
def define_keyboard(char, lan='', admin=False):

	# button assemble
	#create_button = lambda text, date: telebot.types.InlineKeyboardButton(text=text, callback_data=date)

	buttons = []

	if lan != 'ru': buttons.append(create_button('Русский', f"{char}#ru"))
	if lan != 'en': buttons.append(create_button('English', f"{char}#en"))
	if lan != 'zh': buttons.append(create_button('中文', f"{char}#zh"))

	keyboard = telebot.types.InlineKeyboardMarkup(row_width=len(buttons))
	keyboard.add(*buttons)
	return keyboard


# Change language keyboard
def define_language_keyboard():
	buttons = []

	buttons.append(create_button('Русский', 'ru'))
	buttons.append(create_button('English', "en"))
	buttons.append(create_button('中文', 'zh'))

	keyboard = telebot.types.InlineKeyboardMarkup(row_width=len(buttons))
	keyboard.add(*buttons)

	return keyboard


# Change language init message
def init_change_language(message):
	chat_id = message.chat.id
	
	keyboard = new_keyboard(list(LANGUAGES_DIC.values()), LANGUAGES)

	#keyboard = define_language_keyboard()
	text = LOCALIZATION['language']
	message = long_message_request(chat_id, text, keyboard)


def edit_message_back(call, char, page):
	user_id = str(call.from_user.id)
	chat_id = call.message.chat.id
	message_id = call.message.message_id

	result = inline_fetch(char, page)

	keyboard = define_full_keyboard(result[0], result[3])
	#output = result[0] + "-" + result[1] + '-' + result[2] + "\n\n" + result[4]
	output = ' - '.join(result[:3]) + '\n\n' + result[4]

	edit_message(chat_id, message_id, output, keyboard)


# TODO Write multilangue one message welcome
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


# Language command Handler
@bot.message_handler(commands=['language'])
def handle_language_tags(message):
	init_change_language(message)


# Language command Handler
@bot.message_handler(commands=['wiki'])
def handle_wiki_tags(message):
	# define keyboard
	keyboard = None
	chat_id = message.chat.id
	user_id = str(message.from_user.id)
	text_message = message.text
	if ' ' not in text_message: return
	request = text_message.split(' ', 1)[1]
	if request == '': return
	result = srch.wiki(request)

	# Print message to a user
	long_message_request(chat_id, result, keyboard)


# Send resent History to admin
@bot.message_handler(commands=['hist'])
def handle_language_tags(message):
	# define keyboard
	keyboard = None
	chat_id = message.chat.id
	user_id = str(message.from_user.id)
	if user_id != ADMIN: return
	# loop up history
	result = logs.read(10)

	# Print message to a user
	long_message_request(chat_id, result, keyboard)


# To Read messagees outloud
@bot.message_handler(commands=['spell'])
def read_outloud(message):
	try:

		# define keyboard
		#keyboard = None
		chat_id = message.chat.id
		user_id = str(message.from_user.id)
		text_message = message.text
		text = "Write some text in front of the command"

		# Return if message is empty
		if ' ' not in text_message: return long_message_request(chat_id, text)
		request = text_message.split(' ', 1)[1]
		if request == '': return

		# Get language
		srch.whatlan(request)
		lang = srch.language

		#print(request,lang)
		bot.send_voice(message.chat.id, get_audio(request, lang))
	except:
		print(sys.exc_info())


#[word,pinyin,translation]
def inline_assembler(query_id, name, description, body):
	keyboard = None
	#keyboard=define_full_keyboard(i[0],i[3])
	return telebot.types.InlineQueryResultArticle(
	 query_id,
	 name,
	 description=description,
	 input_message_content=telebot.types.InputTextMessageContent(body),
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

			description = pinyin_str + " " + definition
			body = " - ".join([query_str, pinyin_str, definition]) + "\n\n" + examples

			#output.append(fetchin([query_str, pinyin_str, definition, n, examples]))
			output.append(inline_assembler(str(n), query_str, description, body))
	print(output)
	return output


# Inline Handler
@bot.inline_handler(lambda query: len(query.query) != 0)
def query_text(inline_query):
	query_str = inline_query.query

	try:
		return bot.answer_inline_query(inline_query.id, inline_fetch(query_str))
	except:
		print(sys.exc_info())

	pinyin_str = ''.join([i[0] for i in pinyin(query_str)])

	output = inline_assembler('1', query_str, pinyin_str,
	                          query_str + " " + pinyin_str)

	bot.answer_inline_query(inline_query.id, [output])


# Check if message send by bot
is_bot = lambda q: q.from_user.is_bot == False and q.via_bot == None


# Handle all incomming text
@bot.message_handler(func=is_bot, content_types=['text'])
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
	if not usr.check_user(user_id): return init_change_language(message)

	# Admin and testers
	if user_id in TESTERS and srch.language not in ('en', 'ru'):
		try:
			avalible = [i for i in LANGUAGES if user_lan not in i]
			keyboard = new_keyboard([LANGUAGES_DIC[i] for i in avalible],
			                        [f'{text_message}#{i}' for i in avalible])
		except:
			print(sys.exc_info())
		#keyboard = define_keyboard(message.text, user_lan)
		result = get_text(user_id, text_message, mode=True)
	else:
		# Get text output
		result = get_text(user_id, text_message)
	print(keyboard)
	print(result)

	# Print message to a user
	long_message_request(message.chat.id, result[0], keyboard)

	# Cancel audio generation in message language is not chinese
	if srch.language != 'zh': return

	if result[1] == None:
		fp = get_audio(text_message)
		bot.send_voice(message.chat.id, fp)
		fp.close()
	else:
		fp = requests.get(result[1], headers=HEADER).content
		bot.send_voice(message.chat.id, fp)


# Call back functions:
# Change language
def change_language(call):
	print('Change language')
	# Define variables
	user_id = str(call.from_user.id)
	chat_id = call.message.chat.id
	message_id = call.message.message_id
	username = call.from_user.username
	first_name = call.from_user.first_name
	lan_code = call.from_user.language_code
	callback_data = call.data
	callback_json = call.json['message']['reply_markup']['inline_keyboard']

	callback_text = [
	 i["text"] for i in callback_json[0] if i['callback_data'] == callback_data
	][0]

	lan = lan_code if lan_code in LANGUAGES else "en"

	usr.add_user(user_id, username, first_name, lan)
	if usr.edit_info(user_id, usr.lan, call.data) is False:
		text = LOCALIZATION[callback_data]['language_change_error'].format(
		 callback_text)
		return long_message_request(chat_id, text)
	text = LOCALIZATION[callback_data]['language_change_success'].format(
	 callback_text)

	edit_message(chat_id, message_id, text)

	print("Success")


# Switch message for other language source
def switch_language_source(call):
	user_id = str(call.from_user.id)
	chat_id = call.message.chat.id
	text_message = call.message.text
	message_id = call.message.message_id

	char, lan = call.data.split('#')
	result = get_text(user_id, char, lan, mode=True)

	avalible = [i for i in LANGUAGES if lan not in i]
	keyboard = new_keyboard([LANGUAGES_DIC[i] for i in avalible],
			                        [f'{char}#{i}' for i in avalible])

	edit_message(chat_id, message_id, result[0], keyboard)


# Start message editing
def next_message(message):
	text = message.text
	lines = text.split('\n\n')
	if len(lines) != 3: return
	edit_web(lines[0], lines[1], lines[2])
	print(text)


# Edit data on bkrs
def handle_database_edit(call):
	chat_id = call.message.chat.id
	message = long_message_request(chat_id, "Write your message:")
	bot.register_next_step_handler(message=message, callback=next_message)


# Call Back handler all in one
@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
	user_id = str(call.from_user.id)
	chat_id = call.message.chat.id
	print(call.data)

	if call.data in ('en', 'ru', 'zh'): change_language(call)
	elif "#" in call.data: switch_language_source(call)
	elif "edit" in call.data and user_id == ADMIN: handle_database_edit(call)
	else: return


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
	logs.save()


if __name__ == "__main__":
	#webhook()
	server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
	#bot.infinity_polling(interval=0, timeout=20)
