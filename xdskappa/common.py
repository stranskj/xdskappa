'''
Created on Mar 4, 2016

Set of common functions for xdskappa tools

@author: stransky
'''

import os, math, subprocess, re, glob, sys, shutil
from xdskappa.xdsinp import XDSINP
from xdskappa.xdataset import XDataset
import xdskappa.run_xds
import xdskappa
from xdskappa import my_print
from distutils import spawn
import logging
import concurrent.futures
import time
import copy


__version__ = xdskappa.__version__



# print=my_print

def GetStatistics(inFile, outFile):
    """
    Generate data file to plot statistics vs. resolution
    
    @param inFile: Input file name (CORRECT.LP or XSCALE.LP)
    @type  inFile: string
    
    @param outFile: Output file name
    @type  outFile: string
    """

    if not os.path.isfile(inFile):
        raise IOError(inFile + " is not available. Problem with data processing?")

    with open(inFile, 'r') as fin:
        firead = fin.read()
        if not 'SUBSET OF INTENSITY DATA WITH SIGNAL/NOISE >= -3.0 A' in firead:
            raise IOError(inFile + " is incomplete. Problem with data processing?")

        # get last table + some appendix in rows
        tab = firead.split('SUBSET OF INTENSITY DATA WITH SIGNAL/NOISE >= -3.0 A')[-1].split('\n')

    with open(outFile, 'w') as fout:
        fout.write('# Legend for columns\n')
        fout.write('# Resol.\tMultipl.\tRmerge\tRmeas\tComplet.\tI/sig\tCC1/2\tAnoCC\tSigAno\n')
        i = 4  # first row with numbers
        while not 'total' in tab[i]:
            # row = tab[i].split()

            row = []
            row.append(tab[i][0:9].strip())  # 0: resolution limit
            row.append(tab[i][10:21].strip())  # 1: Number of observed refl.
            row.append(tab[i][22:29].strip())  # 2: Number of unique refl.
            row.append(tab[i][30:39].strip())  # 3: Number of possible refl.
            row.append(tab[i][40:51].strip())  # 4: Completeness
            row.append(tab[i][52:62].strip())  # 5: R-factor observed
            row.append(tab[i][63:72].strip())  # 6: R-factor expecte
            row.append(tab[i][72:81].strip())  # 7: Compared
            row.append(tab[i][82:89].strip())  # 8: I/Sigma
            row.append(tab[i][90:99].strip())  # 9: R-meas
            row.append(tab[i][100:108].strip())  # 10: CC(1/2)
            row.append(tab[i][109:114].strip())  # 11: Anomal Correlation
            row.append(tab[i][115:123].strip())  # 12: SigAno
            row.append(tab[i][124:131].strip())  # 13: Nano

            res = row[0]
            try:
                multiplicity = "{:.2f}".format(float(row[1]) / float(row[2]))
            except ZeroDivisionError:
                multiplicity = "0.00"

            Rfac = row[5].strip('%')
            Rmeas = row[9].strip('%')
            completness = row[4].strip('%')
            Isig = row[8]
            CC = row[10].strip('*')
            AnoCC = row[11].strip('*')
            SigAno = row[12]

            fout.write(
                res + '\t' + multiplicity + '\t' + Rfac + '\t' + Rmeas + '\t' + completness + '\t' + Isig + '\t' + CC + '\t' + AnoCC + '\t' + SigAno + '\n')
            i += 1
    return


def GetWinSize():
    """
    Get size of screens
    
    @return: size of screens
    @type return: list of tuples
    """
    winsize = []
    if spawn.find_executable('xrandr'):  # TODO: nefunguje po ssh
        getwinsize = subprocess.Popen('xrandr', stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        for line_b in getwinsize.stdout:
            line = line_b.decode()
            if '*' in line:
                #    lin = re.search('[0-9]+[x][0-9]+', line)
                row = line.split()[0].split('x')  # lin.string[lin.begin():lin.end()].split('x')
                size = row[0], row[1]
                winsize.append(size)
        getwinsize.wait()

    # else:
    if len(winsize) == 0:
        size = '1920', '1080'
        winsize.append(size)
    return winsize


def ShowStatistics(Names, Scale=None, plot_name='gnuplot.plt'):
    """
    Shows statistics vs. resolution in multiplot using gnuplot
    
    @param Names: List of pahts do dataset results
    @type  Names: list of strings
    
    @param Scale: Path to scaled data
    @type  Scale: string 
    """
    for data in Names:
        #      if os.path.isfile(data+'/CORRECT.LP'):
        try:
            GetStatistics(data + '/CORRECT.LP', data + '/statistics.out')
        except IOError as e:
            my_print(e)
            my_print('Skipping...')
            Names.remove(data)
    if not (Scale == None):
        for sc in Scale:
            #      Names.append(Scale)
            if os.path.isfile(sc + '/XSCALE.LP'):
                try:
                    GetStatistics(sc + '/XSCALE.LP', sc + '/statistics.out')
                except IOError as e:
                    my_print(e)
                    my_print('Skipping...')
                    Scale.remove(sc)

    winsize = GetWinSize()

    #    winsize = ['1920','1080']

    plt = open(plot_name, 'w')

    plt.write('\
set terminal x11 size ' + winsize[0][0] + ',' + winsize[0][1] + ' \n\
set multiplot layout 3,3 \n\
set xlabel "Resolution [A]"\n\
set nokey \n \n\
set title "Completeness"\n\
set ylabel "%"\n\
set yrange [0:100] \n\
set xrange [*:*] reverse \n\
#set logscale x \n\
plot ')
    for data in Names:
        plt.write("'" + data + "/statistics.out' using 1:5 with lines title '" + data + "', ")
    if not (Scale == None):
        for sc in Scale:
            plt.write("'" + sc + "/statistics.out' using 1:5 with lines lw 3 title '" + sc + "', ")
    plt.write('\n')

    plt.write('\n\
set title "Rmerge"\n\
plot ')
    for data in Names:
        plt.write("'" + data + "/statistics.out' using 1:3 with lines title '" + data + "', ")
    if not (Scale == None):
        for sc in Scale:
            plt.write("'" + sc + "/statistics.out' using 1:3 with lines lw 3 title '" + sc + "', ")
    plt.write('\n')

    plt.write('\n\
set title "Rmeas"\n\
plot ')
    for data in Names:
        plt.write("'" + data + "/statistics.out' using 1:4 with lines title '" + data + "', ")
    if not (Scale == None):
        for sc in Scale:
            plt.write("'" + sc + "/statistics.out' using 1:4 with lines lw 3 title '" + sc + "', ")
    plt.write('\n')

    plt.write('\n\
set title "CC(1/2)"\n\
plot ')
    for data in Names:
        plt.write("'" + data + "/statistics.out' using 1:7 with lines title '" + data + "', ")
    if not (Scale == None):
        for sc in Scale:
            plt.write("'" + sc + "/statistics.out' using 1:7 with lines lw 3 title '" + sc + "', ")
    plt.write('\n')

    plt.write('\n\
set title "Redundancy"\n\
set ylabel "" \n\
set yrange [ 0:* ] \n\
plot ')
    for data in Names:
        plt.write("'" + data + "/statistics.out' using 1:2 with lines title '" + data + "', ")
    if not (Scale == None):
        for sc in Scale:
            plt.write("'" + sc + "/statistics.out' using 1:2 with lines lw 3 title '" + sc + "', ")
    plt.write('\n')

    plt.write('\n\
set title "I/sig(I)"\n\
set ylabel "" \n\
set yrange [ 0:* ] \n\
plot ')
    for data in Names:
        plt.write("'" + data + "/statistics.out' using 1:6 with lines title '" + data + "', ")
    if not (Scale == None):
        for sc in Scale:
            plt.write("'" + sc + "/statistics.out' using 1:6 with lines lw 3 title '" + sc + "', ")
    plt.write('\n')

    plt.write('\n\
set title "Anomalous I/sig(I)"\n\
set ylabel "" \n\
set yrange [ 0:* ] \n\
plot ')
    for data in Names:
        plt.write("'" + data + "/statistics.out' using 1:9 with lines title '" + data + "', ")
    if not (Scale == None):
        for sc in Scale:
            plt.write("'" + sc + "/statistics.out' using 1:9 with lines lw 3 title '" + sc + "', ")
    plt.write('\n')

    plt.write('\n\
set title "Anomalous CC"\n\
set ylabel "%" \n\
set yrange [ *:* ] \n\
plot ')
    for data in Names:
        plt.write("'" + data + "/statistics.out' using 1:8 with lines title '" + data + "', ")
    if not (Scale == None):
        for sc in Scale:
            plt.write("'" + sc + "/statistics.out' using 1:8 with lines lw 3 title '" + sc + "', ")
    plt.write('\n')

    plt.write('\n\
set title "Legend"\n\
set ylabel "" \n\
set yrange [ 1000:1100 ] \n\
set xlabel "" \n\
set key #center \n\
set tics textcolor rgb "white" \n\
unset border \n\
unset ytics \n\
unset xtics \n\
plot ')
    for data in Names:
        plt.write("'" + data + "/statistics.out' using 1:2 with lines title '" + data + "', ")

    if not (Scale == None):
        for sc in Scale:
            plt.write("'" + sc + "/statistics.out' using 1:2 with lines lw 3 title '" + sc + "', ")

    plt.write('\n')

    plt.write('unset multiplot \n')

    plt.close()

    my_print(" ")
    my_print("Input file to plot merging statistics was written to {}. To see the graphs, run:".format(plot_name))
    my_print(" ")
    my_print("gnuplot -p " + plot_name)


#    if spawn.find_executable('gnuplot') == None:
#        print "Gnuplot not found in $PATH. You can plot results using statistic.out in subdirectories"
#    arg = 'gnuplot -p gnuplot.plt'.split()
#    plot = subprocess.Popen(arg)
#    plot.wait()

def getISa(path):
    corlp = path
    if not os.path.isfile(corlp):
        raise IOError(path + "/CORRECT.LP is not available. Problem with data processing?")
    fcor = open(corlp, 'r')

    line = fcor.readline()
    while (line.split() != ['a', 'b', 'ISa']) and (line != ''):
        line = fcor.readline()

    if line == '':
        return 'N/A'

    line = fcor.readline().split()
    fcor.close()
    return line[2]


def ReadISa(Paths):
    outDict = {}
    for dataset in Paths:
        try:
            outDict[dataset] = getISa(dataset + '/CORRECT.LP')
        except IOError:
            outDict[dataset] = 'N/A'

    return outDict


def PrintISa(Paths):
    my_print('\nISa for individual datasets:')
    my_print('\tISa\tDataset')

    isalist = ReadISa(Paths)

    for dataset in sorted(isalist):
        my_print('\t' + isalist[dataset] + '\t' + dataset)
    return

def xds_worker(path):

    with open(path + '/xds.log', 'a') as log:
        xds = subprocess.Popen(['xds_par'], cwd=path, stdout=log, stderr=subprocess.STDOUT)

        # for line_b in xds.stdout:
        #     line = line_b.decode()
        #     log.write(line)
        #     if '***** COLSPOT *****' in line:
        #         my_print('Finding strong reflections...')
        #
        #     if '***** IDXREF *****' in line:
        #         my_print('Indexing...')
        #
        #     if '***** INTEGRATE *****' in line:
        #         my_print('Integrating...')

        xds.wait()

    xdsinp = XDSINP(path)
    xdsinp.read()
    job = xdsinp['JOB'][0]

    with open(os.path.join(path,job+'.LP'), 'r') as log:
        if '!!! ERROR !!!' in log.read():
            my_print(
                path +": An error during data procesing using XDS. Check "+job+".LP or xds.log files fo further details.")
            error = True
        else:
            my_print(path +":Finished.")
            error = False
    return xds.returncode, error

def RunXDS(Paths, job_control=None, force = False):
    '''
    Runs XDS in all Paths. If possible, jobs in parallel
    :@param Paths: Paths to the XDS.INP files and processing folders
    :@type Paths: list
    :@param job_control: How should be job control preformed. Input in PHIL scope format
    :@type job_control: freephil.scope
    :@param force: Perform all XDS jobs regardless encountered errors.
    :@type force: bool
    :@return:
    '''

    if spawn.find_executable('xds_par') == None:
        raise xdskappa.RuntimeErrorUser("Cannot find XDS executable.")


    assert len(Paths) > 0

    first_xdsinp = XDSINP(Paths[0])
    first_xdsinp.read()

    xds_jobs = first_xdsinp['JOB'][0].split()

    for job in xds_jobs:
        if job not in xdskappa.run_xds.XDS_JOBS:
            import difflib
            closest = difflib.get_close_matches(job,xdskappa.run_xds.XDS_JOBS,1)
            message = 'Unknown XDS job name: {}\n'.format(job)
            if len(closest) > 0:
                message += 'Did you mean {}?'.format(closest[0])
            raise xdskappa.RuntimeErrorUser(message)

    # Fallback to old RunXDS
    if job_control is None: # or job_control.max_jobs == 1
        RunXDS_old(Paths)
        return

    # Secure correct order of XDS jobs
    xds_jobs = [job for job in xdskappa.run_xds.XDS_JOBS if job in xds_jobs]

    for pth in Paths:
        shutil.copy(pth+'/XDS.INP',pth+'/XDS.INP_original_to_run')
        with open(pth+'/xds.log','w') as log:
            log.write('Original XDS.INP copied to XDS.INP_original_to_run.\n')

    if job_control.nproc is None:
        import multiprocessing
        nproc = multiprocessing.cpu_count()
    else:
        nproc = job_control.nproc

    try:
        run_Paths = copy.copy(Paths)
        failed = []
        for job in xds_jobs:

            job_pwr = job_control.job.__dict__[job.lower()]
            if len(job_pwr) == 2:
                job_cpu = job_pwr[0] * job_pwr[1]
            else:
                job_cpu = job_pwr[0]

            parallel_jobs = max(int(nproc/job_cpu),1) # +1 ?
            if job_control.max_jobs is not None:
                parallel_jobs = job_control.max_jobs#min(parallel_jobs,job_control.max_jobs)

            xdskappa.my_print('\nRunning {job} in {par_job} parallel jobs...'.format(job=job, par_job=min(parallel_jobs,len(run_Paths))))
            if len(run_Paths) == 0:
                raise xdskappa.RuntimeErrorUser('No XDS jobs to be run. All previous jobs finished with error? You can eforce XDS steps using parameter -f.')

            time_start = time.time()
            with concurrent.futures.ThreadPoolExecutor(max_workers=parallel_jobs) as ex:
                running_jobs = {}
                for pth in run_Paths:
                    xdsinp = XDSINP(pth)
                    xdsinp.read()
                    xdsinp['JOB'] = [job]
                    xdsinp['MAXIMUM_NUMBER_OF_PROCESSORS'] = ["{}".format(job_pwr[0])]
                    if len(job_pwr) == 2:
                        xdsinp['MAXIMUM_NUMBER_OF_JOBS'] = ["{}".format(job_pwr[1])]
                        #TODO: Maybe fix to 1, and do it on xdskappa level, to have CPU slightly oversaturated?
                        #Needs testing...
                    xdsinp.write()
                    running_jobs[pth] = ex.submit(xds_worker, pth)
                    if (job == 'CORRECT') and (pth == Paths[0]):
                        concurrent.futures.wait(running_jobs.values())

                concurrent.futures.wait(running_jobs.values())
                for path, rj in running_jobs.items():
                    if rj.result()[1] and not force:
                        run_Paths.remove(path)
                        failed.append(path)

            el_time = time.time() - time_start
            my_print('Finished {} in {:.1f}s.'.format(job,el_time))
    finally:
        for pth in Paths:
            shutil.copy(pth + '/XDS.INP_original_to_run', pth + '/XDS.INP')
            with open(pth+'/xds.log','a') as log:
                log.write('Original XDS.INP restored.\n')
    if len(failed) > 0:
        my_print('WARNING: Following runs have failed XDS jobs. Check the log files:')
        for path in failed:
            my_print('\t'+path)

def RunXDS_old(Paths):
    if spawn.find_executable('xds_par') == None:
        raise xdskappa.RuntimeErrorUser("Cannot find XDS executable.")

    for path in Paths:
        my_print("Processing " + path + ":")
        if not os.path.isfile(path + '/XDS.INP'):
            logging.warning("File not found: " + path + '/XDS.INP')
            continue

        with open(path + '/xds.log', 'w') as log:
            xds = subprocess.Popen(['xds_par'], cwd=path, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

            for line_b in xds.stdout:
                line = line_b.decode()
                log.write(line)
                if '***** COLSPOT *****' in line:
                    my_print('Finding strong reflections...')

                if '***** IDXREF *****' in line:
                    my_print('Indexing...')

                if '***** INTEGRATE *****' in line:
                    my_print('Integrating...')

            xds.wait()

        with open(path + '/xds.log', 'r') as log:
            if '!!! ERROR !!!' in log.read():
                my_print(
                    "An error during data procesing using XDS. Check IDXREF.LP, INTEGRATE.LP, other *.LP or xds.log files fo further details.")
            else:
                my_print('Finished.')

    return


def ForceXDS(paths, job_control=None):
    rerun = []
    for path in paths:
        with open(path + '/xds.log') as log:
            lines = log. read()
        if 'YOU MAY CHOOSE TO CONTINUE DATA' in lines:

            my_print("Attempting integration of: " + path)
            inp = XDSINP(path)
            inp.read()
            inp.SetParam('JOB= DEFPIX INTEGRATE CORRECT')
            inp.write()
            rerun.append(path)

    RunXDS(rerun,job_control=job_control)

    return


def BackupOpt(Paths, bckname):
    for path in Paths:
        pathbck = path + '/' + bckname
        # try:
        #    os.mkdir(pathbck)
        # except:
        #    print "Backup directory already exists, overwritting content: "+ pathbck 

        if os.path.isdir(pathbck):
            my_print('Backup in ' + pathbck + ' exists, deleting...')
            try:
                shutil.rmtree(pathbck, ignore_errors=False, onerror=IOError)
            except IOError:
                my_print('Nothing to remove')

        #try:
        # shutil.copytree(path, pathbck, symlinks=True)
        os.mkdir(pathbck)
        dircont = os.listdir(path)
        for fi in dircont:
            if os.path.isfile(path + '/' + fi):
                shutil.copy2(path + '/' + fi, pathbck + '/' + fi)

        # except Exception as e:
        #     my_print(e)
    return


def OptimizeXDS(Paths, Optim):
    if Optim == None or len(Optim) == 0:
        logging.warning('No optimization settings given.')
        return False

    if 'ALL' in Optim:
        Optim.extend(['BEAM', 'FIX', 'GEOMETRY'])
        Optim.remove('ALL')

    opt = ''
    for o in Optim:
        if not o in ['BEAM', 'FIX', 'GEOMETRY', 'ALL']:
            logging.warning('Unknown parameter to optimize: ' + o)
        else:
            opt += o + ' '
    my_print('Optimizing integration: ' + opt)  # TODO: co optimalizuje

    for path in Paths:
        inp = XDSINP(path)
        inp.read()
        if 'FIX' in Optim:
            #           inp = XDSINP(path)
            #          inp.read()
            inp.SetParam('REFINE(INTEGRATE)= ')
        #           inp.write()

        if 'GEOMETRY' in Optim:
            if os.path.isfile(path + '/GXPARM.XDS'):
                shutil.copy(path + '/GXPARM.XDS', path + '/XPARM.XDS')

        if 'BEAM' in Optim:
            if os.path.isfile(path + '/INTEGRATE.LP'):
                #               inp = XDSINP(path)
                #              inp.read()

                with open(path + '/INTEGRATE.LP') as intlp:

                    # find SUGGESTED VALUES FOR INPUT PARAMETERS, accending two rows inp.SetParam()

                    while not 'SUGGESTED VALUES FOR INPUT PARAMETERS' in intlp.readline():
                        pass

                    for i in range(2):
                        line = intlp.readline().split()
                        inp.SetParam(line[0] + ' ' + line[1])
                        inp.SetParam(line[2] + ' ' + line[3])


        #               inp.write()

        #        inp = XDSINP(path)  #TODO: otevrit, precist a zapsat jen jednou
        #        inp.read()
        inp.SetParam('JOB= DEFPIX INTEGRATE CORRECT')
        inp.write()

    return True


def Scale(Paths, Outname):
    try:
        os.mkdir('scale')
    except FileExistsError:
        my_print("\nDirectory already exists: scale")

    with open('scale/XSCALE.INP', 'w') as xscaleinp:
        xscaleinp.write('OUTPUT_FILE= ' + Outname + '\n')
        for path in Paths:
            if os.path.isfile(path + '/XDS_ASCII.HKL'):
                xscaleinp.write('   INPUT_FILE= ../' + path + '/XDS_ASCII.HKL\n')
            else:
                my_print('XDS_ASCII.HKL not available in ' + path)
                my_print('Excluding from scaling')

    my_print('\nScaling with xscale_par...')
    with open(os.devnull, 'w') as FNULL:
        xscale = subprocess.Popen('xscale_par', cwd='scale', stdout=FNULL, stderr=subprocess.STDOUT)
        xscale.wait()

    with open('scale/XSCALE.LP') as fout:
        if '!!! ERROR !!!' in fout:
            my_print('Error in scaling. Please read: scale/XSCALE.LP')
        else:
            my_print('Scaled. Output written in: scale/' + Outname)


def ReadDatasetListFile(inData):
    """
    Process file with list of datasets
    
    @param inData: path to dataset list file
    @type  inData: string
    
    @return Datasets: Dictionary of datasets
    @type Datasets: dict
    @return names: List of dataset's names 
    @type names: list
    """
    if not os.path.isfile(inData):
        raise xdskappa.RuntimeErrorUser('File not found: ' + inData)

    fin = open(inData, 'r')
    DatasetsDict = {}
    names = []
    for line in fin:
        row = line.strip().split(xdskappa.LIST_SEPARATOR)
        if row[0][0] == '#':
            continue
        names.append(row[0])
        DatasetsDict[row[0]] = row[1].strip('\n\r\t ')
    fin.close()
    return DatasetsDict, names


def MakeXDSParam(inParList):
    """
    Parse input from prameters modifing XDS.INP
    
    @param inParList: Parameters from input -p or --parameter
    @type inParList: list of list of string
    
    @return outParLitst: list of parameters as strings "PAR= VALUE1 VALUE2 ..."
    @type   outParLitst: list of string 
    """
    outParList = []
    i = -1
    for par in inParList:
        while par:
            if par[0].find("=") > -1:
                outParList.append(par[0])
                i += 1
            else:
                outParList[i] += " " + par[0]
            del par[0]
    return outParList


def ReadXDSParamFile(inFile):
    """
    Parse input file with parameters for modifing XDS.INP
    
    @param inFile: File with XDS.INP-like parameters
    @type inFile: file
    """
    if not os.path.isfile(inFile):
        raise xdskappa.RuntimeErrorUser('File not found: ' + inFile)

    with open(inFile, 'r') as fin:
        outParList = []
        for line in fin:
            outParList.append(line.strip('\r\n\t '))

    return outParList


def ProcessParams(inParam, inParamFile):
    """
    Parses input from -p- and -P-like input
    @param inParam: List of with paramters
    @type inParam: List
    @param inParamFile: Path to file with parameters
    @type inParamFile: string

    @return Dictionary of XDS parameters
    @type XDSINP
    """

    out_dict = XDSINP('temp')
    if inParamFile:
        # mod_list += ReadXDSParamFile(inParamFile)
        out_dict.path = inParamFile
        # try:
        out_dict.read()
        # except IOError as e:
        #     raise IOError(e)
        #     return

    mod_list = []
    #    par_dict = XDSINP('temp')
    if inParam:
        mod_list += MakeXDSParam(inParam)

    for par in mod_list:
        out_dict.SetParam(par)

    return out_dict


def PrepareXDSINP(inData, Datasets, Names):
    """
    Makes working dirs and XDS.INP for all chosen datasets
    
    @param inData: Parsed input
    @type inData: Namespace
    @param Datasets: Datasets list
    @type Datasets: dict
    @param Names: List of keys in Datasets (ordered)
    @type Names: list
    """
    my_print("\nProcessing...")

    # TODO: nejak z funkcnit/prerozdelit kvuli toolum?
    file_dict = XDSINP('temp')
    if inData.XDSParameterFile:
        # mod_list += ReadXDSParamFile(inData.XDSParameterFile)
        file_dict.path = inData.XDSParameterFile
        #try:
        file_dict.read()
        # except IOError as e:
        #     my_print(e)
        #     sys.exit(1)

    mod_list = []
    par_dict = XDSINP('temp')
    if inData.XDSParameter:
        mod_list += MakeXDSParam(inData.XDSParameter)

    for par in mod_list:
        par_dict.SetParam(par)

        # print params to XDSKAPPA_run.INP

    if inData.ReferenceData:  # if global reference dataset entered as -p REFERENCE_DATASET= data/XDS_ASCII.HKL, overwritten later in XDS.INP setting
        refdataset = inData.ReferenceData
    else:
        refdataset = Names[0]

    # Dictionary of modifications
    par_full = XDSINP('temp')
    par_full.path = 'XDSKAPPA_run.INP'

    for key in file_dict:
        par_full[key] = file_dict[key]

    for key in par_dict:
        par_full[key] = par_dict[key]

    with open('XDSKAPPA_run.INP', 'w') as kapinp:
        for key in par_full:
            kapinp.write(par_full.GetParam(key))

    my_print('Parameters used to modify XDS.INP files were written to XDSKAPPA_run.INP.')

    for path in Names:
        try:
            os.mkdir(path)
        except FileExistsError:
            my_print("Directory already exists: " + path)

        dts = XDataset(Datasets[path])  # gives template relative to running director to find frames
        inp = XDSINP(path, dts)
        inp.SetDefaults()  # read in geometry from frame header etc.
        # inp.read()

        if Datasets[path][0] == "/":  # setup templates path relative to XDS.INP directory
            template = Datasets[path]
        else:
            template = '../' + Datasets[path]
        inp.SetParam('NAME_TEMPLATE_OF_DATA_FRAMES= ' + template)

        if not path == refdataset:
            inp.SetParam("REFERENCE_DATA_SET= ../" + refdataset + "/XDS_ASCII.HKL")

        for key in par_full:
            inp[key] = par_full[key]

        # for key in file_dict:
        #    inp[key] = file_dict[key]

        # for key in par_dict:
        #    inp[key] = par_dict[key]    
        # poor Multiparam support
        # for parm in mod_list:
        #    inp.SetParam(parm)

        inp.write()
    return


def GetDatasets(inData):
    # print string(inData.dataPath)
    Datasets = []
    firstframe = re.compile("[_-][0]+[1].cbf")
    for datapath in inData.dataPath:
        # TODO: dereference '~'; bash apparently does it by default
        try:
            leadingFrames = [fi for fi in os.listdir(datapath) if
                             firstframe.search(fi)]  # get first frame of each dataset
        except os.error:
            raise xdskappa.RuntimeErrorUser("Cannot access: " + datapath + " No such directory")

        for setname in leadingFrames:
            prefix = firstframe.split(setname)[0] + "_"  # dataset prefix without last
            if len(glob.glob(datapath + "/" + prefix + "*.cbf")) >= inData.minData:  # more than 1 frame = dataset
                digits = len(setname) - len(prefix) - 4  # number of ? in template name
                Datasets.append(datapath + "/" + prefix + '?' * digits + '.cbf')
    if len(Datasets) == 0:
        raise xdskappa.RuntimeErrorUser('No datasets were found.')
    Datasets.sort()
    DatasetsDict = {}
    names = []
    numdigit = int(math.log10(len(Datasets))) + 1
    for i, name in enumerate(Datasets, 1):
        key = str(i).zfill(numdigit) + "_" + name.split("_?")[0].replace("/", "_")
        DatasetsDict[key] = name
        names.append(key)
    names.sort()

    out_file_name = inData.DatasetListFile
    if out_file_name is None:
        out_file_name = 'datasets.list'

    with open(out_file_name, 'w') as fdatasets:
        fdatasets.write(
            '# Written by xdskappa ({}).\n #Use # in line begining to disable dataset processing.\n# Dataset name\tFrame name template\n'.format(
                __version__))
        for key in names:
            fdatasets.write(key + xdskappa.LIST_SEPARATOR + DatasetsDict[key] + "\n")

    return DatasetsDict, names


