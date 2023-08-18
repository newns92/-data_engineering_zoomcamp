## Environment Setup
- Download [Anaconda](https://www.anaconda.com/download) or [Miniconda](https://docs.conda.io/en/latest/miniconda.html#)
- First, create a **conda environment** via `conda create -n zoom_project python=3.9`
- Activate it via `conda activate zoom_project`
- Check packages:
    - If the environment isn't activated, then do so via `conda list -n zoom_project`
    - If the environment *is* activated, then do so via `pip list` or `conda list`
- Install the package requirements found in `requirements.txt` via `pip install -r requirements.txt`
- Check packages again if desired (recommended)

## Download Data
- Run `get_data.py` in the `zoom_project` Conda environment to collect data from THDB's API and put that into a parquet file