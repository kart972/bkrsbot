#!/usr/bin/python3

import requests
from bs4 import BeautifulSoup

url_main = 'https://bkrs.info/'

cookies = {
 'mybbuser': '6039739_hMZ7d7rInWQZh1qXnNTZxIqDeYzHOiGqXSlyhbfYPsjefcFo9q'
}
header = {
 'User-Agent':
 "Mozilla/5.0 (X11; Linux x86_64; rv:101.0) Gecko/20100101 Firefox/101.0"
}

#edit_icon

search_url = 'https://bkrs.info/slovo.php?ch='
login_url = 'https://bkrs.info/login.php'
edit_url = 'https://bkrs.info/form.php?ch='


def edit_web(name, pinyin, text):
	req = requests.get(search_url + name, cookies=cookies)
	soup = BeautifulSoup(req.text, 'html.parser')

	add_url = soup.select('#edit_icon')

	if add_url != []: add_url = add_url[0].get('href')
	else: add_url = "form.php?word_add=" + name

	url = url_main + add_url

	data = {'ch': name, 'py': pinyin, 'ru': text}

	print(url, data)

	x = requests.post(url, data=data, cookies=cookies)

	with open('./Output/page.html', 'w') as f:
		f.write(x.text)
	print(x.status_code)


if __name__ == "__main__":  #login()
	edit_web('重排序', 'zhòngpáixù', 'Вторично приводить в порядок')
