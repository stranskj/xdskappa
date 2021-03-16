#!/bin/python

import xdskappa.common as common
import os, sys
from xdskappa.xdsinp import XDSINP
import xdskappa
import argparse
import logging
import logging.config
import freephil as phil

prog_name='xdskappa.run_xds'
prog_short_description='Runs XDS without generating XDS.INP from scratch. Useful after custom modifications of XDS.INP. No scaling with xscale is done.'
#logging.config.dictConfig(xdskappa.logging_config(prog_name))

__version__ = xdskappa.__version__

XDS_JOBS = ['XYCORR', 'INIT', 'COLSPOT', 'IDXREF', 'DEFPIX', 'INTEGRATE', 'CORRECT']

phil_job_control =  phil.parse(
    '''
job_control
.help = Controlling of  processing flow. The parameters are following freePHIL syntax. They can be passed to XDSkappa as a file, or typed in directly after -J. Note, that actual performance can be determined not only by available CPU, but also available data throughput. 
{
    nproc = None
    .type = int
    .help = Overall maximum number of CPUs to be used. If None, all cores are used.
    job
    .help = Define maximum number of cores used by XDS with in a run. This determines number of runs runnnig in parallel.
    {
        xycorr = 1
        .type = ints(size=1)
        init = 4
        .type = ints(size=1)
        colspot = 4
        .type = ints(size_min=1, size_max=2)
        .help = Second number specifies number of jobs to be spawned by XDS itself. Left on XDS, if empty.
        idxref = 2
        .type = ints(size=1)
        defpix = 1
        .type = ints(size=1)
        integrate = 4
        .type = ints(size_min=1, size_max=2)
        .help = Second number specifies number of jobs to be spawned by XDS itself. Left on XDS, if empty.
        correct = 4 
        .type = ints(size=1)
    } 
    max_jobs = None
    .type = int
    .help = Maximum number of jobs to be run in parallel. If None, derived automatically.
}
    '''
)

def parse_job_control(args, file_out='job_control.phil',verbose=False, return_unhandled=False, quick_parse=False):
    '''
    Parses CLI input into a PHIL object
    @param args: List of CLI argumetns
    @type  args: list
    @return: freephil.scope_extract
    '''

    def _is_a_phil_file(filename):
        return any(
            filename.endswith(phil_ext)
            for phil_ext in (".phil", ".param", ".params", ".eff", ".def")
        )


    # Parse the command line phil parameters
    user_phils = []
    unhandled = []
    interpretor = phil_job_control.command_line_argument_interpreter()

    # TODO: enable space separated = ; clever splits and strips?

    for arg in args:
        if (
                _is_a_phil_file(arg)
                and os.path.isfile(arg)
                and os.path.getsize(arg) > 0
        ):
            try:
                user_phils.append(phil.parse(file_name=arg))
                xdskappa.my_print('Job resource control parameters were read from: {}'.format(arg))
            except Exception:
                if return_unhandled:
                    unhandled.append(arg)
                else:
                    raise
        # Treat "has a schema" as "looks like a URL (not phil)
        elif "=" in arg:  # and not urlparse(arg).scheme:
            try:
                user_phils.append(interpretor.process_arg(arg=arg))
            except Exception:
                if return_unhandled:
                    unhandled.append(arg)
                else:
                    raise
        else:
            unhandled.append(arg)

    # Fetch the phil parameters
    phil_out, unused = phil_job_control.fetch(
        sources=user_phils, track_unused_definitions=True
    )

    # Print if bad definitions
    if len(unused) > 0:
        msg = [item.object.as_str().strip() for item in unused]
        msg = "\n".join(["  %s" % line for line in msg])
        raise xdskappa.RuntimeErrorUser(
            "The following definitions were not recognised\n%s" % msg
        )

    # Extract the parameters
    with open(file_out,'w') as fiout:
        phil_out.show(out=fiout,attributes_level=1)

    xdskappa.my_print('Job resource controlling parameters were written to: {}'.format(file_out))
    return phil_out.extract().job_control



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
        common.RunXDS(names, job_control=in_data.job_control, force=in_data.ForceXDS)

        if in_data.ForceXDS and in_data.job_control is None:
            common.ForceXDS(names, job_control=in_data.job_control)
        
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
        parser.add_argument('-J', dest='job_control', nargs='*', metavar='PHIL_FILE',
                            help='Controlling of XDS parallelization. Takes PHIL arguments, '
                                 'or PHIL file. If no argument is used, default values are used. '
                                 'When no additional parameters are used, default values are '
                                 'used, and a control file is written to "job_contol.param". Use '
                                 '"-J help" for more details.')
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
        if self._args.job_control is not None:
            import xdskappa.run_xds
            if self._args.job_control is not None:
                import xdskappa.run_xds
                if 'help' in self._args.job_control:
                    xdskappa.run_xds.phil_job_control.show(attributes_level=1)
                    raise xdskappa.Exit
            self._args.job_control = xdskappa.run_xds.parse_job_control(self._args.job_control)

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