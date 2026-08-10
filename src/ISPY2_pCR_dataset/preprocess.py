import os
import pydicom
from glob import glob
from tqdm import tqdm
from datetime import datetime
from pathlib import Path
import shutil
import os
from tqdm import tqdm
from glob import glob
import dicom2nifti
import os
import subprocess
import shutil
from pathlib import Path
from typing import List
import pydicom
import nibabel as nib
import dicom2nifti
import os
from tqdm import tqdm
from glob import glob
from pathlib import Path
import dicom2nifti
import dicom2nifti.settings as settings
import os
import subprocess
from pathlib import Path
import SimpleITK as sitk
import numpy as np
import torchio as tio
from glob import glob
from tqdm import tqdm
import SimpleITK as sitk
import os
import numpy as np
import torch
import SimpleITK as sitk
import os
import torchio as tio
import torch
from tqdm import tqdm
from glob import glob
import shutil
import subprocess
import numpy as np
import time
import torchio as tio
from glob import glob
from tqdm import tqdm
import SimpleITK as sitk
import os
import SimpleITK as sitk
from glob import glob
from tqdm import tqdm
import torch
import numpy as np
import os
from tqdm import tqdm
from glob import glob
import os
import pandas as pd
from sklearn.model_selection import StratifiedKFold
from glob import glob
import os
from tqdm import tqdm
import torch
import pandas as pd

def _rename_and_move_study_dirs(download_dir: str):

    for study_dir in tqdm(glob(os.path.join(download_dir, "*"))):

        for file in glob(os.path.join(study_dir, "*.dcm"))[:1]:
            ds = pydicom.dcmread(file)
            study_date = ds.get("StudyDate")
            study_date = datetime.strptime(study_date, "%Y%m%d").date()
            study_id = ds.get("StudyID")
            series_description = ds.get("SeriesDescription") 
            series = ds.get("SeriesNumber")

        try:
            new_dir_name = f"ISPY2-{study_id.replace('_', '-')}_{study_date}_{series}_{series_description.replace(' ', '-').replace('/', '-').replace('_', '-')}"        
            partent_dir = str(Path(study_dir).parent)
            os.rename(study_dir, os.path.join(partent_dir, new_dir_name))
        except:
            print(f"Failed to rename {study_dir}")
            continue

    for study_dir in tqdm(glob(os.path.join(download_dir, "*"))):

        patient_id = os.path.basename(study_dir).split("_")[0][:-3]
        
        partent_dir = str(Path(study_dir).parent)
        new_dir = os.path.join(partent_dir, patient_id)

        if not os.path.exists(new_dir):
            os.makedirs(new_dir)
        
        shutil.move(study_dir, new_dir)

def _dicom_to_nifti_dcm2niix(
    dicom_dir: str | Path,
    output_nifti_path: str | Path,
    gzip: bool = True,
    overwrite: bool = False,
    extra_args: List[str] | None = None,
) -> List[Path]:
    """
    Convert a DICOM directory to NIfTI using dcm2niix.

    Parameters
    ----------
    dicom_dir : str or Path
        Directory containing DICOM files.
    output_nifti_path : str or Path
        Desired output NIfTI file path (used to derive output dir + filename).
    gzip : bool, default=True
        Whether to gzip the output (.nii.gz).
    overwrite : bool, default=False
        Whether to overwrite existing output directory.
    extra_args : list of str, optional
        Additional dcm2niix command-line arguments.

    Returns
    -------
    List[Path]
        List of generated NIfTI files.
    """

    dicom_dir = Path(dicom_dir).expanduser().resolve()
    output_nifti_path = Path(output_nifti_path).expanduser().resolve()

    if not dicom_dir.is_dir():
        raise ValueError(f"DICOM directory does not exist: {dicom_dir}")

    out_dir = output_nifti_path.parent
    out_dir.mkdir(parents=True, exist_ok=True)

    # dcm2niix uses filename *pattern*, not full path
    filename_stem = output_nifti_path.stem
    if filename_stem.endswith(".nii"):
        filename_stem = filename_stem[:-4]

    if overwrite:
        for f in out_dir.glob(f"{filename_stem}*"):
            f.unlink()

    cmd = [
        "dcm2niix",
        "-z", "y" if gzip else "n",
        "-f", filename_stem,
        "-o", str(out_dir),
        str(dicom_dir),
    ]

    if extra_args:
        cmd[1:1] = extra_args

    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(
            "dcm2niix failed\n"
            f"Command: {' '.join(cmd)}\n"
            f"STDOUT:\n{result.stdout}\n"
            f"STDERR:\n{result.stderr}"
        )

def _convert_DCEMRI_to_niigz(download_dir: str):

    failed_conversions = []

    for patient_dir in tqdm(glob(os.path.join(download_dir, "ISPY2-*"))):
        print(f"Processing patient directory: {patient_dir}")

        for study_dir in os.listdir(patient_dir):
            study_dir = os.path.join(patient_dir, study_dir)      

            if not os.path.isdir(study_dir):
                continue        

            if "DCE" in study_dir:
                output_file = study_dir + ".nii.gz"
                # if os.path.exists(output_file):
                #     pass
                #     # print(f"Output file {output_file} already exists. Skipping conversion.")
                # else:            
                try:
                    # dicom2nifti.dicom_series_to_nifti(study_dir, output_file)
                    nifti_files = _dicom_to_nifti_dcm2niix(study_dir, output_file)                

                except Exception as e:
                    print(patient_dir)
                    failed_conversions.append(patient_dir.split("/")[-1])
                    print(f"Error converting {study_dir}: {e}\n\n")
            
    for file in glob(os.path.join(download_dir, "ISPY2-*/*.json")):
        os.remove(file)

def _dicom_seg_to_nifti(
    seg_dcm: str | Path,
    output_nii: str | Path,
):
    """
    Convert a DICOM SEG file to NIfTI (.nii.gz).

    Parameters
    ----------
    seg_dcm : path
        Path to DICOM SEG file
    reference_dicom_dir : path
        Directory containing the referenced DICOM images
    output_nii : path
        Output .nii.gz file
    """

    seg_dcm = Path(seg_dcm)
    # reference_dicom_dir = Path(reference_dicom_dir)
    output_nii = Path(output_nii)

    output_nii.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        "segimage2itkimage",
        "--inputDICOM", str(seg_dcm),
        # "--inputImageDirectory", str(reference_dicom_dir),
        "--outputDirectory", str(output_nii),
    ]

    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def _convert_FTV_to_niigz(download_dir: str):

    for patient_dir in tqdm(glob(os.path.join(download_dir, "ISPY2-*"))):
        print(f"Processing patient directory: {patient_dir}")

        for study_dir in sorted(os.listdir(patient_dir)):
            study_dir = os.path.join(patient_dir, study_dir)

            if study_dir.endswith(".nrrd"):
                continue 

            if study_dir.endswith(".nii.gz"):
                continue       

            if "Analysis-Mask" in study_dir:
                # print(f"Processing study directory: {study_dir}")
                
                seg_file = glob(os.path.join(study_dir, "*.dcm"))[0]

                output_nii = Path(study_dir).parent
                # print(output_nii)

                _dicom_seg_to_nifti(
                    seg_dcm=seg_file,
                    output_nii=output_nii,
                )

                filename = seg_file.split("/")[-2]
                
                os.rename(os.path.join(output_nii, "1.nrrd"), os.path.join(output_nii, f"{filename}.nrrd"))
                os.remove(os.path.join(output_nii, "meta.json"))


    for file in tqdm(glob(os.path.join(download_dir, "ISPY2-*/*.nrrd"))):

        img = sitk.ReadImage(file)
        sitk.WriteImage(img, file.replace(".nrrd", ".nii.gz"))
        os.remove(file)   

def _get_final_patient_ids(download_dir: str):
    final_patient_ids_3_timepoints = []
    final_patient_ids_4_timepoints = []

    for patient_dir in tqdm(glob("/media/johannes/HDD_8.0TB/ISPY2_new/ISPY2-*")):
        files = sorted(glob(os.path.join(patient_dir, "*DCE*.nii.gz")))

        if len(files) >=3:    
            if "T0" in files[0]:
                img = sitk.ReadImage(files[0])
                arr = sitk.GetArrayFromImage(img)
                if arr.shape[0]>=4:
                    if "T1" in files[1]:
                        img = sitk.ReadImage(files[1])
                        arr = sitk.GetArrayFromImage(img)
                        if arr.shape[0]>=4:
                            if "T2" in files[2]:
                                img = sitk.ReadImage(files[2])
                                arr = sitk.GetArrayFromImage(img)
                                if arr.shape[0]>=4:
                                    final_patient_ids_3_timepoints.append(patient_dir.split("/")[-1])

                                    if len(files)>=4:
                                        if "T3" in files[3]:
                                            img = sitk.ReadImage(files[3])
                                            arr = sitk.GetArrayFromImage(img)
                                            if arr.shape[0]>=4:
                                                final_patient_ids_4_timepoints.append(patient_dir.split("/")[-1])


    print("Patients with at least 3 timepoints:", len(final_patient_ids_3_timepoints))
    torch.save(final_patient_ids_3_timepoints, os.path.join(download_dir, "final_patient_ids_3_timepoints.pt"))
    print("Patients with at least 4 timepoints:", len(final_patient_ids_4_timepoints))
    torch.save(final_patient_ids_4_timepoints, os.path.join(download_dir, "final_patient_ids_4_timepoints.pt"))

def _preprocess_patients(download_dir: str):
        patient_ids_3 = torch.load(os.path.join(download_dir, "final_patient_ids_3_timepoints.pt"))
        print(len(patient_ids_3))

        patient_ids_4 = torch.load(os.path.join(download_dir, "final_patient_ids_4_timepoints.pt"))
        print(len(patient_ids_4))

        patient_ids = patient_ids_3 + patient_ids_4
        print(len(patient_ids))
        patient_ids = np.unique(patient_ids)
        patient_ids = list(patient_ids)
        print(len(patient_ids))

        failed_patients = []

        for patient_id in tqdm(patient_ids):

            try: 
                # print(patient_id)

                target_folder = f"/home/johannes/Data/SSD_2.0TB/GNN_pCR/data/breast_cancer/data_processed/{patient_id}/"

                if os.path.exists(target_folder):
                    print(f"Patient {patient_id} already processed, skipping.")
                    # time.sleep(5)
                    continue

                files_dce = sorted(glob(f"/media/johannes/HDD_8.0TB/ISPY2_new/{patient_id}/*DCE*.nii.gz"))
                files_ftv = sorted(glob(f"/media/johannes/HDD_8.0TB/ISPY2_new/{patient_id}/*Analysis*.nii.gz"))

                try:
                    assert len(files_dce) == len(files_ftv), f"Number of DCE {len(files_dce)} and FTV {len(files_ftv)} files do not match for patient {patient_id}."
                except:
                    print(f"Number of DCE {len(files_dce)} and FTV {len(files_ftv)} files do not match for patient {patient_id}.")
                    continue

                for file in files_dce+files_ftv:
                    if not os.path.exists(target_folder):
                        os.makedirs(target_folder)
                    
                    shutil.copy(file, target_folder)
                
                files_dce = sorted(glob(f"{target_folder}/*DCE.nii.gz"))

                for file in files_dce:
                    img = sitk.ReadImage(file)  # 4D image

                    size = list(img.GetSize())      # [x, y, z, t]
                    index = [0, 0, 0, 0]

                    # Extract timepoint 0
                    size_tp = size.copy()
                    size_tp[3] = 0  # remove time dimension

                    index[3] = 0
                    img0 = sitk.Extract(img, size_tp, index)

                    index[3] = 1
                    img1 = sitk.Extract(img, size_tp, index)

                    index[3] = 4
                    img5 = sitk.Extract(img, size_tp, index)

                    sitk.WriteImage(img0, file.replace(".nii.gz", "_timepoint0.nii.gz"))
                    sitk.WriteImage(img1, file.replace(".nii.gz", "_timepoint1.nii.gz"))
                    sitk.WriteImage(img5, file.replace(".nii.gz", "_timepoint5.nii.gz"))
                
                # files_dce_timepoints = sorted(glob(f"{target_folder}/*DCE*_timepoint*.nii.gz"))

                # fixed_image = files_dce_timepoints[0]  # timepoint0 as fixed image
                
                # for moving_image in files_dce_timepoints:

                #     cmd = [
                #     "./reg_aladin",
                #     "-ref", fixed_image,
                #     "-flo", moving_image,
                #     "-res", moving_image.replace(".nii.gz", "_reg.nii.gz"),
                #     "-platf", "1", 
                #     "-rigOnly"
                #     ]


                #     result = subprocess.run(
                #         cmd,
                #         stdout=subprocess.PIPE,
                #         stderr=subprocess.PIPE,
                #         text=True,
                #     )
            
            except:
                print(f"Error processing patient {patient_id}, skipping.")
                failed_patients.append(patient_id)
                continue
            
        for patient_id in failed_patients:
            # os.remove(f"/home/johannes/Data/SSD_2.0TB/GNN_pCR/data/breast_cancer/data_processed/{patient_id}/")
            os.remove(os.path.join(download_dir, f"{patient_id}"))

def _resample_crop(download_dir: str):

    for patient in tqdm(glob(f"{download_dir}/ISPY2*")):
        # print(patient) 

        dce_files = sorted(glob(f"{patient}/*DCE_timepoint*.nii.gz"))
        ftv_files = sorted(glob(f"{patient}/*Analysis*.nii.gz"))

        for i in range(len(dce_files)//3):

            seg = sitk.ReadImage(ftv_files[i], sitk.sitkUInt16)
            ftv = sitk.Cast((seg == 1), sitk.sitkUInt8)
            sitk.WriteImage(ftv, "./tmp_ftv.nii.gz")
            bounding_box = sitk.Cast((seg == 1) | (seg == 17), sitk.sitkUInt8)
            sitk.WriteImage(bounding_box, "./tmp_bounding_box.nii.gz")

            dce_tp0=tio.ScalarImage(dce_files[i*3])
            dce_tp1=tio.ScalarImage(dce_files[i*3+1])
            dce_tp2=tio.ScalarImage(dce_files[i*3+2])
            ftv=tio.LabelMap("./tmp_ftv.nii.gz")
            bounding_box=tio.LabelMap("./tmp_bounding_box.nii.gz")

            dce_tp0 = tio.ToCanonical()(dce_tp0)
            dce_tp1 = tio.ToCanonical()(dce_tp1)
            dce_tp2 = tio.ToCanonical()(dce_tp2)
            
            ftv = tio.ToCanonical()(ftv)
            bounding_box = tio.ToCanonical()(bounding_box)
            
            ftv = tio.Resample(target=dce_tp0)(ftv)
            bounding_box = tio.Resample(target=dce_tp0)(bounding_box)

            subject = tio.Subject(
                dce_tp0=dce_tp0,
                dce_tp1=dce_tp1,
                dce_tp2=dce_tp2,
                ftv=ftv,
                bounding_box=bounding_box,
            )

            transform = tio.Resample((2.0, 2.0, 2.0))
            subject_resampled = transform(subject)

            transform = tio.CropOrPad(target_shape=(64, 64, 64), mask_name='bounding_box')
            subject_cropped = transform(subject_resampled)

            transform = tio.ZNormalization()
            subject_cropped["dce_tp0"] = transform(subject_cropped["dce_tp0"])
            subject_cropped["dce_tp1"] = transform(subject_cropped["dce_tp1"])
            subject_cropped["dce_tp2"] = transform(subject_cropped["dce_tp2"])

            subject_cropped["dce_tp0"].save(dce_files[i*3].replace(".nii.gz", "_resampled_cropped.nii.gz"))
            subject_cropped["dce_tp1"].save(dce_files[i*3+1].replace(".nii.gz", "_resampled_cropped.nii.gz"))
            subject_cropped["dce_tp2"].save(dce_files[i*3+2].replace(".nii.gz", "_resampled_cropped.nii.gz"))
            subject_cropped["ftv"].save(ftv_files[i].replace(".nii.gz", "_resampled_cropped.nii.gz"))        

            os.remove("./tmp_ftv.nii.gz")
            os.remove("./tmp_bounding_box.nii.gz")

def _create_3_channel_volumes(download_dir: str):
    for patient in tqdm(glob(f"{download_dir}/ISPY2*")):
        # print(patient) 
        # break

        dce_files = sorted(glob(f"{patient}/*DCE_timepoint*resampled*.nii.gz"))
        ftv_files = sorted(glob(f"{patient}/*Analysis*resampled*.nii.gz"))

        for i in range(len(dce_files)//3):
            # print(dce_files[i*3], dce_files[i*3+1], dce_files[i*3+2], ftv_files[i])

            dce_tp0 = sitk.ReadImage(dce_files[i*3])
            dce_tp1 = sitk.ReadImage(dce_files[i*3+1])
            dce_tp2 = sitk.ReadImage(dce_files[i*3+2])
            ftv = sitk.ReadImage(ftv_files[i], sitk.sitkUInt8)

            # Create 3-channel volume
            array_tp0 = sitk.GetArrayFromImage(dce_tp0)
            array_tp1 = sitk.GetArrayFromImage(dce_tp1)
            array_tp2 = sitk.GetArrayFromImage(dce_tp2)
            array_ftv = sitk.GetArrayFromImage(ftv)

            channel_0 = array_tp1 - array_tp0
            channel_1 = array_tp2 - array_tp0
            channel_2 = array_ftv

            array_3ch = np.stack([channel_0, channel_1, channel_2], axis=0)  # Shape: (3, D, H, W)
            torch_3ch = torch.from_numpy(array_3ch).float()
            torch_3ch = torch_3ch.unsqueeze(0)  # Shape: (1, 3, D, H, W)

            patient_id = os.path.basename(dce_files[i*3]).split("_")[0]
            aquistion_time = os.path.basename(dce_files[i*3]).split("_")[1]
            dir_path = os.path.dirname(dce_files[i*3])
            filepath = os.path.join(dir_path, f"{patient_id}_{aquistion_time}.pt")

            torch.save(torch_3ch, filepath)

def _add_label_to_filename(download_dir: str, clinical_data_path: str):
    df = pd.read_excel(clinical_data_path)
    df.head()

    for file in tqdm(glob(f"{download_dir}/ISPY*/*.pt")):
        # print(file)
        # break
        patient_id = os.path.basename(file).split("-")[1]
        label = df[df["Patient_ID"] == int(patient_id)]["pCR"].values[0]
        new_file = file.replace(".pt", f"_pCR_{label}.pt")
        os.rename(file, new_file)

def _create_data_splits(download_dir: str):
    final_patients_ids_3_timepoints = []
    final_patients_ids_4_timepoints = []

    for patient_dir in glob('/home/johannes/Data/SSD_2.0TB/GNN_pCR/data/breast_cancer/data_processed/ISPY*'):
        
        patient_id = os.path.basename(patient_dir)
        files = os.listdir(patient_dir)

        if len(files) == 40:
            final_patients_ids_4_timepoints.append(patient_id)
            final_patients_ids_3_timepoints.append(patient_id)
        elif len(files) == 30:
            final_patients_ids_3_timepoints.append(patient_id)

    print(f'Number of patients with 3 timepoints: {len(final_patients_ids_3_timepoints)}')
    print(f'Number of patients with 4 timepoints: {len(final_patients_ids_4_timepoints)}')

    # Save the patient ids
    torch.save(final_patients_ids_3_timepoints, 'final_patient_ids_3_timepoints.pt')
    torch.save(final_patients_ids_4_timepoints, 'final_patient_ids_4_timepoints.pt')

    # %%
    patient_ids_3_timepoints = torch.load('final_patient_ids_3_timepoints.pt')
    patient_ids_4_timepoints = torch.load('final_patient_ids_4_timepoints.pt')
    df = pd.read_excel("/home/johannes/Data/SSD_2.0TB/GNN_pCR/data/breast_cancer/ISPY2-Imaging-Cohort-1-Clinical-Data.xlsx")

    patient_labels_3_timepoints = []
    for patient_id in patient_ids_3_timepoints:
        patient_id_int = int(patient_id.split('-')[1])
        label = df.loc[df['Patient_ID'] == patient_id_int, 'pCR'].values[0]
        patient_labels_3_timepoints.append(label)

    patient_labels_4_timepoints = []
    for patient_id in patient_ids_4_timepoints:
        patient_id_int = int(patient_id.split('-')[1])
        label = df.loc[df['Patient_ID'] == patient_id_int, 'pCR'].values[0]
        patient_labels_4_timepoints.append(label)

    assert len(patient_ids_3_timepoints) == len(patient_labels_3_timepoints)
    assert len(patient_ids_4_timepoints) == len(patient_labels_4_timepoints)

    # %%
    patients_3_timepoints = {}
    patients_4_timepoints = {}

    skf_3_timepoints = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    skf_4_timepoints = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    for fold, (train_val_index, test_index) in enumerate(skf_3_timepoints.split(patient_ids_3_timepoints, patient_labels_3_timepoints)):

        n_test = len(test_index)
        n_train = len(train_val_index) - n_test

        train_index = train_val_index[:n_train]
        val_index = train_val_index[n_train:]

        print(f"Fold_{fold}: Train size: {len(train_index)}, Val size: {len(val_index)}, Test size: {len(test_index)}")

        train_ids = [patient_ids_3_timepoints[i] for i in train_index]
        val_ids = [patient_ids_3_timepoints[i] for i in val_index]
        test_ids = [patient_ids_3_timepoints[i] for i in test_index]

        assert set(train_ids).isdisjoint(val_ids)
        assert set(train_ids).isdisjoint(test_ids)
        assert set(val_ids).isdisjoint(test_ids)
        
        patients_3_timepoints[fold] = {
            'train': train_ids,
            'val': val_ids,
            'test': test_ids
        }

    for fold, (train_val_index, test_index) in enumerate(skf_4_timepoints.split(patient_ids_4_timepoints, patient_labels_4_timepoints)):

        n_test = len(test_index)
        n_train = len(train_val_index) - n_test

        train_index = train_val_index[:n_train]
        val_index = train_val_index[n_train:]

        print(f"Fold_{fold}: Train size: {len(train_index)}, Val size: {len(val_index)}, Test size: {len(test_index)}")

        train_ids = [patient_ids_4_timepoints[i] for i in train_index]
        val_ids = [patient_ids_4_timepoints[i] for i in val_index]
        test_ids = [patient_ids_4_timepoints[i] for i in test_index]

        assert set(train_ids).isdisjoint(val_ids)
        assert set(train_ids).isdisjoint(test_ids)
        assert set(val_ids).isdisjoint(test_ids)
        
        patients_4_timepoints[fold] = {
            'train': train_ids,
            'val': val_ids,
            'test': test_ids
        }

    torch.save(patients_3_timepoints, 'data_splits_3_timepoints.pt')
    torch.save(patients_4_timepoints, 'data_splits_4_timepoints.pt')

def preprocess_data(download_dir: str = None, clinical_file_path: str = None):

    assert download_dir is not None, "Please provide a valid download directory to preprocess the data."
    assert clinical_file_path is not None, "Please provide a valid clinical data path."

    _rename_and_move_study_dirs(download_dir)
    _convert_DCEMRI_to_niigz(download_dir)
    _convert_FTV_to_niigz(download_dir)
    _get_final_patient_ids(download_dir)
    _preprocess_patients(download_dir)
    _resample_crop(download_dir)
    _create_3_channel_volumes(download_dir)    
    _add_label_to_filename(download_dir, clinical_file_path)
    # _create_data_splits(download_dir)
