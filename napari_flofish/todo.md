Plugin todo:
- Segmentation widget
- Make sample data from zenodo
- Container widget
- display widget return values in widget
- project all layers
- compute statistics (=assign spots)
- restrict layers available in pulldown menus
- make widget parameters depend on widget argument (i.e. max threshold value depends on layer)
- async processing

Manual:
1. use plugin as exploration tool to find good spot detection parameters
2. use pipeline engine to process set of pictures in reproducible fashion
  
Set up environment:
1. napari
   1. check that console works
   2. open vsi files: conda install aicsimageio
2. napari plugin development 
   1. conda install napari-flofish
3. project
    1. omnipose: install from git clone on MacOS
        1. cd /Users/adele/Projects/omnipose && pip install -e .
        2. cd /Users/adele/Projects/cellpose-omni && pip install -e .
        3. GUI: omnipose
    2. pip install jsonpickle bioio bioio-ome-tiff bioio-ome-zarr bioio-bioformats
    3. pip install big-fish
    4. conda install scyjava
    5. export JAVAHOME=/Users/adele/miniconda3/envs/omnipose/lib/jvm
    6. set $JAVA_HOME for bioio-bioformats
    7. edit peakdetect.py to: from scipy.fft import ifft
    8. check that tests pass
4. PyCharm
   1. Add project dirs to PYTHONPATH (in Settings)

