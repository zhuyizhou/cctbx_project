
from __future__ import division

def exercise_anomalous_maps_misc () :
  from mmtbx.regression.make_fake_anomalous_data import generate_cd_cl_inputs
  import mmtbx.utils
  from iotbx import file_reader
  mtz_file, pdb_file = generate_cd_cl_inputs(
    file_base = "tst_mmtbx_maps_misc")
  pdb_in = file_reader.any_file(pdb_file)
  hierarchy = pdb_in.file_object.construct_hierarchy()
  xrs = pdb_in.file_object.xray_structure_simple()
  for s in xrs.scatterers() :
    if (s.scattering_type == "Cd2+") :
      s.fp = -0.29
      s.fdp = 2.676
      s.flags.set_use_fp_fdp(True)
  mtz_in = file_reader.any_file(mtz_file)
  f_obs = mtz_in.file_server.miller_arrays[0]
  flags = mtz_in.file_server.miller_arrays[0]
  flags = flags.customized_copy(data=flags.data()==1)
  fmodel = mmtbx.utils.fmodel_simple(
    update_f_part1_for=None,
    f_obs=f_obs,
    r_free_flags=flags,
    xray_structures=[xrs],
    scattering_table="n_gaussian",
    skip_twin_detection=True)
  map_coeffs = fmodel.map_coefficients(
    map_type="anom_residual",
    exclude_free_r_reflections=True)
  map_anom = map_coeffs.fft_map(
    resolution_factor=0.25).apply_sigma_scaling().real_map_unpadded()
  for s in xrs.scatterers() :
    if (s.scattering_type == "Cd2+") :
      assert (map_anom.eight_point_interpolation(s.site) < 0)
    elif (s.scattering_type == 'Cl1-') :
      assert (map_anom.eight_point_interpolation(s.site) > 10)
  # this simply checks whether anomalous data will cause problems when
  # mixed with other options (i.e. array size errors)
  map2 = fmodel.map_coefficients(
    map_type="2mFo-DFc",
    exclude_free_r_reflections=True)

if (__name__ == "__main__") :
  exercise_anomalous_maps_misc()
  print "OK"
