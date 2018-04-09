from __future__ import division
import mmtbx.model
from libtbx.utils import Sorry
from cctbx import maptbx
from libtbx import group_args
from scitbx.array_family import flex

def get_map_histograms(data, n_slots=20, data_1=None, data_2=None):
  h0, h1, h2 = None, None, None
  data_min = None
  hmhcc = None
  if(data_1 is None):
    h0 = flex.histogram(data = data.as_1d(), n_slots = n_slots)
  else:
    data_min = min(flex.min(data_1), flex.min(data_2))
    data_max = max(flex.max(data_1), flex.max(data_2))
    h0 = flex.histogram(data = data.as_1d(), n_slots = n_slots)
    h1 = flex.histogram(data = data_1.as_1d(), data_min=data_min,
      data_max=data_max, n_slots = n_slots)
    h2 = flex.histogram(data = data_2.as_1d(), data_min=data_min,
      data_max=data_max, n_slots = n_slots)
    hmhcc = flex.linear_correlation(
      x=h1.slots().as_double(),
      y=h2.slots().as_double()).coefficient()
  return group_args(h_map = h0, h_half_map_1 = h1, h_half_map_2 = h2,
    _data_min = data_min, half_map_histogram_cc = hmhcc)

def get_map_counts(map_data, crystal_symmetry=None):
  a = map_data.accessor()
  map_counts = group_args(
    origin       = a.origin(),
    last         = a.last(),
    focus        = a.focus(),
    all          = a.all(),
    min_max_mean = map_data.as_1d().min_max_mean().as_tuple(),
    d_min_corner = maptbx.d_min_corner(map_data=map_data,
      unit_cell = crystal_symmetry.unit_cell()))
  return map_counts

class input(object):
  def __init__(self,
               map_data         = None,
               map_data_1       = None,
               map_data_2       = None,
               model            = None,
               crystal_symmetry = None,
               box              = True):
    #
    assert [model, crystal_symmetry].count(None) != 2
    if(crystal_symmetry is None and model is not None):
      crystal_symmetry = model.crystal_symmetry()
    if([model, crystal_symmetry].count(None)==0):
      assert model.crystal_symmetry().is_similar_symmetry(crystal_symmetry)
    if(not [map_data_1, map_data_2].count(None) in [0,2]):
      raise Sorry("None or two half-maps are required.")
    #
    self._map_data         = map_data
    self._half_map_data_1  = map_data_1
    self._half_map_data_2  = map_data_2
    self._model            = model
    self._crystal_symmetry = crystal_symmetry
    #
    self._counts = get_map_counts(
      map_data         = self._map_data,
      crystal_symmetry = crystal_symmetry)
    self._map_histograms = get_map_histograms(
      data    = self._map_data,
      n_slots = 20,
      data_1  = self._half_map_data_1,
      data_2  = self._half_map_data_2)
    # Shift origin
    sites_cart = None
    if(self._model is not None):
      sites_cart = self._model.get_sites_cart()
    soin = maptbx.shift_origin_if_needed(
      map_data         = self._map_data,
      sites_cart       = sites_cart,
      crystal_symmetry = crystal_symmetry)
    self._map_data = soin.map_data
    if(self._model is not None):
      self._model.set_sites_cart(sites_cart = soin.sites_cart)
    if(self._half_map_data_1 is not None):
      self._half_map_data_1 = maptbx.shift_origin_if_needed(
        map_data         = self._half_map_data_1,
        sites_cart       = None,
        crystal_symmetry = None).map_data
      self._half_map_data_2 = maptbx.shift_origin_if_needed(
        map_data         = self._half_map_data_2,
        sites_cart       = None,
        crystal_symmetry = None).map_data
    # Box
    if(self._model is not None and box):
      xrs = self._model.get_xray_structure()
      if(self._half_map_data_1 is not None):
        self._half_map_data_1 = mmtbx.utils.extract_box_around_model_and_map(
          xray_structure = xrs,
          map_data       = self._half_map_data_1,
          box_cushion    = 5.0).map_box
        self._half_map_data_2 = mmtbx.utils.extract_box_around_model_and_map(
          xray_structure = xrs,
          map_data       = self._half_map_data_2,
          box_cushion    = 5.0).map_box
      box = mmtbx.utils.extract_box_around_model_and_map(
        xray_structure = xrs,
        map_data       = self._map_data,
        box_cushion    = 5.0)
      self._model.set_xray_structure(xray_structure = box.xray_structure_box)
      self._crystal_symmetry = self._model.crystal_symmetry()
      self._map_data = box.map_box

  def counts(self): return self._counts

  def histograms(self): return self._map_histograms

  def map_data(self): return self._map_data

  def map_data_1(self): return self._half_map_data_1

  def map_data_2(self): return self._half_map_data_2

  def model(self): return self._model

  def xray_structure(self): return self.model().get_xray_structure()

  def crystal_symmetry(self): return self._crystal_symmetry

  def hierarchy(self): return self._model.get_hierarchy()