#!/bin/python

import common, os
from xdsinp import XDSINP

def ParseInput():
    parser = argparse.ArgumentParser(prog= 'xdskappa', description='Modify input files to perform optimization of integration and rerun XDS.', epilog='Dependencies: XDS')
    
    parser.add_argument('dataPath', nargs='*', help="Directory (or more) with input frames")
    parser.add_argument('-D','--dataset-file', dest='DatasetListFile', nargs='?', default=None, const='datasets.list', metavar='FILE', help='List of datasets to use. Entries are in format: output_subdirectory<tab>path/template_????.cbf. When no file is given, "datasets.list" is expected.')
    
    parser.add_argument('-opt','--optimize', dest='OptIntegration', nargs='?', action='append', const= 'ALL', metavar='ALL FIX BEAM GEOMETRY', help='Run XDS twice, with optimized parameters in second run. FIX - fix parameters in integration; BEAM - copy BEAM parameters from INTEGRATE.LP; GEOMETRY - copy GXPARM.XDS to XPARM.XDS. One keyword per parameter occurance. When given without a value, ALL is presumed.')
    parser.add_argument('--backup', dest='BackupOpt', nargs='?', const='backup', default=None, metavar='NAME', help='Backup datasets folders prior optimization to their subfolder ("backup" on empty value) . It will erase older backup of [NAME] if present. No backup by default.')
    
    parser.add_argument('--no-run', dest='NoRun', action='store_false',default=True, help="Only modify files, don't run xds_par.")

    # help on empty input
    if len(sys.argv) == 1:
        parser.print_help()     # help on empty input
        sys.exit(1)

    return parser.parse_args()

def PrintISaOptimized(OldIsa,NewIsa):
    """
    @param OldIsa: Dictionary of old ISa values
    @type dictionary
    
    @param NewIsa: Dictionary of new ISa values
    @type dictionary
    """
    print 'ISa for individual datasets before (Old) and after (New) optimization:'
    print '\tOld\tNew\tDataset'
    for dataset in sorted(OldIsa):
        
        try:
            oisa = OldIsa[dataset]
        except KeyError:
            oisa = 'N/A'
        
        try:
            nisa = NewIsa[dataset]
        except KeyError:
            nisa = 'N/A'
            
        print '\t' + oisa + '\t' + nisa + '\t' + dataset
    return

def main():
    print ""
    print "\txdskappa.optimize " + common.VERSION
    print "\tAuthor: Jan Stransky"
    print "\t========================"
    print " "

    in_data = ParseInput()
#    print in_data

    if os.path.isfile(in_data.DatasetListFile):
        datasets,names = common.ReadDatasetListFile(in_data.DatasetListFile)
    else:
        print "File not found: " + in_data.DatasetListFile
        sys.exit(1)

    if in_data.BackupOpt != None:
        print 'Backing up previous run...'
        common.BackupOpt(names, in_data.BackupOpt)
    
    print "Applying settings for optimization..."    
    common.OptimizeXDS(names, in_data.OptIntegration)
    
    if in_data.NoRun:
        oldisa = common.ReadISa(names)
        
        print "Running XDS..."
        common.RunXDS(names)
        
        newisa = common.ReadISa(names)
        PrintISaOptimized(oldisa, newisa)        

if __name__ == "__main__":
    import sys
    try:
        import argparse #sys,os,subprocess,shlex,,re,glob,math
    #    from distutils import spawn
    except Exception:
        print "Your python is probably to old. At least version 2.7 is required."
        print "Your version is: " +  sys.version
        sys.exit(1)

    main()
    sys.exit(0)