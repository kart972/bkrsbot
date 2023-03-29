#!/usr/bin/python

# Foreign imports
import os
from bs4 import BeautifulSoup
import requests
from pypinyin import pinyin as get_pinyin

# Constants
MAIN_URL = 'https://bkrs.info/'
SEARCH_URL = "https://bkrs.info/slovo.php?ch="
SEARCH_URL_EN = "https://www.yellowbridge.com/chinese/sentsearch.php?word="
AUDIO_URL_EN = "https://www.yellowbridge.com/gensounds/py/"

#SEARCH_URL_DIC = {'cn-en':'https://www.yellowbridge.com/chinese/sentsearch.php?word={}',
#		'cn-ru':'https://bkrs.info/slovo.php?ch={}',
#		'en-cn':'https://www.yellowbridge.com/chinese/dictionary.php?searchMode=E&word={}',
#		'cn-cn':'https://tw.ichacha.net/mhy/{}.html'}

LANGUAGES_URL_DIC = {'en':'https://www.yellowbridge.com/chinese/dictionary.php?searchMode=E&word={}',
					'ru':'https://bkrs.info/slovo.php?ch={}',
					'cn':{'en':'https://www.yellowbridge.com/chinese/sentsearch.php?word={}',
							'ru':'https://bkrs.info/slovo.php?ch={}',
							'cn':'https://tw.ichacha.net/mhy/{}.html'}}
							
							

				
SEARCH_URL_DIC ={'en-en':'https://www.yellowbridge.com/chinese/dictionary.php?searchMode=E&word={}',
		'ru-en':'https://bkrs.info/slovo.php?ch={}',
		'cn-ru':'https://bkrs.info/slovo.php?ch={}',
		'en-ru':'https://www.yellowbridge.com/chinese/dictionary.php?searchMode=E&word={}',
		'cn-en':'https://www.yellowbridge.com/chinese/sentsearch.php?word={}',
		'cn-cn':'https://tw.ichacha.net/mhy/{}.html',
		'en-cn':'https://www.yellowbridge.com/chinese/dictionary.php?searchMode=E&word={}',
		'ru-cn':'https://bkrs.info/slovo.php?ch={}'}	
HOME = '/'.join(os.path.realpath(__file__).split('/')[:-1]) + '/'
OUTPUT = "Output/"
INPUT = "Input/"


class Search:
	# Download webpage
	# And add url in the top
	def download_page(self,
	                  url: str,
	                  path: str = "temp",
	                  save: bool = True) -> None:
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
		if save:
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
	def whatlan(self, text_input: str) -> None:
		character_hex = ord(text_input[0])

		if character_hex >= int(0x4E00):
			self.language = "cn"
		elif character_hex >= int(0x0410) and character_hex <= int(
		  0x044f) or character_hex == int(0x0401) or character_hex == int(0x451):
			self.language = "ru"
		elif character_hex >= int(0x0041) and character_hex <= int(0x007A):
			self.language = 'en'

	


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
		

	def ch_english(self, text,name=''):
		picky = lambda list1, numbers: [list1[i] for i in numbers]
		# Css patterns
		csspath_maininfo = "html body div#pgWrapper main#pgMain div#dictOut.tabGroup div#tabBody.rounded.shadow table#mainData.grid.boldFirstCol tr td"
		csspath_example = "html body div#pgWrapper main#pgMain div#dictOut.tabGroup div#tabBody.rounded.shadow table#sentences.grid.maxwidth tr td li"

		# Start BeautifulSoup OBJ
		soup = BeautifulSoup(text, 'html.parser')
		maininfo_list = soup.select(csspath_maininfo)

		if maininfo_list == []:return None,None
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

	def main(self, name: str, lan='ru') -> tuple:
		func_dic = {'en':self.ch_english,'ru':self.ch_ru,'cn':self.cn_chinese}
		
		# Determine language
		self.whatlan(name)
		
		# Get url
		search_url = LANGUAGES_URL_DIC[self.language] if self.language != 'cn' else LANGUAGES_URL_DIC[self.language][lan]
		print(search_url)
		
		
		# Search selections
		if name == 'debug': return
		elif name != '': plain_text = self.download_page(search_url.format(name), "word")
		else: plain_text = self.open_file("word")


		#print('self.language',self.language)
		if self.language == 'cn':
			result = func_dic[lan](plain_text,name)
		elif self.language == 'en':
			result = self.en_chinese(plain_text,name)
		elif self.language == 'ru':  # not implemented
			result = (None,None)
		#input(result)
		return result
		
		#if lan == 'ru': return self.ch_ru(plain_text, name)
		#if lan == 'en' and self.language == 'en': return self.en_chinese(plain_text,name)
		#if lan == 'cn' and self.language == 'cn': return self.cn_chinese(plain_text,name)
		#return self.ch_english(plain_text)
		
	def cn_chinese(self,text,name):
		check_selecter = "#related"
		css_selector = '#content'
		soup = BeautifulSoup(text, 'html.parser')
		
		if soup.select(check_selecter) != []:return None,None
		table = soup.select(css_selector)
		
		print(table)
		
		main_info = str(table[0].div).replace('<div>','').replace('</div>','')
		pinyin = main_info.split('<br/>')[0].split('<div>')[-1]
		text  = '\n'.join(main_info.split('<br/>',1)[-1].split('<br/>'))
		
		#pinyin = pinyin.replace('<br/>','')
		text = text.replace('<br/>','') 		
		
		return (name,pinyin,text),None
			
	
	def en_chinese(self,text,name=''):
		
		css_selector = '#multiRow tr'
		soup = BeautifulSoup(text, 'html.parser')
		table = soup.select(css_selector)
		
		results = [" - ".join([i.get_text() for i in l]) for l in table if name in l.get_text()]
		
		#input(results)
		return ["\n".join(results)],None

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


if __name__ == "__main__":
	sch = Search()
	while True:
		input("\n\n".join(sch.main("中国", "cn")[0]))
		
