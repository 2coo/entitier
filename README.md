##### 1. Cabocha & Mecab suulgah #####

https://stmsy.github.io/nlp/
https://qiita.com/katsuta/items/cedb51c8e4156e9918ec

Dictionary ni mecab-ipa-neologd

##### 2. import hiih #####

from entity import Tagger

##### 3. davtaltand bish neg udaa l ajillah gazar Tagger classiin objectiin zarla #####
##### uchir ni Dotroo file aas data unshij bga tul davtaltand bichvel bainga file aas unshij code 130 dahin udaan bolno. #####

# neg udaa l zarlaj jishee
tagger = Tagger()

# harin umnun zarlatsan bolhoor Tagger classin cabocherity classiig hedench udaa ashiglaj bolno
for zadlah_text in data:
	result = tagger.cabocherity(zadlah_text)
	# cabocherity func ni ugiig tag hiij, tuuniigee string helbereer butsaaj bga


