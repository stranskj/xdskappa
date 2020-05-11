#!/bin/python
# from xdsinp	import XDSINP
# from _imaging import path
# from xdataset import XDataset
import xdskappa
import xdskappa.common as common
import xdskappa.optimize as opt
from xdskappa.xdsinp import XDSINP
import argparse
import sys
import logging
import logging.config
import pkg_resources
import importlib

logging.config.dictConfig(common.logging_config)

__version__ = xdskappa.__version__


def parse_usage():
    return  '''xdskappa -h
        or
    xdskappa dataPath [-p PAR= VALUE] [-P [FILE]] [-opt] 
            [--min-dataset NUM] ...
        OR
    xdskappa dataPath1 dataPath2 ... dataPathN [-p PAR= VALUE]
            [--min-dataset NUM] [-P [FILE]] [-opt] ...
        OR
    xdskappa -D [-p PAR= VALUE] [-P [FILE]] [-opt] ...
        OR
    xdskappa -D FILE [-p PAR= VALUE] [-P [FILE]] [-opt] ...
            '''


def epilog():
    return_str = 'List of available commands in this package:\n'
    try:

        if 'win' in sys.platform:
            suffix = '.exe'
        else:
            suffix = ''

        for ep in (ept for ept in pkg_resources.iter_entry_points('console_scripts')  # ):
                   if 'saxspoint' in ept.module_name):
            try:
                module = importlib.import_module(ep.module_name)
                return_str += ep.name + suffix + '\n\t' + module.prog_short_description + '\n\n'
            except:
                return_str += 'Cannot find {}\nTry reinstall the package.'.format(ep.module_name)
    except Exception as e:
        logging.exception(e)
        return_str += 'Here is typicaly list of available commands. Something is wrong.'

    return return_str


def ParseInput():
    parser = argparse.ArgumentParser(prog='xdskappa',
                                     description='Finds all data collection runs, makes XDS.INP files and attempts '
                                                 'running XDS for all runs and scale them. Currently works on D8 '
                                                 'Venture.',
                                     epilog=epilog(), usage=parse_usage())

    parser.add_argument('dataPath', nargs='*', help="Directory with input frames. Multiple values are accepted.")
    parser.add_argument('-D', '--dataset-file', dest='DatasetListFile', nargs='?', default=None, const='datasets.list',
                        metavar='FILE',
                        help='File with list of datasets to use. When no value FILE is given, "datasets.list" is expected.')

    parser.add_argument('-out', '--output-file', dest='OutputScale', metavar='FILE', default='scaled.HKL',
                        help='File name for output from scaling.')

    parser.add_argument('-g', dest='ShowGraphs', default=True, action='store_true',
                        help='Show merging statistics in graphs in the end.')

    parser.add_argument('--min-dataset', dest='minData', default=2, metavar='NUM', type=int,
                        help="Minimal number of frames to be considered as dataset.")

    parser.add_argument('-p', '--parameter', dest='XDSParameter', nargs='+', action='append', metavar='PAR= VALUE',
                        help='Modification to all XDS.INP files. Parameters format as defined for XDS.INP. Overrides '
                             'parameters from --parameter-file.')
    parser.add_argument('-P', '--parameter-file', dest='XDSParameterFile', nargs='?', default=None,
                        const='XDSKAPPA.INP', metavar='FILE',
                        help='File with list of parameters to modify XDS.INP files. Parameters format as defined for '
                             'XDS.INP. When no value FILE is given, "XDSKAPPA.INP" is expected.')

    parser.add_argument('-r', '--reference-dataset', dest='ReferenceData', metavar='DATASET',
                        help='Name of reference dataset from working list. The first one used by default. For '
                             'external reference dataset use: -p REFERENCE_DATA_SET= path/data/XDS_ASCII.HKL')

    parser.add_argument('-f', '--force', dest='ForceXDS', action='store_true',
                        help='Force integration on unsuccesfull indexing.')
    parser.add_argument('-opt', '--optimize', dest='OptIntegration', nargs='?', action='append', const='ALL',
                        metavar='ALL FIX BEAM GEOMETRY',
                        help='Run XDS twice, with optimized parameters in second run. FIX - fix parameters in '
                             'integration; BEAM - copy BEAM parameters from INTEGRATE.LP; GEOMETRY - copy GXPARM.XDS '
                             'to XPARM.XDS. One keyword per parameter occurance. When given without a value, '
                             'ALL is presumed.')
    parser.add_argument('--backup', dest='BackupOpt', nargs='?', const='backup', default=None, metavar='NAME',
                        help='Backup datasets folders prior optimization to their subfolder ("backup" on empty value)'
                             '. It will erase older backup of [NAME] if present. No backup by default.')

    # help on empty input
    if len(sys.argv) == 1:
        parser.print_help()  # help on empty input
        sys.exit(1)
    logging.info('Command line input: ' + ' '.join(sys.argv))
    args = parser.parse_args()
    logging.debug('Input understanding:')
    logging.debug(args)  # + '\n'.join([key + ': ' + val for key, val in vars(args).items()]))
    return args


def run():
    xdskappa.intro()
    # logging.info('''
    #
    # Xdskappa ({version}, {date})
    # ==========================
    #
    # '''.format(version=__version__, date=datetime.datetime.now()))
    in_data = ParseInput()
    # print in_data

    if (len(in_data.dataPath) == 0) and (in_data.DatasetListFile == None):
        raise xdskappa.RuntimeErrorUser("Nor path to data, nor dataset file specified. See help or documentation.")

    if len(in_data.dataPath) > 0:
        datasets, names = common.GetDatasets(in_data)
        common.my_print("Found datasets:")
        for d in names:
            common.my_print(datasets[d])
        common.my_print("Found datasets saved to datasets.list")

    if in_data.DatasetListFile:
        datasets, names = common.ReadDatasetListFile(in_data.DatasetListFile)

    common.my_print("Using datasets (name, path):")
    for d in names:
        common.my_print(d + '\t' + datasets[d])

    common.PrepareXDSINP(in_data, datasets, names)

    if in_data.ReferenceData:
        names.insert(0, names.pop(names.index(in_data.ReferenceData)))

    common.RunXDS(names)

    if in_data.ForceXDS:
        common.ForceXDS(names)

    common.PrintISa(names)

    if in_data.OptIntegration != None:  # TODO: Nedelej pri neuspesne indexaci
        if in_data.BackupOpt != None:
            common.my_print('Backing up previous run...')
            common.BackupOpt(names, in_data.BackupOpt)

        oldisa = common.ReadISa(names)
        common.OptimizeXDS(names, in_data.OptIntegration)

        common.my_print("Running XDS...")
        common.RunXDS(names)

        newisa = common.ReadISa(names)
        opt.PrintISaOptimized(oldisa, newisa)

    # common.OptimizeXDS(names, in_data.OptIntegration)
    # common.RunXDS(names)
    # common.PrintISa(names)

    common.Scale(names, in_data.OutputScale)

    if in_data.ShowGraphs:
        common.ShowStatistics(names, ['scale'])


def main():
    try:
        run()
    except KeyboardInterrupt:
        common.my_print('Keyboard interrupt. Exiting...')
        sys.exit(0)
    except xdskappa.RuntimeErrorUser as e:
        logging.error('ERROR: ' + str(e))
        sys.exit(2)
    except Exception as e:
        logging.exception(e)
        sys.exit(2)


if __name__ == "__main__":
    main()
    sys.exit(0)
