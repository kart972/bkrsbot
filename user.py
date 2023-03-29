import json


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
		with open(self.path, 'r') as f:
			self.data = json.load(f)

	def save(self):
		with open(self.path, 'w') as f:
			json.dump(self.data, f)
