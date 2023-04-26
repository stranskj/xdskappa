import pytest
import xdskappa.xdataset

@pytest.mark.parametrize('cbf_file', ['../data_test/20190911_omega_????.cbf',
                                    '../data_test/20190911_phi_????.cbf',
                                    '../data_test/221109_omega_????.cbf',
                                    '../data_test/221109_phi_????.cbf'])
def test_XDataset(cbf_file):
    dts = xdskappa.xdataset.XDataset(cbf_file, 1)
    assert True