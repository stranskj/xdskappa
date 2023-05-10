import math

import pytest
import xdskappa.xdataset
from xdskappa.xdataset import rotate_by_axis_matrix
import math
import numpy

@pytest.mark.parametrize('cbf_file', ['../data_test/20190911_omega_????.cbf',
                                    '../data_test/20190911_phi_????.cbf',
                                    '../data_test/221109_omega_????.cbf',
                                    '../data_test/221109_phi_????.cbf'])
def test_XDataset(cbf_file):
    dts = xdskappa.xdataset.XDataset(cbf_file, 1)
    ax_vec = dts.AxesVector()
    ax = dts.GetAxes()
    axes = dts.axes
    assert True

@pytest.mark.parametrize('axis,angle', [([1,0,0], 45), ([1,0,0], 20), ([1,0,0], 70),
                                        ([0,1,0], 45), ([0,1,0], 20), ([0,1,0], 70),
                                        ([0,0,1], 45), ([0,0,1], 20), ([0,0,1], 70),
                                        ([1,1,1], 45), ([1,1,1], 20), ([1,1,1], 70),
                                        ([1,1,0], 45), ([1,1,0], 20), ([1,1,0], 70),
                                        ([1,0,1], 45), ([1,0,1], 20), ([1,0,1], 70),
                                        ([0,1,1], 45), ([0,1,1], 20), ([0,1,1], 70),
                                        ([1,1,2], 45), ([1,1,2], 20), ([1,1,2], 70),
                                        ([1,2,1], 45), ([1,2,1], 20), ([1,2,1], 70),
                                        ([2,1,1], 45), ([2,1,1], 20), ([2,1,1], 70),
                                        ([4,10,-61], 45),([4,10,-61], 20),([4,10,-61], 70),
                                        ])
def test_rotation_matrix(axis, angle):
    np_axis = numpy.array(axis)
    RM = rotate_by_axis_matrix(axis, math.radians(angle))
    self_rot = RM @ np_axis
    assert numpy.linalg.norm(np_axis-self_rot) < 0.00000001
   # assert RM.T @ RM == numpy.array[[1,0,0], [0,1,0], [0,0,1]]