#!/bin/python
VERSION = '0.1 (25th Feb 2016)'

# XDS.INP defaults
ORGX= 495
ORGY= 501
def setXDSINP(path,strFrame):
	fheader = cbfphoton2.photonCIF(strFrame)
	axis = GetAxis(fheader)
	data_range = 360 # TODO
	QX=
	QY=
	parameters = {}

	parameters['JOB'] = 'XYCORR INIT COLSPOT IDXREF DEFPIX INTEGRATE CORRECT'
	parameters['ORGX'] = str(ORGX)
	parameters['ORGY'] = str(ORGY)
	parameters['DETECTOR_DISTANCE'] = axis['DX']['_diffrn_scan_axis.displacement_start']
	parameters['OSCILLATION_RANGE'] = axis['OMEGA']['_diffrn_scan_axis.angle_increment']
	parameters['X-RAY_WAVELENGTH'] = fheader['_diffrn_radiation_wavelength.wavelength']
	parameters['NAME_TEMPLATE_OF_DATA_FRAMES'] = strFrame # TODO
#	parameters['REFERENCE_DATA_SET'] = ''
	parameters['DATA_RANGE'] = '1 ' + str(data_range)
	parameters['SPOT_RANGE'] = '1 ' + str(int(data_range/2))
	parameters['SPACE_GROUP_NUMBER'] = '0'
	parameters['UNIT_CELL_CONSTANTS'] = '70 80 90 90 90 90'
	parameters['INCLUDE_RESOLUTION_RANGE'] = '50 0'
	parameters["FRIEDEL'S_LAW"] = 'FALSE'
	parameters['STRICT_ABSORPTION_CORRECTION'] = 'TRUE'
	parameters['TRUSTED_REGION'] = '0.0 1.2'
	parameters['VALUE_RANGE_FOR_TRUSTED_DETECTOR_PIXELS'] = '6000. 30000.'
	parameters['STRONG_PIXEL'] = '4'
	parameters['MINIMUM_NUMBER_OF_PIXELS_IN_A_SPOT'] = '4'
	parameters['REFINE(IDXREF)'] = 'CELL BEAM ORIENTATION AXIS ! DISTANCE POSITION'
	parameters['REFINE(INTEGRATE)'] = 'DISTANCE POSITION BEAM ORIENTATION ! AXIS CELL'
	parameters['DETECTOR'] = 'PILATUS'
	parameters['MINIMUM_VALID_PIXEL_VALUE'] = '0'
	parameters['OVERLOAD'] = fheader['_array_intensities.overload']
	parameters['SENSOR_THICKNESS'] = 0
	parameters['NX'] = fheader['X-Binary-Size-Fastest-Dimension']
	parameters['NY'] = fheader['X-Binary-Size-Second-Dimension']
	parameters['QX'] = QX
	parameters['QY'] = QY
	parameters['ROTATION_AXIS'] = '0 -1 0'
	parameters['DIRECTION_OF_DETECTOR_X-AXIS'] = detectorX #TODO
	parameters['DIRECTION_OF_DETECTOR_Y-AXIS'] = detectorY #TODO
	parameters['INCIDENT_BEAM_DIRECTION'] = '0 0 1'
	parameters['FRACTION_OF_POLARIZATION'] = '0.98' #TODO: test fheader['_diffrn_radiation_wavelength.polarizn_source_ratio']
	parameters['POLARIZATION_PLANE_NORMAL'] = '0 1 0'
	
	return parameters 

def GetAxis(header):
	axis = {}
	for loop in header["loop_"]:
		if "_diffrn_scan_axis.displacement_increment" in loop[0]:
			for ax in loop[1]:
				axis[ax['_diffrn_scan_axis.axis_id']]= ax
			break
	
	print axis
	return axis

def MakeXDSINP(path):
	os.mkdir(path)
	if not os.path.isfile(path + "/XDS.INP"):
		fxds = open(path + "/XDS.INP",'w')
		fxds.write("! written by xdskappa version "+ VERSION)
		fxds.write("""
JOB= XYCORR INIT COLSPOT IDXREF DEFPIX INTEGRATE CORRECT
ORGX= XXX ORGY= XXX  ! check these values with adxv !
DETECTOR_DISTANCE= XXX
OSCILLATION_RANGE= XXX
X-RAY_WAVELENGTH= XXX
NAME_TEMPLATE_OF_DATA_FRAMES=photon.cbf
! REFERENCE_DATA_SET=xxx/XDS_ASCII.HKL ! e.g. to ensure consistent indexing
DATA_RANGE=
SPOT_RANGE=
! BACKGROUND_RANGE=1 10 ! rather use defaults (first 5 degree of rotation)

SPACE_GROUP_NUMBER=0                   ! 0 if unknown
UNIT_CELL_CONSTANTS= 70 80 90 90 90 90 ! put correct values if known
INCLUDE_RESOLUTION_RANGE=50 0  ! after CORRECT, insert high resol limit; re-run CORRECT
! IDXREF now obeys INCLUDE_RESOLUTION_RANGE and EXCLUDE_RESOLUTION_RANGE to exclude ice-rings

FRIEDEL'S_LAW=FALSE     ! This acts only on the CORRECT step
! If the anom signal turns out to be, or is known to be, very low or absent,
! use FRIEDEL'S_LAW=TRUE instead (or comment out the line); re-run CORRECT

! remove the "!" in the following line:
! STRICT_ABSORPTION_CORRECTION=TRUE
! if the anomalous signal is strong: in that case, in CORRECT.LP the three
! "CHI^2-VALUE OF FIT OF CORRECTION FACTORS" values are significantly> 1, e.g. 1.5
!
! exclude (mask) untrusted areas of detector, e.g. beamstop shadow :
! UNTRUSTED_RECTANGLE= 1800 1950 2100 2150 ! x-min x-max y-min y-max ! repeat
! UNTRUSTED_ELLIPSE= 2034 2070 1850 2240 ! x-min x-max y-min y-max ! if needed
! UNTRUSTED_QUADRILATERAL= x1 y1 x2 y2 x3 y3 x4 y4 ! see documentation
!
! parameters with changes wrt default values:
TRUSTED_REGION=0.0 1.2 ! partially use corners of detector (0 1.4143: use all pixels)
VALUE_RANGE_FOR_TRUSTED_DETECTOR_PIXELS=6000. 30000. ! often 7000 or 8000 is ok
STRONG_PIXEL=4           ! COLSPOT: only use strong reflections (default is 3)
MINIMUM_NUMBER_OF_PIXELS_IN_A_SPOT=3 ! default of 6 is sometimes too high
! close spots/long cell axis: reduce SEPMIN and CLUSTER_RADIUS from their defaults of 6 and 3
! SEPMIN=4  CLUSTER_RADIUS=2 ! should be default for Pilatus and other detectors with low PSF
! since XDS 01-MAR-2015, POSITION is used instead of DISTANCE. Older versions do it the other way round.
! nowadays headers are usually correct so refine DISTANCE/POSITION in INTEGRATE but not IDXREF
REFINE(IDXREF)=CELL BEAM ORIENTATION AXIS ! DISTANCE POSITION
REFINE(INTEGRATE)= DISTANCE POSITION BEAM ORIENTATION ! AXIS CELL
! REFINE(CORRECT)=CELL BEAM ORIENTATION AXIS DISTANCE POSITION ! Default is: refine everything

! parameters specifically for this detector and beamline:
DETECTOR= XXX MINIMUM_VALID_PIXEL_VALUE=XXX OVERLOAD=XXX
SENSOR_THICKNESS= 0
! attention CCD detectors: for very high resolution (better than 1A) make sure to specify SILICON
! as about 32* what CORRECT.LP suggests (absorption of phosphor is much higher than that of silicon).
! Better: read the article http://strucbio.biologie.uni-konstanz.de/xdswiki/index.php/SILICON .
NX= XXX NY= XXX  QX= XXX  QY= XXX ! to make CORRECT happy if frames are unavailable

ROTATION_AXIS=1 0 0  ! Australian Synchrotron, SERCAT ID-22 (?), APS 19-ID (?), ESRF BM30A, SPring-8, SSRF BL17U need -1 0 0. Diamond ID24 needs 0 -1 0
DIRECTION_OF_DETECTOR_X-AXIS=1 0 0
DIRECTION_OF_DETECTOR_Y-AXIS=0 1 0
INCIDENT_BEAM_DIRECTION=0 0 1
FRACTION_OF_POLARIZATION=0.98   ! better value is provided by beamline staff!
POLARIZATION_PLANE_NORMAL=0 1 0
!used by DEFPIX and CORRECT to exclude ice-reflections / ice rings - uncomment if necessary
!EXCLUDE_RESOLUTION_RANGE= 3.93 3.87 !ice-ring at 3.897 Angstrom
!EXCLUDE_RESOLUTION_RANGE= 3.70 3.64 !ice-ring at 3.669 Angstrom
!EXCLUDE_RESOLUTION_RANGE= 3.47 3.41 !ice-ring at 3.441 Angstrom
!EXCLUDE_RESOLUTION_RANGE= 2.70 2.64 !ice-ring at 2.671 Angstrom
!EXCLUDE_RESOLUTION_RANGE= 2.28 2.22 !ice-ring at 2.249 Angstrom
!EXCLUDE_RESOLUTION_RANGE= 2.102 2.042 !ice-ring at 2.072 Angstrom - strong
!EXCLUDE_RESOLUTION_RANGE= 1.978 1.918 !ice-ring at 1.948 Angstrom - weak
!EXCLUDE_RESOLUTION_RANGE= 1.948 1.888 !ice-ring at 1.918 Angstrom - strong
!EXCLUDE_RESOLUTION_RANGE= 1.913 1.853 !ice-ring at 1.883 Angstrom - weak
!EXCLUDE_RESOLUTION_RANGE= 1.751 1.691 !ice-ring at 1.721 Angstrom - weak
		""")
		fxds.close
	return

def GetDatasets(inData):
	#print string(inData.dataPath)
	Datasets = []
	firstframe = re.compile("[_-][0]+[1].cbf")
	for datapath in inData.dataPath :
		try:
			leadingFrames = [fi for fi in os.listdir(datapath) if firstframe.search(fi)] #get first frame of each dataset
		except os.error:
			print "Cannot access: " + datapath + " No such directory"
			exit(1)

		for setname in leadingFrames :
			prefix = firstframe.split(setname)[0] + "_"		#dataset prefix without last 
			if len(glob.glob(datapath + "/" + prefix + "*.cbf")) >= inData.minData :  # more than 1 frame = dataset
				digits = len(setname) - len(prefix) - 4		#number of ? in template name
				Datasets.append(datapath + "/" + prefix + '?' * digits + '.cbf')
	Datasets.sort()	
	DatasetsDict = {}
	names = []
	numdigit = int(math.log10(len(Datasets)))+1
	for i,name in enumerate(Datasets):
		key = str(i).zfill(numdigit) + "_" + name.split("_?")[0].replace("/","_")
		DatasetsDict[key] = name
		names.append(key)
	names.sort()
	fdatasets = open('datasets.list','w')
	for key in names:
		fdatasets.write(key + "\t" + DatasetsDict[key] + "\n")
	return DatasetsDict,names

def ParseInput():
	parser = argparse.ArgumentParser(description='Finds all data collection runs, makes XDS.INP files and attempts running XDS for all runs and scale them. Currently for omega scans on D8 Venture at BIOCEV.', epilog='Dependencies: xds_par')
	
	parser.add_argument('dataPath', nargs='+', help="Directory (or more) with input data")
	parser.add_argument('--min-dataset', dest='minData', default=2, metavar='NUM', type=int, help="Minimal number of frames to be concidered as dataset.")

        # help on empty input
        if len(sys.argv) == 1:
                parser.print_help()     # help on empty input
                sys.exit(1)

	return parser.parse_args()

def main():
	
	in_data = ParseInput()
	print in_data

	datasets,names = GetDatasets(in_data)
	
	print "Found datasets:"
#	print datasets
	for d in names :
		print datasets[d]
	MakeXDSINP('test')

if __name__ == "__main__":
        import sys
        try:
                import sys,os,subprocess,shlex,argparse,re,glob,math
                from distutils import spawn
        except Exception:
                print "Your python is probably to old. At least version 2.7 is required."
                print "Your version is: " +  sys.version
                sys.exit(1)
	import cbfphoton2 
	ph = cbfphoton2.photonCIF('photon.cbf')
	print ph['loop_']
	print GetAxis(ph)
	main()
	exit(0)
