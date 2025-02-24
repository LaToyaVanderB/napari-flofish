import pytest

import numpy as np
import pandas as pd
from skimage import io
from pathlib import Path

from napari_flofish._widget import (
    read_in_vsi_widget,
    background_filtering_magic_widget,
    spot_detection_magic_widget,
    spot_thresholding_magic_widget,
    spot_decomposition_magic_widget,
    # ExampleQWidget,
    # ImageThreshold,
    # threshold_autogenerate_widget,
    # threshold_magic_widget,
)

@pytest.fixture
def dic_masks():
    return io.imread('data/expected/DIC masks.tif')

@pytest.fixture
def rna():
    return io.imread('data/expected/rpoD.tif')

@pytest.fixture
def rna_background_filtered():
    return io.imread('data/expected/rpoD background filtered.tif')

@pytest.fixture
def rna_LoG_filtered():
    return io.imread('data/expected/rpoD LoG filtered.tif')

@pytest.fixture
def rna_local_maxima():
    return io.imread('data/expected/rpoD local maxima.tif')

@pytest.fixture
def rna_LoG_local_maxima():
    return io.imread('data/expected/rpoD LoG[local maxima].tif')

@pytest.fixture
def spots_detected_50():
    return pd.read_csv('data/expected/rpoD spots detected thr=50.csv').drop('index', axis=1).rename(columns={'axis-0': 0, 'axis-1': 1, 'axis-2': 2})

@pytest.fixture
def spots_thresholded_100():
    return pd.read_csv('data/expected/rpoD spots thresholded thr=100.csv').drop('index', axis=1).rename(columns={'axis-0': 0, 'axis-1': 1, 'axis-2': 2})

@pytest.fixture
def spots_decomposed_50():
    return pd.read_csv('data/expected/rpoD spots decomposed thr=50.csv').drop('index', axis=1).rename(
        columns={'axis-0': 0, 'axis-1': 1, 'axis-2': 2})

@pytest.fixture
def rna_background_filtered_test():
    return io.imread('data/test/rpoD background filtered.tif')

@pytest.fixture
def rna_LoG_filtered_test():
    return io.imread('data/test/rpoD LoG filtered.tif')

@pytest.fixture
def spots_test():
    return pd.read_csv('data/test/rpoD spots thr=50.0.csv')

@pytest.fixture
def rna_local_maxima_test():
    return io.imread('data/test/rpoD local maxima.tif')

@pytest.fixture
def rna_LoG_local_maxima_test():
    return io.imread('data/test/rpoD LoG[local maxima].tif')


scale = (200, 65, 65)
spot_radius = (800, 120, 120)


def test_read_in_vsi_widget(make_napari_viewer):
    viewer = make_napari_viewer()
    my_widget = read_in_vsi_widget()
    base_dir = "/Volumes/KINGSTON/Florence/smFISH/zenodo/smfish-analysis/tests/data/exp16"
    cfg_file = Path(base_dir) / "config.json"
    vsi_file = Path(base_dir) / "input/MG1655_GLU_OD_0.3_left_CY5, CY3.5 NAR, CY3, DAPI_02.vsi"
    cell_file = Path(base_dir) / "input/MG1655_GLU_OD_0.3_left_DIC_02.tif"
    result = my_widget(cfg_file=cfg_file, vsi_file=vsi_file, cell_file=cell_file)
    assert len(result) == 5


def test_background_filtering_magic_widget(make_napari_viewer, rna, rna_background_filtered):
    viewer = make_napari_viewer()
    layer = viewer.add_image(rna)

    my_widget = background_filtering_magic_widget()
    result = my_widget(img_layer=layer, sigma_z=0.75, sigma_yx=2.3)
    assert np.all(result[0] - rna_background_filtered == 0)


def test_spot_detection_magic_widget(make_napari_viewer, dic_masks, rna_background_filtered, rna_LoG_filtered, rna_local_maxima, spots_detected_50):
    viewer = make_napari_viewer()
    layer = viewer.add_image(rna_background_filtered)
    layer.metadata['channel'] = 'rpoD'
    layer.metadata.update({
        'threshold': 50,
    })
    viewer.add_image(dic_masks, name='DIC masks')

    my_widget = spot_detection_magic_widget()
    result = my_widget(img_layer=layer, threshold=50, scale_z=200, scale_yx=65, spot_radius_z=800, spot_radius_yx=120)

    assert np.all(result[0][0] - rna_LoG_filtered == 0)
    assert np.all(result[1][0] - rna_local_maxima == 0)
    test_spots = pd.concat([pd.DataFrame(result[2][0]), result[2][1]['features']], axis=1)
    assert test_spots.equals(spots_detected_50)


def test_spot_thresholding_magic_widget(make_napari_viewer, dic_masks, rna_LoG_filtered, rna_local_maxima, spots_detected_50, spots_thresholded_100):
    viewer = make_napari_viewer()
    layer = viewer.add_points(spots_detected_50.iloc[:, 0:3])
    layer.features = spots_detected_50.iloc[:, 3:]
    layer.metadata['channel'] = 'rpoD'
    viewer.add_image(rna_LoG_filtered, name='rpoD LoG filtered')
    viewer.add_image(rna_local_maxima, name='rpoD local maxima')
    viewer.add_image(dic_masks, name='DIC masks')

    my_widget = spot_thresholding_magic_widget()

    same_spots, props, _ = my_widget(viewer=viewer, img_layer=viewer.layers[0], threshold=50)
    test_spots = pd.concat([pd.DataFrame(same_spots), props['features']], axis=1)
    assert test_spots.equals(spots_detected_50)

    fewer_spots, props, _ = my_widget(img_layer=layer, threshold=100)
    test_spots = pd.concat([pd.DataFrame(fewer_spots), props['features']], axis=1)
    assert test_spots.equals(spots_thresholded_100)


def test_spot_decomposition_magic_widget(make_napari_viewer, dic_masks, rna, spots_detected_50, spots_decomposed_50):
    viewer = make_napari_viewer()
    layer = viewer.add_points(spots_detected_50.iloc[:, 0:3])
    layer.metadata['channel'] = 'rpoD'
    layer.metadata['threshold'] = 50
    layer.metadata['scale'] = scale
    layer.metadata['spot_radius'] = spot_radius

    viewer.add_image(dic_masks, name='DIC masks')
    viewer.add_image(rna, name='rpoD')

    my_widget = spot_decomposition_magic_widget()
    result = my_widget(viewer=viewer, point_layer=layer)

    test_spots = pd.concat([ pd.DataFrame(result[0][0]), result[0][1]['features']], axis=1)
    # assert test_spots.equals(spots_decomposed_50)    # etc.
    assert abs(test_spots.shape[0] - spots_decomposed_50.shape[0]) / spots_decomposed_50.shape[0] < 0.1
    assert test_spots.shape[0] > spots_detected_50.shape[0]


# def test_threshold_autogenerate_widget():
#     # because our "widget" is a pure function, we can call it and
#     # test it independently of napari
#     im_data = np.random.random((100, 100))
#     thresholded = threshold_autogenerate_widget(im_data, 0.5)
#     assert thresholded.shape == im_data.shape
#     # etc.


# # make_napari_viewer is a pytest fixture that returns a napari viewer object
# # you don't need to import it, as long as napari is installed
# # in your testing environment
# def test_threshold_magic_widget(make_napari_viewer):
#     viewer = make_napari_viewer()
#     layer = viewer.add_image(np.random.random((100, 100)))
#
#     # our widget will be a MagicFactory or FunctionGui instance
#     my_widget = threshold_magic_widget()
#
#     # if we "call" this object, it'll execute our function
#     thresholded = my_widget(viewer.layers[0], 0.5)
#     assert thresholded.shape == layer.data.shape





# def test_image_threshold_widget(make_napari_viewer):
#     viewer = make_napari_viewer()
#     layer = viewer.add_image(np.random.random((100, 100)))
#     my_widget = ImageThreshold(viewer)
#
#     # because we saved our widgets as attributes of the container
#     # we can set their values without having to "interact" with the viewer
#     my_widget._image_layer_combo.value = layer
#     my_widget._threshold_slider.value = 0.5
#
#     # this allows us to run our functions directly and ensure
#     # correct results
#     my_widget._threshold_im()
#     assert len(viewer.layers) == 2


# # capsys is a pytest fixture that captures stdout and stderr output streams
# def test_example_q_widget(make_napari_viewer, capsys):
#     # make viewer and add an image layer using our fixture
#     viewer = make_napari_viewer()
#     viewer.add_image(np.random.random((100, 100)))
#
#     # create our widget, passing in the viewer
#     my_widget = ExampleQWidget(viewer)
#
#     # call our widget method
#     my_widget._on_click()
#
#     # read captured output and check that it's as we expected
#     captured = capsys.readouterr()
#     assert captured.out == "napari has 1 layers\n"
