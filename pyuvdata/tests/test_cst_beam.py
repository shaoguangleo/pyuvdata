import nose.tools as nt
import os
import numpy as np
import copy
from pyuvdata.data import DATA_PATH
from pyuvdata import UVBeam
from pyuvdata.cst_beam import CSTBeam
import pyuvdata.tests as uvtest

filenames = ['HERA_NicCST_150MHz.txt', 'HERA_NicCST_123MHz.txt']
cst_files = [os.path.join(DATA_PATH, f) for f in filenames]


def test_frequencyparse():
    beam1 = CSTBeam()

    parsed_freqs = [beam1.name2freq(f) for f in cst_files]
    nt.assert_equal(parsed_freqs, [150e6, 123e6])

    test_path = '/pyuvdata_1510194907049/_t_env/lib/python2.7/site-packages/pyuvdata/data/'
    test_files = [os.path.join(test_path, f) for f in filenames]
    parsed_freqs = [beam1.name2freq(f) for f in test_files]
    nt.assert_equal(parsed_freqs, [150e6, 123e6])

    test_names = ['HERA_Sim_120.87kHz.txt', 'HERA_Sim_120.87GHz.txt', 'HERA_Sim_120.87Hz.txt']
    test_files = [os.path.join(test_path, f) for f in test_names]
    parsed_freqs = [beam1.name2freq(f) for f in test_files]
    nt.assert_equal(parsed_freqs, [120.87e3, 120.87e9, 120.87])


def test_read_power():
    beam1 = UVBeam()
    beam2 = UVBeam()

    uvtest.checkWarnings(beam1.read_cst_beam, [cst_files],
                         {'beam_type': 'power', 'telescope_name': 'TEST', 'feed_name': 'bob',
                          'feed_version': '0.1', 'model_name': 'E-field pattern - Rigging height 4.9m',
                          'model_version': '1.0'}, nwarnings=2,
                         message='No frequency provided. Detected frequency is')

    nt.assert_equal(beam1.pixel_coordinate_system, 'az_za')
    nt.assert_equal(beam1.beam_type, 'power')
    nt.assert_equal(beam1.data_array.shape, (1, 1, 2, 2, 181, 360))

    # test passing in other polarization
    beam2.read_cst_beam(cst_files, beam_type='power', frequency=[150e6, 123e6],
                        feed_pol='y', telescope_name='TEST',
                        feed_name='bob', feed_version='0.1',
                        model_name='E-field pattern - Rigging height 4.9m',
                        model_version='1.0')

    nt.assert_true(np.allclose(beam1.freq_array, beam2.freq_array))

    nt.assert_true(np.allclose(beam2.polarization_array, np.array([-6, -5])))
    nt.assert_true(np.allclose(beam1.data_array[:, :, 0, :, :, :], beam2.data_array[:, :, 0, :, :, :]))

    # test single frequency
    uvtest.checkWarnings(beam1.read_cst_beam, [cst_files[0]],
                         {'beam_type': 'power', 'telescope_name': 'TEST', 'feed_name': 'bob',
                          'feed_version': '0.1', 'model_name': 'E-field pattern - Rigging height 4.9m',
                          'model_version': '1.0'},
                         message='No frequency provided. Detected frequency is')

    nt.assert_equal(beam1.freq_array, [150e6])
    nt.assert_equal(beam1.pixel_coordinate_system, 'az_za')
    nt.assert_equal(beam1.beam_type, 'power')
    nt.assert_equal(beam1.data_array.shape, (1, 1, 2, 1, 181, 360))

    # test single frequency and not rotating the polarization
    uvtest.checkWarnings(beam2.read_cst_beam, [cst_files[0]],
                         {'beam_type': 'power', 'telescope_name': 'TEST', 'feed_name': 'bob',
                          'feed_version': '0.1', 'model_name': 'E-field pattern - Rigging height 4.9m',
                          'model_version': '1.0', 'rotate_pol': False},
                         message='No frequency provided. Detected frequency is')

    nt.assert_equal(beam2.freq_array, [150e6])
    nt.assert_equal(beam2.pixel_coordinate_system, 'az_za')
    nt.assert_equal(beam2.beam_type, 'power')
    nt.assert_equal(beam2.polarization_array, np.array([-5]))
    nt.assert_equal(beam2.data_array.shape, (1, 1, 1, 1, 181, 360))
    nt.assert_true(np.allclose(beam1.data_array[:, :, 0, :, :, :], beam2.data_array))

    # test reading in multiple polarization files
    beam1.read_cst_beam([cst_files[0], cst_files[0]], beam_type='power', frequency=[150e6],
                        feed_pol=['xy', 'yx'], telescope_name='TEST',
                        feed_name='bob', feed_version='0.1',
                        model_name='E-field pattern - Rigging height 4.9m',
                        model_version='1.0')
    nt.assert_true(np.allclose(beam1.polarization_array, np.array([-7, -8])))
    nt.assert_equal(beam1.data_array.shape, (1, 1, 2, 1, 181, 360))
    nt.assert_true(np.allclose(beam1.data_array[:, :, 0, :, :, :], beam1.data_array[:, :, 1, :, :, :]))

    # test errors
    nt.assert_raises(ValueError, beam1.read_cst_beam, cst_files, beam_type='power',
                     frequency=[150e6, 123e6, 100e6], telescope_name='TEST',
                     feed_name='bob', feed_version='0.1',
                     model_name='E-field pattern - Rigging height 4.9m',
                     model_version='1.0')

    nt.assert_raises(ValueError, beam1.read_cst_beam, cst_files[0], beam_type='power',
                     frequency=[150e6, 123e6], telescope_name='TEST',
                     feed_name='bob', feed_version='0.1',
                     model_name='E-field pattern - Rigging height 4.9m',
                     model_version='1.0')

    nt.assert_raises(ValueError, beam1.read_cst_beam, [cst_files[0], cst_files[0], cst_files[0]],
                     beam_type='power',
                     feed_pol=['x', 'y'], telescope_name='TEST',
                     feed_name='bob', feed_version='0.1',
                     model_name='E-field pattern - Rigging height 4.9m',
                     model_version='1.0')

    nt.assert_raises(ValueError, beam1.read_cst_beam, cst_files[0], beam_type='power',
                     feed_pol=['x', 'y'], telescope_name='TEST',
                     feed_name='bob', feed_version='0.1',
                     model_name='E-field pattern - Rigging height 4.9m',
                     model_version='1.0')


def test_read_efield():
    beam1 = UVBeam()
    beam2 = UVBeam()

    uvtest.checkWarnings(beam1.read_cst_beam, [cst_files],
                         {'beam_type': 'efield', 'telescope_name': 'TEST', 'feed_name': 'bob',
                          'feed_version': '0.1', 'model_name': 'E-field pattern - Rigging height 4.9m',
                          'model_version': '1.0'}, nwarnings=2,
                         message='No frequency provided. Detected frequency is')

    nt.assert_equal(beam1.pixel_coordinate_system, 'az_za')
    nt.assert_equal(beam1.beam_type, 'efield')
    nt.assert_equal(beam1.data_array.shape, (2, 1, 2, 2, 181, 360))

    # test passing in other polarization
    beam2.read_cst_beam(cst_files, beam_type='efield', frequency=[150e6, 123e6],
                        feed_pol='y', telescope_name='TEST',
                        feed_name='bob', feed_version='0.1',
                        model_name='E-field pattern - Rigging height 4.9m',
                        model_version='1.0')
    nt.assert_equal(beam2.feed_array[0], 'y')
    nt.assert_equal(beam2.feed_array[1], 'x')
    nt.assert_equal(beam1.data_array.shape, (2, 1, 2, 2, 181, 360))
    nt.assert_true(np.allclose(beam1.data_array[:, :, 0, :, :, :], beam2.data_array[:, :, 0, :, :, :]))

    # test single frequency and not rotating the polarization
    uvtest.checkWarnings(beam2.read_cst_beam, [cst_files[0]],
                         {'beam_type': 'efield', 'telescope_name': 'TEST', 'feed_name': 'bob',
                          'feed_version': '0.1', 'model_name': 'E-field pattern - Rigging height 4.9m',
                          'model_version': '1.0', 'rotate_pol': False},
                         message='No frequency provided. Detected frequency is')

    nt.assert_equal(beam2.pixel_coordinate_system, 'az_za')
    nt.assert_equal(beam2.beam_type, 'efield')
    nt.assert_equal(beam2.feed_array, np.array(['x']))
    nt.assert_equal(beam2.data_array.shape, (2, 1, 1, 1, 181, 360))
    nt.assert_true(np.allclose(beam1.data_array[:, :, 0, 1, :, :], beam2.data_array))

    # test reading in multiple polarization files
    beam1.read_cst_beam([cst_files[0], cst_files[0]], beam_type='efield', frequency=[150e6],
                        feed_pol=['x', 'y'], telescope_name='TEST',
                        feed_name='bob', feed_version='0.1',
                        model_name='E-field pattern - Rigging height 4.9m',
                        model_version='1.0')
    nt.assert_equal(beam1.data_array.shape, (2, 1, 2, 1, 181, 360))
    nt.assert_true(np.allclose(beam1.data_array[:, :, 0, :, :, :], beam1.data_array[:, :, 1, :, :, :]))
