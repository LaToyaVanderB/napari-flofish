__version__ = "0.0.1"

from ._reader import napari_get_reader
from ._sample_data import make_sample_data, smRNAfish_Ecoli_rpoD_rnlAB_hipBA, get_smRNAfish_Ecoli_rpoD_rnlAB_hipBA
from ._widget import (
    read_in_vsi_widget,
    background_filtering_magic_widget,
    spot_detection_magic_widget,
    spot_thresholding_magic_widget,
    spot_decomposition_magic_widget,
    # ImageThreshold,
)
    # ExampleQWidget, ImageThreshold, threshold_autogenerate_widget,
    # threshold_magic_widget,
    # spot_detection_autogenerate_widget,
# from ._writer import write_multiple, write_single_image

__all__ = (
    "napari_get_reader",
    "read_in_vsi_widget",
    "background_filtering_magic_widget",
    "spot_detection_magic_widget",
    "spot_thresholding_magic_widget",
    "spot_decomposition_magic_widget",
    "make_sample_data",
    "smRNAfish_Ecoli_rpoD_rnlAB_hipBA",
    "get_smRNAfish_Ecoli_rpoD_rnlAB_hipBA",
    # "write_single_image",
    # "write_multiple",
    # "make_sample_data",
    # "ExampleQWidget",
    # "ImageThreshold",
    # "threshold_autogenerate_widget",
    # "threshold_magic_widget",
    # "background_filtering_autogenerate_widget",
    # "spot_detection_autogenerate_widget",
)
