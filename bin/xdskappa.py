#!/bin/python
#from xdsinp	import XDSINP
#from _imaging import path
#from xdataset import XDataset
import common
from xdsinp import XDSINP


def ParseInput():
	parser = argparse.ArgumentParser(prog= 'xdskappa', description='Finds all data collection runs, makes XDS.INP files and attempts running XDS for all runs and scale them. Currently works on D8 Venture at BIOCEV.', epilog='Dependencies: XDS, gnuplot')
	
	parser.add_argument('dataPath', nargs='*', help="Directory (or more) with input frames")
	parser.add_argument('-D','--dataset-file', dest='DatasetListFile', nargs='?', default=None, const='datasets.list', metavar='FILE', help='List of datasets to use. Entries are in format: output_subdirectory<tab>path/template_????.cbf. When no file is given, "datasets.list" is expected.')
	
	parser.add_argument('-out','--output-file', dest='OutputScale', metavar= 'FILE', default='scaled.HKL', help='File name for output from scaling.')
	
	parser.add_argument('-g', dest='ShowGraphs', action='store_true', help='Show merging statistics in graphs in the end.')
	
	parser.add_argument('--min-dataset', dest='minData', default=2, metavar='NUM', type=int, help="Minimal number of frames to be concidered as dataset.")
	
	parser.add_argument('-p','--parameter', dest='XDSParameter', nargs='+', action='append', metavar='PAR= VALUE', help='Modification to all XDS.INP files. Parameters format as defined for XDS.INP. Overrides parameters from --parameter-file.')
	parser.add_argument('-P','--parameter-file', dest='XDSParameterFile', nargs='?', default=None, const='XDSKAPPA.INP',metavar='FILE', help='File with list of parameters to modify XDS.INP files. Parameters format as defined for XDS.INP. When no file given, "XDSKAPPA.INP" is expected.')
	
	parser.add_argument('-r','--reference-dataset', dest='ReferenceData', metavar='DATASET', help='Name of reference dataset from working list. The first one used by default. For external reference dataset use: -p REFERENCE_DATASET= path/data/XDS_ASCII.HKL')
	
	parser.add_argument('-f', '--force', dest='ForceXDS', action='store_true', help='Force integration on unsuccesfull indexing.')
	parser.add_argument('-opt','--optimize', dest='OptIntegration', nargs='?', action='append', const= 'ALL', metavar='ALL FIX BEAM GEOMETRY', help='Run XDS twice, with optimized parameters in second run. FIX - fix parameters in integration; BEAM - copy BEAM parameters from INTEGRATE.LP; GEOMETRY - copy GXPARM.XDS to XPARM.XDS. One keyword per parameter occurance. When given without a value, ALL is presumed.')
	parser.add_argument('--backup', dest='BackupOpt', nargs='?', const='backup', default=None, metavar='NAME', help='Backup datasets folders prior optimization to their subfolder ("backup" on empty value) . It will erase older backup of [NAME] if present. No backup by default.')
	

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
	#print in_data

	if len(in_data.dataPath) > 0:
		datasets,names = common.GetDatasets(in_data)
		print "Found datasets:"
		for d in names :
			print datasets[d]
		print "Found datasets saved to datasets.list"
	
	if in_data.DatasetListFile :
		datasets,names = common.ReadDatasetListFile(in_data.DatasetListFile)
	
	print "Using datasets (name, path):"
	for d in names :
		print d + '\t' +datasets[d]
		
	common.PrepareXDSINP(in_data,datasets,names)
	
	if in_data.ReferenceData:
		names.insert(0, names.pop(names.index(in_data.ReferenceData)))
	
	common.RunXDS(names)
	
	if in_data.ForceXDS:
		common.ForceXDS(names)
			
	common.PrintISa(names)
	
	if in_data.OptIntegration != None:			#TODO: Nedelej pri neuspesne indexaci
		if in_data.BackupOpt != None:
			print 'Backing up previous run...'
			common.BackupOpt(names, in_data.BackupOpt)
		common.OptimizeXDS(names, in_data.OptIntegration)
		common.RunXDS(names)
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
