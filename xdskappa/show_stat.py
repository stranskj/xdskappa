#!/bin/python

import xdskappa.common as common
import os, sys
from xdskappa.xdsinp import XDSINP
import xdskappa
import argparse


def ParseInput():
        parser = argparse.ArgumentParser(prog= 'xdskappa.show_stat', description='Shows merging statistic vs. resolution.', epilog='Dependencies: XDS, gnuplot')

#        parser.add_argument('dataPath', nargs='*', help="Directory (or more) with input frames")
        parser.add_argument('-D','--dataset-file', dest='DatasetListFile', nargs='?', default='datasets.list', const='datasets.list', metavar='FILE', help='List of datasets to use. Entries are in format: output_subdirectory<tab>path/template_????.cbf. When no file is given, "datasets.list" is expected.')
        parser.add_argument('-s', '--scaled', dest='Scaled', nargs='?', default=None, const='scale', action='append', metavar= 'FOLDER', help='Folder to results from XSCALE to include show statistics.')
        parser.add_argument('-g', '--gnuplot-input', dest='gnuplot_input', nargs='?', default='gnuplot.plt', const='gnuplot.plt', metavar= 'FILENAME', help='Name for GNUplot input file.')
        
        # help on empty input
#        if len(sys.argv) == 1:
#                parser.print_help()     # help on empty input
#                sys.exit(1)

        return parser.parse_args()

def main():
    print("")
    print("\txdskappa.show_stat " + xdskappa.VERSION)
    print("\tAuthor: Jan Stransky")
    print("\t========================")
    print(" ")
    print(xdskappa.LICENSE)
    print(" ")
    
    in_data = ParseInput()
 #   print in_data

    if os.path.isfile(in_data.DatasetListFile):
        datasets,names = common.ReadDatasetListFile(in_data.DatasetListFile)
    else:
        print("File not found: " + in_data.DatasetListFile)
        sys.exit(1)
        
    common.ShowStatistics(names, in_data.Scaled, in_data.gnuplot_input)    
        
    return    

if __name__ == "__main__":

    main()
    sys.exit(0)