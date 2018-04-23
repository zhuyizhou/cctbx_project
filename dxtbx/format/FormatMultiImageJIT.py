from __future__ import absolute_import, division
from dxtbx.format.FormatMultiImage import FormatMultiImage

class FormatMultiImageJIT(FormatMultiImage):

  '''
  Just-in-Time version of FormatMultiImage that does not instantiate the models ahead of time.
  It creates an ImageSetJIT class and returns it. Saves time when image file contains
  too many images to setup before processing.
  '''

  @classmethod
  def get_imageset(Class,
                   filenames,
                   beam=None,
                   detector=None,
                   goniometer=None,
                   scan=None,
                   as_sweep=False,
                   as_imageset=False,
                   single_file_indices=None,
                   format_kwargs=None,
                   template=None,
                   check_format=True,
                   just_in_time=True):

    return super(FormatMultiImageJIT, Class).get_imageset(filenames,
                                                           beam,
                                                           detector,
                                                           goniometer,
                                                           scan,
                                                           as_sweep,
                                                           as_imageset,
                                                           single_file_indices,
                                                           format_kwargs,
                                                           template,
                                                           check_format,
                                                           just_in_time)
