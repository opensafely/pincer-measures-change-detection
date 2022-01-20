import pandas as pd
import numpy as np
from utilities import (
    OUTPUT_DIR,
    match_input_files_filtered,
    get_date_input_file_filtered,
    get_practice_characteristics,
)

practice_characteristics_df = pd.DataFrame(
    columns=[
        "date",
        "practice",
        "list_size",
        "region",
        "rural_urban",
        "prop_over_65",
        "index_of_multiple_deprivation",
    ]
)

for file in OUTPUT_DIR.iterdir():

    if match_input_files_filtered(file.name):

        df = pd.read_feather(OUTPUT_DIR / file.name)
        date = get_date_input_file_filtered(file.name)

        practice_characteristics = get_practice_characteristics(df, date)

        practice_characteristics_df = practice_characteristics_df.append(
            practice_characteristics
        )


practice_characteristics_df.to_csv(OUTPUT_DIR / "practice_characteristics.csv")
