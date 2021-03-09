# xdskappa 
## Introduction
_xdskappa_ is a programme designed to simplify processing X-ray diffraction data collected on diffractometers with 4-circle goniometers using _XDS_. The software was primarily designed for D8 Venture in CMS, IBT but it is know to work also with ither D8 Venture systems. Data collected in-situ (using ISXstage) can be also processed.

There are no limitations on geometry when collecting data.

## Data requirements 
Collected frames need to be converted to CBF format with complete headers.

### How to get CBF file from D8 Venture

In _Proteum_, tab _Reduce data_, _Convert images_. Select datasets to convert and path where to put CBF files. Choose `cbf` from drop down menu and uncheck `unwrap`. It is also possible to set the system for automatic conversion of the collected frames.

_Note:_ The `unwrap` option actually does nothing to CBF, the conversion might not even work in later  versions of Proteum, when it is checked

_Note 2:_ The CBF conversion can be performed as the data are collected.

The plugin for conversion is sold separately by Bruker, so it is highly advised to do the conversion on site as soon as possible.

Do not use long file names due to problems with long path names (see *Important notes*).

### Other conversion tools
There are other tools to convert the dat from `sfrm` to `cbf`, namely `sfrmtools` and `adxv`. However, these tools  produces CMF files with incomplete headers, therefore they cannot be used for processing with XDSkappa.

## Usage 
### Basic usage
The most basic usage is to supply only folder(s) with collected data:
```
xdskappa foo1
```
The commmand will find datasets in folder `foo1`, creates `XDS.INP` files with account to actual geometry and runs basic data processing and scaling using XDS and XSCALE.

*Note*: This behaviour is different form other XDS related tools, where filename template is given.

### Example with description 
Let `foo` is a folder with files `foo_01_0001.cbf` - `foo_01_0180.cbf`, `foo_02_0001.cbf` - `foo_02_0180.cbf` and let `bar` is a folder with files `bar_01_0001.cbf` - `bar_01_0180.cbf`, `bar_02_0001.cbf` - `bar_02_0180.cbf`. `foo` and `bar` are subfolders of current working subfolder. _xdskappa_ is run with following command:
```
xdskappa foo bar
```
The programme will find datasets in given folders, generates `XDS.INP` from file headers, attempts processing using _XDS_ and scales them using _XSCALE_. Following files and folders are produced:
  - **Subfolders with processed datasets**: for each found dataset one subfolder is made. The name of the subfolder is composed from a number, path to data (where "/" is replaced to "_") and file name (before number series). In the example these subfolders are created: `1_foo_foo_01`, `2_foo_foo_02`, `3_bar_bar_01` and `4_bar_bar_02`. Each subfolder consists of input file `XDS.INP` and _XDS_ processing results.
  - **datasets.list**: a file which lists all found datasets. Each row consists of name of the datasets and name template as used by _XDS_. You can modify this file to specify which datasets you want to use with _xdskappa_. A `#` is accepted as a comment.
  - **scale**: folder with input file `XSCALE.INP` and outputs of scaling. Scaled, unmerged data are stored in `scale/scaled.HKL`
  - **xdskappa.log**: Log file

There are no limitations on geometry when collecting data.

## Arguments 
More detailed description of programme arguments:
  - **--h, -- --help**: shows help message and exits
  - **Not-named positional argument(s)**: __This, or --D is requiered.__ Give one or more directories, where to look for frames. It is advised to use as the very first argument. See [[group:public:navody:navody_k_programum:xdskappa#important_notes|Path names]]. Found datasets names and paths are stored in `datasets.list`. 
  - **--D [FILE], -- --dataset-file [FILE]**: __This, or data path(s) is requiered__. Specify file, which includes list of datasets to use. Such file (`datasets.list`) is normally generated, when path(s) is given. Entries are in format: output_subdirectory<tab>path/template_????.cbf. `#` can be used for comments, e.g. exclude some datasets from processing. When the argument is given with no value, a file with name `datasets.list` is expected.
  - **--out FILE, -- --output-file FILE**: File name for output from scaling. The default file name is `scale.HKL`. The output is placed in subfolder `scaled`.
  - **--g**: Shows merging statistics in graphs in the end for all datasets and scaled data. Also gnuplot input file `gnuplot.plt` is generated, which can be further used. Data for the plots are stored in file `statistics.out` in each subdirectory, where columns have meanings in this order: resolution, redundancy, _Rmerge_, _Rmeas_, completeness, _I/sigma(I)_, _CC(1/2)_, Anomalous _CC(1/2)_, Anomalous _I/sigma(I)_
  - **-- --min-dataset NUM**: Minimal number of frames to be considered as dataset when looking for datasets in paths. Default value is 2. The aim is to exclude dark frames from data processing.
  - **--p PAR= VALUE [PAR= VALUE ...], -- --parameter PAR= VALUE [PAR= VALUE ...]**: Give an argument(s) to be used for processing of all datasets. One or more parameters (space separated) can be used with one `-p`. Parameters are in format as defined for XDS.INP. These parameters override parameters from `-P` and those generated from frame headers. Parameters, merged with those given via `-P`, are stored in `XDSKAPPA_run.INP`. _Example:_ `-p ORGX= 393 ORGY= 505 FRIEDEL'S_LAW= TRUE -p UNIT_CELL_CONSTANTS= 77 77 38 90 90 90 SPACE_GROUP_NUMBER= 96`
  - **--P [FILE], -- --parameter-file [FILE]**: Give an argument(s) to be used for processing of all datasets via file. Parameters are in format as defined for XDS.INP. When `-P` is given with no value, file `XDSKAPPA.INP` is expected. Parameters, merged with those give via `-p` are stored in `XDSKAPPA_run.INP`.
  - **--r DATASET, -- --reference-dataset DATASET**: Specifies name of dataset (as in `datasets.list`), which should be used as reference. See more in [[group:public:navody:navody_k_programum:xdskappa#tips_tricks|Tips & trikcs]]
  - **--f, -- --force**: Force integration on unsuccessful indexing.
  - **--opt [ALL FIX BEAM GEOMETRY], -- --optimize [ALL FIX BEAM GEOMETRY]**: Run XDS twice, with optimized parameters in second run. `FIX` - fix parameters in integration; `BEAM` - copy BEAM parameters from `INTEGRATE.LP`; `GEOMETRY` - copy `GXPARM.XDS` to `XPARM.XDS`. One keyword per parameter occurance. When given without a value, `ALL` is presumed.
  - **-- --backup [NAME]**: Backup datasets folders prior optimization to their subfolder ("backup" on empty value) . It will erase older backup of [NAME] if present. No backup by default.
  - **--J [PHIL_FILE or PHIL_COMMANDS]**: Controlling of XDS parallelization. Takes PHIL arguments, or PHIL file. If no argument is used, default values are used. When no additional parameters are used, default values are used, and a control file is written to "job_contol.param". Use `-J help` for more details.'

## Important notes 
  * **Path names**: you can use relative or absolute path names to folders with frames. Some Linux shells will expand `~` and `..` to absolute path before passing it to programme, which can cause problems with too long path names. _Example:_ `ln -s /some/very/long/path/which/has/to/be/truncated/for/XDS linkname` will create a symbolink link (shortcut) with name `linkname`. Works for both files and folders.
  * **Path name lenghts**: _XDS_ limits length path name to about 40 characters. Use symbolic links to overcome the problem.
  * **Hierarchy of parameters**: Parameters to XDS.INP are placed with increasing priority: generated based on frame headers, supplied via file (`-P`), supplied vie command line (`-p`). _Example:_Parameter `JOB=` has default value `XYCORR INIT COLSPOT IDXREF DEFPIX INTEGRATE CORRECT`. That can be overwritten by `JOB= DEFPIX INTEGRATE CORRECT` present in file `XDSKAPPA.INP` and running `xdskappa data -P`. All of that can be overwritten by running `xdskappa data -P -p JOB= CORRECT`.
  * **Scaling graphs**: Since Jan 2017, data for graphs plotting are always generated. To see them run: `gnuplot -p gnuplot.plt`. The parameter `-g` is irrelevant now.

## *XDSkappa* tools
Some of the *XDSkappa* steps are also available in separate tools. This allows more detailed data processing, and also processing of data from different sources, where processing multiple very similar datasets is needed (fragment screening, multicrystal data from synchrotrons, etc.). This is initial set, other tools will come in later versions.

Each tool has its set of command line parameters, use `-h` for detailed help.

### xdskappa.run_xds
This tool runs *XDS* at multiple datasets. The datasets definition in `dataset.list`, the folder structure and starting `XDS.INP` for each dataset. The tool can modify `XDS.INP` in similar fashion as the core `xdskappa`.

Appart other multidataset cases, for standard 4-circle data collection the tool can be useful, when some datasets needs special care with dataset-specific commands in `XDS.INP`, for example `EXCLUDE_DATA_RANGE=`, ice rings showing during the data collection, etc.

The most important difference from the core `xdskappa` is that the input files are _not_ generated automaticaly; in the core, the `XDS.INP` is generated from scratch with every run.

### xdskappa.optimize
This tool performs the optimization steps as with `-opt` of the core `xdskappa`, but keeps rules from `xdskappa.run_xds`. User can pick, if the subsequent XDS run should be performed.

### xdskappa.show_stat
Extract merging statistics, and prepares them for plotting using _GNUplot_. In difference from the core tool, multiple folders with scaled data (e.g. containing `XSCALE.LP`) can be used. This can be useful for comparision of different data processing strategies. 

## Logging
XDSkappa produces several types of logs: overall log, run log for debugging and XDS logs. Error messages are designed with the best intentions to be informative enough; however, suggestions on improvement are welcome.

### Overall log
All actions of XDSkappa are logged to the file `xdskappa.log`. This file is never overwritten by XDSkappa, new messages always append to the existing file. This enables keeping history of all actions done using XDSkappa.

### Run log
Running of every tool produces a debug log file with the name of the tool: `tool_name.debug.log`. This file contains extensive information about the run, including full exception tracebacks, if the programme fails. Please, send this file to developers, if the programme fails with an exception. This file is overwritten with every run of the tool.

### XDS logs
Each run-processing folder also contains `xds.log`, which contains the same information as XDS produces to the terminal, when it is run traditionally. 

## Job control
XDS great advantage is great level of parallelization. However, with the relatively small detectors used in D8 Venture, modern CPUs can be still underused during the processing. Therfore, XDSkappa implements another level of parallelization to speed up the processing

The run of XDS is splitted to the individual XDS jobs, which are run in parallel for given number of runs/datasets. The number of parallel datasets is determined per XDS job.

This parallelization is triggered using `-J` parameter. When no additional parameter is provided, the parallelization is determined automatically, and the parameters are saved in file `job_control.param`. Optionally, file name with custom parameters, or directly the parameters can be provided. To see the description of the parameters, use `-J help`

The ob control parameters use PHIL syntax, the same type as used in _Phenix_ or _DIALS_.

## Tips & tricks 
#### Problem: Path to my data is too long. 
Use symbolic link to make a shortcut:
  ```
ln -s /some/very/long/path/which/has/to/be/truncated/for/XDS linkname
```
This will create a symbolink link (shortcut) with name `linkname`. Works for both files and folders.

#### Problem: I have already processed the data, I want just run optimization 
When `-opt` is given, _XDS_ is always run twice, where the second run is with `JOB= DEFPIX INTEGRATE CORRECT`, which is set automaticaly. Therefore, when you want to optimize already processed data, force the first run to be some short "meaningless" job by `-p`, e.g. add `-p JOB= XYCORR`. The run command can look like this:
  `xdskappa -D -P -p JOB= XYCORR -opt`

#### Problem: I have already processed the data, I just want to see output graphs. 
See the tool `xdskappa.show_stat`.

#### Problem: How can I choose a reference dataset? 
This includes two cases:
  - Dataset is one of those being processed:
     * Use parameter `-r` and give it a name of dataset. This change will be nowhere stored. By default, the first dataset is used.
     * In datasets list (e.g. file `datasets.list`), put the reference dataset description to the first place.
  - Dataset is not related to this data processing (data collected on different crystal, different place, different soak, etc.)
     * Use standard parameter for _XDS_: `-p REFERENCE_DATA_SET= some/data/XDS_ASCII.HKL`. This will override the default choice of first dataset.

## Files & folders
Detailed list and description of files, file types and folders used and produced by _xdskappa_.

### Working folder 
A folder in which _xdskappa_ is run.

### Parameter file 
A file which is used to supply parameters adjusting _XDS_ runs. It is a text file (of any name) which take whatever argument can be used in `XDS.INP`. The file is supplied to _xdskappa_ by `-P`. Parameters from this file are overridden by parameter `-p`.

Default files of this type:
  * **XDSKAPPA_run.INP**: Output. Compilation of parameters given to _xdskappa_ with `-p` and `-P`
  * **XDSKAPPA.INP**: Input. A default file name, which is expected, when `-P` is given without value

### Log files
See the section *Logging*

## Dependencies
  - _XDS_, namely `xds_par`
  - _XSCALE_, namely `xscale_par`
  - _gnuplot_ (optional)
