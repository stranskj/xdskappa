#!/bin/python
VERSION = '0.1 (25th Feb 2016)'
LIST_SEPARATOR = '/t'
# XDS.INP defaults
ORGX= 495
ORGY= 501

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

def PrepareXDSINP(inData,Datasets,Names):
	print "Processing..."
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
		fdatasets.write(key + LIST_SEPARATOR + DatasetsDict[key] + "\n")
	return DatasetsDict,names

def ParseInput():
	parser = argparse.ArgumentParser(description='Finds all data collection runs, makes XDS.INP files and attempts running XDS for all runs and scale them. Currently for omega scans on D8 Venture at BIOCEV.', epilog='Dependencies: xds_par')
	
	parser.add_argument('dataPath', nargs='*', help="Directory (or more) with input data")
	parser.add_argument('--dataset-file', dest='DatasetListFile', metavar='FILE', help='List of datasets to use. Entries are in format: output_subdirectory path/template_????.cbf')
	
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
