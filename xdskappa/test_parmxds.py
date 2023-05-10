import os.path

import pytest
from xdskappa.parmxds import ParmXds
from xdskappa.xdataset import XDataset

@pytest.mark.parametrize('path', ['../data_test/XPARM.XDS', '../data_test/GXPARM.XDS'])
def test_ParmXds(path):
    fi_parm = ParmXds(path)
    path_out = 'out_' + os.path.split(path)[1]
    fi_parm.read()

    fi_parm.write(path_out)
    assert os.path.isfile(path_out)

@pytest.mark.parametrize('cbf_file', ['../data_test/20190911_omega_????.cbf',
                                    '../data_test/20190911_phi_????.cbf',
                                    '../data_test/221109_omega_????.cbf',
                                    '../data_test/221109_phi_????.cbf'])
def test_ParmXds_from_dataset(cbf_file):
    path_out = 'XPARM_' + os.path.splitext(os.path.split(cbf_file)[1])[0] + '.XDS'
    dts = XDataset(cbf_file)
    fi_parm = ParmXds()
    fi_parm.set_from_dataset(dts)
    fi_parm.write(path_out)
    assert os.path.isfile(path_out)