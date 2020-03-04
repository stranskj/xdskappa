#!/bin/python

import common, os
from xdsinp import XDSINP


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
    print("\txdskappa.show_stat " + common.VERSION)
    print("\tAuthor: Jan Stransky")
    print("\t========================")
    print(" ")
    print(common.LICENSE)
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
    import sys
    try:
        import argparse #sys,os,subprocess,shlex,,re,glob,math
    #    from distutils import spawn
    except Exception:
        print("Your python is probably to old. At least version 2.7 is required.")
        print("Your version is: " +  sys.version)
        sys.exit(1)

    main()
    sys.exit(0)