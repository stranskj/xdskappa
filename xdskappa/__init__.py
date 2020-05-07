from .version import version

__version__ = version

from xdskappa.common import my_print
import sys, os
import datetime

LIST_SEPARATOR = '\t'
LICENSE = "The software is distributed under GNU General Public License v3."
VERSION = __version__

def intro():
    my_print("")
    executable_name = os.path.split(sys.argv[0])[-1]
    my_print('\t{}'.format(executable_name))
    my_print("\tVersion: {}".format( __version__))
    my_print("\tDate: {}".format(datetime.datetime.now()))
    my_print("\tAuthor: Jan Stransky")
    my_print("\t========================")
    my_print(" ")
    my_print(LICENSE)
    my_print(" ")