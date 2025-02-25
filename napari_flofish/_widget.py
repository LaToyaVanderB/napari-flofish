"""
Widgets to call Big-FISH functions. 
"""

import napari
from typing import List

from magicgui import magic_factory

from flofish.image import Image
from flofish.experiment import Experiment

from bigfish import detection
from bigfish import stack

import numpy as np
import pandas as pd
from pathlib import Path



@magic_factory(
    cfg_file={"label": "Config file"},
    vsi_file={"label": "VSI file"},
    cell_file={"label": "DIC file"},
)
def read_in_vsi_widget(
        cfg_file=Path.home(),
        vsi_file=Path.home(),
        cell_file=Path.home(),
) -> List[napari.types.LayerDataTuple]:

    img = Image.from_dict(params={ "vsi_file": vsi_file, "cell_file": cell_file }, exp=Experiment.from_cfg_file(cfg_file=cfg_file))
    img.read_image()
    img.read_cells()
    img.align()

    layer_data_tuples = []
    layer_data_tuples.append((img.cells['aligned'], { 'name': "DIC", 'colormap': 'grey', 'visible': True, 'blending': 'additive' }, 'image'))
    for ch, data in reversed(img.mrna.items()):
        layer_data_tuples.append((data['aligned'], { 'name': ch, 'colormap': img.experiment.channels[ch]['colormap'], 'visible': False, 'blending': 'additive' }, 'image'))

    return layer_data_tuples


@magic_factory(
    sigma_z={"widget_type": "FloatSlider", "max": 5},
    sigma_yx={"widget_type": "FloatSlider", "max": 5},
    auto_call=False
)
def background_filtering_magic_widget(
    img_layer: "napari.layers.Image", sigma_z: "float" = 0.75, sigma_yx: "float" = 2.3
) -> "napari.types.LayerDataTuple":
    return (stack.remove_background_gaussian(img_layer.data, (sigma_z, sigma_yx, sigma_yx)),
            { 'name': f'{img_layer.name} background filtered', 'metadata': { 'channel' : img_layer.name } }, 'image')


@magic_factory(
    threshold={"widget_type": "IntSlider", "min": 0, "max": 200},
    scale_z={"widget_type": "FloatSlider", "max": 2000},
    scale_yx={"widget_type": "FloatSlider", "max": 2000},
    spot_radius_z={"widget_type": "FloatSlider", "max": 2000},
    spot_radius_yx={"widget_type": "FloatSlider", "max": 2000},
    auto_call=False
)
def spot_detection_magic_widget(
    viewer: "napari.Viewer",
    img_layer: "napari.layers.Image",
    threshold: int=50,
    scale_z: float=200, scale_yx: float=65,
    spot_radius_z: float=800, spot_radius_yx: float=120,
) -> List[napari.types.LayerDataTuple]:
    # if we return the mask and the LoG filtered image as layers, then we can re-threshold
    # the spots *after* spot detection

    # spot radius
    spot_radius_px = detection.get_object_radius_pixel(
        voxel_size_nm=(scale_z, scale_yx, scale_yx),
        object_radius_nm=(spot_radius_z, spot_radius_yx, spot_radius_yx),
        ndim=3)

    # LoG filter
    rna_log = stack.log_filter(img_layer.data, sigma=spot_radius_px)

    # local maximum detection
    mask = detection.local_maximum_detection(rna_log, min_distance=spot_radius_px)

    spots, features = threshold_spots(rna_log, mask, threshold)

    # if we have DIC masks, we add the cell labels to the spot
    # features for display purposes
    if 'DIC masks' in viewer.layers:
        cell_masks = viewer.layers['DIC masks'].data
        features['label'], features['in_cell'] = get_labels(cell_masks, spots)

    spots_metadata = img_layer.metadata
    channel = spots_metadata['channel']
    spots_metadata.update({
        'threshold': threshold,
        'scale': (scale_z, scale_yx, scale_yx),
        'spot_radius': (spot_radius_z, spot_radius_yx, spot_radius_yx)
    })

    return [
        (rna_log, { 'name': f'{channel} LoG filtered', 'metadata': img_layer.metadata }, 'image'),
        (mask, { 'name': f'{channel} local maxima', 'metadata': img_layer.metadata }, 'labels'),
        (spots, {
            'name': f'{channel} spots detected thr={threshold}',
            'features': features,
            'metadata': spots_metadata,
            'symbol': 'disc',
            'size': 10,
            'border_width': 0.1,
            'border_color': 'in_cell',
            'border_color_cycle': ['cyan', 'red'] if features.iloc[0]['in_cell'] == True else ['red', 'cyan'],
            'face_color': 'transparent',
            'opacity': 0.5,
            'out_of_slice_display': True
            },
         'points'),
    ]


def threshold_spots(rna_log, mask, threshold):
    spots, _ = detection.spots_thresholding(rna_log, mask, threshold)
    log_intensities = np.resize(np.array([rna_log[s[0], s[1], s[2]] for s in spots]), (len(spots), 1))

    spots_with_intensities = np.concatenate((spots, log_intensities), axis=1)
    features = pd.DataFrame(spots_with_intensities, columns=['z', 'y', 'x', 'intensity_LoG'])
    features['label'] = -1
    features['in_cell'] = 1

    return spots, features


@magic_factory(
    threshold={"widget_type": "IntSlider", "min": 0, "max": 2000},
    auto_call=False
)
def spot_thresholding_magic_widget(
    viewer: "napari.Viewer",
    img_layer: "napari.layers.Points", threshold: float=50,
) -> "napari.types.LayerDataTuple":
    spots_metadata = img_layer.metadata
    spots_metadata.update({ 'threshold': threshold})
    channel = spots_metadata['channel']

    rna_log = viewer.layers[f'{channel} LoG filtered'].data
    mask = viewer.layers[f'{channel} local maxima'].data.astype(bool)
    spots, features = threshold_spots(rna_log, mask, threshold)

    # if we have DIC masks, we add the cell labels to the spot
    # features for display purposes
    if 'DIC masks' in viewer.layers:
        cell_masks = viewer.layers['DIC masks'].data
        features['label'], features['in_cell'] = get_labels(cell_masks, spots)

    return (spots, {
        'name': f'{channel} spots thresholded thr={threshold}',
        'features': features,
        'metadata': spots_metadata,
        'symbol': 'disc',
        'size': 10,
        'border_width': 0.1,
        'border_color': 'in_cell',
        # this breaks if we don't have features, ie when reading img.json
        # actually we do have features when reading img.json
        'border_color_cycle': ['cyan', 'red'] if features.iloc[0]['in_cell'] == True else ['red', 'cyan'],
        'face_color': 'transparent',
        'opacity': 0.5,
        'out_of_slice_display': True
    },
            'points')


def get_labels(cell_masks, spots):
    labels = [ cell_masks[y, x] for (y, x) in spots[:, 1:3] ]
    in_cell = [ 0 if l == 0 else 1 for l in labels ]

    return pd.Series(labels, dtype='int64'), pd.Series(in_cell, dtype='int64')


@magic_factory(
    auto_call=False
)
def spot_decomposition_magic_widget(
    viewer: "napari.Viewer",
    point_layer: "napari.layers.Points",
) -> List[napari.types.LayerDataTuple]:
    spots = point_layer.data
    metadata = point_layer.metadata
    channel = metadata['channel']

    rna = viewer.layers[f'{channel}'].data

    decomp_spots, dense_regions, reference_spot = detection.decompose_dense(
        rna,
        spots,
        voxel_size=metadata['scale'],
        spot_radius=metadata['spot_radius'],
        alpha=0.5,  # alpha impacts the number of spots per candidate region
        beta=2,  # beta impacts the number of candidate regions to decompose
        gamma=1  # gamma the filtering step to denoise the image
    )

    features = pd.DataFrame(decomp_spots, columns=['z', 'y', 'x'])
    features['label'] = -1
    features['in_cell'] = 1
    # if we have DIC masks, we add the cell labels to the spot
    # features for display purposes
    if 'DIC masks' in viewer.layers:
        cell_masks = viewer.layers['DIC masks'].data
        features['label'], features['in_cell'] = get_labels(cell_masks, decomp_spots)

    metadata.update({ 'decomposed': 1 })

    return [
        (dense_regions[:, 1:3], {
            'name': f'{channel} dense regions thr={metadata["threshold"]}',
            'symbol': 'disc',
            'size': 10,
            'border_width': 0,
            'face_color': 'cyan',
            'opacity': 0.5
        },
         'points'),
        (decomp_spots, {
            'name': f'{channel} spots decomposed thr={metadata["threshold"]}',
            'features': features,
            'metadata': metadata,
            'symbol': 'x',
            'size': 10,
            'border_width': 0.1,
            'border_color': 'in_cell',
            'border_color_cycle': ['cyan', 'red'] if features.iloc[0]['in_cell'] == True else ['red', 'cyan'],
            'face_color': 'transparent',
            'opacity': 0.5
        },
         'points')
    ]