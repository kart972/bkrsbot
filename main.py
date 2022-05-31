#!/usr/bin/python
import os

class web:

	# --Varialbles--
	def __init__(self,url=None, proxy=False, language=None):
		self.url = url
		self.language = language
		self.title = ''
		self.proxy = proxy
		self.pinyin = ''


	# --Language detection--
	def whatlan(self):
		fstchr = ord(self.url[0])
		
		if fstchr>=int(0x4E00):
			self.language = "cn"
		elif fstchr>=int(0x0410) and fstchr <= int(0x044f) or fstchr == int(0x0401) or fstchr == int(0x451):
			self.language = "ru"
		elif fstchr>=int(0x0041) and fstchr <= int(0x007A):
			self.language = 'en'
		#print('____________Debug Language_________________','Language detedtion',fstchr,self.language,sep='\n')


	# --Downloadind--
	def downloadwpage(self):
		
		if self.proxy:
			#print('____________Debug_________________','Downloding1',self.url,sep='\n')
			os.system(f'''export http_proxy="http://127.0.0.1:2341"; export https_proxy="http://127.0.0.1:2341"; export ftp_proxy="http://127.0.0.1:2341"; export no_proxy="localhost,127.0.0.1,::1"; script ./logs/out -c "wget --quiet -t 3 -O - '{self.url}' > ./logs/temp" ''')

		elif not self.proxy:
			#print('____________Debug_________________','Downloding1.1',self.url,sep='\n')
			os.system(f'''script ./logs/out -c "wget --quiet -t 3 -O - '{self.url}' > ./logs/temp"''')

		print('____________Debug_________________','Downloding Finished',self.proxy,sep='\n')
	
	
	# --Reading--
	
	def readfile(self):
		cfile = open('./logs/temp','r')
		ctxt = cfile.read()
		cfile.close()
		return ctxt


	# --Get WebPage  main part--
	def parting(self, text):
		if self.language is None:
			if "id='ru_ru'" in text:
				self.language = 'ru'
			elif "id='ch'" in text:
				self.language = 'cn'
		if self.language == 'cn':
			
			
			#---Word not found---
			if 'такого слова нет' in text:
				text = '<a href="{}">{}</a>\nWord is not found'.format(self.url,self.title)
				return text
		
		
			if "<div id='ch'>" in text:
				mainpart = (text.split("<div id='ch'>"))[1]
			elif "<div id='ch' class=''>" in text:
				mainpart = (text.split("<div id='ch' class=''>"))[1]
				

			mainpart = (mainpart.split("<br />"))[0]
		elif self.language == 'ru':
			if "<div id='ru_ru'>" in text:
			
			#---Word not found---			
				if 'Такого слова нет.' in text:
					text = '<a href="{}">{}</a>\nWord is not found'.format(self.url,self.title)
					return text
				
				mainpart = (text.split("<div id='ru_ru'>"))[1]
				mainpart = (mainpart.split('\n\n\n'))[0]
			
		
		#print('____________Debug Languge and mainpart_________________',self.language,text,sep='\n')
		return mainpart

	
	
	# -- NEW --
	# --Checking AND Deleting--
	
	def replaceplus(self,toreplist,text,repwith=''):
		
		print()
		
		if len(toreplist) == 1:
			if toreplist[0] in text:
				text = text.replace(toreplist[0],repwith)

		elif len(toreplist) > 1:
			for temp in toreplist:
				if temp in text:
					text = text.replace(temp,repwith)
					#print('____________Debug PinYin_________________',temp,sep='\n')
		return text
	
	
	# --Formatting--
	
	def formatting(self, text):
		if 'Word is not found' in text:
			text = '<a href="{}">{}</a>\nWord is not found'.format(self.url,self.title)
			return text
		temp_title = ""	
		# ---When Looking Up Chinese Character---
		
		if self.language == 'cn':
			DEFAULT_CH_FLILTERE = ["</div>","<div class='py'>","<div class='ru'><div>","<div>","<div class='ru'>"]
			
			self.pinyin = (((text.split("<div class='py'>"))[1]).split('<',1))[0]
			
			text = self.replaceplus(DEFAULT_CH_FLILTERE, text)
			
			temp_title = ((text.split('\n\n'))[0]).replace("\n",'',1)
			
			text = (text.split('\n\n'))[0] + "\n\n" + self.pinyin + "\n\n" + (text.split('\n\n'))[2]
			
			text = text.replace("\n",'',1)
				
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

		
		# ---When Handling Chinese Traditional Character---
		
		if self.title != temp_title:
			self.title +=" " + temp_title


		if 'no-such-word' in text:
			text = "Word does not exist"


		# For a single traditional character

		if "сокр." not in text and "вм." in text and "см." not in text:
			self.url = (((text.split("href='"))[1]).split("'"))[0]
			#print('____________Debug LINK_________________','Traditional Character',self.url,sep='\n')
			text = self.main()
		
		self.title = '<a href="{}">{}</a>'.format(self.url,self.title)
		text = self.title + "\n\n" + (text.split("\n\n",1))[1]
		
		return text


	# --Main--

	def main(self):
		
		if self.url != "":
			if 'bkrs.info' not in self.url:
				self.whatlan()
				
				if self.language == 'en':
					text = ''' English is not implemented yet'''
					return text

				self.title = self.url.capitalize()
				self.url = "https://bkrs.info/slovo.php?ch=" + self.url

				
			self.downloadwpage()
		page_txt = self.readfile()
		main_info = self.parting(page_txt)

		main_info = self.formatting(main_info)

		print('____________Debug MAIN INFO_________________',main_info,sep='\n')

		return main_info



if __name__ == '__main__':
	debug = True
	#a = input("Is there a need for Proxy\n")
	#meow = web(input(), True if a == '' else False)
	if debug == True:
		list_input = input().split(' ')
		print(list_input)
		for i in list_input:
			meow = web(i)
			meow.main()
	else:
		meow = web(input())
		meow.main()
