import pytest
import xdskappa.xdataset
import xdskappa.xdsinp as xdsinp
import os

@pytest.mark.parametrize('cbf_file', ['../data_test/20190911_omega_????.cbf',
                                    '../data_test/20190911_phi_????.cbf',
                                    '../data_test/221109_omega_????.cbf',
                                    '../data_test/221109_phi_????.cbf'])
def test_XDINP(cbf_file):
    dts = xdskappa.xdataset.XDataset(cbf_file, 1)
    path = os.path.split(cbf_file)[1].rsplit('_', maxsplit=1)[0]

    inp = xdsinp.XDSINP('test',dts)
    inp.SetDefaults()

    inp.path = path+'_XDS.INP'

    inp.write()
    assert True