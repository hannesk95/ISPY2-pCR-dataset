import sys
sys.path.append("..")
from src.ISPY2_pCR_dataset import preprocess_data

if __name__ == "__main__":
    preprocess_data(download_dir="../downloads",
                    clinical_file_path="../data/ISPY2-Imaging-Cohort-1-Clinical-Data.xlsx")