# ISPY2 Dataset Curation for Breast Cancer pCR Prediction

Implementation of the ISPY2 dataset curation pipeline for breast cancer pathologic complete response (pCR) prediction from our publication [&#34;Graph Representation Learning of Longitudinal Medical Imaging Trajectories for Treatment Response Prediction&#34;](https://arxiv.org/pdf/2607.04912).

## Example Usage

```python
import ISPY2_pCR_dataset.ISPY2_pCR_dataset as dataset

file_path = "path/to/tcia/manifest/xlsx/file" # can be found at https://github.com/compai-lab/2026-miccai-grail-kiechle
output_dir = "path/to/output/directory"

dataset.download_data(file_path=file_path, 
                      output_dir=output_dir)
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
