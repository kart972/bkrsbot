import json
import time


class User:

	def __init__(self, data: dict = None):
		self.lan = 'lan'
		self.nick = 'nick'
		self.name = 'name'
		self.path = "./logs/users.json"

		if isinstance(data, dict): self.data = data
		else:
			self.data = {}
			self.load_users()

	def check_user(self, user_id) -> bool:
		if user_id in self.data: return True
		return False

	def add_user(self,
	             user_id: str,
	             user_nick: str,
	             user_name: str,
	             language: str = 'en') -> bool:

		if self.check_user(user_id): return False
		self.data[user_id] = {
		 self.lan: language,
		 'nick': user_nick,
		 'name': user_name
		}
		return True

	def get_info(self, user_id: str, info: str) -> str:
		if user_id not in self.data:
			return
		if info is None:
			return
		if info not in self.data[user_id]:
			return
		return self.data[user_id][info]

	def edit_info(self, user_id: str, info: str, value: str) -> bool:
		if user_id not in self.data: return False
		if info not in self.data[user_id]: return False
		if self.data[user_id][info] == value: return False
		self.data[user_id][info] = value
		return True

	def flush(self) -> dict:
		return self.data

	def load_users(self):
		try:
			with open(self.path, 'r') as f:
				self.data = json.load(f)
		except FileNotFoundError:
			self.data = {}
		

	def save(self):
		with open(self.path, 'w') as f:
			json.dump(self.data, f)


class Logs:

	def __init__(self):
		self.log_string = ''
		self.path = "./logs/logs.log"

	def add(self, information_list: list) -> None:

		current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
		information_list.insert(0,current_time)
		self.log_string += ' - '.join(information_list) + '\n'
		print('Added successfully')

	def read(self,lines:int=0)->str:
		output = lambda a, lines: "".join(a) if lines == 0 else ''.join(a[-lines:]) 
		try:
			with open(self.path)as f:return output(f.readlines(),lines)
		except FileNotFoundError:
			return ''
	
	def save(self) -> bool:
		if self.log_string == '': return False
		try:
			with open(self.path, 'a') as f:
				f.write(self.log_string)
		except FileNotFoundError:
			with open(self.path, 'w') as f:
				f.write(self.log_string)
		self.log_string = ''
		print('Saved successfully')
		return True


class Word:
	def __init__(self,word,pronunciation,meanings,examples=None,similar=None,audio=None,alternatives=None):
		self.word = word
		self.pronunciation = pronunciation
		self.meanings = meanings
		self.examples = examples
		self.similar = similar
		self.alternatives = alternatives
		self.audio = audio
		
		
	def get_audio(self):
		return self.audio

	def get_alternatives(self):
		return self.alternatives
	
	def return_text(self):
		result = []
		validate = lambda a,l:l.append(a) if a != None else None
		
		for i in [self.word,self.pronunciation,self.meanings,self.examples,
		self.similar]:validate(i,result)
		
		return '\n\n'.join(result)
		
