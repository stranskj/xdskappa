#!/bin/python
def GetEolChar(sdata):
	for eolc in ['\r\n','\r','\n'] :
		if eolc in sdata :
			break
	return eolc

import re,sys,os

class photonCIF(dict):	

	def __init__(self,strFilename=None):
		dict.__init__(self)
		self._ordered = []
		if strFilename is not None:  # load the file)
			self.GetHeader(strFilename)
	def __setitem__(self, key, value):
		if key not in self._ordered:
			self._ordered.append(key)
		return dict.__setitem__(self, key, value)

	def pop(self, key, default=None):
		if key  in self._ordered:
			self._ordered.remove(key)
		return dict.pop(self, key, default)

	def popitem(self, key, default=None):
		if key  in self._ordered:
			self._ordered.remove(key)
		return dict.popitem(self, key, None)


	def analyseOneLoop(self,fields, start_idx):		#fabio/cbfimage.py
		"""Processes one loop in the data extraction of the CIF file
	    @param fields: list of all the words contained in the cif file
	    @type fields: list
	    @param start_idx: the starting index corresponding to the "loop_" key
		@type start_idx: integer
		@return: the list of loop dictionaries, the length of the data
			extracted from the fields and the list of all the keys of the loop.
		@rtype: tuple
		"""
		loop = []
		keys = []
		i = start_idx + 1
		finished = False
		while not finished:
			if fields[i][0] == "_":
				keys.append(fields[i])
				i += 1
			else:
				finished = True
		data = []
		while True:
			if i >= len(fields):
				break
			elif len(fields[i]) == 0:
				break
			elif fields[i][0] == "_":
				break
			elif fields[i] in ("loop_", "stop_", "global_", "data_", "save_"):
				break
			else:
				data.append(fields[i])
				i += 1
	
		for k in range(len(data)) :
			element = {}
			row = data[k].split(" ")
			while row[0] == '' :
				del row[0]
			#l = 0
			for l,key in enumerate(keys) :		# TODO: what if len(row) > len(keys)
				if l < len(row):
					element[key] = row[l]
				else:
					element[key] = "?"
		#	l += 1

			loop.append(element)
			
	#        if len(data) < len(keys):
	#            element = {}
	#            for j in keys:
	#                if k < len(data):
	#                    element[j] = data[k]
	#                else :
	#                    element[j] = "?"
	#                k += 1
	#            loop.append(element)
	
	#       else:
	#           for i in range(len(data) / len(keys)):
	#               element = {}
	#               for j in keys:
	#                   element[j] = data[k]
	#                   k += 1
	#               loop.append(element)"""
		return loop, 1 + len(keys) + len(data), keys
	
		
	def GetHeader(self,frame):
	
		try :
			frame_file = open(frame,'r')
		except IOError :
			print("File not found: " + frame)
			sys.exit(1)
		
#		header = {}
	
		frame_split = frame_file.read().split('--CIF-BINARY-FORMAT-SECTION-')		#last '-' omitted to pervent empty first line later in binary processing
		frame_header = frame_split[0]
		frame_binary = frame_split[1]
		eolc = GetEolChar(frame_header)
		fields = frame_header.split(eolc)
	#	print fields
	
	#	Parts of _parseCIF from fabio/cbfimage.py
		loopidx = []
		looplen = []
		loop = []
	
		for idx, field in enumerate(fields):
			if field.lower() == "loop_":
				loopidx.append(idx)
		if loopidx:
			for i in loopidx:
				loopone, length, keys = self.analyseOneLoop(fields, i)
				loop.append([keys, loopone])
				looplen.append(length)
				
			for i in range(len(loopidx) - 1, -1, -1):	# omit loops from fields
				f1 = fields[:loopidx[i]] + fields[loopidx[i] + looplen[i]:]
				fields = f1
			
			self["loop_"] = loop
				
		for i in range(len(fields) - 1):
			row = fields[i].split(' ')
			if len(row) == 0:
				continue
			if len(row) == 1:
				row.append("?")
			if len(row) > 2:
				par = ''
				for j in range(1,len(row)-1,1):
					par = par + row[j]
					row[1] = par
			self[row[0]] = row[1]
		
		# process binary part (get header)
		binary = frame_binary.split(eolc)
		for row in binary :
			if len(row) > 0:
				if re.match('[a-zA-Z_]',row[0]) :
					row_split = row.split(': ')
					self[row_split[0]] = row_split[1]
				else:
					pass
			else:
				break		#binary header should end with empty line (it does at least for Photon2, Feb 2016)
	#	print loop
	#	print looplen
	#	print fields
#		return header

def Test():
	hd = photonCIF('photon.cbf')
	print(hd)
	print(hd['_diffrn_radiation_wavelength.wavelength'])
	print(hd['_diffrn_measurement_axis.axis_id'])
	
if __name__ == "__main__":
	import sys,re

	Test()
#	print hd 
#	print hd['_diffrn_radiation_wavelength.wavelength']
#	print hd['_diffrn_measurement_axis.axis_id']
	
	sys.exit(0)

