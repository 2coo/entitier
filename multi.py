from multiprocessing import Pool, TimeoutError, cpu_count
import numpy as np
from entity import Tagger
import os
import time

def multi_function(splitted_array):
	result_file = open('result.txt', 'a')
	for index, ads in enumerate(splitted_array):
		print(index)
		result = tagger.cabocherity(ads)
		# print(result)
		result_file.write(result+'\n')
	result_file.close()
	

if __name__ == '__main__':
	started = time.time()

	read_file = open('source.txt', 'r')
	all_text = read_file.read()
	read_file.close()

	
	# ## WRITING FILE
	if os.path.exists(os.path.realpath('result.txt')):
		os.remove(os.path.realpath('result.txt'))

	tagger = Tagger()
	unique_data = list(set(tagger.entity(all_text).split('\n\n')))

	result_file = open('result.txt', 'a')
	for index, row in enumerate(unique_data):
		print(index)
		print(row)
		result = tagger.cabocherity(row)
		result_file.write(result+'\n')

	# blanked = tagger.less_word_to_blank()
	# result_file.write(blanked)
	result_file.close()
	
	
	# cpuCount = cpu_count() - 1
	# dataframe_split = np.array_split(unique_data, 100)
	# tagger = Tagger()
	# print(tagger.location_list)
	# print(tagger.cabocherity('２４時間年中無休・低月会費で使い放題。入会キャンペーン中！横浜市港南区最戸'))
	# pool = Pool(processes=cpuCount)
	# pool.map(multi_function, dataframe_split)
	# pool.close()
	# pool.join()

	print(time.time() - started)
