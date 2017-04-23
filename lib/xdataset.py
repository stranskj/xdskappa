import cbfphoton2,os,re,sys,math,glob

class XDataset():
	"""
	Class describing one X-ray difraction dataset
	"""
	def __init__(self,_strTemplate,_intFrame=1):
		"""
		Constructor

		@param _strTemplate: Template of frame name
		@type  _strTemplate: string
		@param _intFrame: Frame number, where a header is read from
		@type _intFrame: 1
		"""
		self.template = _strTemplate
		frame = self.GetFrameName(_intFrame)
		self.frange = len(glob.glob(self.template.split("?")[0] + "*.cbf"))
		self.fheader = cbfphoton2.photonCIF(frame)
		self.geometry = {}
		self.SetGeometry()
		self.detector = {}
		self.SetDetector()

	def GetFrameName(self,frame):
		"""
		Returns a frame name of frame number "frame" from self.template

		@param frame: frame number
		@type frame: int
		"""
		digits = self.template.count("?")
		squest = self.template.index("?")

		prefix = self.template[:squest]
		suffix = self.template[squest + digits:]

		frame_num = prefix + str(frame).zfill(digits) + suffix

		return frame_num
	def GetAxes(self):
		axis = {}
		for loop in self.fheader["loop_"]:
			if "_diffrn_scan_axis.displacement_increment" in loop[0]:
				for ax in loop[1]:
					axis[ax['_diffrn_scan_axis.axis_id']]= ax
			
				break
		return axis
			
		#raise KeyError('No axis information found in image header')
		
	def TwothetaVector(self,twotheta=None):
		"""
		Calculates dectector axes vectors
		
		@param twotheta: twotheta offset of the detector; read from frame header when None
		@type  twotheta: string
		
		@return x-axis vector, y-axis vector as string
		"""
		if twotheta == None:
			axes = self.GetAxes()
			twotheta = axes['TWOTHETA']['_diffrn_scan_axis.angle_start']
			self['TWOTHETA']['ANGLE'] = twotheta
		
		#TODO dependent on twotheta axis vector
		detectorX = "{:.5f}".format(math.cos(math.radians(float(twotheta)))) + " 0 " + "{:.5f}".format(math.sin(math.radians(float(twotheta))))
		detectorY = '0 1 0'
		
		return detectorX, detectorY
		
	def SetOrigin(self,ORGX=None,ORGY=None):
		"""
		Sets detector origin as defined by XDS (the closest point on detector to crystal)
		
		@param ORGX: user defined origin X
		@type  ORGX: int
		@param ORGY: user defined origin Y
		@type  ORGY: int
		"""
		if ORGX:
			self.geometry['ORGX'] = str(ORGX)
		else:
			self.geometry['ORGX'] = str(int(int(self.fheader['X-Binary-Size-Fastest-Dimension'])/2))
			
		if ORGY:
			self.geometry['ORGY'] = str(ORGY)
		else:
			self.geometry['ORGY'] = str(int(int(self.fheader['X-Binary-Size-Second-Dimension'])/2))	
	
	def SetPixelSize(self,QX=None,QY=None):
		"""
		Returns size of pixels in mm
		
		@param QX, QY: user defined pixel sizes
		@type  QX, QY: float 
		
		@return string, string: x-size, y-size of pixel
		"""
		for loop in self.fheader["loop_"]:
			if "_array_structure_list_axis.displacement_increment" in loop[0]:
				for elem in loop[1]:
					if elem['_array_structure_list_axis.axis_id'] == 'ELEMENT_X':
						pixX = elem['_array_structure_list_axis.displacement_increment']
					if elem['_array_structure_list_axis.axis_id'] == 'ELEMENT_Y':
						pixY = elem['_array_structure_list_axis.displacement_increment']
		
		if QX:
			pixX = "{:.5f}".format(QX)
		if QY:
			pixY = "{:.5f}".format(QY)
		
		return pixX, pixY
	
	def SetDetector(self):
		
		pixX, pixY = self.SetPixelSize()
		
		self.detector['Pixel_Size_X']  = pixX
		self.detector['Pixel_Size_Y']  = pixY
		self.detector['Pixel_Count_X'] = self.fheader['X-Binary-Size-Fastest-Dimension']
		self.detector['Pixel_Count_Y'] = self.fheader['X-Binary-Size-Second-Dimension']
		self.detector['Name'] = 'PILATUS'		#TODO
		
	def PhiVector(self,angOmegaStr,angChiStr):
		angOmega = math.radians(float(angOmegaStr))
		angChi   = math.radians(float(angChiStr))
		
		vecPhi = [0]*3		
		vecPhi[0] = math.sin(angChi)*math.cos(angOmega)
		vecPhi[1] = math.cos(angChi) 
		vecPhi[2] = math.sin(angChi)*math.sin(angOmega)
		
		vecPhiStr = ''
		for i in range(3):
			vecPhiStr += "{:.7f}".format(vecPhi[i]) + ' ' 
		
		return vecPhiStr.strip()
	
	def SetOscilation(self,axes,scan):
		oscil = float(axes[scan]['_diffrn_scan_axis.angle_increment'])
		#self.geometry['OSCILATION'] = axes[self.geometry['SCAN']]['_diffrn_scan_axis.angle_increment']
		if oscil < 0:
			oscil *= -1
			ax = self.geometry[scan]['VECTOR'].split()
			axCorr = ''
			for i in range(3):
				coord = -1*float(ax[i])
				axCorr += "{:.7f}".format(coord) + ' '
			axCorr.strip()
		else:
			axCorr = self.geometry[scan]['VECTOR']
			
		oscilStr = 	"{:.7f}".format(oscil)
		
		return oscilStr,axCorr		

	def SetGeometry(self):
		try:
			axes = self.GetAxes()
		except KeyError as e:
			print e
			sys.exit(1)
			
		self.geometry['DISTANCE'] = axes['DX']['_diffrn_scan_axis.displacement_start']
		self.geometry['SCAN'] = self.fheader['_diffrn_measurement_axis.axis_id']
		self.geometry['BEAM']['VECTOR'] = '0 0 1' 	#TODO get from CBF? 
		self.geometry['BEAM']['WAVELENGHT'] = self.fheader['_diffrn_radiation_wavelength.wavelength']
		self.geometry['OMEGA'] = {}
  
		self.geometry['CHI'] = {}
		self.geometry['PHI'] = {}
		self.geometry['TWOTHETA'] = {}
		self.geometry['OMEGA']['VECTOR'] = '0 -1 0' 	#TODO get from CBF? 
		self.geometry['OMEGA']['ANGLE'] = axes['OMEGA']['_diffrn_scan_axis.angle_start']	
		
		self.geometry['PHI']['ANGLE'] = axes['PHI']['_diffrn_scan_axis.angle_start']	
		self.geometry['CHI']['VECTOR'] = '0 -1 0' 
		self.geometry['CHI']['ANGLE'] = axes['CHI']['_diffrn_scan_axis.angle_start']	
		self.geometry['TWOTHETA']['VECTOR'] = '0 -1 0'
		self.geometry['TWOTHETA']['ANGLE'] = axes['TWOTHETA']['_diffrn_scan_axis.angle_start']
		self.SetOrigin()
		self.geometry['PHI']['VECTOR'] = self.PhiVector(self.geometry['OMEGA']['ANGLE'], self.geometry['CHI']['ANGLE'])
		self.geometry['OSCILATION'],self.geometry[self.geometry['SCAN']]['VECTOR'] = self.SetOscilation(axes, self.geometry['SCAN'])
		self.geometry['X-DETECTOR'],self.geometry['Y-DETECTOR'] = self.TwothetaVector(self.geometry['TWOTHETA']['ANGLE'])

def Test():
	datset = XDataset('test/photon2_????.cbf',1)
	
	print "Data range: " + str(datset.frange)
	print "Template: " + datset.template
	print "Frame example: " + datset.GetFrameName(5)
	print "Frame example: " + datset.GetFrameName(10)
	
	print "Geometry:"
	for key in datset.geometry:
		if type(datset.geometry[key]).__name__ == 'str':
			print key + ": " + datset.geometry[key]
		elif type(datset.geometry[key]).__name__ == 'dict':	
			for subkey in datset.geometry[key]:
				print key + ":" + subkey + ": " + datset.geometry[key][subkey]
		else:
			print key + ": type " + type(datset.geometry[key]).__name__
			
		
	print "Detector:"
	for key in datset.detector:
		print key + ": " + datset.detector[key]	
			
	 
if __name__ == "__main__":
	Test()
	sys.exit(0)