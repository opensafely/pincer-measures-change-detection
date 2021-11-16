import pandas as pd
import numpy as np
import json
from utilities import *
from config import indicators_list, backend

#these are not generated in the main generate measures action
additional_indicators = ["e","f"]
indicators_list.extend(additional_indicators)

practice_list = []
practice_list_event = []
patient_counts_dict = {"numerator": {}, "denominator": {}}
patient_dict = {"numerator": {}, "denominator": {}}
num_events_total = 0

for file in OUTPUT_DIR.iterdir():
    
    if match_input_files(file.name):

        df = pd.read_feather(OUTPUT_DIR / file.name)
        date = get_date_input_file(file.name)
        practice_list.extend(np.unique(df['practice']))


        for indicator in indicators_list:
            
            if indicator in ["e", "f"]:
                df_e_f = pd.read_feather(OUTPUT_DIR / f'indicator_e_f_{date}.feather')
                
                df_subset_numerator = df_e_f[df_e_f[f'indicator_{indicator}_numerator']==1]
                
           
            else:
                df_subset_numerator = df[df[f'indicator_{indicator}_numerator']==1]
                # get unique patients
            
            #keep running count of total events
            num_events_total += df_subset_numerator[f'indicator_{indicator}_numerator'].sum()


            # the same denominator is used for both mtx measures
            if indicator in ["me_no_fbc", "me_no_lft"]:
                df_subset_denominator = df[df[f'indicator_me_denominator']==1]
            else:
                df_subset_denominator = df[df[f'indicator_{indicator}_denominator']==1]
            
            # get all practices that experience an event
            practice_list_event.extend(np.unique(df_subset_numerator['practice']))

            patients_numerator = list(df_subset_numerator['patient_id'])
            patients_denominator = list(df_subset_denominator['patient_id'])

            if indicator not in patient_dict["numerator"]:
                #create key
                patient_dict["numerator"][indicator] = patients_numerator

            else:
                patient_dict["numerator"][indicator].extend(patients_numerator)


            if indicator not in patient_dict["denominator"]:
                #create key
                patient_dict["denominator"][indicator] = patients_denominator

            else:
                patient_dict["denominator"][indicator].extend(patients_denominator)

        
num_practices = int(len(np.unique(practice_list)))
num_practices_event = int(len(np.unique(practice_list_event)))


with open(f'output/practice_count_{backend}.json', 'w') as f:
    json.dump({"num_practices": num_practices, "num_practices_event": num_practices_event}, f)


unique_patients_total = []
unique_patients_total_denominator = []

for (key, value) in patient_dict["numerator"].items():
    #get unique patients
    unique_patients_numerator = len(np.unique(patient_dict["numerator"][key]))
    unique_patients_total.extend(np.unique(patient_dict["numerator"][key]))

    #add to dictionary as num(mil)
    patient_counts_dict["numerator"][key] = (unique_patients_numerator)

for (key, value) in patient_dict["denominator"].items():
    #get unique patients
    unique_patients_denominator = len(np.unique(patient_dict["denominator"][key]))
    unique_patients_total_denominator.extend(np.unique(patient_dict["denominator"][key]))

    #add to dictionary as num(mil)
    patient_counts_dict["denominator"][key] = (unique_patients_denominator)


with open(f'output/patient_count_{backend}.json', 'w') as f:
    json.dump({"num_patients": patient_counts_dict}, f)


counts_dict = {}

for indicator in indicators_list:
    counts_dict[indicator] = {}
    df = pd.read_csv(OUTPUT_DIR / f'measure_indicator_{indicator}_rate.csv')
    num_practices, percentage_practices = get_percentage_practices(df)
    num_events = get_number_events(df, indicator)
    num_patients_numerator = get_number_patients(indicator, "numerator")
    num_patients_denominator = get_number_patients(indicator, "denominator")

    counts_dict[indicator]['events'] = num_events
    counts_dict[indicator]['patients_numerator'] = num_patients_numerator
    counts_dict[indicator]['patients_denominator'] = num_patients_denominator
    counts_dict[indicator]['num_practices'] = num_practices
    counts_dict[indicator]['percent_practice'] = percentage_practices

counts_dict["total_patients"] = len(np.unique(unique_patients_total))
counts_dict["total_patients_denominator"] = len(np.unique(unique_patients_total_denominator))
counts_dict["total_events"] = float(num_events_total)

with open(f'output/indicator_summary_statistics_{backend}.json', 'w') as f:
    json.dump({"summary": counts_dict}, f) 
    