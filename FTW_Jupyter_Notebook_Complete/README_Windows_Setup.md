# Windows setup for the FTW Jupyter notebook

This setup keeps FTW separate from your existing Python installation. The official FTW repository recommends an isolated `uv` environment.

## 1. Install `uv`

Open PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Close and reopen PowerShell.

## 2. Clone FTW

```powershell
cd $HOME
git clone https://github.com/fieldsoftheworld/ftw-baselines.git
cd ftw-baselines
```

## 3. Create the environment and install FTW

```powershell
uv sync --all-extras --dev
```

## 4. Install Jupyter and register the kernel

Run from the `ftw-baselines` folder:

```powershell
uv pip install --python .venv\Scripts\python.exe notebook ipykernel
uv run python -m ipykernel install --user --name ftw-baselines --display-name "Python (FTW)"
```

## 5. Verify the installation

```powershell
uv run ftw --help
uv run ftw model list
uv run python -c "import torch, rasterio, geopandas, pyarrow; print('Imports OK'); print('PyTorch:', torch.__version__); print('CUDA available:', torch.cuda.is_available())"
```

## 6. Launch Jupyter

From the `ftw-baselines` folder:

```powershell
uv run jupyter notebook
```

In the notebook UI, select the **Python (FTW)** kernel. Open `FTW_Field_Boundary_Detection.ipynb` and run cells from top to bottom.

## What the notebook does

- Uses a small example area in Iowa, USA.
- Uses the latest year currently listed in the FTW CLI docs (2025).
- Tries `FTW_PRUE_EFNET_B5_CCBY`; verify it exists using `ftw model list`.
- Runs on CPU by default. Use `GPU_ID = 0` only if CUDA and a compatible NVIDIA GPU are available.
- Produces `inference_data.tif`, `inference_output.tif`, `polygons.parquet`, `field_boundaries.geojson`, `field_boundaries_preview.png`, and `run_summary.json`.

First inference may download imagery and model weights and take time.

## Troubleshooting

- **`ftw` not found:** Ensure the kernel is `Python (FTW)` and installed from this same environment.
- **Model name not found:** Run `uv run ftw model list`, then set `MODEL_NAME` to a listed model.
- **GPU error:** Keep `GPU_ID = -1` to run on CPU.
- **No polygons:** Try another small agricultural bounding box and inspect output/logs.
- **GeoParquet or GeoJSON error:** Check that `geopandas` and `pyarrow` import in the same kernel.
- **Year error:** Current documented CLI range is 2015–2025; update only if the installed FTW version documents newer support.

Official references:
- https://github.com/fieldsoftheworld/ftw-baselines
- https://fieldsofthe.world/tutorial.html

The notebook and setup guide are prepared, but the live model has not been executed in your local environment. Initial setup or model/data selection may need troubleshooting.
