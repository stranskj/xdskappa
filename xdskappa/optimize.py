#!/bin/python

import xdskappa
import xdskappa.common as common
import os, sys, argparse
from xdskappa.xdsinp import XDSINP

import logging.config

prog_name = 'xdskappa.optimize'
prog_short_description = 'Performs XDS optimization steps'
#logging.config.dictConfig(xdskappa.logging_config(prog_name))

__version__ = xdskappa.__version__


def PrintISaOptimized(OldIsa, NewIsa):
    """
    @param OldIsa: Dictionary of old ISa values
    @type dictionary
    
    @param NewIsa: Dictionary of new ISa values
    @type dictionary
    """
    xdskappa.my_print('ISa for individual datasets before (Old) and after (New) optimization:')
    xdskappa.my_print('\tOld\tNew\tDataset')
    for dataset in sorted(OldIsa):

        try:
            oisa = OldIsa[dataset]
        except KeyError:
            oisa = 'N/A'

        try:
            nisa = NewIsa[dataset]
        except KeyError:
            nisa = 'N/A'

        xdskappa.my_print('\t' + oisa + '\t' + nisa + '\t' + dataset)
    return


def run(in_data):

    if os.path.isfile(in_data.DatasetListFile):
        datasets, names = common.ReadDatasetListFile(in_data.DatasetListFile)
    else:
        raise xdskappa.RuntimeErrorUser("File not found: " + in_data.DatasetListFile)

    if in_data.BackupOpt != None:
        xdskappa.my_print('Backing up previous run...')
        common.BackupOpt(names, in_data.BackupOpt)

    xdskappa.my_print("Applying settings for optimization...")
    common.OptimizeXDS(names, in_data.OptIntegration)

    if in_data.NoRun:
        oldisa = common.ReadISa(names)

        xdskappa.my_print("Running XDS...")
        common.RunXDS(names)

        newisa = common.ReadISa(names)
        PrintISaOptimized(oldisa, newisa)


class OptimizeJob(xdskappa.Job):
    def __worker__(self):
        '''
        The actual programme worker
        :return:
        '''
        self.job_exit = run(self._args)

    def __program_arguments__(self):
        '''
        Settings of CLI arguments. self._parser to be used as argparse.ArgumentParser()
        '''
        parser = self._parser
        parser.add_argument('-D', '--dataset-file', dest='DatasetListFile', nargs='?', default='datasets.list',
                            const='datasets.list', metavar='FILE',
                            help='List of datasets to use. Entries are in format: '
                                 'output_subdirectory<tab>path/template_????.cbf. When no file is given, "datasets.list" '
                                 'is expected.')

        parser.add_argument('-opt', '--optimize', dest='OptIntegration', nargs='?', action='append', const='ALL',
                            metavar='VAL',
                            help='Parameters to optimized in befor INTEGRATION. FIX - fix parameters in integration; BEAM '
                                 '- copy BEAM parameters from INTEGRATE.LP; GEOMETRY - copy GXPARM.XDS to XPARM.XDS. One '
                                 'keyword per parameter occurance. When given without a value, ALL is presumed.')
        parser.add_argument('--backup', dest='BackupOpt', nargs='?', const='backup', default=None, metavar='NAME',
                            help='Backup datasets folders prior optimization to their subfolder ("backup" on empty value)'
                                 '. It will erase older backup of [NAME] if present. No backup by default.')

        parser.add_argument('--no-run', dest='NoRun', action='store_false', default=True,
                            help="Only modify files, don't run xds_par.")

    def __set_meta__(self):
        self._program_short_description = prog_short_description

    def __argument_processing__(self):
        '''
        Adjustments of raw input arguments. Modifies self._args, if needed

        '''
        if self._args.OptIntegration == None:
            self._args.OptIntegration = ['ALL']

    def __help_epilog__(self):
        '''
        Epilog for the help

        '''
        pass

def main():
    job = OptimizeJob()
    return job.job_exit


if __name__ == "__main__":
    sys.exit(main())