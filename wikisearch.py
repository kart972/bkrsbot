# Foreign imports
from bs4 import BeautifulSoup
import requests

import json

# locals
from tools.language_recognizer import Language

# Constants
DEFAULT_IMAGE = 'https://upload.wikimedia.org/wikipedia/commons/thumb/8/80/Wikipedia-logo-v2.svg/200px-Wikipedia-logo-v2.svg.png'


class Wiki:

	def __init__(self, language='en'):
		self.language_code = language
		self.headers = {
		 # 'Authorization': 'Bearer YOUR_ACCESS_TOKEN',
		 'User-Agent':
		 'Mozilla/5.0 (X11; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/81.0'
		}
		self.number_of_results = 10
		self.base_url = 'https://api.wikimedia.org/core/v1/wikipedia/'
		pass

	def clean(self, plain_text):
		soup = BeautifulSoup(plain_text, 'html.parser').get_text()
		return soup

	def get_laguages(self, page_title) -> list:
		# Set the article title and get related articles in other languages.
		endpoint = '/page/' + page_title + '/links/language'

		url = self.base_url + self.language_code + endpoint
		response = requests.get(url, headers=self.headers).json()

		language_links = {}

		for language in response:
			link = 'https://{code}.wikipedia.org/wiki/{title}'.format(
			 code=language['code'], title=language['key'])
			language_name = language['code']
			language_links[language_name] = [link,language['key']]
		

		return language_links

	def search_pages(self, search_query: str) -> list:
		self.set_language(search_query)
		# output list
		output = []
		endpoint = '/search/page'
		url = self.base_url + self.language_code + endpoint
		parameters = {'q': search_query, 'limit': self.number_of_results}
		response = requests.get(url, headers=self.headers, params=parameters).json()

		for page in response['pages']:
			display_title = page['title']
			article_url = 'https://' + self.language_code + '.wikipedia.org/wiki/' + page[
			 'key']

			try:
				summery = self.clean(page['excerpt'])
			except:
				summery = None

			try:
				article_description = self.clean(page['description'])
			except:
				article_description = 'a Wikipedia article'
			try:
				thumbnail_url = 'https:' + page['thumbnail']['url']
			except:
				thumbnail_url = DEFAULT_IMAGE
			output.append({
			 "title": display_title,
			 "url": article_url,
			 "description": article_description,
			 "summery": summery,
			 "thumbnail": thumbnail_url,
			 "language": self.language_code
			})

		return output

	def page_image(self, title):
		image_url_title = "https://" + self.language_code + ".wikipedia.org/w/api.php?action=query&pilicense=any&format=json&piprop=thumbnail&pithumbsize=600&prop=pageimages|pageterms&titles="
		raw_image_json = requests.get(image_url_title + title).json()

		raw_image_json_main = raw_image_json['query']['pages']

		# If its empty return default picture
		if not (raw_image_json): return DEFAULT_IMAGE

		for key, value in raw_image_json_main.items():
			print(value)
			if 'thumbnail' in value:
				image = value['thumbnail']['source']
				break
		else:
			image = DEFAULT_IMAGE

		return image

	def get_page(self, url):
		css_sel = 'div#mw-content-text div.mw-parser-output p'

		plain_text = requests.get(url).content

		soup = BeautifulSoup(plain_text, 'html.parser')
		main = soup.select(css_sel)

		# Check if page is empty
		if main == []: return None

		for m in main:
			#print(m.attrs != {})
			if m.attrs != {}: continue
			text = m.get_text()
			break

		return text

	def set_language(self,search_query):
		lan = Language()
		src = lan.whatlan(search_query)
		self.language_code = src
		
	def search(self, search_query, dest="zh"):
		lan = Language()
		src = lan.whatlan(search_query)
		self.language_code = src
		
		languages = self.get_laguages(search_query)
		print(languages.keys())
		if dest in languages.keys():
			text = '<a href="{}">{}</a>\n'.format(languages[dest][0], search_query)
			text += self.get_page(languages[dest][0])

			title = languages[dest][1]
		
		else:
			result = self.search_pages(search_query)

			page = result[0]
			
			text = '<a href="{}">{}</a>\n'.format(page['url'], search_query)
			text += page['summery']

			title = page['title']
		
		return text,self.page_image(title)



		
		
	def main(self, search_query, src="en", dest="zh"):
		lan = Language()
		src = lan.whatlan(search_query)
		self.language_code = src
		result = self.search_pages(search_query)

		if result == []:return False,None
		
		[print(i['title']) for i in result]
		page = result[0]
		title = page['title']

		print(self.page_image(title))
		languages = self.get_laguages(title)
		print(languages.keys())
		if dest in languages.keys():
			text = '<a href="{}">{}</a>\n'.format(languages[dest][0], search_query)
			text += self.get_page(languages[dest][0])

			title = languages[dest][1]
		
		else:
			text = '<a href="{}">{}</a>\n'.format(page['url'], search_query)
			text += page['summery']

			title = page['title']
		
		return text,self.page_image(title)


if __name__ == "__main__":
	wikipage = Wiki('en')
	#print(wikipage.search_pages('minecraft'))
	#text = wikipage.main("телеграм", dest="zh")
	#print(text)
	while True:
		text = "собака"
		print(text)
		print(wikipage.search(text, dest="zh"))
		input()
