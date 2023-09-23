class Language:
	def __init__(self):
		self.language = None
		
	# Determine language function
	def whatlan(self, text_input: str) -> bool:
		self.language = None
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
		
		return self.language