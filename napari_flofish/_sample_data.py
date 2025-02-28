"""
This module is an example of a barebones sample data provider for napari.

It implements the "sample data" specification.
see: https://napari.org/stable/plugins/guides.html?#sample-data

Replace code below according to your needs.
"""

from urllib.request import urlretrieve
import zipfile
from appdirs import AppDirs

from napari.types import LayerData
from pathlib import Path
from typing import List

import numpy as np


def smRNAfish_Ecoli_rpoD_rnlAB_hipBA(cleanup: True) -> List[LayerData]:
    """
    Download test data from Zenodo
    Unzip them to _tests/data/expected directory

    Returns:
        List[LayerData]: image layer data tuple
    """
    
    # download and unzip data
    appdir = AppDirs("napari-flofish")
    datadir = Path(appdir.user_data_dir)
    datadir.mkdir(parents=True, exist_ok=True)
    get_smRNAfish_Ecoli_rpoD_rnlAB_hipBA(datadir, cleanup)

    # make layer data tuples
    layer_data_tuples = []
    # do stuff
    # ...
    
    return layer_data_tuples


def get_smRNAfish_Ecoli_rpoD_rnlAB_hipBA(datadir: Path, cleanup: True):
    # dataset = "smRNAfish-Ecoli-rpoD-rnlAB-hipBA"
    uri = "https://zenodo.org/records/14879324/files/test.zip"

    # download
    dataset = "test"
    zipfilename = datadir / f"{dataset}.zip"
    if not zipfilename.is_file():
        urlretrieve(uri, filename=zipfilename)

    # unzip
    with zipfile.ZipFile(str(zipfilename), "r") as myzip:
        myzip.extractall(datadir)
        
    # clean up
    if cleanup:
        zipfilename.unlink()
        
    
def make_sample_data():
    """Generates an image"""
    # Return list of tuples
    # [(data1, add_image_kwargs1), (data2, add_image_kwargs2)]
    # Check the documentation for more information about the
    # add_image_kwargs
    # https://napari.org/stable/api/napari.Viewer.html#napari.Viewer.add_image

    return [(np.random.rand(512, 512), {})]
