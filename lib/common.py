'''
Created on Mar 4, 2016

Set of common functions for xdskappa tools

@author: stransky
'''

VERSION = '0.1.2 (16th Mar 2016)'
LIST_SEPARATOR = '\t'

import os,math,subprocess,re,glob,sys
from xdsinp import XDSINP
from xdataset import XDataset
from distutils import spawn

def GetStatistics(inFile, outFile):
    if os.path.isfile(inFile) == False :
        raise IOError(inFile + " is not available. Problem with data processing?")
        return 
    fin = open(inFile,'r')
    
    
    # get last table + some appendix in rows
    tab = fin.read().split('SUBSET OF INTENSITY DATA WITH SIGNAL/NOISE >= -3.0 A')[-1].split('\n')
    fin.close()
    
    fout = open(outFile,'w')
    fout.write('# Legend for columns\n')
    fout.write('# Resol.\tMultipl.\tRmerge\tRmeas\tComplet.\tI/sig\tCC1/2\tAnoCC\tSigAno\n')
    i = 4 # first row with numbers
    while not 'total' in tab[i]:
        row = tab[i].split()
        
        res = row[0]
        multiplicity = "{:.2f}".format(float(row[1]) / float(row[2]))
        Rfac = row[5].strip('%')
        Rmeas = row[9].strip('%')
        completness = row[4].strip('%')
        Isig = row[8]
        CC = row[10].strip('*')
        AnoCC = row[11].strip('*')
        SigAno = row[12]
        
        fout.write(res+'\t'+multiplicity+'\t'+Rfac+'\t'+Rmeas+'\t'+completness+'\t'+Isig+'\t'+CC+'\t'+AnoCC+'\t'+SigAno+'\n')
        i += 1
    fout.close()
    
def GetWinSize():
    winsize = []
    if spawn.find_executable('xrandr'):
        getwinsize = subprocess.Popen('xrandr',stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        
        for line in getwinsize.stdout:
            if '*' in line:
        #    lin = re.search('[0-9]+[x][0-9]+', line)
                row = line.split()[0].split('x') #lin.string[lin.begin():lin.end()].split('x')
                size = row[0],row[1]
                winsize.append(size)
        getwinsize.wait()
    else:
        size = 1920,1080
        winsize.append(size)
    return winsize
    
def ShowStatistics(Names,Scale=None):
    for data in Names:
        if os.path.isfile(data+'/CORRECT.LP'):
            GetStatistics(data+'/CORRECT.LP', data+'/statistics.out')
    
    if os.path.isfile(Scale+'/XSCALE.LP'):
            GetStatistics(Scale+'/XSCALE.LP', Scale+'/statistics.out')
    
    winsize = GetWinSize()
    
#    winsize = ['1920','1080']
    
    Names.append(Scale)        
    plt = open('gnuplot.plt','w')
    
    plt.write('\
set terminal x11 size '+ winsize[0][0] +',' +winsize[0][1] +' \n \
set xlabel "Resolution [A]"\n \
set multiplot layout 3,3 \n \
set nokey \n \
set title "Completness"\n \
set ylabel "%"\n \
set yrange [0:100] \n \
set xrange [*:*] reverse \n \
#set logscale x \n \
plot ')
    for data in Names:
        plt.write("'" + data + "/statistics.out' using 1:5 with lines, ")
    plt.write('\n')
    
    plt.write(' \
set title "Rmerge"\n \
plot ')
    for data in Names:
        plt.write("'" + data + "/statistics.out' using 1:3 with lines, ")
    plt.write('\n')
    
    plt.write(' \
set title "Rmeas"\n \
plot ')
    for data in Names:
        plt.write("'" + data + "/statistics.out' using 1:4 with lines, ")
    plt.write('\n')
        
    plt.write(' \
set title "CC(1/2)"\n \
plot ')
    for data in Names:
        plt.write("'" + data + "/statistics.out' using 1:7 with lines, ")
    plt.write('\n')

    plt.write(' \
set title "Redundancy"\n \
set ylabel "" \n \
set yrange [ 0:* ] \n \
plot ')
    for data in Names:
        plt.write("'" + data + "/statistics.out' using 1:2 with lines, ")
    plt.write('\n')
    
    plt.write(' \
set title "I/sig(I)"\n \
set ylabel "" \n \
set yrange [ 0:* ] \n \
plot ')
    for data in Names:
        plt.write("'" + data + "/statistics.out' using 1:6 with lines, ")
    plt.write('\n')
    
    plt.write(' \
set title "Anomalous I/sig(I)"\n \
set ylabel "" \n \
set yrange [ 0:* ] \n \
plot ')
    for data in Names:
        plt.write("'" + data + "/statistics.out' using 1:9 with lines, ")
    plt.write('\n')
        
    plt.write(' \
set title "Anomalous CC"\n \
set ylabel "%" \n \
set yrange [ *:* ] \n \
plot ')
    for data in Names:
        plt.write("'" + data + "/statistics.out' using 1:8 with lines, ")
    plt.write('\n')
    
    plt.write(' \
#unset multiplot \n \
set title "Legend"\n \
set ylabel "" \n \
set yrange [ 1000:1100 ] \n \
set xlabel "" \n \
set key #center \n \
set tics textcolor rgb "white" \n \
unset border \n \
unset ytics \n \
unset xtics \n \
plot ')
    for data in Names:
        plt.write("'" + data + "/statistics.out' using 1:2 with lines title '"+data +"', ")
    plt.write('\n')
    
    plt.write('unset multiplot \n')
    
    plt.close()
    
    if spawn.find_executable('gnuplot') == None:
        print "Gnuplot not found in $PATH. You can plot results using statistic.out in subdirectories"
    arg = 'gnuplot -p gnuplot.plt'.split()
    plot = subprocess.Popen(arg)
    plot.wait()

def getISa(path):
    corlp = path
    if os.path.isfile(corlp) == False :
        raise IOError(path + "/CORRECT.LP is not available. Problem with data processing?")
        return 'N/A'
    fcor = open(corlp,'r')
    
    line = fcor.readline()
    while line.split() != ['a', 'b', 'ISa'] :
        line = fcor.readline()

    line = fcor.readline().split()
    fcor.close()
    return line[2]

def PrintISa(Paths):
    print 'ISa for individual datasets:'
    print '\tISa\tDataset'
    for dataset in Paths:
        try:
            isa = getISa(dataset + '/CORRECT.LP')
        except IOError:
            isa = 'N/A'
        
        print '\t' + isa + '\t' + dataset
    return

def RunXDS(Paths):
    if spawn.find_executable('xds_par') == None:
        print "ERROR: Cannot find XDS executable."
        sys.exit(1)
        
    for path in Paths:
        print "Processing " + path + ":"
        if not os.path.isfile(path+'/XDS.INP'):
            print "File not found: "+path+'/XDS.INP'
            continue
        
        log = open(path + '/xds.log','w')
        xds = subprocess.Popen(['xds_par'],cwd= path, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        
        for line in xds.stdout:
            log.write(line)
            if '***** COLSPOT *****' in line:
                print 'Finding strong reflections...'
            
            if '***** IDXREF *****' in line:
                print 'Indexing...'
                
            if '***** INTEGRATE *****' in line:
                print 'Integrating...'
        
        xds.wait()
        log.close()
                
        log = open(path + '/xds.log','r')
        if '!!! ERROR !!!' in log.read():
            print "An error during data procesing using XDS. Check IDXREF.LP, INTEGRATE.LP, other *.LP or xds.log files fo further details."
        else:
            print 'Finished.'
        log.close()
    return 

def ForceXDS(paths):
    for path in paths:
        log = open(path + '/xds.log')
        if 'YOU MAY CHOOSE TO CONTINUE DATA' in log.read():
            inp = XDSINP(path)
            inp.read()
            inp.SetParam('JOB= DEFPIX INTEGRATE CORRECT')
            inp.write()
            log.close()
            
            print "Attempting integration of: " + path
            RunXDS([path])
        else:
            log.close() 
    return  
        
def Scale(Paths, Outname):
    try:
        os.mkdir('scale')
    except:
        print "Directory already exists: scale"
    
    xscaleinp = open('scale/XSCALE.INP','w')
    
    xscaleinp.write('OUTPUT_FILE= '+ Outname + '\n')
    for path in Paths:
        if os.path.isfile(path + '/XDS_ASCII.HKL'):
            xscaleinp.write('   INPUT_FILE= ../' + path + '/XDS_ASCII.HKL\n')
        else:
            print 'XDS_ASCII.HKL not available in ' + path
            print 'Excluding from scaling'
    
    xscaleinp.close()
    
    print 'Scaling with xscale_par...'
    xscale = subprocess.Popen('xscale_par', cwd= 'scale', stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    xscale.wait()
    
    fout = open('scale/XSCALE.LP')
    if '!!! ERROR !!!' in fout:
        print 'Error in scaling. Please read: scale/XSCALE.LP'
    else:
        print 'Scaled. Output written in: scale/' + Outname
    
    

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
        raise IOError('File not found: ' + inData)
        sys.exit(1)
        
    fin = open(inData,'r')
    DatasetsDict = {}
    names = []
    for line in fin:
        row = line.split(LIST_SEPARATOR)
        names.append(row[0])
        DatasetsDict[row[0]] = row[1].strip('\n\r\t ')
    fin.close()    
    return DatasetsDict,names

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
            else :
                outParList[i] += " " + par[0]
            del par[0]
    return outParList

def ReadXDSParamFile(inFile):
    """
    Parse input file with prameters for modifing XDS.INP
    
    @param inFile: File with XDS.INP-like parameters
    @type inFile: file
    """
    if not os.path.isfile(inFile):
        raise IOError('File not found: ' + inFile)
        return
    fin = open(inFile,'r')
    outParList = []
    for line in fin:
        outParList.append(line.strip('\r\n\t '))
    fin.close()
    return outParList

        
def PrepareXDSINP(inData,Datasets,Names):
    """
    Makes working dirs and XDS.INP for all choosen datasets
    
    @param inData: Parsed input
    @type inData: Namespace
    @param Datasets: Datasets list
    @type Datasets: dict
    @param Names: List of keys in Datasets (ordered)
    @type Names: list
    """
    print "Processing..."
    
    #TODO: nejak z funkcnit/prerozdelit kvuli toolum?
    file_dict = XDSINP('temp')
    if inData.XDSParameterFile:
        #mod_list += ReadXDSParamFile(inData.XDSParameterFile)
        file_dict.path = inData.XDSParameterFile
        file_dict.read()
        
    mod_list = []
    par_dict = XDSINP('temp')    
    if inData.XDSParameter:
        mod_list += MakeXDSParam(inData.XDSParameter)
    
    for par in mod_list:
        par_dict.SetParam(par)   
         
    
    if inData.ReferenceData:        #if global reference dataset entered as -p REFERENCE_DATASET= data/XDS_ASCII.HKL, overwritten later in XDS.INP setting
        refdataset = inData.ReferenceData
    else:
        refdataset = Names[0]
        
    #Dictionary of modifications
        
    for path in Names:
        try:
            os.mkdir(path)
        except:
            print "Directory already exists: "+ path
        
        
        
        dts = XDataset(Datasets[path])        # gives template relative to running director to find frames    
        inp = XDSINP(path,dts)
        inp.SetDefaults()        #read in geometry from frame header etc.
        #inp.read()
        
        if Datasets[path][0] == "/":        # setup templates path relativ to XDS.INP directory
            template = Datasets[path]
        else:
            template = '../' + Datasets[path]
        inp.SetParam('NAME_TEMPLATE_OF_DATA_FRAMES= ' + template)
        
        if not path == refdataset:
            inp.SetParam("REFERENCE_DATA_SET= ../" + refdataset + "/XDS_ASCII.HKL")
        
        for key in file_dict:
            inp[key] = file_dict[key]
            
        for key in par_dict:
            inp[key] = par_dict[key]    
        # poor Multiparam support
        #for parm in mod_list:
        #    inp.SetParam(parm)
                
        inp.write()
    return

def GetDatasets(inData):
    #print string(inData.dataPath)
    Datasets = []
    firstframe = re.compile("[_-][0]+[1].cbf")
    for datapath in inData.dataPath :
        #TODO: dereference '~'; bash apparently does it by default
        try:
            leadingFrames = [fi for fi in os.listdir(datapath) if firstframe.search(fi)] #get first frame of each dataset
        except os.error:
            print "Cannot access: " + datapath + " No such directory"
            sys.exit(1)

        for setname in leadingFrames :        
            prefix = firstframe.split(setname)[0] + "_"        #dataset prefix without last 
            if len(glob.glob(datapath + "/" + prefix + "*.cbf")) >= inData.minData :  # more than 1 frame = dataset
                digits = len(setname) - len(prefix) - 4        #number of ? in template name
                Datasets.append(datapath + "/" + prefix + '?' * digits + '.cbf')
    Datasets.sort()    
    DatasetsDict = {}
    names = []
    numdigit = int(math.log10(len(Datasets)))+1
    for i,name in enumerate(Datasets):
        key = str(i).zfill(numdigit) + "_" + name.split("_?")[0].replace("/","_")
        DatasetsDict[key] = name
        names.append(key)
    names.sort()
    fdatasets = open('datasets.list','w')
    for key in names:
        fdatasets.write(key + LIST_SEPARATOR + DatasetsDict[key] + "\n")
    fdatasets.close()    
    return DatasetsDict,names
