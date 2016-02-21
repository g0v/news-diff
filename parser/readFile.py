import json

def is_json(myjson):
	try:
		json_object = json.loads(myjson)
	except ValueError, e:
		return False
	return True

def findRef(refurl):
	if 

#
# read file
#
lines = open('./extract/20160201.txt').readlines()
meta = ''
title = ''
content = ''
for i in range(0, len(lines)):	
	currentLine = lines[i]
	if is_json(currentLine) or (len(meta) == 0):
		#
		# output previous
		#
		if len(meta)>0:
			meta = json.loads(meta)
			#
			# get news from
			#
			refUrl =  meta['url']

			break
		#
		# new block
		#
		meta = currentLine
		title = '' 
		content = ''
	elif len(meta) > 0 and len(title) == 0:
		title = currentLine
	else:
		content += currentLine
