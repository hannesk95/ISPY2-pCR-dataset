from .download import download_data
from .preprocess import preprocess_data

def download_and_preprocess(download_dir=None, manifest_file_path=None, clinical_file_path=None, first_n: int = None):
    download_data(download_dir=download_dir, manifest_file_path=manifest_file_path, first_n=first_n)
    preprocess_data(download_dir=download_dir, clinical_file_path=clinical_file_path)
    