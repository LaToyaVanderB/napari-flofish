from napari_flofish import napari_get_reader


def test_reader(make_napari_viewer):
    """An example of how you might test your plugin."""

    # read data
    my_test_file = '/Volumes/KINGSTON/Florence/smFISH/zenodo/smfish-analysis/tests/data/exp16/output/MG1655_GLU_OD_0.3_left_02/img.json'
    reader = napari_get_reader(my_test_file)
    assert callable(reader)

    # make sure we're delivering the right format
    viewer = make_napari_viewer()
    layer_data_list = reader(my_test_file)
    assert isinstance(layer_data_list, list) and len(layer_data_list) > 0
    layer_data_tuple = layer_data_list[0]
    assert isinstance(layer_data_tuple, tuple) 


def test_get_reader_pass():
    reader = napari_get_reader("fake.file")
    assert reader is None
