#!/usr/bin/python
# -*- coding: utf-8 -*-
# Cifrario DPMC (Dynamic Polynomial Matricial Cipher)
# Author: Andrea Olivari
import sys
import codecs
from random import randint, uniform
from math import *
import numpy as np
import time
from numpy.linalg import *
from collections import OrderedDict
from eval import NumericStringParser
from stringUtilities import extendedAscii, myChr
np.set_printoptions(suppress=True) # remove scientific notation

rows = 0
columns = 0
msg = ""
msg_len = 0
start   = 0
jump    = 0
points  = 0
ilsj    = [] #ilen_istart_ijump
toSend  = []
old_new_y = OrderedDict()
nsp = NumericStringParser()
closest_min = lambda a,l:min(l,key=lambda x:abs(x-a))
closest_max = lambda a,l:max(l,key=lambda x:abs(x-a))


def stringToMatrix(key):
	global rows
	global columns 

	slash_index = key.find("/")
	space_index = key.find(" ")
	rows = int(key[:slash_index])
	columns = int(key[(slash_index+1):space_index])
	content = key[(space_index+1):]
	print u"\n[+] Rows = %s" %rows
	print u"[+] Columns = %s" %columns
	print u"[+] Content = '%s'" %content

	index = 0
	matrix = []
	for r in range (0,rows):
		row = []
		for c in range(0,columns):
			row.append(ord('%s' %content[index]))
			index += 1
		matrix.append(row)

	return np.array(matrix)

def showMatrix(matName,mat):
	print u"\n%s:\n" %matName
	print mat

def getIndex(row,col): # partiamo da 1!
	res = (row-1)*columns+col
	return res

def matrixContainsValue(mat,v,exclude): # exclude e' l'indice da non contare (-1 se non ci interessa un indica da scartare)
	for r in range(0,rows):
		for c in range(0,columns):
			index = getIndex(r,c)
			if(index != exclude and mat[r][c] == v):
				return True
	return False

def removeDup(mat):
	for r in range(0,rows):
		for c in range(0,columns):
			while(matrixContainsValue(mat,mat[r][c],getIndex(r,c))):
				mat[r][c] = mat[r][c]+1

def roundTrick(num):
	#print u"Passo a roundTrick il valore %s" %num
	snum = str(num)
	res = snum
	if(snum[len(snum)-1] == '5'):
		res = snum[:-1]
		res += "6"
	#print u"ritorno %s" %res
	return res

def removeScientificNotation(num):
	#print u"input = %s" %num
	if("e-" not in num):
		return num
	zeros = int(num[(num.find("e")+2):])
	res = "0."
	if(num[0] == '-'):
		res = "-%s" %res
		num = num[1:]
	for x in range(0,zeros-1):
		res += "0"

	dot_index = num.find(".")
	e_index = num.find("e")

	if(dot_index > -1):
		res += num[:dot_index]
		res += num[dot_index+1:e_index]
	else:  
		res += num[:e_index]

	#print u"ritorno %s" %res
	return res

def solvePol(pol, val):
	newpol = ""
	for i in range(0,len(pol)):
		if(pol[i] != 'x'):
			newpol += pol[i]
		else:
			newpol += str(val)

	#print u"\nrisolvo %s e ottengo %s" %(newpol,nsp.eval(newpol))
	return str(nsp.eval(newpol))

def simplify(val):
	count = 0
	significant = False

	if("e-" in val):
		val = removeScientificNotation(val)
	if("." in val):
		dot_index = val.find(".")
		tmp = "%s." %val[:dot_index]
		val = val[(dot_index+1):]
		len_val = len(val)
		while(count < len_val and (count < 3 or significant is False)):
			if(val[count] != '0'):
				significant = True
			tmp += val[count]
			count += 1

		if(count < len_val):
			tmp += val[count]
			count += 1
			val = round(float(roundTrick(tmp)),count-1)
		else:
			val = float(tmp)

	return val

def simplifyMatrixVals(mat):
	for r in range(0,rows):
		for c in range(0,columns):
			val = str(mat[r][c])
			mat[r][c] = simplify(val)

def mod(val,n):
	#print u"%s mod %s = %s" %(val,n,val%n)
	return val%n

def definePars(): # definisce indice di partenza e valore di jump
	global ilsj

	available = points-3
	max_jump = int(available/msg_len)
	print u"\n[i] Il massimo valore possibile per jump e' %s" %max_jump
	jump = randint(1,max_jump)
	
	start = ilsj[0]
	while(start in ilsj):
		start = randint(1,points)
	start = 8

	return start,jump

def initToSend(points):
	global toSend
	for i in range(0,points):
		toSend.append("0")
	#print u"\ntoSend: \n%s" %toSend

def get(mat,i):
	i = mod(i,rows*columns)
	row = i/columns
	column = i%columns
	return mat[row][column]

def encode(i,val):
	print u"i = %s" %i
	num = get(inv_AAt, i*get(AAt,i))*get(AAt,i)
	den = get(A,(get(A,i)*i))
	print u"%s*%s*%s/%s = %s" %(val,get(inv_AAt, i*get(AAt,i)),get(AAt,i),den,val*num/den)
	return val*num/den

def switch(indexes):
	global toSend

	switches = {}
	used = []
	dic_used = {} #test // usiamo le chiavi per effettuare la ricerca (più efficiente)

	print u""
	for i in indexes:
		newpos = mod((i+get(A,i))*get(AAt,i),points)
		ok = False
		while(ok is False):
			try:
				a = dic_used[newpos]
				newpos = mod(newpos+1,points)
			except:
				ok = True
				dic_used[newpos] = ""
				switches[i] = newpos

		'''while(newpos in used):
			print u"quiiiiiii"
			newpos = mod(newpos+1,points)'''

		switches[i] = newpos
		#used.append(newpos)
		#print u"%s --> %s" %(i,newpos)

	print u"\n%s\n" %switches

	newlist = []
	indexes = []
	for i in range(0,points):
		newlist.append(0)
	for oldi,newi in switches.iteritems():
		#print u"%s --> %s" %(oldi,newi)
		newlist[newi] = toSend[oldi]
		indexes.append(newi)

	toSend = newlist[:]
	return indexes

def checkScientificNotations():
	for v in toSend:
		if("e-" in str(v)):
			print u"[+] NOTAZIONE SCIENTIFICA IN %s" %v
			time.sleep(0.5)

def generateRandom(toSend):
	maxi = None
	mini = None
	max_decimals = None
	min_decimals = None

	for v in toSend:
		sv = str(v)
		#print u"\nv = %s" %sv

		if(sv != '0'):
			dec_qty = 0
			decSplit = sv[sv.find(".")+1:]
			#print u"decSplit = %s" %decSplit
			dec_qty = len(decSplit)
			
			if(max_decimals is None or dec_qty > max_decimals):
				max_decimals = dec_qty
			if(min_decimals is None or dec_qty < min_decimals):
				min_decimals = dec_qty
				print u"min_decimals = %s con v = %s" %(min_decimals,v)

			v = float(v)
			if(maxi is None or v > maxi):
				maxi = v
			if(mini is None or v < mini):
				mini = v

	maxi += norm_AAt
	mini -= norm_AAt

	print u"\nmax value = %s" %maxi
	print u"min value = %s\n" %mini

	print u"max decimals = %s" %max_decimals
	print u"min decimals = %s" %min_decimals

	for i in range(0,len(toSend)):
		if(toSend[i] == '0'):
			toSend[i] = uniform(maxi,mini)
			decimals = randint(min_decimals,max_decimals)
			#print u"decimals = %s" %decimals
			toSend[i] = round(toSend[i],decimals)

	return toSend

def crypt():
	global ilsj
	global start
	global jump
	global msg_len

	# calcolo gli indici su cui andro' a scrivere
	indexes = []
	indexes += ilsj
	
	#checkScientificNotations()

	i = 0
	act_index = start
	while(i < msg_len):
		act_index = mod(act_index,len(toSend))
		if(act_index not in indexes):
			indexes.append(act_index)
			act_index += jump
			i += 1
		else:
			act_index += 1

	print u"\nlen(indexes) = %s" %len(indexes)
	print u"[+] indexes:\n%s" %indexes

	print u""
	# inserisco len in ilen
	toSend[indexes[0]] = encode(indexes[0],msg_len)
	toSend[indexes[1]] = encode(indexes[1],start)
	toSend[indexes[2]] = encode(indexes[2],jump)

	#checkScientificNotations()

	#print u"\n%s" %toSend
	for i in range(0,msg_len):

		#print u"\nCifro '%s' (abbiamo ord(%s) = %s)" %(msg[i],msg[i], extendedAscii(ord('%s' %msg[i])))
		toSend[indexes[i+3]] = encode(indexes[i+3],extendedAscii(ord('%s' %msg[i])))

	checkScientificNotations()

	print u"\n%s" %toSend
	for i in range(0,len(toSend)):
		if("e-" in str(toSend[i])):
			toSend[i] = removeScientificNotation(toSend[i])

	# Adesso eseguiamo gli spostamenti
	# yi --> ((i+aval(i mod j))*tval(i mod k)) mod np 
	indexes = switch(indexes)

	print u"\nSwitched toSend: \n%s\n" %toSend

	checkScientificNotations()

	for i in range(0,len(toSend)):
		#print u"chiamo simplify(%s)" %str(toSend[i])
		toSend[i] = simplify(str(toSend[i]))

	checkScientificNotations()
	print u"%s\n" %toSend

	'''for i in range(0,len(toSend)):
		print u"toSend[%s] = %s" %(i,toSend[i])'''

	print u"indexes: \n%s\n" %indexes
	newToSend = toSend[:]
	for i in indexes:
		den = simplify(solvePol(pol,i))
		#print u"%s/%s" %(toSend[i],den)
		if(den <= 0):
			den = 1.0  
		newToSend[i] = divResult(float(toSend[i]),den)


	checkScientificNotations()
	print u"\nnewToSend:\n%s\n" %newToSend

	newToSend = generateRandom(newToSend)
	
	for i in range(0,len(newToSend)):
		newToSend[i] = removeScientificNotation(str(newToSend[i]))

	checkScientificNotations()
	print u"\nfinal toSend: \n\n%s\n" %newToSend

	of = open("decrypt_input.txt","w")
	toWrite = "["
	for v in newToSend:
		toWrite += "'%s', " %v

	toWrite = toWrite[:-2]
	toWrite += "]"
	of.write(toWrite)
	of.close()

def divResult(num,den):
	sres = str(num/den)
	snum = str(num)
	sden = str(den)
	calc = sres[:]
	'''print u"\nsnum = %s" %snum
	print u"sden = %s" %sden
	print u"vogliamo ottenere %s a partire da %s e %s" %(snum,sres,den)'''

	sres = removeScientificNotation(sres)
	if(sres[0] == '-'):
		tmp = "-"
		sres = sres[1:]
	else:
		tmp = ""
	ftmp = 0.0
	for c in sres:
		tmp += c
		ftmp = float(tmp)
		calc = str(simplify(str(ftmp*den)))
		#print u"%s * %s = %s" %(ftmp,den,calc)
		if(calc[0:len(snum)] == snum):
			#print u"%s * %s = %s" %(ftmp,den,calc)
			#print u"[OK]"
			break

	return ftmp

# --------------------------------- decrypt ----------------------------------

def readInput(msg):
	vector = []
	started = False
	tmp = ""

	for c in msg:
		if started and c != '\'':
			tmp += c
		elif c == '\'' and started is False:
			started = True
		elif c == '\'' and started:
			started = False
			vector.append(str(tmp))
			tmp = ""

	return vector

def getOldy(index):
	polRes = simplify(solvePol(pol,index))
	if(polRes <= 0):
		polRes = 1.0
	res = vector[index]*polRes
	#print u"oldy(%s) = %s*%s = %s" %(index,vector[index],simplify(solvePol(pol,index)),res)
	return res

def recoverVal(oldy,index):
	#print u"%s / (%s / %s)" %(oldy,(get(inv_AAt,index*get(AAt,index))*get(AAt,index)),(get(A,get(A,index)*index)))
	res = oldy/((get(inv_AAt,index*get(AAt,index))*get(AAt,index))/( get(A,get(A,index)*index)))
	return res

def recoverValues(origVector):
	msgValues = []
	'''print u"\nold_new_indexes pairs: \n"
	print old_new_y'''
	k = 0

	logfile = open("log","w")
	print u""

	for iorig,i in old_new_y.iteritems():
		got = int(round(simplify(str(recoverVal(origVector[k],iorig))),0))
		msgValues.append(got)
		#print u"abbiamo iorig=%s, i=%s e origVector[%s] = %s" %(iorig,i,k,origVector[k])
		#logfile.write("\nabbiamo iorig=%s, i=%s e origVector[%s] = %s" %(iorig,i,k,origVector[k]))
		#print "ho trovato %s e tramite semplificazione ho tenuto -> %s, che e' uguale a %s" %(recoverVal(origVector[k],iorig),got,unichr(got))
		#logfile.write("\nho trovato %s e tramite semplificazione ho tenuto -> %s, che e' uguale a %s" %(recoverVal(origVector[k],iorig),got,unichr(got)))
		k += 1

	logfile.close()
	return msgValues

def recoverOrigIndexes(): # ritorna gli originali indici usati (non contiene ilen,istart e ijump)
	indexes = []
	for v in ilsj:
		indexes.append(int(v))
	
	act_index = start
	i = 0
	while(i < msg_len):
		act_index = mod(act_index,vector_len)
		if(act_index not in indexes):
			indexes.append(act_index)
			act_index += jump
			i += 1
		else:
			act_index += 1

	return indexes

def closestMatch(val,free_indexes):
	found = closest_min(val,free_indexes)

	if(found >= val):
		return found
	return closest_max(val,free_indexes)


def recoverFinalIndexes(finalIndexes,origIndexes):
	newIndexes = []
	oldIndexes = origIndexes[3:]
	free_indexes = []
	for i in range(0,vector_len):
		free_indexes.append(True)

	for v in finalIndexes:
		newIndexes.append(int(v))
		free_indexes[v] = False
	for i in oldIndexes:
		newpos = mod((i+get(A,i))*get(AAt,i),vector_len)

		while(free_indexes[newpos] is False):
			#print u"quiiii recoverFinalIndexes, i = %s" %i
			newpos = mod(newpos+1,vector_len)

		free_indexes[newpos] = False
		newIndexes.append(newpos)
		#print u"%s --> %s" %(i,newpos)

	print u"esco da recoverFinalIndexes.."
	return newIndexes

def recoverOrigVector(indexes):
	origVector = []

	for i in indexes:
		polRes = simplify(solvePol(pol,i))
		if(polRes <= 0):
			polRes = 1.0
		yi = vector[i]
		product = polRes*yi
		simpleProduct = simplify(str(polRes*yi))
		origVector.append(simpleProduct)
		 #print u"oldy(%s) = %s*%s = %s --> %s" %(i,yi,polRes,product,simpleProduct)

	return origVector

def defineOldNewPairs(origIndexes,finalIndexes):
	global old_new_y

	for i in range(0,len(origIndexes)):
		old_new_y[origIndexes[i]] = finalIndexes[i]
		#print u"%s <--> %s" %(origIndexes[i],finalIndexes[i])
	print u""

def decode(msgValues):
	res = ""
	for v in msgValues:
		res += myChr(v)
		'''if(v == 138):
			res += u'è'
		else:
			res += unichr(v)'''
	return res

def decrypt():
	global start
	global jump
	global msg_len

# indice contenente la lunghezza del messaggio
	ilen = mod(det_AAt,points)
	print u"\n[+] ilen  = %s" %ilen

	#indice contenente l'indice di partenza del messaggio
	istart = mod(norm_AAt,points)
	print u"[+] istart = %s" %istart
	if(istart == ilen):
		istart = mod(istart+1,points)
	#indice contenente il valore di jump
	ijump = mod(norm_AAt*det_AAt,points)
	while(ijump == istart or ijump == ilen):
		ijump = mod(ijump+1,points)
	print u"[+] ijump  = %s" %ijump

	ilsj.append(ilen)
	ilsj.append(istart)
	ilsj.append(ijump)

	for i in range(0,len(vector)):
		try:
			vector[i] = float(vector[i])
		except:
			print u"vector[%s] = %s" %(i,vector[i])
			sys.exit(1)
	print u""

	newilen   = mod((ilen+get(A,ilen))*get(AAt,ilen),points)
	newistart = mod((istart+get(A,istart))*get(AAt,istart),points)
	if(newistart == newilen):
		istart = mod(newistart+1,points)
	newijump  = mod((ijump+get(A,ijump))*get(AAt,ijump),points)
	while(newijump == newistart or newijump == newilen):
		newijump = mod(newijump+1,points)

	print u"newilen   = %s" %newilen
	print u"newistart = %s" %newistart
	print u"newijump  = %s\n" %newijump
	# rimuovo le modifiche indotte dal polinomio
	oldyilen   = getOldy(newilen)
	oldyistart = getOldy(newistart)
	oldyijump  = getOldy(newijump)

	msg_len = int(round(simplify(str(recoverVal(oldyilen,ilen))),0))
	start   = int(round(simplify(str(recoverVal(oldyistart,istart))),0))
	jump    = int(round(simplify(str(recoverVal(oldyijump,ijump))),0))

	print u"\nrecovered msg_len   = %s" %msg_len
	print u"recovered start     = %s" %start
	print u"recovered jump      = %s" %jump

	origIndexes = recoverOrigIndexes()
	#print u"\ngli indici originali prima del riordinamento erano:\n\n%s\n" %origIndexes

	finalIndexes = [newilen,newistart,newijump]
	finalIndexes = recoverFinalIndexes(finalIndexes,origIndexes)
	#print u"gli indici finali dopo il riordinamento sono: \n\n%s\n" %finalIndexes

	defineOldNewPairs(origIndexes[3:],finalIndexes[3:])

	print u"Rimuoviamo le modifiche indotte dal polinomio..\n"
	# adesso rimuoviamo le modifiche indotte dal polinomio
	origVector = recoverOrigVector(finalIndexes[3:])

	msgValues = recoverValues(origVector)
	#print u"\nmsgValues:\n\n%s\n" %msgValues

	#print u"\nMessaggio decifrato: \n\n'%s'\n" %decode(msgValues)
	return decode(msgValues)

# -----------------------------------------------------------------------------

# Key
start_time = time.time()
pol = "sin(x^2)-tan(x/3)+(x^2)"; 
print u"\n[+] Polynom key = %s\n" %pol
print u"[+] String key: "
A = stringToMatrix("7/7 AEOGASKAKSDKSDKSDKALALAKWI9211234567890987ABGH518"); 
#A = stringToMatrix("4/4 AEOGC IMFNHQBDPL")

showMatrix("A",A)
# A trasposta
At = A.transpose()
showMatrix("At",At)
# A*At
AAt = np.matmul(A,At)
showMatrix("AAt",AAt)
# AAt senza duplicati
removeDup(AAt)
showMatrix("AAt with no duplicates",AAt)

det_AAt = int(det(AAt))
print u"\ndet(AAt) = %s\n" %det_AAt
norm_AAt = int(norm(AAt, np.inf))
print u"norm(AAt) = %s" %norm_AAt

inv_AAt = inv(AAt)
showMatrix("inv(AAt)",inv_AAt)

simplifyMatrixVals(inv_AAt)
inv_AAt[0][0] = '{:.10f}'.format(inv_AAt[0][0])
showMatrix("inv(AAt) simplified",inv_AAt)

removeDup(inv_AAt)
showMatrix("inv(AAt) with no duplicates",inv_AAt)

print u"\n/*--------------*\\"
print u"| 1) Encrypt     |"
print u"| 2) Decrypt     |"
print u"\*--------------*/"
choice = input(" -> ")

if(choice == 1):
	print u"\nInput file content: "
	msg = codecs.open('crypt_input.txt', 'r', encoding='utf-8').read()
	print u"\n'%s'" %msg

	msg_len = len(msg)
	print u"\n[+] Message length: %s" %msg_len

	points = msg_len

	while(int(points) < (msg_len+3)):
		points = raw_input("[*] Number of values to send [default: %s] -> " %(msg_len+3))
		if(len(points) == 0):
			points = str(msg_len+3)
		if(points < (msg_len+3)):
			print u"[!] The maxium number of values to send is %s." %(msg_len+3)

	points = int(points)
	print u"\n[+] points = %s" %points
	# indice contenente la lunghezza del messaggio
	ilen = mod(det_AAt,points)
	print u"[+] ilen = %s" %ilen

	#indice contenente l'indice di partenza del messaggio
	istart = mod(norm_AAt,points)
	if(istart == ilen):
		istart = mod(istart+1,points)
	print u"[+] istart = %s" %istart
	#indice contenente il valore di jump
	ijump = mod(norm_AAt*det_AAt,points)
	while(ijump == istart or ijump == ilen):
		ijump = mod(ijump+1,points)
	print u"[+] ijump = %s" %ijump

	ilsj.append(int(ilen))
	ilsj.append(int(istart))
	ilsj.append(int(ijump))

	start, jump = definePars()
	print u"[+] start = %s" %start
	print u"[+] jump = %s" %jump

	# da qui comincia la fase di cifratura
	# inizializzo toSend
	initToSend(points)
	crypt()

elif(choice == 2):
	#print u"\nIl file di input contiene il seguente messaggio:"
	msg = codecs.open('decrypt_input.txt', 'r', encoding='utf-8').read()
	#print u"\n'%s'" %msg
	vector = readInput(msg)
	#print vector
	vector_len = len(vector)
	print u"\n[+] Vector length: %s" %vector_len

	points = vector_len
	output = codecs.open('decrypted.txt', 'w', encoding='utf-8')
	output.write(decrypt())
	output.close()

else:
	print u"\n[!] Invalid choice!\n"

end_time = time.time()
print "\nExecution Time: %s" %(end_time-start_time)

