import sys
sys.path.append("..")
from src.ISPY2_pCR_dataset import download_data

if __name__ == "__main__":

    download_data(file_path="/home/johannes/Data/SSD_2.0TB/ISPY2-pCR-dataset/data/ISPY2-Cohort1-inclu-ACRIN6698-full-manifes-nbia-digest.xlsx",
                  download_dir="../downloads")