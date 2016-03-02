#!/bin/python
from xdsinp	import XDSINP
#from _imaging import path
from xdataset import XDataset
VERSION = '0.1 (25th Feb 2016)'
LIST_SEPARATOR = '\t'
# XDS.INP defaults
#ORGX= 495
#ORGY= 501

def getISa(path):
	corlp = path
	if os.path.isfile(corlp) == False :
		raise IOError(path + "/CORRECT.LP is not available. Problem with data processing?")
		return 'N/A'
	fcor = open(corlp,'r')
	
	line = fcor.readline()
	while line.split() != ['a', 'b', 'ISa'] :
		line = fcor.readline()

	line = fcor.readline().split()
	return line[2]

def PrintISa(Paths):
	print 'ISa for individual datasets:'
	print '\tISa\tDataset'
	for set in Paths:
		try:
			isa = getISa(set + '/CORRECT.LP')
		except IOError:
			isa = 'N/A'
		
		print '\t' + isa + '\t' + set
	return

def RunXDS(Paths):
	for path in Paths:
		print "Processing " + path + ":"
		if not os.path.isfile(path+'/XDS.INP'):
			print "File not found: "+path+'/XDS.INP'
			continue
		
		log = open(path + '/xds.log','w')
		xds = subprocess.Popen(['xds_par'],cwd= path, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
		
		for line in xds.stdout:
			log.write(line)
			if '***** COLSPOT *****' in line:
				print 'Finding strong reflections...'
			
			if '***** IDXREF *****' in line:
				print 'Indexing...'
				
			if '***** INTEGRATE *****' in line:
				print 'Integrating...'
		
		xds.wait()
		log.close()
				
		log = open(path + '/xds.log','r')
		if '!!! ERROR !!!' in log.read():
			print "An error during data procesing using XDS. Check IDXREF.LP, INTEGRATE.LP, other *.LP or xds.log files fo further details."
		else:
			print 'Finished.'
		log.close()
		
def Scale(Paths, Outname):
	try:
		os.mkdir('scale')
	except:
		print "Directory already exists: scale"
	
	xscaleinp = open('scale/XSCALE.INP','w')
	
	xscaleinp.write('OUTPUT_FILE= '+ Outname + '\n')
	for path in Paths:
		if os.path.isfile(path + '/XDS_ASCII.HKL'):
			xscaleinp.write('   INPUT_FILE= ../' + path + '/XDS_ASCII.HKL\n')
		else:
			print 'XDS_ASCII.HKL not available in ' + path
			print 'Excluding from scaling'
	
	xscaleinp.close()
	
	print 'Scaling with xscla_par...'
	xscale = subprocess.Popen('xscale_par', cwd= 'scale', stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	xscale.wait()
	
	fout = open('scale/XSCALE.LP')
	if '!!! ERROR !!!' in fout:
		print 'Error in scaling. Please read: scale/XSCALE.LP'
	else:
		print 'Scaled. Output written in: scale/' + Outname
	
	

def ReadDatasetListFile(inData):
	"""
	Process file with list of datasets
	
	@param inData: path to dataset list file
	@type  inData: string
	
	@return Datasets: Dictionary of datasets
	@type Datasets: dict
	@return names: List of dataset's names 
	@type names: list
	"""
	if not os.path.isfile(inData):
		raise IOError('File not found: ' + inData)
		exit(1)
		
	fin = open(inData,'r')
	DatasetsDict = {}
	names = []
	for line in fin:
		row = line.split(LIST_SEPARATOR)
		names.append(row[0])
		DatasetsDict[row[0]] = row[1]
	fin.close()	
	return DatasetsDict,names

def MakeXDSParam(inParList):
	"""
	Parse input from prameters modifing XDS.INP
	
	@param inParList: Parameters from input -p or --parameter
	@type inParList: list of string
	"""
	outParList = []
	i = -1
	while inParList:
		if inParList[0].find("=") > -1:
			outParList.append(inParList[0])
			i += 1
		else :
			outParList[i] += " " + inParList[0]
		del inParList[0]
	return outParList

def ReadXDSParamFile(inFile):
	"""
	Parse input file with prameters for modifing XDS.INP
	
	@param inFile: File with XDS.INP-like parameters
	@type inFile: file
	"""
	if not os.path.isfile(inFile):
		raise IOError('File not found: ' + inFile)
		return
	fin = open(inFile,'r')
	outParList = []
	for line in fin:
		outParList.append(line)
	
	return outParList
		
def PrepareXDSINP(inData,Datasets,Names):
	"""
	Makes working dirs and XDS.INP for all choosen datasets
	
	@param inData: Parsed input
	@type inData: Namespace
	@param Datasets: Datasets list
	@type Datasets: dict
	@param Names: List of keys in Datasets (ordered)
	@type Names: list
	"""
	print "Processing..."
	mod_list = []
	
	if inData.XDSParameterFile:
		mod_list += ReadXDSParamFile(inData.XDSParameterFile)
		
	if inData.XDSParameter:
		mod_list += MakeXDSParam(inData.XDSParameter)
	
	if inData.ReferenceData:		#if global reference dataset entered as -p REFERENCE_DATASET= data/XDS_ASCII.HKL, overwritten later in XDS.INP setting
		refdataset = inData.ReferenceData
	else:
		refdataset = Names[0]
		
	for path in Names:
		try:
			os.mkdir(path)
		except:
			print "Directory already exists: "+ path
		
		
		
		dts = XDataset(Datasets[path])		# gives template relative to running director to find frames	
		inp = XDSINP(path,dts)
		inp.SetDefaults()		#read in geometry from frame header etc.
		#inp.read()
		
		if Datasets[path][0] == "/":		# setup templates path relativ to XDS.INP directory
			template = Datasets[path]
		else:
			template = '../' + Datasets[path]
		inp.SetParam('NAME_TEMPLATE_OF_DATA_FRAMES= ' + template)
		
		if not path == refdataset:
			inp.SetParam("REFERENCE_DATA_SET= ../" + refdataset + "/XDS_ASCII.HKL")
		
		for parm in mod_list:
			inp.SetParam(parm)
				
		inp.write()
	return

def GetDatasets(inData):
	#print string(inData.dataPath)
	Datasets = []
	firstframe = re.compile("[_-][0]+[1].cbf")
	for datapath in inData.dataPath :
		#TODO: dereference '~'; bash apparently does it by default
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
		fdatasets.write(key + LIST_SEPARATOR + DatasetsDict[key] + "\n")
	return DatasetsDict,names

def ParseInput():
	parser = argparse.ArgumentParser(description='Finds all data collection runs, makes XDS.INP files and attempts running XDS for all runs and scale them. Currently for omega scans on D8 Venture at BIOCEV.', epilog='Dependencies: xds_par')
	
	parser.add_argument('dataPath', nargs='*', help="Directory (or more) with input data")
	parser.add_argument('--dataset-file', dest='DatasetListFile', metavar='FILE', help='List of datasets to use. Entries are in format: output_subdirectory path/template_????.cbf')
	
	parser.add_argument('-o','--output-file', dest='OutputScale', metavar= 'FILE', default='scaled.ahkl', help='File name for output from scaling.')
	
	parser.add_argument('--min-dataset', dest='minData', default=2, metavar='NUM', type=int, help="Minimal number of frames to be concidered as dataset.")
	
	parser.add_argument('-p','--parameter', dest='XDSParameter', nargs='+', metavar='PAR= VALUE', help='Modification to all XDS.INP. Parameters format as defined for XDS.INP. Overrides parameters from --parameter-file.')
	parser.add_argument('--parameter-file', dest='XDSParameterFile', metavar='FILE', help='File with list of parameters to modify XDS.INP. Parameters format as defined for XDS.INP')
	
	parser.add_argument('-r','--reference-dataset', dest='ReferenceData', metavar='DATASET', help='Reference dataset from working list, named by subdirectory. The first one used by default. For external reference dataset use: -p REFERENCE_DATASET= path/data/XDS_ASCII.HKL')
	

	# help on empty input
	if len(sys.argv) == 1:
		parser.print_help()     # help on empty input
		sys.exit(1)

	return parser.parse_args()

def main():
	
	in_data = ParseInput()
	print in_data

	if len(in_data.dataPath) > 0:
		datasets,names = GetDatasets(in_data)
		print "Found datasets:"
		for d in names :
			print datasets[d]
		print "Found datasets saved to dataset.list"
	
	if in_data.DatasetListFile :
		datasets,names = ReadDatasetListFile(in_data.DatasetListFile)
	
	print "Using datasets:"
	for d in names :
		print datasets[d]
		
	PrepareXDSINP(in_data,datasets,names)
	
	RunXDS(names)
	
	PrintISa(names)
	
	Scale(names, in_data.OutputScale)
	
	

if __name__ == "__main__":
	import sys
	try:
		import sys,os,subprocess,shlex,argparse,re,glob,math
		from distutils import spawn
	except Exception:
		print "Your python is probably to old. At least version 2.7 is required."
		print "Your version is: " +  sys.version
		sys.exit(1)

	main()
	exit(0)
