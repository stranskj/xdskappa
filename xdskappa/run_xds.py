#!/bin/python

import xdskappa.common as common
import os, sys
from xdskappa.xdsinp import XDSINP
import xdskappa
import argparse
import logging
import logging.config

prog_name='xdskappa.run_xds'
prog_short_description='Runs XDS without generating XDS.INP from scratch. Useful after custom modifications of XDS.INP. No scaling with xscale is done.'
#logging.config.dictConfig(xdskappa.logging_config(prog_name))

__version__ = xdskappa.__version__

def ParseInput():
        parser = argparse.ArgumentParser(prog= prog_name,
                                         description='Modifies existing XDS.INPs, run XDS and shows overall '
                                                     'statistics (no scaling)',
                                         epilog='Dependencies: XDS, gnuplot')

#        parser.add_argument('dataPath', nargs='*', help="Directory (or more) with input frames")
        parser.add_argument('-D','--dataset-file',
                            dest='DatasetListFile',
                            nargs='?',
                            default='datasets.list',
                            const='datasets.list',
                            metavar='FILE',
                            help='List of datasets to use. Entries are in format: '
                                 'output_subdirectory<tab>path/template_????.cbf. When no file is given, '
                                 '"datasets.list" is expected.')

#        parser.add_argument('-out','--output-file', dest='OutputScale', metavar= 'FILE', default='scaled.HKL', help='File name for output from scaling.')

        parser.add_argument('-g',
                            dest='ShowGraphs',
                            action='store_true',
                            help='Show merging statistics in graphs in the end.')

#       parser.add_argument('--min-dataset', dest='minData', default=2, metavar='NUM', type=int, help="Minimal number of frames to be considered as dataset.")

        parser.add_argument('-p','--parameter',
                            dest='XDSParameter',
                            nargs='+',
                            action='append',
                            metavar='PAR= VALUE',
                            help='Modification to all XDS.INP files. Parameters format as defined for XDS.INP. '
                                 'Overrides parameters from --parameter-file.')
        parser.add_argument('-P','--parameter-file',
                            dest='XDSParameterFile',
                            nargs='?',
                            default=None,
                            const='XDSKAPPA.INP',
                            metavar='FILE',
                            help='File with list of parameters to modify XDS.INP files. Parameters format as defined '
                                 'for XDS.INP. When no file given, "XDSKAPPA.INP" is expected.')

        parser.add_argument('-r','--reference-dataset',
                            dest='ReferenceData',
                            metavar='DATASET',
                            help='Name of reference dataset from working list. The first one used by default. For '
                                 'external reference dataset use: -p REFERENCE_DATA_SET= path/data/XDS_ASCII.HKL')
        
        parser.add_argument('--no-run',
                            dest='norun',
                            action='store_false',
                            default=True,
                            help="Only modify XDS.INP, don't run xds_par.")

        parser.add_argument('-f', '--force',
                            dest='ForceXDS',
                            action='store_true',
                            help='Force integration on unsuccesfull indexing.')
#      parser.add_argument('-opt','--optimize', dest='OptIntegration', nargs='?', action='append', const= 'ALL', metavar='ALL FIX BEAM GEOMETRY', help='Run XDS twice, with optimized parameters in second run. FIX - fix parameters in integration; BEAM - copy BEAM parameters from INTEGRATE.LP; GEOMETRY - copy GXPARM.XDS to XPARM.XDS. One keyword per parameter occurance. When given without a value, ALL is presumed.')
#     parser.add_argument('--backup', dest='BackupOpt', nargs='?', const='backup', default=None, metavar='NAME', help='Backup datasets folders prior optimization to their subfolder ("backup" on empty value) . It will erase older backup of [NAME] if present. No backup by default.')


        # help on empty input
 #       if len(sys.argv) == 1:
 #               parser.print_help()     # help on empty input
 #               sys.exit(1)

        return parser.parse_args()

def run(in_data):
    '''
    Actual worker
    '''
#    print in_data

    if os.path.isfile(in_data.DatasetListFile):
        datasets,names = common.ReadDatasetListFile(in_data.DatasetListFile)
    else:
        print("File not found: " + in_data.DatasetListFile)
        sys.exit(1)

    parmod = common.ProcessParams(in_data.XDSParameter,in_data.XDSParameterFile)
    if not len(parmod) == 0:
        print("Modifying XDS.INP files:")
        for name in names:
            try:
                print(name+"/XDS.INP")
                inXDS = XDSINP(name)
                inXDS.read()
                for key in parmod:
                    inXDS[key] = parmod[key]
                inXDS.write()
            except IOError as e:
                print(e)
                print("Skipping.")
                continue

    if in_data.norun:
        common.RunXDS(names)
        
        if in_data.ForceXDS:
            common.ForceXDS(names)
        
        common.PrintISa(names)
    return                

class RunXDSJob(xdskappa.Job):
    def __worker__(self):
        '''
        The actual programme worker
        :return:
        '''
        self.job_exit = run(self._args)

    def __set_meta__(self):
        self._program_short_description = prog_short_description

    def __program_arguments__(self):
        '''
        Settings of CLI arguments. self._parser to be used as argparse.ArgumentParser()
        '''
        parser = self._parser
        parser.add_argument('-D', '--dataset-file',
                            dest='DatasetListFile',
                            nargs='?',
                            default='datasets.list',
                            const='datasets.list',
                            metavar='FILE',
                            help='List of datasets to use. Entries are in format: '
                                 'output_subdirectory<tab>path/template_????.cbf. When no file is given, '
                                 '"datasets.list" is expected.')

        #        parser.add_argument('-out','--output-file', dest='OutputScale', metavar= 'FILE', default='scaled.HKL', help='File name for output from scaling.')

        parser.add_argument('-g',
                            dest='ShowGraphs',
                            action='store_true',
                            help='Show merging statistics in graphs in the end.')

        #       parser.add_argument('--min-dataset', dest='minData', default=2, metavar='NUM', type=int, help="Minimal number of frames to be considered as dataset.")

        parser.add_argument('-p', '--parameter',
                            dest='XDSParameter',
                            nargs='+',
                            action='append',
                            metavar='PAR= VALUE',
                            help='Modification to all XDS.INP files. Parameters format as defined for XDS.INP. '
                                 'Overrides parameters from --parameter-file.')
        parser.add_argument('-P', '--parameter-file',
                            dest='XDSParameterFile',
                            nargs='?',
                            default=None,
                            const='XDSKAPPA.INP',
                            metavar='FILE',
                            help='File with list of parameters to modify XDS.INP files. Parameters format as defined '
                                 'for XDS.INP. When no file given, "XDSKAPPA.INP" is expected.')

        parser.add_argument('-r', '--reference-dataset',
                            dest='ReferenceData',
                            metavar='DATASET',
                            help='Name of reference dataset from working list. The first one used by default. For '
                                 'external reference dataset use: -p REFERENCE_DATA_SET= path/data/XDS_ASCII.HKL')

        parser.add_argument('--no-run',
                            dest='norun',
                            action='store_false',
                            default=True,
                            help="Only modify XDS.INP, don't run xds_par.")

        parser.add_argument('-f', '--force',
                            dest='ForceXDS',
                            action='store_true',
                            help='Force integration on unsuccesfull indexing.')

    def __argument_processing__(self):
        '''
        Adjustments of raw input arguments. Modifies self._args, if needed

        '''
        pass

    def __help_epilog__(self):
        '''
        Epilog for the help

        '''
        pass

def main():
    job = RunXDSJob()
    return job.job_exit


if __name__ == "__main__":
    sys.exit(main())