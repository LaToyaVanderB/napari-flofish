Plugin todo:
- segmentation widget
- container widget
- display widget return values in widget
- project all layers
- compute statistics (=assign spots)
- restrict layers available in pulldown menus
- make widget parameters depend on widget argument (i.e. max threshold value depends on layer)
- async processing
- fix scale
- upload packages
- fix Omnipose GPU 
   - do not load automatically at start up
   - deal with no GPU
  
Set up environment:

   - Omnipose

      On MacOS: install from git source or git clone on MacOS in a conda env with python<=3.10.11 (see [this issue](https://github.com/kevinjohncutler/omnipose/issues/14))

      First add `jupyterlab` to `omnipose_mac_environment.yml` from [Omnipose](https://omnipose.readthedocs.io/installation.html) repository, then:
      ```
      conda env create --name myenv --file /Volumes/DataDrive/omnipose_mac_environment.yml
      conda activate myenv
      pip install git+https://github.com/kevinjohncutler/omnipose.git
      pip install git+https://github.com/kevinjohncutler/cellpose-omni.git
      ```

   - Omnipose GUI

      Run `omnipose` from the command line.


   - Other
      ```
      conda install -c conda-forge scyjava
      pip install "napari[pyqt6]"
      pip install bioio bioio_bioformats big-fish jsonpickle pathlib  
      ```
   - Might be needed:
      - `export JAVA_HOME=/Users/adele/miniconda3/envs/myenv/lib/jvm`
      - deactivate and reactivate myenv for `scyjava` to work
      - edit `peakdetect.py` fft import line to: `from scipy.fft import fft, ifft`
      - `pip install "napari[pyqt6]"`

   

   


