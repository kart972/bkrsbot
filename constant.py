#!/usr/bin/python
import os

# System variables
TOKEN = os.environ["TOKEN"]
ADMIN = os.environ["ADMIN"]
HOOK = os.environ["HOOK"]
PROXY = os.environ["PROXY"]
#LOCAL = bool(os.environ["LOCAL"])
admin = '@free4q'

HEADER = {
 'User-Agent':
 'Mozilla/5.0 (X11; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/81.0'
}
PROXY = 'http://127.0.0.1:2341'

WELCOME = 'Добро пожаловать!\
Это бот-словарь, который переводит слова с китайского на русский и наоборот.\
Обновление 0.8🎉'


LOCALIZATION = {'en':
				{"welcome":f"Welcome!\nThis is a Chinese dictionary bot that will help you look up Chinese characters, their meanings, and use cases.\nCurrently, it is still in beta. If you encounter any issues or have any ideas for improving, feel free to reach out to the admin:{admin}",
				"error":"Word {} is not found"},
				 'ru':
				{"welcome":f"Добро пожаловать!\nЭто бот-словарь китайского языка, который поможет вам искать китайские иероглифы, их значения и использование.\nВ настоящее время он все еще находится в бета-версии. Если у вас возникнут какие-либо проблемы или у вас есть идеи для улучшения, не стесняйтесь связаться с администратором:{admin}",
				"error":"Слово {} не найденно"}}

