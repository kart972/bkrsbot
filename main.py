#!/usr/bin/python
import os
MAIN_URL = 'https://bkrs.info/'

class web:
	global MAIN_URL

	# --Varialbles--
	def __init__(self,t_input=None, url=None, proxy=False, language=None):
		self.input = t_input
		print(t_input)
		self.url = url
		self.language = language
		self.title = ''
		self.proxy = proxy
		self.pinyin = ''
		self.audio = True
		self.loop = 0
		
	# -- Return Not found
	def notfound(self):
		if self.language == 'cn':
			linedict = 'https://dict.naver.com/linedict/zhendict/#/cnen/search?query=' + self.title
			text = '<a href="{a}">{b}</a>\n<a href="{c}">{b}</a>\nСлово не найдено.'.format(a=self.url,b=self.title,c = linedict)
			
		if self.language == 'ru':
			text = '<a href="{a}">{b}</a>\nСлово не найдено.'.format(a=self.url,b=self.title)
		print(self.language)
		return text
	
			
	# --Checking AND Deleting--
	
	def replaceplus(self,toreplist,text,repwith=''):
		
		if len(toreplist) == 1:
			if toreplist[0] in text:
				text = text.replace(toreplist[0],repwith)

		elif len(toreplist) > 1:
			for temp in toreplist:
				if temp in text:
					text = text.replace(temp,repwith)

		return text
	
		


	# --Language detection--
	def whatlan(self,t_input):
		fstchr = ord(t_input[0])
		
		if fstchr>=int(0x4E00):
			self.language = "cn"
		elif fstchr>=int(0x0410) and fstchr <= int(0x044f) or fstchr == int(0x0401) or fstchr == int(0x451):
			self.language = "ru"
		elif fstchr>=int(0x0041) and fstchr <= int(0x007A):
			self.language = 'en'



	# --Downloadind--
	def downloadwpage(self):
		#print('____________Debug Download________________','Downloading url',self.url,self.title,sep='\n')
		if self.proxy:
			#print('____________Debug_________________','Downloding1',self.url,sep='\n')
			os.system(f'''curl -s --output ./logs/temp '{self.url}' ''')

		elif not self.proxy:
			#print('____________Debug_________________','Downloding1.1',self.url,sep='\n')
			os.system(f'''curl -s --output ./logs/temp '{self.url}' ''')

		#print('____________Debug_________________','Downloding Finished',self.proxy,sep='\n')
	
	
	# --Download Audio--
	def download_audio(self,text):
		if '<img ' not in text:
			return False
			
		else:
			add_url = (((text.split("new Audio('"))[1]).split("');mp3.play();"))[0]
			if 'downloads' in add_url:
				true_url = MAIN_URL + add_url
				print(true_url)
				os.system(f'''wget --quiet -t 3 -O - '{true_url}' > ./logs/audio''')
				return True
				
	# --Reading--
	
	def readfile(self):
		cfile = open('./logs/temp','r')
		ctxt = cfile.read()
		cfile.close()
		return ctxt

	
	# --GET Main Part Of A Webpage--
	
	def parting(self, text):
		if self.language is None:
			if "id='ru_ru'" in text:
				self.language = 'ru'
			elif "id='ch'" in text or 'ch_long' in text:
				self.language = 'cn'
		
		# -- Chinese
		if self.language == 'cn':
			if 'такого слова нет' in text or 'ch_long' in text:
				return False
			
			if "<div id='ch'>" in text:
				mainpart = (text.split("<div id='ch'>"))[1]
			elif "<div id='ch' class=''>" in text:
				mainpart = (text.split("<div id='ch' class=''>"))[1]
			
			mainpart = (mainpart.split("<br />"))[0]
			return mainpart
			
		# -- Russian	
		elif self.language == 'ru':
			if "<div id='ru_ru'>" in text:
			
			# --- If Word s found ---			
				if 'Такого слова нет.' not in text:
					mainpart = (text.split("<div id='ru_ru'>"))[1]
					mainpart = (mainpart.split('\n\n\n'))[0]
					return mainpart
			#---Word not found---					
				if 'начальная форма:' not in text:
					return False
				
				#---- Ask if person spell word wrong
				
				elif 'начальная форма:' not in text and 'похожие слова:' in text:
					return False
				
				else:
					
					#----Loop preventing----
					
					if self.loop > 3:
						return False
					
					#----Looking for wrong spelling----
					
					if 'gray' in ((((text.split('начальная форма:</div>'))[1]).split('</a>'))[0]) and 'похожие слова:' in text:
						if 'gray' in ((((text.split('похожие слова:</div>'))[1]).split('</a>'))[0]):
							return False
						self.input = (((((text.split('похожие слова:</div>'))[1]).split('</a>'))[0]).split('>'))[-1]
						self.title = self.title + '\nВозможно вы имели ввиду:\n'
					
					else:
						self.input = (((((text.split('начальная форма:</div>'))[1]).split('</a>'))[0]).split('>'))[-1]
						self.title = self.title + '\nНачальная форма:\n'
					
					print('____________Debug WORD NOT FOUND BUT LOOKING FOR IT_________________',self.title,self.loop,sep='\n')
					text, _ = self.main()
					self.loop+=1
					return text


	
	# --Formatting--
	
	def formatting(self, text):
		
		temp_title = ""	
		# ---When Looking Up Chinese Character---
		
		if self.language == 'cn':
			DEFAULT_CH_FLILTERE = ["</div>","<div class='py'>","<div class='ru'><div>","<div>","<div class='ru'>"]
			
			self.pinyin = (((text.split("<div class='py'>"))[1]).split('<',1))[0]
			
			text = self.replaceplus(DEFAULT_CH_FLILTERE, text)
			
			temp_title = ((text.split('\n\n'))[0]).replace("\n",'',1)
			
			text = (text.split('\n\n'))[2]
			
			#text = text.replace("\n",'',1)
				
			text = self.replaceplus(["<hr class='hr_propper' />"], text,"\n\n")
			
		
		# ---When Looking Up Russian Word---
		
		elif self.language == 'ru':
			DEFAULT_RU_FLILTERE = ["</div>","<br />","<div class='ch_ru'>",'<div>']
			
			text = self.replaceplus(DEFAULT_RU_FLILTERE, text)
			
			temp_title = self.title
			
			text = text.replace('\n','\n\n',1)

			if '•' in text:
				text = (text.split('•'))[0]
			
		
		# ---When Looking Up English Word/Pinyin---
		
		elif self.language == 'en':
			text = ''' English is not implemented yet'''
			return text
			
			
		# ---Common Formating---

		text = self.replaceplus(['<div class="m3"><div class="ex">'],text,' -- ')
		text = self.replaceplus(['<div class="m2"><div class="ex">','<div class="m2">'],text,' - ')
		text = self.replaceplus(["<b>","</b>",],text)
		text = self.replaceplus(["<span class='green'>","</span>"],text,'"')
		text = self.replaceplus(['<div class="ex">',"<div class='m2'>"],text,'')
		text = self.replaceplus(['<div class="m4">'],text,' --- ')
		
		# ---When Handling Chinese Traditional Character---
		# ---Break the cycle
		
		if self.title != temp_title:
			if self.language == 'ru':
				text = self.title + text
			if self.language == 'en':
				self.title +=" " + temp_title
			return text


		# For a single traditional character

		if "сокр." not in text and "вм." in text and "см." not in text:
			self.url = (((text.split("href='"))[1]).split("'"))[0]
			text, _ = self.main()
		
		

		self.title = '<a href="{}">{}</a>'.format(self.url,self.title)
		if self.language == 'cn':
		
			text = self.title + "\n" + self.pinyin + '\n\n' + text
		elif self.language == 'ru':
		
			text = self.title + "\n\n" + (text.split("\n\n",1))[1]
		
		return text


	# --Main--

	def main(self):
		#self.loop+=1
		if self.input != "":
			if 'bkrs.info' not in self.input:
				self.whatlan(self.input)
				
				if self.language == 'en':
					text = ''' English is not implemented yet'''
					return text
				
				
				# ---Fixing maybe you're loking for another word
				
				if self.title == '':
					self.title = self.input.capitalize()
				else:
					self.title = self.title + self.input.capitalize()
					
				# ---Russian Multiword Input Search!
					
				if ' ' in self.input:
					self.url = "https://bkrs.info/slovo.php?ch=" + self.replaceplus([' '],self.input,'+')
					print('____________Debug NEW MULTIWORD SYSTEM_________________',self.input,sep='\n')
				else:
					self.url = "https://bkrs.info/slovo.php?ch=" + self.input

			else:
				self.url = self.input	
			self.downloadwpage()
		page_txt = self.readfile()
		main_info = self.parting(page_txt)
		
		# --Check if text ok for russian language--
		if main_info is False:
			main_info = self.notfound()
			print('____________Debug NOT FOUND_________________',main_info,self.language,sep='\n')
			return main_info, False
		
		
		# --Download audio Toggle--
		
		if self.audio is True:
			audio_check = self.download_audio(main_info)
		else:
			audio_check = False
		
		# -- Privent from unnecessary formatting
		print(self.loop)
		if self.loop == 0:
			main_info = self.formatting(main_info)
		
		
		print('____________Debug MAIN INFO_________________',main_info,audio_check,sep='\n')
		
		return main_info, audio_check



if __name__ == '__main__':
	debug = True
	#a = input("Is there a need for Proxy\n")
	#meow = web(input(), True if a == '' else False)
	
	# --DOUBLE SPACE FOR TESTING
	if debug == True:
		list_input = input().split('  ')
		print(list_input)
		for i in list_input:
			meow = web(i)
			meow.main()
	else:
		meow = web(input())
		meow.main()
