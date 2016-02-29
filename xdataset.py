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
		self.frange = len(glob.glob(self.template.split("?")[0]))
		self.fheader = cbfphoton2.photonCIF(frame)
		self.geometry = self.SetGeometry

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

	def SetGeometry(self):
		geometry = {}
		axes = self.GetAxes()
		geometry['DISTANCE'] = axes['DX']['_diffrn_scan_axis.displacement_start']
		geometry['SCAN'] = self.fheader['_diffrn_measurement_axis.axis_id']
		geometry['OSCILATION'] = axes[geometry['scan']]['_diffrn_scan_axis.angle_increment']
		geometry['OMEGA'] = {}
		geometry['CHI'] = {}
		geometry['PHI'] = {}
		geometry['OMEGA']['VECTOR'] = '0 -1 0' 	#TODO get from CBF? 
		geometry['OMEGA']['ANGLE'] = axes['OMEGA']['_diffrn_scan_axis.angle_start']	
		geometry['PHI']['VECTOR'] = '0 -1 0' #TODO, now irelevant for omega scans
		geometry['PHI']['ANGLE'] = axes['PHI']['_diffrn_scan_axis.angle_start']	#TODO, now irelevant for omega scans
		geometry['CHI']['VECTOR'] = '0 -1 0' #TODO, now irelevant for omega scans
		geometry['CHI']['ANGLE'] = axes['CHI']['_diffrn_scan_axis.angle_start']	#TODO, now irelevant for omega scans
		geometry['TWOTHETA']['VECTOR'] = '0 -1 0'
		geometry['TWOTHETA']['ANGLE'] = axes['TWOTHETA']['_diffrn_scan_axis.angle_start']
		geometry['X-DETECTOR'] = "{:.5f}".format(math.cos(float(geometry['TWOTHETA']['ANGLE']))) + " 0 " + "{:.5f}".format(math.sin(float(geometry['TWOTHETA']['ANGLE']))) 
		geometry['Y-DETECTOR'] = '0 1 0'
		return geometry
