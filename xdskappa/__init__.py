from .version import version
__version__ = version

LIST_SEPARATOR = '\t'
LICENSE = "The software is distributed under GNU General Public License v3."
VERSION = __version__

def intro():
    print("")
    print("\t{}".format( __version__))
    print("\tAuthor: Jan Stransky")
    print("\t========================")
    print(" ")
    print(LICENSE)
    print(" ")