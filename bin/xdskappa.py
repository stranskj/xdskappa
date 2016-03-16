#!/bin/python
#from xdsinp	import XDSINP
#from _imaging import path
#from xdataset import XDataset
import common
from xdsinp import XDSINP


def ParseInput():
	parser = argparse.ArgumentParser(prog= 'xdskappa', description='Finds all data collection runs, makes XDS.INP files and attempts running XDS for all runs and scale them. Currently for omega scans on D8 Venture at BIOCEV.', epilog='Dependencies: xds_par')
	
	parser.add_argument('dataPath', nargs='*', help="Directory (or more) with input data")
	parser.add_argument('-d','--dataset-file', dest='DatasetListFile', metavar='FILE', help='List of datasets to use. Entries are in format: output_subdirectory path/template_????.cbf')
	
	parser.add_argument('-o','--output-file', dest='OutputScale', metavar= 'FILE', default='scaled.ahkl', help='File name for output from scaling.')
	
	parser.add_argument('-g', dest='ShowGraphs', action='store_true', help='Show merging statistics in graphs in the end.')
	
	parser.add_argument('--min-dataset', dest='minData', default=2, metavar='NUM', type=int, help="Minimal number of frames to be concidered as dataset.")
	
	parser.add_argument('-p','--parameter', dest='XDSParameter', nargs='+', action='append', metavar='PAR= VALUE', help='Modification to all XDS.INP. Parameters format as defined for XDS.INP. Overrides parameters from --parameter-file.')
	parser.add_argument('--parameter-file', dest='XDSParameterFile', metavar='FILE', help='File with list of parameters to modify XDS.INP. Parameters format as defined for XDS.INP')
	
	parser.add_argument('-r','--reference-dataset', dest='ReferenceData', metavar='DATASET', help='Reference dataset from working list, named by subdirectory. The first one used by default. For external reference dataset use: -p REFERENCE_DATASET= path/data/XDS_ASCII.HKL')
	
	parser.add_argument('-f', '--force', dest='ForceXDS', action='store_true', help='Force integration on unsuccesfull indexing.')
	

	# help on empty input
	if len(sys.argv) == 1:
		parser.print_help()     # help on empty input
		sys.exit(1)

	return parser.parse_args()

def main():
	print ""
	print "\txdskappa " + common.VERSION
	print "\tAuthor: Jan Stransky"
	print "\t========================"
	
	in_data = ParseInput()
#	print in_data

	if len(in_data.dataPath) > 0:
		datasets,names = common.GetDatasets(in_data)
		print "Found datasets:"
		for d in names :
			print datasets[d]
		print "Found datasets saved to dataset.list"
	
	if in_data.DatasetListFile :
		datasets,names = common.ReadDatasetListFile(in_data.DatasetListFile)
	
	print "Using datasets:"
	for d in names :
		print datasets[d]
		
	common.PrepareXDSINP(in_data,datasets,names)
	
	if in_data.ReferenceData:
		names.insert(0, names.pop(names.index(in_data.ReferenceData)))
	
	common.RunXDS(names)
	
	if in_data.ForceXDS:
		for path in names:
			log = open(path + '/xds.log')
			if 'YOU MAY CHOOSE TO CONTINUE DATA' in log.read():
				inp = XDSINP(path)
				inp.read()
				inp.SetParam('JOB= DEFPIX INTEGRATE CORRECT')
				inp.write()
				log.close()
				
				print "Attempting integration of: " + path
				common.RunXDS([path])
			else:
				log.close()
			
		
	common.PrintISa(names)
	
	common.Scale(names, in_data.OutputScale)
	
	if in_data.ShowGraphs:
		common.ShowStatistics(names, 'scale')
	

if __name__ == "__main__":
	import sys
	try:
		import argparse #sys,os,subprocess,shlex,,re,glob,math
	#	from distutils import spawn
	except Exception:
		print "Your python is probably to old. At least version 2.7 is required."
		print "Your version is: " +  sys.version
		sys.exit(1)

	main()
	sys.exit(0)