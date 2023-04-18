#!/usr/bin/python

# Foreign imports
import os
from bs4 import BeautifulSoup
import requests
from pypinyin import pinyin as get_pinyin
import concurrent.futures
import wikipedia

# Constants
MAIN_URL = 'https://bkrs.info/'
SEARCH_URL = "https://bkrs.info/slovo.php?ch="
SEARCH_URL_EN = "https://www.yellowbridge.com/chinese/sentsearch.php?word="
AUDIO_URL_EN = "https://www.yellowbridge.com/gensounds/py/"

LANGUAGES_URL_DIC = {
 'en':
 'https://www.yellowbridge.com/chinese/dictionary.php?searchMode=E&word={}',
 'ru': 'https://bkrs.info/slovo.php?ch={}',
 'zh': {
  'en': 'https://www.yellowbridge.com/chinese/sentsearch.php?word={}',
  'ru': 'https://bkrs.info/slovo.php?ch={}',
  'zh': 'https://tw.ichacha.net/mhy/{}.html'
 }
}
WIKI_SEARCH_URL = "https://zh.wikipedia.org/w/index.php?title=Special:%E6%90%9C%E7%B4%A2&variant=zh-cn&search={}"
WIKI_URL = 'https://zh.wikipedia.org/zh-cn/{}'
HOME = '/'.join(os.path.realpath(__file__).split('/')[:-1]) + '/'
OUTPUT = "Output/"
INPUT = "Input/"


class Search:

	def __init__(self):
		self.language = ''

	# Download webpage
	# And add url in the top
	def download_page(self, url: str, path: str = "", save: bool = True) -> None:
		headers = {
		 'User-Agent':
		 'Mozilla/5.0 (X11; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/81.0'
		}
		# Get webpage text
		for i in range(5):
			try:
				text = requests.get(url, headers=headers).text
				break
			except:
				pass
		plain_text = '<!--' + url + '-->' + "\n" + text
		#plain_text = url+"\n"+text
		# Keep logs
		if path == "": return text

		file_path = HOME + INPUT + path
		with open(file_path, 'w') as f:
			f.write(plain_text)
		return text

	# Read website
	# and url in the top
	def open_file(self, file_name: str) -> str:
		file_path = HOME + INPUT + file_name
		with open(file_path) as f:
			return f.read()

	# Determine language function
	def whatlan(self, text_input: str) -> bool:
		character_hex = ord(text_input[0])

		if character_hex >= int(0x4E00):
			self.language = "zh"
		elif character_hex >= int(0x0410) and character_hex <= int(
		  0x044f) or character_hex == int(0x0401) or character_hex == int(0x451):
			self.language = "ru"
		elif character_hex >= int(0x0041) and character_hex <= int(0x007A):
			self.language = 'en'
		else:
			self.whatlan(text_input[1:])

		return True

	def get_info(self, data_list):
		pattern_list = [
		 "Traditional Script", "Simplified Script", "English Definition",
		 "Part of Speech"
		]

		new_list = []
		for n, i in enumerate(data_list):
			for p in pattern_list:
				if p in i:
					new_list.append(data_list[n + 1])

		return new_list

	def ch_english(self, text, name=''):
		picky = lambda list1, numbers: [list1[i] for i in numbers]
		# Css patterns
		csspath_maininfo = "html body div#pgWrapper main#pgMain div#dictOut.tabGroup div#tabBody.rounded.shadow table#mainData.grid.boldFirstCol tr td"
		csspath_example = "html body div#pgWrapper main#pgMain div#dictOut.tabGroup div#tabBody.rounded.shadow table#sentences.grid.maxwidth tr td li"

		# Start BeautifulSoup OBJ
		soup = BeautifulSoup(text, 'html.parser')
		maininfo_list = soup.select(csspath_maininfo)

		if maininfo_list == []: return None, None
		#[print(self.url),self.display_ln(maininfo_list),print(maininfo_list)]

		# Handle examples
		examp = soup.select(csspath_example)

		example_list = [
		 "".join([j.get_text() for j in i.select("span")]) for i in examp
		]
		example_list = [
		 e + "\n" + ''.join([i[0] for i in get_pinyin(e)]) for e in example_list
		]

		# Main info
		main_list = self.get_info(maininfo_list)

		# Get audio
		audio = soup.select(".bigger")[0]
		try:
			audio_url = AUDIO_URL_EN + "_".join(
			 audio.span.get('onclick').split("sayPY('")[-1].split("')")[0].split(
			  " ")) + '.mp3' if True else None

		except Exception as e:
			print(e)
		# If there is a lack of elements in list
		pick = [2, 1, 0, 3] if len(main_list) > 3 else [2, 1, 0]

		main_list = picky(main_list, pick)
		main_list = [i.get_text().strip() for i in main_list]

		# PinYin
		pinyin = soup.select("div.bigger")
		pinyin = pinyin if pinyin != [] else soup.select("span.bigger")
		main_list.insert(2, pinyin[0].get_text())

		#print(main_list)
		if "Same" in main_list[0]:
			main_list[0] = main_list[1]

		main_list += example_list

		return main_list, None

	def main(self, name: str, lan='ru', syn=True) -> tuple:
		func_dic = {'en': self.ch_english, 'ru': self.ch_ru, 'zh': self.zh_chinese}

		# Determine language
		self.whatlan(name)

		# Get url
		search_url = LANGUAGES_URL_DIC[
		 self.language] if self.language != 'zh' else LANGUAGES_URL_DIC[
		  self.language][lan]
		print(search_url)

		map_urls = [search_url.format(name), LANGUAGES_URL_DIC['ru'].format(name)]
		# Search selections
		if syn is True:
			with concurrent.futures.ThreadPoolExecutor() as executor:
				plain_text_list = list(executor.map(self.download_page, map_urls,
				                                    ["", '']))
			plain_text = plain_text_list[0]
			plain_text_syn = plain_text_list[1]
		else:
			plain_text = self.download_page(map_urls[0], '')

		#print('self.language',self.language)
		if self.language == 'zh':
			result = func_dic[lan](plain_text, name)
			if syn is False: return result
			synonyms = self.get_synonyms(plain_text_syn)
			if result[0] != None and synonyms != None: result[0].append(synonyms)

		elif self.language == 'en':
			result = self.en_chinese(plain_text, name)
		elif self.language == 'ru':  # not implemented
			result = [self.ru_chinese(plain_text), None]

		#input(result)
		return result

	def ru_chinese(self, plain_text, length=2):
		css_selector = "#ru_ru"
		css_translation = ".ch_ru"
		css_check = "#no-such-word"
		css_correction = "#words_hunspell a"
		css_russ_dic = "#ruch_fullsearch div"
		css_chi_dic = "#xinsheng_fullsearch"

		soup = BeautifulSoup(plain_text, 'html.parser')
		if soup.select(css_check) != []:
			correction = soup.select(css_correction)
			if correction == [] or length < 1: return None
			url = MAIN_URL + correction[0]['href']
			print(url)
			return self.ru_chinese(self.download_page(url), length - 1)

		title = soup.select(css_selector)[0].get_text()
		translation = soup.select(css_translation)[0].get_text()

		return [title.capitalize(), translation]

	def get_synonyms(self, text):
		#text=self.download_page(LANGUAGES_URL_DIC['ru'].format(name), "")
		css_selector = '#synonyms'

		soup = BeautifulSoup(text, 'html.parser')
		synonyms = soup.select(css_selector)
		if synonyms == []: return None
		result = synonyms[0].get_text().replace('\t', '')
		return result

	def html_cleaner(self, text) -> str:
		if "<" not in text or '>' not in text: return text
		diff = []
		[
		 diff.append('<{}>'.format(i.split('>')[0])) for i in text.split('<')
		 if '>' in i and '<{}>'.format(i.split('>')[0]) not in diff
		]
		#input(diff)

		for i in diff:
			text = text.replace(i, '')
		return text

	def zh_chinese(self, text, name):
		check_selecter = "#related"
		css_selector = '#content'
		soup = BeautifulSoup(text, 'html.parser')

		if soup.select(check_selecter) != []: return None, None
		table = soup.select(css_selector)

		#print(table[0].div.get_text())

		main_info = str(table[0].div).replace('<div>', '').replace('</div>', '')
		pinyin = main_info.split('<br/>')[0].split('<div>')[-1]
		text = '\n'.join(main_info.split('<br/>', 1)[-1].split('<br/>'))

		#input(text)
		text = self.html_cleaner(text)
		pinyin = self.html_cleaner(pinyin)
		name = self.html_cleaner(name)

		return [name, pinyin, text], None

	def en_chinese(self, text, name=''):

		css_selector = '#multiRow tr'
		soup = BeautifulSoup(text, 'html.parser')
		table = soup.select(css_selector)

		results = [
		 " - ".join([i.get_text() for i in l]) for l in table
		 if name in l.get_text()
		]
		if results == []: return None, None

		#input(results)
		return ["\n".join(results)], None

	def ch_ru(self, plain_text, name):
		# Ensure that word is exists
		if 'такого слова нет' in plain_text: return None, None
		if 'пословный перевод' in plain_text: return None, None

		soup = BeautifulSoup(plain_text, 'html.parser')
		# Get title
		title = soup.find("div", attrs={"id": "ch"})
		title_text = title.get_text().strip()
		# Get Pinyin and audio
		pinyin = soup.find("div", attrs={"class": "py"})
		pinyin_text = pinyin.get_text().strip()

		print(get_pinyin(name), '_' in pinyin_text)
		if '_' in pinyin_text:
			pinyin_text = ''.join([i[0] for i in get_pinyin(name)]) + '*'

		audio_url = MAIN_URL + pinyin.img.get('onclick').split("Audio('")[-1].split(
		 "');mp3.play();")[0] if 'img' in str(pinyin) else None

		# Get Main text
		ru_div = soup.find("div", attrs={"class": "ru"})
		meanings = ru_div.get_text().strip()

		text = '\n\n'.join([title_text, pinyin_text, meanings])

		return [title_text, pinyin_text, meanings], audio_url

	def wiki(self, user_input):
		list_css_sel = ".mw-search-results"
		image_css_sel = "table.infobox img"
		css_sel = 'div#mw-content-text div.mw-parser-output p'

		prep_url = lambda a, rep='_': rep.join(a.split(' '))
		# Prepare url
		# If there spaces in a user input
		url_key = user_input
		if ' ' in user_input: url_key = prep_url(user_input, '+')

		url = WIKI_SEARCH_URL.format(url_key)
		print(url)

		# Check if result is a list
		plain_text = self.download_page(url, '')
		soup = BeautifulSoup(plain_text, 'html.parser')
		wiki_list = soup.select(list_css_sel)
		if wiki_list == []:
			return self.wiki_page(plain_text)

	def wiki_page(self, plain_text, user_input):
		image_css_sel = "table.infobox img"
		css_sel = 'div#mw-content-text div.mw-parser-output p'

		soup = BeautifulSoup(plain_text, 'html.parser')
		main = soup.select(css_sel)
		text = '<a href="{}">{}</a>\n'.format(url, user_input)

		# Check if page exists
		if main == []: return url, None

		for m in main:
			print(m.attrs != {})
			if m.attrs != {}: continue
			text += m.get_text()
			break

		# Get image
		image = soup.select(image_css_sel)
		if image == []: return text, None

		return text, image[0]['src'][2:]

	def get_image(self, urls):
		IMAGE_FORMATS = ('jpg', 'jpeg', 'png', 'PNG')

		for i in urls:
			if i.split(".")[-1] in IMAGE_FORMATS: return i

		return None

	def new_wiki(self, user_input, searchMode=True):
		#default url
		image_url = "https://en.wikipedia.org/w/api.php?action=query&prop=pageimages|pageterms&piprop=thumbnail&pithumbsize=600&titles="
		down_image = lambda name: requests.get(image_url + name).json()

		default_url = "zh.wikipedia.org/wiki/"
		print(default_url + user_input)

		# set language
		wikipedia.set_lang("zh")
		print(user_input)
		# Search
		if searchMode is True:
			search = wikipedia.search(user_input)

			print(search)

			if search == []: return None
			else: return search

		try:
			page = wikipedia.page(user_input)
		except wikipedia.exceptions.DisambiguationError as e:
			return "\n".join(e.options), user_input, None

		if page == []: return None, None
		summary = page.summary
		raw_image_json = down_image(page.title)
		print(raw_image_json)
		raw_image_json = raw_image_json['query']['pages']
		#
		if not (raw_image_json): return summary, user_input, None

		for key, value in raw_image_json.items():
			if (value['thumbnail']['source']):
				image = value['thumbnail']['source']
				break
		else:
			image = None

		#images = tuple(page.images)
		#image = self.get_image(images) if images != []  else None

		print(image)
		return summary, user_input, image


if __name__ == "__main__":
	sch = Search()
	#output = sch.main("погода", "zh")
	#print(len(output))
	#print(sch.wiki('天氣'))
	#print("\n\n".join(sch.main("天气", "ru",True)[0]))

	#print(sch.wiki('supper mario'))
	#print(sch.wiki('Flash'))
	#print(sch.wiki('far cry 3'))

	print(sch.new_wiki('Mario (歌手)', False))

	#print("\n\n".join(sch.main("法国", "zh")[0]))
	#print("\n\n".join(sch.main("茄科", "zh")[0]))
	#print("\n\n".join(sch.main("щвабра", "zh")[0]))
	#while True:input("\n\n".join(sch.main("天气", "en")[0]))
