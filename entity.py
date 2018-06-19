import re
import unicodedata
import CaboCha
import MeCab

class Tagger:
	def __init__(self):
		self.cabocha = self.init_cabocha()
		self.company_list = self.get_company_list()
		self.location_list = self.get_location_list()
		self.location_keywords = [
			'市',
			'町',
			'区',
			'駅',
			'線',
		]
		self.FULLTEXT = ""
		self.LESS_WORDS_LIST = {}
		self.date_formats = [
			{'en': '([0-9]{1,2}( | of ))?(January|February|March|April|May|June|July|August|September|October|November|December|january|february|march|april|may|june|july|august|september|october|november|december)( \d+[0-9]{1,4},?)?( [0-9]{1,4})?'},
			{'ja': '((\d+)年(\d+)ヶ?月(\d+)日)|(\d+)ヶ?月(\d+)日|(\d+)年|(\d+)ヶ?月|(\d+)日'},
		]
		self.REGEXES = {
			'UrlRe': re.compile('((https?:\/\/)?(www.)?(((([\da-zA-z-]){2,})+|([\d\u30A0-\u30FF-]{2,})|([\d\u3040-\u309F-]{2,})|([\d\u4E00-\u9FFF-]{2,}))\.?)+\.((?!JR)[a-zA-z]{2,6})(\/([a-z0-9]+)?)*)'),
			'DateRe': re.compile('|'.join(['('+row[list(row.keys())[0]]+')' for row in self.date_formats]), re.I),
			'NumberRe': re.compile('(\d+)(万|千)?', re.I),
			'NumberDRe': re.compile('(\d+\.\d+)(万|千)?', re.I),
			'NumberCRe': re.compile('((\d+,((\d+,)*)\d+$))(万|千)?', re.I),
			'TimeRe': re.compile(' <NUMBERD?> (時|分|秒)', re.I),
			'MoneyRe': re.compile('(\$|HK$|Z$|£|€|₨|￥|Z$|円|dollar|dollars|JPY|AUD|USD|EUR|GBP) <NUMBER(D|C)?> (\$|HK$|Z$|£|€|₨|￥|Z$|円|dollar|dollars|JPY|AUD|USD|EUR|GBP)', re.I),
			'PercentRe': re.compile(' <NUMBERD?> (%|割)', re.I),
		}

	def init_cabocha(self):
		### DEFAULT DICTIONARY
		# c = CaboCha.Parser('')
		### NEOLOGD DICTIONARY
		c = CaboCha.Parser('-d dic/mecab-ipadic-neologd')
		return c
	def escape_special_chars(self, text):
		chars = ['.','|','(',')','+','-','*','?','!','[',']']
		for char in chars:
			text = text.replace(char, '\\'+char)
		return text

	def get_company_list(self):
		company_data = open('data/company.txt','r')
		company_text = company_data.read()
		company_data.close()

		company_text = self.escape_special_chars(company_text)

		company_list = []
		for line in company_text.split('\n'):
			if line.strip() == '':
				continue
			if line not in company_list:
				company_list.append(line)

		company_list.sort()
		# company_list.sort(key=len, reverse=False)

		return company_list

	def get_location_list(self):
		cities_data = open('data/cities.txt','r')
		cities_text = cities_data.read()
		cities_data.close()
		stations_data = open('data/stations.txt','r')
		stations_text = stations_data.read()
		stations_data.close()

		# cities_text = self.escape_special_chars(cities_text)
		# stations_text = self.escape_special_chars(stations_text)

		location_list = []

		for line in cities_text.split('\n'):
			if line.strip() == '':
				continue
			if line not in location_list:
				if line.find('\t') > 0:
					for col in line.split('\t'):
						location_list.append(col)
				else:
					location_list.append(line)
		for line in stations_text.split('\n'):
			if line.strip() == '':
				continue
			if line not in location_list:
				if line.find('\t') > 0:
					for col in line.split('\t'):
						location_list.append(col)
				else:
					location_list.append(line)

		location_list.sort()
		# location_list.sort(key=len, reverse=False)

		return location_list
	def BinarySearch(self, search, array):
		left = 0
		right = len(array)-1
		while left <= right:
			mid = int((left+right)/2)
			if array[mid] == search:
				return array[mid]
			elif array[mid] < search:
				left = mid + 1
			elif array[mid] > search:
				right = mid - 1
			else:
				return None
	def is_location(self, word):
		# print(word)
		if self.BinarySearch(search=word, array=self.location_list):
			return True
		elif self.BinarySearch(search=word, array=self.location_list) == None:
			### REMOVE LOCATION KEYWORDS
			if re.search('|'.join(self.location_keywords), word):
				rmved = re.sub('|'.join(self.location_keywords),'',word)
				if self.BinarySearch(search=rmved, array=self.location_list):
					return True
			# elif self.BinarySearch(search=word+next_word, array=self.location_list):
			# 	return 2
			else:
				for keyword in self.location_keywords:
					added = word+keyword
					if self.BinarySearch(search=added, array=self.location_list):
						return True
		return False
			

	def entity(self, text):
		converted = unicodedata.normalize('NFKC', text)
		### ENTITY url, date, number, money, count, percent, count		
		converted = converted.replace('m2', 'METERKVADRAT')
		
		converted = self.REGEXES['UrlRe'].sub(' <WEBSITE> ',converted)
		converted = self.REGEXES['DateRe'].sub(' <DATE> ',converted)
		converted = self.REGEXES['NumberDRe'].sub(' <NUMBERD> ', converted)
		converted = self.REGEXES['NumberCRe'].sub(' <NUMBERC> ', converted)
		converted = self.REGEXES['NumberRe'].sub(' <NUMBER> ', converted)

		converted = converted.replace('METERKVADRAT','m2')

		converted = self.REGEXES['TimeRe'].sub(' <TIME> ',converted)
		converted = self.REGEXES['MoneyRe'].sub(' <MONEY> ', converted)
		converted = self.REGEXES['PercentRe'].sub(' <PERCENT> ', converted)
		converted = re.sub(' (<NUMBERD>|<NUMBERC>) ',' <NUMBER> ', converted)
		
		return converted
	
	def cabocherity(self, sentence):
		sentence = re.sub('&.*?;','',sentence)
		### WEBSITE, DATE, MONEY, NUMBER, PERCENT, TIME
		# entitied = self.entity(sentence)
		### COMPANY NAME
		tree = self.cabocha.parse(entitied)

		result_text = ""
		for i in range(tree.chunk_size()):
			chunk = tree.chunk(i)
			for ix  in range(chunk.token_pos,chunk.token_pos + chunk.token_size):
				# print(tree.token(ix).surface, tree.token(ix).feature)
				if tree.token(ix).surface not in self.LESS_WORDS_LIST:
					self.LESS_WORDS_LIST[tree.token(ix).surface] = 1
				else:
					self.LESS_WORDS_LIST[tree.token(ix).surface] += 1
				if self.BinarySearch(search=tree.token(ix).surface, array=self.company_list):
					result_text += ' COMPANY '
				elif len(set(['名詞','固有名詞','地域']) & set(tree.token(ix).feature.split(','))) == 3:
					result_text += ' LOCATION '
				# elif self.is_location(tree.token(ix).surface):
				# 	result_text += ' LOCATION '
				elif '助詞' == tree.token(ix).feature.split(',')[0]:
					result_text += ' '+tree.token(ix).surface
				elif '記号'  == tree.token(ix).feature.split(',')[0] or ('名詞' == tree.token(ix).feature.split(',')[0] and 'サ変接続' == tree.token(ix).feature.split(',')[1] and not any([False if other == '*' else True for other in tree.token(ix).feature.split(',')[2:]])):
					result_text += ' '
				else:
					result_text += tree.token(ix).surface
			result_text += ' '
		result_text = re.sub(' +', ' ',result_text)
		result_text = result_text.strip()
		
		result_text = re.sub(' LOCATION '+'|'.join(self.location_keywords),' LOCATION ',result_text)

		self.FULLTEXT += result_text + '\n'

		return result_text

	def less_word_to_blank(self):
		sorted_list = sorted((value, key) for (key,value) in self.LESS_WORDS_LIST.items())
		for word in sorted_list:
			searched = re.search('[\da-zA-z]', word[1])
			# print(word)
			# if word[0] == 1 and searched and (len(word) - 1) == (searched.end() - searched.start()):
			# 	print(word[1])
		return self.FULLTEXT
