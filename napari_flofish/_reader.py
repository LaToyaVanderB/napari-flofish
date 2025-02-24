"""
This module is an example of a barebones numpy reader plugin for napari.

It implements the Reader specification, but your plugin may choose to
implement multiple readers or even other plugin contributions. see:
https://napari.org/stable/plugins/guides.html?#readers
"""
import numpy as np
import pandas as pd
import json
from skimage import io
from pathlib import Path


def napari_get_reader(path):
    """A basic implementation of a Reader contribution.

    Parameters
    ----------
    path : str or list of str
        Path to file, or list of paths.

    Returns
    -------
    function or None
        If the path is a recognized format, return a function that accepts the
        same path or list of paths, and returns a list of layer data tuples.
    """
    if isinstance(path, list):
        # reader plugins may be handed single path, or a list of paths.
        # if it is a list, it is assumed to be an image stack...
        # so we are only going to look at the first file.
        path = path[0]

    # if we know we cannot read the file, we immediately return None.
    if not path.endswith(".json"):
        return None

    # otherwise we return the *function* that can read ``path``.
    return reader_function


def reader_function(path):
    """Take a path or list of paths and return a list of LayerData tuples.

    Readers are expected to return data as a list of tuples, where each tuple
    is (data, [add_kwargs, [layer_type]]), "add_kwargs" and "layer_type" are
    both optional.

    Parameters
    ----------
    path : str
        Path to img.json file

    Returns
    -------
    layer_data : list of tuples
        A list of LayerData tuples where each tuple in the list contains
        (data, metadata, layer_type), where data is a numpy array, metadata is
        a dict of keyword arguments for the corresponding viewer.add_* method
        in napari, and layer_type is a lower-case string naming the type of
        layer. Both "meta", and "layer_type" are optional. napari will
        default to layer_type=="image" if not provided
    """
    # handle both a string and a list of strings
    # paths = [path] if isinstance(path, str) else path
    # # load all files into array
    # arrays = [np.load(_path) for _path in paths]
    # # stack arrays into single array
    # data = np.squeeze(np.stack(arrays))
    #
    # # optional kwargs for the corresponding viewer.add_* method
    # add_kwargs = {}
    #
    # layer_type = "image"  # optional, default is "image"
    #
    # return [(data, add_kwargs, layer_type)]

    layer_tuples = read_smfish_json(path)
    pass
    return layer_tuples


def read_smfish_json(path):
    layer_list = [
        { 'file': 'DIC.tif', 'layer_type': "image",
          'add_kwargs': { 'name': "DIC", 'colormap': 'grey', 'visible': True, 'blending': 'additive' } },
        { 'file': 'DIC_masks_pp.tif', 'layer_type': 'labels',
          'add_kwargs': { 'name': "DIC masks", 'visible': False, 'blending': 'additive', 'opacity': 0.2 } },
        { 'file': 'DIC_masks_pp_expanded.tif', 'layer_type': 'labels',
          'add_kwargs': { 'name': "DIC masks expanded", 'visible': False, 'blending': 'additive', 'opacity': 0.2 } },
        { 'file': 'DAPI.tif', 'layer_type': "image",
          'add_kwargs': { 'name': "DAPI", 'colormap': 'blue', 'visible': True, 'blending': 'additive' } },
        { 'file': 'DAPI_masks.tif', 'layer_type': 'labels',
          'add_kwargs': { 'name': "DAPI masks", 'visible': False, 'blending': 'additive', 'opacity': 0.2 } },
    ]


    layer_tuples = []
    with open(path, "r") as f:
        img = json.load(f)
        colors = { i[0]: i[1]['colormap'] for i in img['results'].items() }

        focus = [ i[1]['z_max_focus'] for i in img['results'].items() if 'z_max_focus' in i[1] ]
        if not focus:
            focus = 20
        else:
            focus = np.max(focus)
        # how do I access the current viewer from here?
        # viewer.dims.set_point(0, focus)

        for ch in img['results'].keys():
            metadata = { 'channel': ch }
            for key, value in img['parameters'].items():
                metadata[key] = value

            layer_list.append({ 'file': f'{ch}.tif', 'layer_type': "image",
                                'add_kwargs': { 'name': f'{ch}', 'metadata': metadata,
                                                'colormap': colors[ch], 'visible': False, 'blending': 'additive' } })

            layer_list.append({ 'file': f'{ch}_filtered.npy', 'layer_type': "image",
                                'add_kwargs': { 'name': f'{ch} background filtered', 'metadata': metadata,
                                                'colormap': colors[ch], 'visible': True, 'blending': 'additive' } })

            threshold = img['results'][ch]['threshold']
            metadata.update({ 'threshold': threshold, 'scale': metadata['scale'], 'spot_radius': metadata['spot_radius'] })
            layer_list.append({ 'file': f'{ch}_spots.npy', 'layer_type': "spots",
                                'add_kwargs': {'name': f'{ch} spots detected thr={threshold}', 'metadata': metadata,
                                               'blending': 'translucent', 'visible': False, 'out_of_slice_display': True,
                                               'symbol': 'disc', 'size': 10, 'border_width': 0.1, 'border_color': colors[ch], 'face_color': 'transparent', 'opacity': 0.5 }})

            layer_list.append({ 'file': f'{ch}_decomposed_spots.npy', 'layer_type': "decomposed_spots",
                                'add_kwargs': {'name': f'{ch} decomposed spots', 'metadata': metadata,
                                               'blending': 'translucent', 'visible': False, 'out_of_slice_display': True,
                                               'symbol': 'disc', 'size': 10, 'border_width': 0.1, 'border_color': colors[ch], 'face_color': 'transparent', 'opacity': 0.5 }})

        for l in layer_list:
            file = Path(path).parent / l['file']
            print(l['file'])
            if file.is_file():
                if file.suffix == '.tif':
                    data = io.imread(file)
                    layer_tuples.append( (data, l['add_kwargs'], l['layer_type']) )
                elif file.suffix == '.npy':
                    data = np.load(file)
                    if l['layer_type'] == "image":
                        layer_tuples.append( (data, l['add_kwargs'], l['layer_type']) )
                    elif l['layer_type'] == "decomposed_spots":
                        l['layer_type'] = "points"
                        layer_tuples.append((data, l['add_kwargs'], l['layer_type']))
                    elif l['layer_type'] == "spots":
                        l['layer_type'] = "points"

                        features = pd.DataFrame(data, columns=['z', 'y', 'x', 'intensity', 'filtered_intensity', 'label'])
                        features['in_cell'] = features.apply(lambda s: False if s['label'] == 0 else True, axis=1)
                        l['add_kwargs']['border_color'] = 'in_cell'
                        l['add_kwargs']['border_color_cycle'] = ['cyan', 'red'] if features.iloc[0]['in_cell'] == True else ['red', 'cyan']

                        spot_data = data[:, :3]
                        l['add_kwargs'].update({'features': features})
                        layer_tuples.append( (spot_data, l['add_kwargs'], l['layer_type']) )

    return layer_tuples

