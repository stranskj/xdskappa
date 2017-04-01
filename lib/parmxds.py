# -*- coding: utf-8 -*-

import os,sys

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
        
    def Read(self,path=None):
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
        
        return
        
def Test():
    fi_parm = ParmXds("XPARM.XDS")
    fi_parm.Read()
    print fi_parm.unit_cell.vec_a
    print fi_parm.wavelenght
    return

if __name__ == "__main__":
    Test()
            