import re
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).parents[1]
OUTPUT_DIR = BASE_DIR / "output"


def match_input_files(file: str) -> bool:
    """Checks if file name has format outputted by cohort extractor"""
    pattern = r'^input_20\d\d-(0[1-9]|1[012])-(0[1-9]|[12][0-9]|3[01])\.csv' 
    return True if re.match(pattern, file) else False

def get_date_input_file(file: str) -> str:
    """Gets the date in format YYYY-MM-DD from input file name string"""
    #check format
    if not match_input_files(file):
        raise Exception('Not valid input file format')
    
    else:
        date = result = re.search(r'input_(.*)\.csv', file)
        return date.group(1)

def validate_directory(dirpath):
    if not dirpath.is_dir():
        raise ValueError(f"Not a directory")

def add_ethnicity(cohort):
    """Add ethnicity using bandings from PRIMIS spec."""

    # eth2001 already indicates whether a patient is in any of bands 1-16
    cohort["ethnicity"] = cohort["ethnicity"].astype("category")
    s = cohort["ethnicity"].copy()
    s = s.cat.add_categories(6)

    # Add band 17 (Patients with any other ethnicity code)
    s.mask(s.isna() & cohort["non_eth2001_dat"].notna(), 6, inplace=True)

    # Add band 18 (Ethnicity not given - patient refused)
    s.mask(s.isna() & cohort["eth_notgiptref_dat"].notna(), 6, inplace=True)

    # Add band 19 (Ethnicity not stated)
    s.mask(s.isna() & cohort["eth_notstated_dat"].notna(), 6, inplace=True)

    # Add band 20 (Ethnicity not recorded)
    s.mask(s.isna(), 6, inplace=True)

    cohort["ethnicity"] = s.astype("int8")

def join_ethnicity(directory: str) -> None:
    """Finds 'input_ethnicity.csv' in directory and combines with each input file."""

    dirpath = Path(directory)
    validate_directory(dirpath)
    filelist = dirpath.iterdir()

    #get ethnicity input file

    ethnicity_df = pd.read_csv(dirpath / 'input_ethnicity.csv')
    
    for file in filelist:
        if match_input_files(file.name):
            df = pd.read_csv(dirpath / file.name)
            merged_df = df.merge(ethnicity_df, how='left', on='patient_id')
            
            merged_df.to_csv(dirpath / file.name, index=False)