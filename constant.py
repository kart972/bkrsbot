#!/usr/bin/python
import os

# System variables
TOKEN = os.environ["TOKEN"]
ADMIN = os.environ["ADMIN"]
TESTERS = os.environ["TESTERS"].split(',')
HOOK = os.environ["HOOK"]
PROXY = os.environ["PROXY"]

admin = '@free4q'

HEADER = {
 'User-Agent':
 'Mozilla/5.0 (X11; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/81.0'
}


WELCOME = 'Добро пожаловать!\
Это бот-словарь, который переводит слова с китайского на русский и наоборот.\
Обновление 0.8🎉'


LOCALIZATION = {'en':
				{"welcome":f"Welcome!\nThis is a Chinese dictionary bot that will help you look up Chinese characters, their meanings, and use cases.\nCurrently, it is still in beta. If you encounter any issues or have any ideas for improving, feel free to reach out to the admin:{admin}",
				"error":'Word <a href="{}">{}</a> is not found',
				"language_change_success":"Language is changed to {}",
				"language_change_error":"Language is already {}"},
				 'ru':
				{"welcome":f"Добро пожаловать!\nЭто бот-словарь китайского языка, который поможет вам искать китайские иероглифы, их значения и использование.\nВ настоящее время он все еще находится в бета-версии. Если у вас возникнут какие-либо проблемы или у вас есть идеи для улучшения, не стесняйтесь связаться с администратором:{admin}",
				"error":'Слово <a href="{}">{}</a> не найденно',
				"language_change_success":"Язык был изменён на {}",
				"language_change_error":"Язык уже был устанавлен как {}"},
			   'zh':
				{"welcome":f"Welcome!\nThis is a Chinese dictionary bot that will help you look up Chinese characters, their meanings, and use cases.\nCurrently, it is still in beta. If you encounter any issues or have any ideas for improving, feel free to reach out to the admin:{admin}",
				"error":'Word <a href="{}">{}</a> is not found',
				"language_change_success":"语言改成为{}",
				"language_change_error":"语言已经设置为{}"},
				'language':'Выберите ваш язык\n\nChoose your language\n\n选择你的语言'
				}

