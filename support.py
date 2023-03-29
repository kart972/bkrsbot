from bs4 import BeautifulSoup
import json
import requests

class extracter:
	# Delete number for more cleaner database
	def delete_number(self,string):
		if ')' in string:
			string_list = string.split(')',1)
			#print("TRUE")
			# Check is there a numbre in front of ( if is then remove it
			try:
				num = int(string_list[0])
				string = string_list[1]
				return string
			except:
				return string
		else:
			return string
			

	# Extract meanings from bs options
	def handle_data(self,ru_div):
		
		m2_lines = []
		m3_lines = []
		type_lines = []
		lines = []
		
		all_div = ru_div.find_all("div")
		
		# Reverse everything only ONE* time
		all_div = all_div[::-1]
		
		# Check if there are words'types like verb, noun, measureword ,etc
		if "I " in str(ru_div):
			for i in all_div:
				cleanup = True
				attrs = i.attrs
				#if i.find("i") is not None: print("--------DEBUGING--------",i,sep='\n')
				if {"class":["m2"]} == attrs:
					m2_lines.append(i.get_text())
				elif{"class":["m3"]} == attrs:
					m3_lines.append(i.get_text())
				elif attrs == {}:
					if lines[-1] == ['type']:
						continue                    						
					i_item = i.find("i")
					#print("--------DEBUGING--------",i,i_item,sep='\n')
					if i_item is not None:
						type_lines.append(i_item.get_text())
					else:													# Spetial check for 结果
						type_lines.append(str((((i.get_text()).split(' ',1))[1])))
					attrs ={"class":['type']}
				else:
					cleanup = False
				if cleanup:
					lines.append(attrs["class"])

		else:		
			# If there is only one div in div.ru
			if all_div == []:
				m2_lines = [ru_div.get_text()]
				lines.append('m2')
				#ONE*
				
			else:		
				for i in all_div:
					#print("--------DEBUGING--------",i,sep='\n')
					cleanup = True
					attrs = i.attrs
					if {"class":["m2"]} == attrs:
						m3_lines.append(i.get_text())
						attrs ={"class":['m3']}
					elif attrs == {}:
						m2_lines.append(i.get_text())
						attrs ={"class":['m2']}
					else:
						cleanup = False
					if cleanup:
						lines.append(attrs["class"])
			
			lines.append('type')
			type_lines.append(None)
			
		
		
		# --Beta-- Remove numbers
		m2_lines = [self.delete_number(m) for m in m2_lines]
			
			
		#print("----Main DEBUG----",m2_lines,len(m2_lines),m3_lines,type_lines,lines,sep="\n\n")
		

		m2_count = 0
		m3_count = 0
		type_count = 0
		m3_list = []
		full_dic = []
		
		# Get particular string from list
		getlist = lambda llist,number: [llist[i] for i in number]
		
		# Words Plus Expamples Dictinary
		word_exp_dic = []
		
		# Reverse read
		for line in lines:
			if 'm2' in line:
				# Revers example list and get examples from a list
				example_list = getlist(m3_lines,m3_list)
				if example_list == []:example_list=None
				
				word_exp_dic.append({"definition":m2_lines[m2_count],"examples": example_list})
				
				m3_list = []
				m2_count+=1
				
				
			elif 'm3' in line:
				m3_list.append(m3_count)
				m3_count+=1
			elif 'type' in line:
				word_exp_dic.reverse()
				full_dic.append({"type":type_lines[type_count],"all_definitions":word_exp_dic})
				type_count+=1
				word_exp_dic = []
				
		
		
		# Reverse Back list
		full_dic = full_dic[::-1]
		
		
		return full_dic

	def main(self,char):
		text = requests.get("https://bkrs.info/slovo.php?ch="+char).text

		soup = BeautifulSoup(text, 'html.parser')

		# Get Main text
		ru_div = soup.find("div",attrs={"class": "ru"})
		
		# Get meanings	
		meanings_dic = self.handle_data(ru_div)

		return meanings_dic