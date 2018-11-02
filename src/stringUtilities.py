

def extendedAscii(val):
	newval = val
	#print "extendedAscii prende in input -> %s" %val

	if(val > 127):
		if(val == 242):   # ò
			newval = 149
		elif(val == 232): # è
			newval = 138
		elif(val == 249): # ù
			newval = 151
		elif(val == 224): # à
			newval = 133
		elif(val == 236): # ì
			newval = 141
		elif(val == 228): # ä
			newval = 132
		elif(val == 246): # ö
			newval = 148
		elif(val == 252): # ü
			newval = 129
		elif(val == 200): # È
			newval = 144 
		elif(val == 171): # «
			newval = 174
		elif(val == 187): # »
			newval = 175

	#print "e ritorna %s" %newval
	return newval

def myChr(val):
	#print "myChr prende in input %s" %val
	char = unichr(val)

	if(val > 127):
		if(val == 130):
			char = u'é'
		elif(val == 132):
			char = u'ä'
		elif(val == 133):
			char = u'à'
		elif(val == 137):
			char = u'ë'
		elif(val == 138):
			char = u'è'
		elif(val == 141):
			char = u'ì'
		elif(val == 144):
			char = u'È'
		elif(val == 145):
			char = u'æ'
		elif(val == 148):
			char = u'ö'
		elif(val == 149):
			char = u'ò'
		elif(val == 151):
			char = u'ù'
		elif(val == 160):
			char = u'á'
		elif(val == 161):
			char = u'í'
		elif(val == 162):
			char = u'ó'
		elif(val == 163):
			char = u'ú'
		elif(val == 174):
			char = u'«'
		elif(val == 175):
			char = u'»'
		elif(val == 168):
			char = u'¿'
		elif(val == 169):
			char = u'®'

	return char