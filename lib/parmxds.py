# -*- coding: utf-8 -*-

import os,sys,common,xdataset,numpy

class UnitCell(): # potentialy utilize cctbx?
    """
    Description of crystallographic unit cell
    @param spgr: Space group number
    @type spgr: int
    """
   
    def __init__(self,spgr=None, a=None, b=None, c=None, alpha=None, beta=None, gamma=None, vec_a=None, vec_b=None, vec_c=None ):
        self.spgr = spgr
        self.a = a
        self.b = b
        self.c = c
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma
        self.vec_a = vec_a
        self.vec_b = vec_b
        self.vec_c = vec_c

class ParmXds():
    """
    Interprets content of XPARM.XDS or GXPARM.XDS files
    """
    def __init__(self,path=None):
        self.path=path
        
    def read(self,path=None):
        """
        Reads file from path
        """
        
        if path==None:
            path = self.path
        
        fi = open(path,'r')
        
        line = fi.readline().split()
        
        if 'XPARM.XDS' in line[0]:     # Skip comment line with XDS version
            line = fi.readline().split()
            
        #first data line
        self.starting_frame = int(line[0])
        self.starting_angle = float(line[1])
        self.oscilation     = float(line[2])
        self.rotation_axis  = (float(line[3]),float(line[4]),float(line[5]))
        
        #second data line
        line = fi.readline().split()
        self.wavelenght  = float(line[0])        
        self.beam_vector = (float(line[1]),float(line[2]),float(line[3]))
        
        #third data line
        line = fi.readline().split()
        self.unit_cell       = UnitCell()
        
        self.unit_cell.spgr  = int(line[0])
        self.unit_cell.a     = float(line[1])
        self.unit_cell.b     = float(line[2])
        self.unit_cell.c     = float(line[3])
        self.unit_cell.alpha = float(line[4])
        self.unit_cell.beta  = float(line[5])
        self.unit_cell.gamma  = float(line[6])
        
        # 4th-6th line
        line = fi.readline().split()
        self.unit_cell.vec_a = (float(line[0]),float(line[1]),float(line[2]))
        line = fi.readline().split()
        self.unit_cell.vec_b = (float(line[0]),float(line[1]),float(line[2]))
        line = fi.readline().split()
        self.unit_cell.vec_c = (float(line[0]),float(line[1]),float(line[2]))
        
        #7th line
        line = fi.readline().split()
        self.seg_num = int(line[0])
        self.nx      = int(line[1])
        self.ny      = int(line[2])
        self.qx      = float(line[3])
        self.qy      = float(line[4])
        
        #8th line
        line = fi.readline().split()
        self.orgx     = float(line[0])
        self.orgy     = float(line[1])
        self.distance = float(line[2])
        
        #9th - 11th line
        line = fi.readline().split()
        self.det_vec_x = (float(line[0]),float(line[1]),float(line[2]))
        line = fi.readline().split()
        self.det_vec_y = (float(line[0]),float(line[1]),float(line[2]))
        line = fi.readline().split()
        self.det_vec_normal = (float(line[0]),float(line[1]),float(line[2]))
        
        # Additional, detector segments
        self.segments = []
        for i in range(self.seg_num):
            line1 = fi.readline()
            line2 = fi.readline()
            self.segments.append((line1,line2))
        
        fi.close()        
        
        return
        
    def set_from_dataset(self,dataset):
        """
        Sets values from xdataset.
        Not set values (keeps current): unit_cell, starting_frame, segments
        @param dataset: Object with dataset secription
        @type dataset: XDataset
        """
        
        
 #       self.starting_frame = int(dataset)
        self.starting_angle = float(0)      # TODO: Possibly DEPLHI parameter?
        self.oscilation     = float(dataset.geometry['OSCILATION'])
        rot_vec_string      = dataset.geometry[dataset.geometry['SCAN']]['VECTOR'].split()
        self.rotation_axis  = (float(rot_vec_string[0]),float(rot_vec_string[1]),float(rot_vec_string[2]))
        
        self.wavelenght  = float(dataset.geometry['BEAM']['WAVELENGHT'])    
        beam_vec_string  = dataset.geometry['BEAM']['VECTOR'].split()
        self.beam_vector = (float(beam_vec_string[0]),float(beam_vec_string[1]),float(beam_vec_string[2]))
        
#        self.seg_num = int(line[0])
        self.nx      = int(dataset.detector['Pixel_Count_X'])
        self.ny      = int(dataset.detector['Pixel_Count_Y'])
        self.qx      = float(dataset.detector['Pixel_Size_X'])
        self.qy      = float(dataset.detector['Pixel_Size_Y'])
        
        #8th line
        self.orgx     = float(dataset.geometry['ORGX'])
        self.orgy     = float(dataset.geometry['ORGY'])
        self.distance = float(dataset.geometry['DISTANCE'])
        
        #9th - 11th line
        det_x_string   = dataset.geometry['X-DETECTOR'].split()
        self.det_vec_x = (float(det_x_string[0]),float(det_x_string[1]),float(det_x_string[2]))
        det_y_string   = dataset.geometry['Y-DETECTOR'].split()
        self.det_vec_y = (float(det_y_string[0]),float(det_y_string[1]),float(det_y_string[2]))
        
        self.det_vec_normal = tuple(numpy.cross(self.det_vec_x,self.det_vec_y))
        
    def write(self,path=None):
        """
           Writes to file at path
        """
        if path==None:
            path = self.path
        
        fi = open(path,'w')
        
        fi.write(' XPARM.XDS    VERSION '+common.VERSION+'\n')
        
        fi.write('{:>6}{:>14.4f}{:>10.4f}{:>10.6f}{:>10.6f}{:>10.6f}\n'.format(
                self.starting_frame,self.starting_angle,
                self.oscilation,*self.rotation_axis))
        
        fi.write('{:>15.6f}{:>15.6f}{:>15.6f}{:>15.6f}\n'.format(
                self.wavelenght,*self.beam_vector))        
        
        fi.write('{:>6}{:>12.4f}{:>12.4f}{:>12.4f}{:>8.3f}{:>8.3f}{:>8.3f}\n'.format(
                self.unit_cell.spgr,self.unit_cell.a,self.unit_cell.b,self.unit_cell.c,
                self.unit_cell.alpha,self.unit_cell.beta,self.unit_cell.gamma))        
        
        fi.write('{:>15.6f}{:>15.6f}{:>15.6f}\n'.format(*self.unit_cell.vec_a))        
        fi.write('{:>15.6f}{:>15.6f}{:>15.6f}\n'.format(*self.unit_cell.vec_b))
        fi.write('{:>15.6f}{:>15.6f}{:>15.6f}\n'.format(*self.unit_cell.vec_c))
        
        fi.write('{:>8}{:>8}{:>8}{:>15.6f}{:>15.6f}\n'.format(
                self.seg_num,self.nx,self.ny,self.qx,self.qy))
        
        fi.write('{:>15.6f}{:>15.6f}{:>15.6f}\n'.format(
                self.orgx,self.orgy,self.distance))               
        
        fi.write('{:>15.6f}{:>15.6f}{:>15.6f}\n'.format(*self.det_vec_x))                
        fi.write('{:>15.6f}{:>15.6f}{:>15.6f}\n'.format(*self.det_vec_y))                
        fi.write('{:>15.6f}{:>15.6f}{:>15.6f}\n'.format(*self.det_vec_normal))                
        
        for seg in self.segments:
            fi.write('{}{}'.format(*seg))
        
        fi.close()        
        
        return
        
def Test():
    fi_parm = ParmXds("XPARM.XDS")
    fi_parm.read()
    print fi_parm.unit_cell.vec_a
    print fi_parm.wavelenght
    dts = xdataset.XDataset('test/photon_????.cbf')
    fi_parm.set_from_dataset(dts)
    fi_parm.write("XPARM_copy.XDS")
    return

if __name__ == "__main__":
    Test()
    sys.exit(0)
            