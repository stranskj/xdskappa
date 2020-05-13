from .version import version

__version__ = version

#from xdskappa.common import my_print
import sys, os
import datetime
import logging

LIST_SEPARATOR = '\t'
LICENSE = "The software is distributed under GNU General Public License v3."
VERSION = __version__

def intro():
    my_print("")
    executable_name = os.path.split(sys.argv[0])[-1]
    my_print("\t========================")
    my_print('\t{}'.format(executable_name))
    my_print("\tVersion: {}".format( __version__))
    my_print("\tDate: {}".format(datetime.datetime.now()))
    my_print("\tAuthor: Jan Stransky")
    my_print("\t========================")
    my_print(" ")
    my_print(LICENSE)
    my_print(" ")
    logging.info('Run command:\n'+" ".join(sys.argv)+'\n')

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
