from .version import version

__version__ = version

#from xdskappa.common import my_print
import sys, os
import datetime, time
import logging
import argparse

LIST_SEPARATOR = '\t'
LICENSE = "The software is distributed under GNU General Public License v3."
VERSION = __version__



class RuntimeErrorUser(RuntimeError):
    '''
    Exception marking user-related errors, which should be handled user-friendly.
    '''
    pass

class RuntimeWarningUser(RuntimeError):
    '''
    Exception marking user-related warnings, which should be handled user-friendly.
    '''
    pass

class Exit(Exception):
    '''
    Exception to cleanly exit XDSkappa.
    '''

def logging_config(prog_name = 'xdskappa'):
    return dict(
    version=1,
    formatters={
        'simple_print': {'format': '%(message)s'}
    },
    handlers={
        'print_stdout': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple_print',
            'level': logging.WARNING
        },
        'file_log': {
            'class': 'logging.FileHandler',
            'formatter': 'simple_print',
            'level': logging.INFO,
            'filename': 'xdskappa.log',
            'mode': 'a'
        },
        'debug_file': {
            'class': 'logging.FileHandler',
            'formatter': 'simple_print',
            'level': logging.DEBUG,
            'filename': prog_name+'.debug.log',
            'mode': 'w'
        },
    },
    root={
        'handlers': ['print_stdout', 'file_log', 'debug_file'],
        'level': logging.DEBUG
    }

)


def my_print(msg):
    '''
    Prints to sdout, but also logs as logging.INFO
    :param args:
    :return:
    '''

    print(msg)
    logging.info(msg)


class Job(object):
    '''
    Generic class for running a programme. Actual programmes inherits this class and modifies class members apropriately.
    '''

    def __init__(self, *args, run=True, **kwargs):
        '''
        Runs the programme using class members. Args, kwargs are passed over to the main programme function.
        '''

        self.run_job = run
        Job.__set_meta__(self)
        try:
            logging.config.dictConfig(logging_config(self._program_name))
        except ValueError or PermissionError as e:
            print(repr(e))
            print('ERROR: Cannot initialize logging. Permission denied.\n'
                  'Check, that you have sufficient rights to write in current folder.')
            self.job_exit = 2
            return
        self.__set_meta__()
        self.__set_argument_parser__()
        self.__program_arguments__()
        self.job_exit = None
        self._args = argparse.Namespace()
        self._args.verbosity = 3  # Ensures printing exception callback, if something goes wrong before running the __worker__
        if self.run_job:
            self.__run__(*args, **kwargs)

    def __set_meta__(self):
        '''
        Sets various package metadata
        '''

        self._program_short_description = 'Package for processing data from multi-axis goniometer'

        self._program_name = os.path.basename(sys.argv[0])
        self._program_version = __version__
        self._usage = None # Ensures standard argparse usage

    def __worker__(self):
        '''
        The actual programme worker
        :return:
        '''
        pass

    def __program_arguments__(self):
        '''
        Settings of CLI arguments. self._parser to be used as argparse.ArgumentParser()
        '''
        pass

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

    def __set_argument_parser__(self, parser=None):
        if parser is not None:
            self._parser = parser
        else:
            description = '''{short_desc}

USAGE
'''.format(short_desc=self._program_short_description)
            self._parser = argparse.ArgumentParser(description=description,
                                                   formatter_class=argparse.RawDescriptionHelpFormatter,
                                                   epilog=self.__help_epilog__(),
                                                   usage=self._usage)
            program_version_message = '%%(prog)s %s \nPython %s' % (self._program_version, sys.version)
            self._parser.add_argument('-V', '--version',
                                      action='version',
                                      version=program_version_message)
            self._parser.add_argument('-v', '--verbosity',
                                      dest='verbosity',
                                      default=0,
                                      action='count',
                                      help='Increases output verbosity')

    def __parse_arguments__(self, argv=None):
        '''

        :param argv:
        :return:
        '''
        if argv is None:
            argv = sys.argv[1:]

        self._args = self._parser.parse_args(argv)
        self.__argument_processing__()

        logging.debug(f'Input understanding:\n{self._args}\n')
        #logging.debug(self._args)  # + '\n'.join([key + ': ' + val for key, val in vars(args).items()]))

    def __run__(self, *args, **kwargs):
        '''
        Running the programme
        '''

        try:
            self.__intro__()
            self.__parse_arguments__()

            start_t = time.time()
            self.__worker__()
            el_time = time.time() - start_t
            my_print('Finished. Time elapsed: {:.1f} s'.format(el_time))
            self.job_exit = 0


        except KeyboardInterrupt:

            my_print('Keyboard interrupt. Exiting...')

            self.job_exit = 0

        except RuntimeErrorUser as e:

            logging.error('ERROR: ' + str(e))

            self.job_exit = 2

        except Exit:
            my_print('Finished.')
            self.job_exit = 0

        except Exception as e:

            logging.debug('''
Program name:    {prog_name}
Package version: {prog_ver}
Python version:  {python_ver}
Program input:
{cli_in}
Input understanding:
{args}'''.format(prog_name=self._program_name,
                 prog_ver=self._program_version,
                 python_ver=sys.version,
                 cli_in=sys.argv,
                 args=self._args))
            logging.exception(e)

            print('Please, report back to the developers. Include the debug file with the report.')

            self.job_exit = 2

    def __intro__(self):
        my_print("")
        my_print("\t========================")
        my_print('\t{}'.format(self._program_name))
        my_print("\tVersion: {}".format(__version__))
        my_print("\tDate: {}".format(datetime.datetime.now()))
        my_print("\tAuthor: Jan Stransky")
        my_print("\t========================")
        logging.debug('Python and system versions:\n'+sys.version)
        my_print(" ")
        my_print(LICENSE)
        my_print(" ")
        logging.info('Run command:\n' + " ".join(sys.argv) + '\n')