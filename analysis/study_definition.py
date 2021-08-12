from cohortextractor import (
    StudyDefinition,
    patients,
    Measure
)

from codelists import *
from co_prescribing_variables import create_co_prescribing_variables

start_date = "2019-01-01"
end_date = "2021-07-01"


study = StudyDefinition(
    index_date = start_date,
    default_expectations={
        "date": {"earliest": start_date, "latest": end_date},
        "rate": "uniform",
        "incidence": 0.5,
    },
    population=patients.satisfying(
       """
       registered
       """
    ),

    registered = patients.registered_as_of("index_date"),

    practice=patients.registered_practice_as_of(
        "index_date",
        returning="pseudo_id",
        return_expectations={"int" : {"distribution": "normal", "mean": 25, "stddev": 5}, "incidence" : 0.5}
    ),

    age = patients.age_as_of(
        "index_date",
        return_expectations={
            "rate": "universal",
            "int": {"distribution": "population_ages"},
        },
    ),

    ###
    # CO-PRESCRIBING-VARS
    ###

    # Used in indicator E
    **create_co_prescribing_variables(anticoagulant_codelist, antiplatelet_including_aspirin_codelist, "anticoagulant", "antiplatelet_including_aspirin"),

     # Used in indicator F
    **create_co_prescribing_variables(aspirin_codelist, antiplatelet_excluding_aspirin_codelist, "aspirin", "antiplatelet_excluding_aspirin"),
    

    ###
    # GI BLEED INDICATORS
    # A - 65 or over, no GI protect, NSAID audit (GI_P3A)
    ###

    oral_nsaid=patients.with_these_medications(
        codelist=oral_nsaid_codelist,
        find_last_match_in_period=True,
        returning="binary_flag",
        include_date_of_match=True,
        date_format="YYYY-MM-DD",
        between=["index_date - 3 months", "index_date"],
    ),

    # gastroprotective proton pump inhibitor
    ppi = patients.with_these_medications(
        codelist = ulcer_healing_drugs_codelist,
        find_last_match_in_period=True,
        returning="binary_flag",
        include_date_of_match=True,
        date_format="YYYY-MM-DD",
        between=["index_date - 3 months", "index_date"],
    ),

    indicator_a_denominator = patients.satisfying(
        """
        (NOT ppi) AND
        (age >=65 AND age <=120)
        """,
    ),

    indicator_a_numerator = patients.satisfying(
        """
        (NOT ppi) AND
        (age >=65 AND age <=120) AND
        oral_nsaid
        """,
    ),

    ###
    # GI BLEED INDICATORS
    # B - Peptic ulcer/GI bleed, no PPI protect, NSAID audit (GI_P3B)
    ###

    peptic_ulcer = patients.with_these_clinical_events(
        codelist=peptic_ulcer_codelist,
        find_last_match_in_period=True,
        returning="binary_flag",
        include_date_of_match=True,
        date_format="YYYY-MM-DD",
        on_or_before="index_date - 3 months",
    ),

    gi_bleed = patients.with_these_clinical_events(
        codelist=gi_bleed_codelist,
        find_last_match_in_period=True,
        returning="binary_flag",
        include_date_of_match=True,
        date_format="YYYY-MM-DD",
        on_or_before="index_date - 3 months",
    ),
  
    indicator_b_denominator=patients.satisfying(
        """
        (NOT ppi) AND
        (gi_bleed OR peptic_ulcer)
        """,
    ),

    indicator_b_numerator=patients.satisfying(
        """
        (NOT ppi) AND
        (gi_bleed OR peptic_ulcer) AND
        oral_nsaid
        """,
    ),    

    ###
    # GI BLEED INDICATORS
    # C - Peptic ulcer/GI bleed, no PPI protect, NSAID audit (GI_P3B)
    ###

    #peptic_ulcer from B
    #gi_bleed from B
    #ppi from A
    #antiplatelet_excluding_aspirin from co-prescribing vars
    #aspirin from co-prescribing vars


    indicator_c_denominator = patients.satisfying(

        """
        (NOT ppi) AND
        (gi_bleed OR peptic_ulcer)
        """,
    ),

    indicator_c_numerator = patients.satisfying(
        """
        (NOT ppi) AND
        (gi_bleed OR peptic_ulcer) AND
        (antiplatelet_excluding_aspirin OR aspirin)
        """,
    ),
      
    ###
    # GI BLEED INDICATORS
    # D – Warfarin/NOACS and NSAID audit (GI_P3D)
    ###

    #anticoagulant from co-prescribing variables

    indicator_d_denominator=patients.satisfying(
        """
    (anticoagulant)
    """,
    ),

    indicator_d_numerator=patients.satisfying(
        """
        (anticoagulant) AND
        oral_nsaid
        """,
    ),


    ###
    # GI BLEED INDICATORS
    # E – Anticoagulation & Antiplatelet & No GI Protection Audit (GI_P3E)
    ###

    #ppi from A
    #anticoagulant from co-prescribing variables


    indicator_e_denominator = patients.satisfying(
        """
        anticoagulant AND
        (NOT ppi)
        """
    ),


    ###
    # GI BLEED INDICATORS
    # F – Aspirin, antiplatelet and no GI protection audit (GI_P3F)
    ###

    #aspirin from C
    #antiplatelet_excluding_aspirin from C
    #ppi from A


    indicator_f_denominator = patients.satisfying(
        """
        aspirin AND
        (NOT ppi)
        """
    ),

    
    ###
    # OTHER PRESCRIBING INDICATORS
    # G - Asthma and non-selective betablockers audit (AS_P3G)
    ###

    asthma=patients.with_these_clinical_events(
        codelist=asthma_codelist,
        find_last_match_in_period=True,
        returning="binary_flag",
        include_date_of_match=True,
        date_format="YYYY-MM-DD",
        on_or_before="index_date - 3 months",
    ),

    asthma_resolved=patients.with_these_clinical_events(
        codelist=asthma_resolved_codelist,
        find_last_match_in_period=True,
        returning="binary_flag",
        include_date_of_match=True,
        date_format="YYYY-MM-DD",
        on_or_before="index_date",
    ),

    non_selective_bb = patients.with_these_medications(
        codelist = non_selective_bb_codelist, 
        find_last_match_in_period=True,
        returning="binary_flag",
        include_date_of_match=True,
        date_format="YYYY-MM-DD",
        between=["index_date - 3 months", "index_date"],
    ),

    indicator_g_denominator = patients.satisfying(
        """
        asthma AND 
        (NOT asthma_resolved)
        """,
    ),

    indicator_g_numerator = patients.satisfying(
        """
        asthma AND 
        (NOT asthma_resolved) AND
        non_selective_bb
        """,
    ),


    ###
    # OTHER PRESCRIBING INDICATORS
    # I - Heart failure and NSAID audit (HF_P3I)
    ###
    
    heart_failure=patients.with_these_clinical_events(
        codelist=heart_failure_codelist,
        find_first_match_in_period=True,
        returning="binary_flag",
        include_date_of_match=True,
        date_format="YYYY-MM-DD",
        on_or_before="index_date - 3 months",
    ),


    indicator_i_denominator = patients.satisfying(
        """
        heart_failure
        """
    ),

    indicator_i_numerator = patients.satisfying(
        """
        heart_failure AND oral_nsaid
        """
    ),

    ###
    # OTHER PRESCRIBING INDICATORS
    # K - Chronic Renal Impairment & NSAID Audit (KI_P3K)
    ###

    #oral_nsaid from A

    egfr=patients.with_these_clinical_events(
        codelist=egfr_codelist,
        find_last_match_in_period=True,
        returning="numeric_value",
        include_date_of_match=True,
        date_format="YYYY-MM-DD",
        between=["index_date - 3 months", "index_date"],
        return_expectations={
            "float": {"distribution": "normal", "mean": 45.0, "stddev": 20},
            "incidence": 0.5,
        },
    ),

    egfr_less_than_45 = patients.categorised_as(
        {
            "0": "DEFAULT",
            "1": """ 0 <= egfr < 45"""
        },
        return_expectations = {
            "rate": "universal",
            "category": {
                        "ratios": {
                            "0": 0.94,
                            "1": 0.06,
                                }
                        },
            },
    ),

    indicator_k_denominator = patients.satisfying(
        """
        egfr_less_than_45
        """,
    ),

    indicator_k_numerator = patients.satisfying(
        """
        egfr_less_than_45 AND
        oral_nsaid
        """,
    ),

    ###
    # MONITORING COMPOSITE INDICATOR
    # AC - ACEI Audit (MO_P13)
    ####

    acei = patients.with_these_medications(
        codelist = acei_codelist, 
        find_first_match_in_period=True,
        returning="binary_flag",
        include_date_of_match=True,
        date_format="YYYY-MM-DD",
        on_or_before="index_date - 15 months",
    ),

    loop_diuretic = patients.with_these_medications(
        codelist = loop_diuretics_codelist, 
        find_first_match_in_period=True,
        returning="binary_flag",
        include_date_of_match=True,
        date_format="YYYY-MM-DD",
        on_or_before="index_date - 15 months",
    ),

    acei_recent = patients.with_these_medications(
        codelist = acei_codelist, 
        find_last_match_in_period=True,
        returning="binary_flag",
        include_date_of_match=True,
        date_format="YYYY-MM-DD",
        between=["index_date - 6 months", "index_date"],
    ),

    loop_diuretic_recent = patients.with_these_medications(
        codelist = loop_diuretics_codelist, 
        find_last_match_in_period=True,
        returning="binary_flag",
        include_date_of_match=True,
        date_format="YYYY-MM-DD",
        between=["index_date - 6 months", "index_date"],
    ),

    renal_function_test = patients.with_these_clinical_events(
        codelist = renal_function_codelist,
        find_last_match_in_period = True,
        returning="binary_flag",
        include_date_of_match=True,
        date_format="YYYY-MM-DD",
        between = ["index_date - 15 months", "index_date"],
    ),

    electrolytes_test = patients.with_these_clinical_events(
        codelist = electrolytes_test_codelist,
        find_last_match_in_period = True,
        returning="binary_flag",
        include_date_of_match=True,
        date_format="YYYY-MM-DD",
        between = ["index_date - 15 months", "index_date"],
    ),

    indicator_ac_denominator = patients.satisfying(
        """
        (age >=75 AND age <=120) AND
        (acei AND acei_recent) OR
        (loop_diuretic AND loop_diuretic_recent)
        """,
    ),

    indicator_ac_numerator = patients.satisfying(
        """
        (age >=75 AND age <=120) AND
        ((loop_diuretic AND loop_diuretic_recent) OR (acei AND acei_recent))AND
        ((NOT renal_function_test) OR (NOT electrolytes_test))
        """,
    ),

    ###
    # MONITORING COMPOSITE INDICATOR
    # ME - Methotrexate audit (MO_P15)
    ####

    methotrexate_6_3_months = patients.with_these_medications(
        codelist = methotrexate_codelist, 
        find_last_match_in_period=True,
        returning="binary_flag",
        include_date_of_match=True,
        date_format="YYYY-MM-DD",
        between=["index_date - 6 months", "index_date - 3 months"],
    ),

    methotrexate_3_months = patients.with_these_medications(
        codelist = methotrexate_codelist, 
        find_last_match_in_period=True,
        returning="binary_flag",
        include_date_of_match=True,
        date_format="YYYY-MM-DD",
        between=["index_date - 3 months", "index_date"],
    ),

    full_blood_count = patients.with_these_clinical_events(
        codelist = full_blood_count_codelist,
        find_last_match_in_period = True,
        returning="binary_flag",
        include_date_of_match=True,
        date_format="YYYY-MM-DD",
        between = ["index_date - 3 months", "index_date"],
    ),

    liver_function_test = patients.with_these_clinical_events(
        codelist = liver_function_test_codelist,
        find_last_match_in_period = True,
        returning="binary_flag",
        include_date_of_match=True,
        date_format="YYYY-MM-DD",
        between = ["index_date - 3 months", "index_date"],
    ),

    indicator_me_denominator = patients.satisfying(
        """
        methotrexate_6_3_months AND
        methotrexate_3_months
        """,
    ),

    indicator_me_no_fbc_numerator = patients.satisfying(
        """
        methotrexate_6_3_months AND
        methotrexate_3_months AND
        (NOT full_blood_count)
        """,
    ),

    indicator_me_no_lft_numerator = patients.satisfying(
        """
        methotrexate_6_3_months AND
        methotrexate_3_months AND
        (NOT liver_function_test)
        """,
    ),

    ###
    # MONITORING COMPOSITE INDICATOR
    # LI - Lithium audit (MO_P17)
    ####

    lithium_6_3_months = patients.with_these_medications(
        codelist = lithium_codelist, 
        find_last_match_in_period=True,
        returning="binary_flag",
        include_date_of_match=True,
        date_format="YYYY-MM-DD",
        between=["index_date - 6 months", "index_date - 3 months"],
    ),

    lithium_3_months = patients.with_these_medications(
        codelist = lithium_codelist, 
        find_last_match_in_period=True,
        returning="binary_flag",
        include_date_of_match=True,
        date_format="YYYY-MM-DD",
        between=["index_date - 3 months", "index_date"],
    ),

    lithium_level_3_months = patients.with_these_medications(
        codelist = lithium_level_codelist, 
        find_last_match_in_period=True,
        returning="binary_flag",
        include_date_of_match=True,
        date_format="YYYY-MM-DD",
        between=["index_date - 3 months", "index_date"],
    ),


    indicator_li_denominator = patients.satisfying(
        """
        lithium_6_3_months AND
        lithium_3_months
        """,
    ),

    indicator_li_numerator = patients.satisfying(
        """
        lithium_6_3_months AND
        lithium_3_months AND 
        (NOT lithium_level_3_months)
        """,
    ),

    ###
    # MONITORING COMPOSITE INDICATOR
    # AM - Amiodarone audit (MO_P18)
    ####
    
    amiodarone_12_6_months = patients.with_these_medications(
        codelist = amiodarone_codelist, 
        find_last_match_in_period=True,
        returning="binary_flag",
        include_date_of_match=True,
        date_format="YYYY-MM-DD",
        between=["index_date - 12 months", "index_date - 6 months"],
    ),

    amiodarone_6_months = patients.with_these_medications(
        codelist = amiodarone_codelist, 
        find_last_match_in_period=True,
        returning="binary_flag",
        include_date_of_match=True,
        date_format="YYYY-MM-DD",
        between=["index_date - 6 months", "index_date"],
    ),

    thyroid_function_test = patients.with_these_clinical_events(
        codelist = thyroid_function_test_codelist, 
        find_last_match_in_period=True,
        returning="binary_flag",
        include_date_of_match=True,
        date_format="YYYY-MM-DD",
        between=["index_date - 6 months", "index_date"],
    ),

    indicator_am_denominator = patients.satisfying(
        """
        amiodarone_12_6_months AND
        amiodarone_6_months
        """,
    ),

    indicator_am_numerator = patients.satisfying(
        """
        amiodarone_12_6_months AND
        amiodarone_6_months AND
        (NOT thyroid_function_test)
        """,
    ),

    ###
    # GI BLEED COMPOSITE INDICATORS
    ###

    gi_bleed_composite_denominator = patients.satisfying(
        """
        indicator_a_denominator OR
        indicator_b_denominator OR
        indicator_c_denominator OR
        indicator_d_denominator OR
        indicator_e_denominator OR
        indicator_f_denominator
        """
    ),

    ###
    # OTHER PRESCRIBING COMPOSITE INDICATOR
    ###

    other_prescribing_composite_denominator = patients.satisfying(
        """
        indicator_g_denominator OR
        indicator_i_denominator OR
        indicator_k_denominator
        """,
    ),

    ###
    #  MONITORING COMPOSITE INDICATOR
    ###

    monitoring_composite_denominator = patients.satisfying(
        """
        indicator_ac_denominator OR
        indicator_me_denominator OR
        indicator_li_denominator OR
        indicator_am_denominator
        """
    ),

    ###
    # ALL COMPOSITE INDICATOR
    #

    all_composite_denominator = patients.satisfying(
        """
        gi_bleed_composite_denominator OR
        other_prescribing_composite_denominator OR
        monitoring_composite_denominator
        """
    )
)

measures = [
]

indicators_list = ["a", "b", "c", "d", "e", "f", "g", "i", "k", "ac", "me_no_fbc", "me_no_lft", "li", "am"]

for indicator in indicators_list:

    if indicator in ["me_no_fbc", "me_no_lft"]:
        m = Measure(
        id=f"indicator_{indicator}_rate",
        numerator=f"indicator_{indicator}_numerator",
        denominator=f"indicator_me_denominator",
        group_by=["practice"]
    )
    else:
        m = Measure(
            id=f"indicator_{indicator}_rate",
            numerator=f"indicator_{indicator}_numerator",
            denominator=f"indicator_{indicator}_denominator",
            group_by=["practice"]
        )

    measures.append(m)