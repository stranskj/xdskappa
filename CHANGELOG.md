v0.5.2
======

## Fixes

* Update for compatibility with recent XDS (20240712 and newer)
  * STRONG_PIXEL changed to SIGNAL_PIXEL
  * Won't work with older XDS versions
* Handling an error, when no `xds.log` was produced

v0.5.1
======

## Fixes

* Dataset correlation table is not created, when only one run/dataset is processed
* Small fixes in log outputs

v0.5.0
======

## New features
* Indexing solution reported after IDXREF and CORRECT
* New order of jobs and parallel XDS runs by default
* Correlation table between datasets extracted to xdskappa.log


## Improvements
* The goniometer geometry is properly calculated regardless of axis naming in the headers
* PEP517 compatible packaging

## Fix
* Nicer error when no dataset is found

v0.4.0
======

## New feature

* Multiple XDS jobs can run in parallel

## Improvements
* Documentation update

## Fix
* Typos in help and logs

v0.3.2
======

## New feature

* ORGX and ORGY are now read from the file headers, which are (usually) correct.

## Fix
* Typos in help and logs


v0.3.1
==========

## New features
  * Progress of *XDSkappa* tools are logged into files

## Improvements
  * Further under the hood modernization
  * Some clarifications in documentation and help
  * Subtools are listed in help
  
## Fixes
  * Forcing integration after not-great indexing did not work.


v0.3.0
==========

## News
  * Technical modernization
    * Python3
    * Proper pythonic packaging

v0.2.5.1
==========

## Fixes:
 * Version string fix


v0.2.5
==========

## New features
* Updated defaults of XDS.INP:
   * DELPHI= 15
   * SEPMIN= 7.0
   * CLUSTER_RADIUS= 3.5
   * DETECTOR= BRUKER
* Example module file for Enviromental Modules

## Fixes:
* Clean up in help
* Fixes in packaging
* Releases Python updated to 2.7.15
* Fixed issues with parsing of non-standard CORRECT.LP
* No longer stalls during scaling


