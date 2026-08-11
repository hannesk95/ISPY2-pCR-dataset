# ISPY2 Dataset Curation for Breast Cancer pCR Prediction

Implementation of the ISPY2 dataset curation pipeline for breast cancer pathologic complete response (pCR) prediction from our publication [&#34;Graph Representation Learning of Longitudinal Medical Imaging Trajectories for Treatment Response Prediction&#34;](https://arxiv.org/pdf/2607.04912).

## Example Usage

```python
from ISPY2_pCR_dataset import download_data, preprocess_data

download_dir = "path/to/output/directory"
manifest_file_path = "path/to/tcia/manifest/xlsx/file" # can be found at https://github.com/hannesk95/ISPY2-pCR-dataset/tree/main/data
clinical_file_path = "path/to/clinical_xlsx/file" # can be found at https://github.com/hannesk95/ISPY2-pCR-dataset/tree/main/data

download_data(download_dir=download_dir,
              manifest_file_path=manifest_file_path)

preprocess_data(download_dir=download_dir,
                clinical_file_path=clinical_file_path)
```

## Citation

```bibtex
@article{kiechle2026graph,
title={Graph Representation Learning of Longitudinal Medical Imaging Trajectories for Treatment Response Prediction},
author={Kiechle, Johannes and Osuala, Richard and Lang, Daniel M and Fischer, Stefan M and Jan{\'\i}{\v{c}}kov{\'a}, Ivana and Lekadir, Karim and Schnabel, Julia A and Peeken, Jan C},
journal={arXiv preprint arXiv:2607.04912},
year={2026}
}
```
