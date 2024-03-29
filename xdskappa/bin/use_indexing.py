# -*- coding: utf-8 -*-
"""
Created on Mon Apr  3 22:00:19 2017

@author: Jan Stransky
"""

import sys, xdataset, parmxds, math, numpy, common, xdsinp

def vector_to_000(vecin,omega,chi,phi):
    """
    Rotates vector to origin of goniometer
    @param vecin: vector to rotate to origin
    @type vecin: list with 3 values
    
    @param omega, chi, phi: position of goniometr
    @type omega, chi, phi: float in radians
    """
    
    #vecout = [0]*3
    
    mOmega =    [[math.cos(omega),0 ,-1*math.sin(omega)],\
                [0, 1, 0],\
                [math.sin(omega), 0, math.cos(omega)]]
                
    mChi =  [[math.cos(chi), -1*math.sin(chi), 0],\
            [math.sin(chi), math.cos(chi), 0],\
            [0, 0, 1]] 
    
    mPhi =    [[math.cos(phi),0 ,-1*math.sin(phi)],\
                [0, 1, 0],\
                [math.sin(phi), 0, math.cos(phi)]]    
    
    vecout = numpy.dot(numpy.dot(numpy.dot(mOmega,mChi),mPhi),vecin)
    
    return vecout
    
def vector_from_000(vecin,omega,chi,phi):
    """
    Rotates vector from origin to goniometer position
    @param vecin: vector to rotate to origin
    @type vecin: list with 3 values
    
    @param omega, chi, phi: position of goniometr
    @type omega, chi, phi: float in radians
    """
    
    #vecout = [0]*3
    
    mOmega =    [[math.cos(omega),0 ,math.sin(omega)],\
                [0, 1, 0],\
                [-1*math.sin(omega), 0, math.cos(omega)]]
                
    mChi =  [[math.cos(chi), math.sin(chi), 0],\
            [-1*math.sin(chi), math.cos(chi), 0],\
            [0, 0, 1]] 
    
    mPhi =    [[math.cos(phi),0 ,math.sin(phi)],\
                [0, 1, 0],\
                [-1*math.sin(phi), 0, math.cos(phi)]]    
    
    vecout = numpy.dot(numpy.dot(numpy.dot(mPhi,mChi),mOmega),vecin)
    
    return vecout    

def process_arguments(argv):
    parser = argparse.ArgumentParser(prog= 'xdskappa.use_indexing', description='Reuse indexing solution on different dataset.', epilog='Dependencies: None')
    
    parser.add_argument('-i','--in-dataset', dest='InDataset', action='append', required=True, metavar='FILE', help='File with indexing solution (geometry file) to re-use on other datasets. Generally XPARM.XDS or GXPARM.XDS generated by IDXREF or CORRECT steps.')
    
    parser.add_argument('-D','--dataset-file', dest='DatasetListFile', nargs='?', required=True, default='datasets.list', const='datasets.list', metavar='FILE', help='List of datasets to re-use indexing. Entries are in format: output_subdirectory<tab>path/template_????.cbf. When no file is given, "datasets.list" is expected.')
        
    # help on empty input
    if len(argv) == 1:
        parser.print_help()     # help on empty input
        sys.exit(1)

    outArgs = parser.parse_args(argv[1:])
    
    return outArgs

def Test000(datasets_out,names_out):
    for name in names_out:
        dts   = xdataset.XDataset(datasets_out[name])
        xinp  = xdsinp.XDSINP(name)
        
        try:
            xinp.read()
        except IOError as err:
            print "Valid XDS.INP file has to be present in output dataset folder. "
            print err
            sys.exit(1)
        
        xparm = parmxds.ParmXds(name + '/XPARM.XDS')     # for re-use of segments part, already sets spg number and unit cell parameters
        xparm.read()
        
        uc_in = xparm.unit_cell
  #      xparm.path = name + '/XPARM.XDS'
        
        # Sets geometry based on frame header
        xparm.set_from_dataset(dts)
        
        # Use ORGX and ORGY from XDS.INP, in case of user modification
        xparm.orgx = float(xinp['ORGX'][0])
        xparm.orgy = float(xinp['ORGY'][0])
        
        phi   = math.radians(float(dts.geometry['PHI']['ANGLE']))
        chi   = math.radians(float(dts.geometry['CHI']['ANGLE']))
        omega = math.radians(float(dts.geometry['OMEGA']['ANGLE']))
        
        xparm.unit_cell.vec_a = vector_from_000(uc_in.vec_a,omega,chi,phi)        
        xparm.unit_cell.vec_b = vector_from_000(uc_in.vec_b,omega,chi,phi)
        xparm.unit_cell.vec_c = vector_from_000(uc_in.vec_c,omega,chi,phi)
        
        xparm.write()
        print 'Reindexed dataset: ' + name
        
        del dts
        del xinp
        
    sys.exit(0)

def Main(args):
    
    datasets_out,names_out = common.ReadDatasetListFile(args.DatasetListFile)
    Test000(datasets_out,names_out)
    
    file_in = args.InDataset[0]
    geom_in = parmxds.ParmXds(file_in)
    geom_in.read()
    
    path_in   = "/".join(file_in.split('/')[:-1])     # get path to dir
    xdsinp_in = xdsinp.XDSINP(path_in)
    
    try:
        xdsinp_in.read()
    except IOError as err:
        print "Valid XDS.INP file has to be present in folder with input geometry. "
        print err
        sys.exit(1)
    
    frame_in = xdsinp_in['NAME_TEMPLATE_OF_DATA_FRAMES'][0]
    
    if '../' in frame_in:           #get rid of ../ in case of relative path
        frame_in = frame_in[3:]
    
    dts_in = xdataset.XDataset(frame_in)
    
    phi_in   = math.radians(float(dts_in.geometry['PHI']['ANGLE']))
    chi_in   = math.radians(float(dts_in.geometry['CHI']['ANGLE']))
    omega_in = math.radians(float(dts_in.geometry['OMEGA']['ANGLE']))
    
    # Rotate input unit vectors to goniometr origin    
    uc_in_000 = geom_in.unit_cell
    uc_in_000.vec_a = vector_to_000(geom_in.unit_cell.vec_a,omega_in,chi_in,phi_in)
    uc_in_000.vec_b = vector_to_000(geom_in.unit_cell.vec_b,omega_in,chi_in,phi_in)
    uc_in_000.vec_c = vector_to_000(geom_in.unit_cell.vec_c,omega_in,chi_in,phi_in)
    
    # hehe, nekde musime sehnat nastaveni goniometru u vzoroveho XPARM, hlavne je problem phi...
    # coz obecne pouzivat DELPHI parametr ? - otestovat, ze se objevi v XPARM.XDS

    for name in names_out:
        dts   = xdataset.XDataset(datasets_out[name])
        xinp  = xdsinp.XDSINP(name)
        
        try:
            xinp.read()
        except IOError as err:
            print "Valid XDS.INP file has to be present in output dataset folder. "
            print err
            sys.exit(1)
        
        xparm = geom_in     # for re-use of segments part, already sets spg number and unit cell parameters
        xparm.path = name + '/XPARM.XDS'
        
        # Sets geometry based on frame header
        xparm.set_from_dataset(dts)
        
        # Use ORGX and ORGY from XDS.INP, in case of user modification
        xparm.orgx = float(xinp['ORGX'][0])
        xparm.orgy = float(xinp['ORGY'][0])
        
        phi   = math.radians(float(dts.geometry['PHI']['ANGLE']))
        chi   = math.radians(float(dts.geometry['CHI']['ANGLE']))
        omega = math.radians(float(dts.geometry['OMEGA']['ANGLE']))
        
        xparm.unit_cell.vec_a = vector_from_000(uc_in_000.vec_a,omega,chi,phi)        
        xparm.unit_cell.vec_b = vector_from_000(uc_in_000.vec_b,omega,chi,phi)
        xparm.unit_cell.vec_c = vector_from_000(uc_in_000.vec_c,omega,chi,phi)
        
        xparm.write()
        print 'Reindexed dataset: ' + name
        
        del dts
        del xinp
        
    print "To use new indexing solution run xdskappa or xdskappa.run_xds with -p JOB= DEFPIX INTEGRATE CORRECT"
    
    return

if __name__ == "__main__":
    
    try:
            import argparse
            
    except Exception:
            print "Your python is probably to old. At least version 2.7 is required."
            print "Your version is: " +  sys.version
            sys.exit(1)

    args = process_arguments(sys.argv)
    Main(args)
    sys.exit(0)
