import cbfphoton2,re,os,sys,glob

MINIMAL_KEY= ['JOB', 'NAME_TEMPLATE_OF_DATA_FRAMES', 'DATA_RANGE', 'SPOT_RANGE', 'ORGX', 'ORGY', 'OSCILLATION_RANGE', 'X-RAY_WAVELENGTH', 'DETECTOR_DISTANCE', 'SPACE_GROUP_NUMBER', 'UNIT_CELL_CONSTANTS']
MULTIPARAM = ['EXCLUDE_RESOLUTION_RANGE','SPOT_RANGE']
class XDSINP(dict):
	"""
	Class for working with single XDS.INP
	"""
	def __init__(self, _strPath, _Dataset=None):
		"""
		Constructor

		@param _strPath: Path where to put/find XDS.INP
		@type  _strPath: string
		@param _Dataset: Dataset related to the XDS.INP
		@type  _Dataset: Dataset object
		"""
		self = {}
		self.path = _strPath + "/XDS.INP"
		self.dataset = _Dataset

		if os.path.isfile(self.path):
			self.read()

	def read(self):
		"""
		Reads XDS.INP from self.path
		"""
		if not os.path.isfile(self.path):
			raise IOError('File not found: ' + self.path)
			return
		fin = open(self.path,'r')
		for line in fin.read().split('\n'):
			self.SetParam(line)

		return

	def write(self):
		"""
		Writes dict(self) content to XDS.INP
		"""
		fout = open(self.path, 'w')
		try:
			for key in MINIMAL_KEY:
				fout.write(self.GetParam(key) + '\n')
		except KeyError as err:
			print err +' in ' + self.path
			exit(1)

		for key,param in self:
			if key not in MINIMAL_KEY:
				fout.write(self.GetParam(key) + '\n')
				
		return

	def GetParam(self,_param):
		"""
		Get parametr _param as a string in format of XDS.INP row

		@param _param: Parametr name as in XDS.INP
		@type  _param: list of string

		@return type: string
		"""	

		try :			
			param = []
			for par in self[_param]:
				param.append(_param + '= ' + par)
		except KeyError:
			param = None
			raise KeyError('Parametr ' + _param + 'not found')
		return param 

	def SetParam(self,_param):
		"""
		SGet parametr _param as a string in format of XDS.INP row

		@param _param: Parametr with value as row in XDS.INP
		@type  _param: list of string
		"""
		par = _param[0].split("=")
		key = par[0].strip(' \r\n\t')
		if _param[0] not in MULTIPARAM and len(_param) > 1:
			raise IOError('Only one occurance of parameter ' + key + 'allowed')
			exit(1)
		for row in _param:
			par = row.split("=")
			key = par[0].strip(' \r\n\t')
			value = par[1].strip(' \r\n\t')
			if not key[0] == '!':
				self[key] = value
				

	def setXDSINP(self,path,strFrame):
		fheader = cbfphoton2.photonCIF(strFrame)
#	        axis = GetAxis(fheader)
		data_range = self.dataset.frange
		scan = self.dataset.geometry['SCAN']
		#QX= TODO
		#QY= TODO
		self['JOB'] = 'XYCORR INIT COLSPOT IDXREF DEFPIX INTEGRATE CORRECT'
		self['ORGX'] = str(ORGX)
		self['ORGY'] = str(ORGY)
		self['DETECTOR_DISTANCE'] = self.dataset.geometry['DISTANCE']
		self['OSCILLATION_RANGE'] = self.dataset.geometry['OSCILATION']
		self['X-RAY_WAVELENGTH'] = fheader['_diffrn_radiation_wavelength.wavelength']
		self['NAME_TEMPLATE_OF_DATA_FRAMES'] = self.dataset.template
#       	self['REFERENCE_DATA_SET'] = ''
		self['DATA_RANGE'] = '1 ' + str(data_range)
		self['SPOT_RANGE'] = '1 ' + str(int(data_range/2))
		self['SPACE_GROUP_NUMBER'] = '0'
		self['UNIT_CELL_CONSTANTS'] = '70 80 90 90 90 90'
		self['INCLUDE_RESOLUTION_RANGE'] = '50 0'
		self["FRIEDEL'S_LAW"] = 'FALSE'
		self['STRICT_ABSORPTION_CORRECTION'] = 'TRUE'
		self['TRUSTED_REGION'] = '0.0 1.2'
		self['VALUE_RANGE_FOR_TRUSTED_DETECTOR_PIXELS'] = '6000. 30000.'
		self['STRONG_PIXEL'] = '4'
		self['MINIMUM_NUMBER_OF_PIXELS_IN_A_SPOT'] = '4'
		self['REFINE(IDXREF)'] = 'CELL BEAM ORIENTATION AXIS ! DISTANCE POSITION'
		self['REFINE(INTEGRATE)'] = 'DISTANCE POSITION BEAM ORIENTATION ! AXIS CELL'
		self['DETECTOR'] = 'PILATUS'
		self['MINIMUM_VALID_PIXEL_VALUE'] = '0'
		self['OVERLOAD'] = fheader['_array_intensities.overload']
		self['SENSOR_THICKNESS'] = 0
		self['NX'] = fheader['X-Binary-Size-Fastest-Dimension']
		self['NY'] = fheader['X-Binary-Size-Second-Dimension']
		self['QX'] = QX
		self['QY'] = QY
		self['ROTATION_AXIS'] = self.dataset.geometry[scan]['VECTOR']
		self['DIRECTION_OF_DETECTOR_X-AXIS'] = self.dataset.geometry['X-DETECTOR']
		self['DIRECTION_OF_DETECTOR_Y-AXIS'] = self.dataset.geometry['X-DETECTOR']
		self['INCIDENT_BEAM_DIRECTION'] = '0 0 1'
		self['FRACTION_OF_POLARIZATION'] = '0.98' #TODO: test fheader['_diffrn_radiation_wavelength.polarizn_source_ratio']
		self['POLARIZATION_PLANE_NORMAL'] = '0 1 0'


# 	def MakeXDSINP(self,path):
#         	os.mkdir(path)
# 	        if not os.path.isfile(path + "/XDS.INP"):
#         	        fxds = open(path + "/XDS.INP",'w')
#                 	fxds.write("! written by xdskappa version "+ VERSION)
# 	                fxds.write("""
# JOB= XYCORR INIT COLSPOT IDXREF DEFPIX INTEGRATE CORRECT
# ORGX= XXX ORGY= XXX  ! check these values with adxv !
# DETECTOR_DISTANCE= XXX
# OSCILLATION_RANGE= XXX
# X-RAY_WAVELENGTH= XXX
# NAME_TEMPLATE_OF_DATA_FRAMES=photon.cbf
# ! REFERENCE_DATA_SET=xxx/XDS_ASCII.HKL ! e.g. to ensure consistent indexing
# DATA_RANGE=
# SPOT_RANGE=
# ! BACKGROUND_RANGE=1 10 ! rather use defaults (first 5 degree of rotation)
# 
# SPACE_GROUP_NUMBER=0                   ! 0 if unknown
# UNIT_CELL_CONSTANTS= 70 80 90 90 90 90 ! put correct values if known
# INCLUDE_RESOLUTION_RANGE=50 0  ! after CORRECT, insert high resol limit; re-run CORRECT
# ! IDXREF now obeys INCLUDE_RESOLUTION_RANGE and EXCLUDE_RESOLUTION_RANGE to exclude ice-rings
# 
# FRIEDEL'S_LAW=FALSE     ! This acts only on the CORRECT step
# ! If the anom signal turns out to be, or is known to be, very low or absent,
# ! use FRIEDEL'S_LAW=TRUE instead (or comment out the line); re-run CORRECT
# 
# ! remove the "!" in the following line:
# ! STRICT_ABSORPTION_CORRECTION=TRUE
# ! if the anomalous signal is strong: in that case, in CORRECT.LP the three
# ! "CHI^2-VALUE OF FIT OF CORRECTION FACTORS" values are significantly> 1, e.g. 1.5
# !
# ! exclude (mask) untrusted areas of detector, e.g. beamstop shadow :
# ! UNTRUSTED_RECTANGLE= 1800 1950 2100 2150 ! x-min x-max y-min y-max ! repeat
# ! UNTRUSTED_ELLIPSE= 2034 2070 1850 2240 ! x-min x-max y-min y-max ! if needed
# ! UNTRUSTED_QUADRILATERAL= x1 y1 x2 y2 x3 y3 x4 y4 ! see documentation
# !
# ! parameters with changes wrt default values:
# TRUSTED_REGION=0.0 1.2 ! partially use corners of detector (0 1.4143: use all pixels)
# VALUE_RANGE_FOR_TRUSTED_DETECTOR_PIXELS=6000. 30000. ! often 7000 or 8000 is ok
# STRONG_PIXEL=4           ! COLSPOT: only use strong reflections (default is 3)
# MINIMUM_NUMBER_OF_PIXELS_IN_A_SPOT=3 ! default of 6 is sometimes too high
# ! close spots/long cell axis: reduce SEPMIN and CLUSTER_RADIUS from their defaults of 6 and 3
# ! SEPMIN=4  CLUSTER_RADIUS=2 ! should be default for Pilatus and other detectors with low PSF
# ! since XDS 01-MAR-2015, POSITION is used instead of DISTANCE. Older versions do it the other way round.
# ! nowadays headers are usually correct so refine DISTANCE/POSITION in INTEGRATE but not IDXREF
# REFINE(IDXREF)=CELL BEAM ORIENTATION AXIS ! DISTANCE POSITION
# REFINE(INTEGRATE)= DISTANCE POSITION BEAM ORIENTATION ! AXIS CELL
# ! REFINE(CORRECT)=CELL BEAM ORIENTATION AXIS DISTANCE POSITION ! Default is: refine everything
# ROTATION_AXIS=1 0 0  ! Australian Synchrotron, SERCAT ID-22 (?), APS 19-ID (?), ESRF BM30A, SPring-8, SSRF BL17U need -1 0 0. Diamond ID24 needs 0 -1 0
# DIRECTION_OF_DETECTOR_X-AXIS=1 0 0
# DIRECTION_OF_DETECTOR_Y-AXIS=0 1 0
# INCIDENT_BEAM_DIRECTION=0 0 1
# FRACTION_OF_POLARIZATION=0.98   ! better value is provided by beamline staff!
# POLARIZATION_PLANE_NORMAL=0 1 0
# !used by DEFPIX and CORRECT to exclude ice-reflections / ice rings - uncomment if necessary
# !EXCLUDE_RESOLUTION_RANGE= 3.93 3.87 !ice-ring at 3.897 Angstrom
# !EXCLUDE_RESOLUTION_RANGE= 3.70 3.64 !ice-ring at 3.669 Angstrom
# !EXCLUDE_RESOLUTION_RANGE= 3.47 3.41 !ice-ring at 3.441 Angstrom
# !EXCLUDE_RESOLUTION_RANGE= 2.70 2.64 !ice-ring at 2.671 Angstrom
# !EXCLUDE_RESOLUTION_RANGE= 2.28 2.22 !ice-ring at 2.249 Angstrom
# !EXCLUDE_RESOLUTION_RANGE= 2.102 2.042 !ice-ring at 2.072 Angstrom - strong
# !EXCLUDE_RESOLUTION_RANGE= 1.978 1.918 !ice-ring at 1.948 Angstrom - weak
# !EXCLUDE_RESOLUTION_RANGE= 1.948 1.888 !ice-ring at 1.918 Angstrom - strong
# !EXCLUDE_RESOLUTION_RANGE= 1.913 1.853 !ice-ring at 1.883 Angstrom - weak
# !EXCLUDE_RESOLUTION_RANGE= 1.751 1.691 !ice-ring at 1.721 Angstrom - weak
# 	                """)
#         	        fxds.close
# 	        return

def Test():
	
	inp = XDSINP('test')

if __name__ == "__main__":
	Test()
	exit(0)
