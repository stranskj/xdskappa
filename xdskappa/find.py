import xdskappa.common as common
import xdskappa
import argparse
import sys

prog_name='xdskappa.find'
prog_short_description='Finds datasets'

import logging.config
#logging.config.dictConfig(xdskappa.logging_config(prog_name))

__version__ = xdskappa.__version__


def run(inpPar):

    datasets,names = common.GetDatasets(inpPar) #TODO: use of output file name
    xdskappa.my_print("Found datasets:")
    for d in names:
        xdskappa.my_print(d + '\t' + datasets[d])
    xdskappa.my_print("Found datasets saved to " + inpPar.DatasetListFile)

    return 0

class FindDatasetsJob(xdskappa.Job):
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
        parser.add_argument('dataPath',
                            nargs='+',
                            help="Directory (or more) with input data")
        parser.add_argument('-o', '--datasets-file',
                            dest='DatasetListFile',
                            metavar='FILE',
                            default='datasets.list',
                            help='File with list of found datasets.')
        parser.add_argument('--min-dataset',
                            dest='minData',
                            default=2,
                            metavar='NUM',
                            type=int,
                            help="Minimal number of frames to be concidered as dataset.")

    def __argument_processing__(self):
        '''
        Adjustments of raw input arguments. Modifies self._args, if needed

        '''
        if len(sys.argv) == 1:
            self._parser.print_help()  # help on empty input
            self.job_exit = 1
            self.run_job = False

    def __help_epilog__(self):
        '''
        Epilog for the help

        '''
        pass

def main():
    job = FindDatasetsJob()
    return job.job_exit


if __name__ == "__main__":
    sys.exit(main())