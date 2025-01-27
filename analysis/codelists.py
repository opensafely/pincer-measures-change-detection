from cohortextractor import (
    codelist_from_csv,
)

# Ethnicity codes
eth2001 = codelist_from_csv(
    "codelists/primis-covid19-vacc-uptake-eth2001.csv",
    system="snomed",
    column="code",
    category_column="grouping_6_id",
)

# Any other ethnicity code
non_eth2001 = codelist_from_csv(
    "codelists/primis-covid19-vacc-uptake-non_eth2001.csv",
    system="snomed",
    column="code",
)

# Ethnicity not given - patient refused
eth_notgiptref = codelist_from_csv(
    "codelists/primis-covid19-vacc-uptake-eth_notgiptref.csv",
    system="snomed",
    column="code",
)

# Ethnicity not stated
eth_notstated = codelist_from_csv(
    "codelists/primis-covid19-vacc-uptake-eth_notstated.csv",
    system="snomed",
    column="code",
)

# Ethnicity no record
eth_norecord = codelist_from_csv(
    "codelists/primis-covid19-vacc-uptake-eth_norecord.csv",
    system="snomed",
    column="code",
)

# Used in AC
acei_codelist = codelist_from_csv(
    "codelists/pincer-acei.csv",
    system="snomed",
    column="id",
)

# Used in AC
loop_diuretics_codelist = codelist_from_csv(
    "codelists/pincer-diur.csv",
    system="snomed",
    column="id",
)

# Used in AC
renal_function_codelist = codelist_from_csv(
    "codelists/pincer-renal.csv",
    system="snomed",
    column="code",
)

# Used in AC
electrolytes_test_codelist = codelist_from_csv(
    "codelists/pincer-electro.csv",
    system="snomed",
    column="code",
)

# Used in ME
methotrexate_codelist = codelist_from_csv(
    "codelists/pincer-met.csv",
    system="snomed",
    column="id",
)

# Used in ME
full_blood_count_codelist = codelist_from_csv(
    "codelists/pincer-fbc.csv",
    system="snomed",
    column="code",
)

# Used in ME
liver_function_test_codelist = codelist_from_csv(
    "codelists/pincer-lft.csv",
    system="snomed",
    column="code",
)

# Used in LI
lithium_codelist = codelist_from_csv(
    "codelists/pincer-lith.csv",
    system="snomed",
    column="id",
)

# Used in LI
lithium_level_codelist = codelist_from_csv(
    "codelists/pincer-lith_lev.csv",
    system="snomed",
    column="code",
)

# Used in AM
amiodarone_codelist = codelist_from_csv(
    "codelists/pincer-amio.csv",
    system="snomed",
    column="id",
)

# Used in AM
thyroid_function_test_codelist = codelist_from_csv(
    "codelists/pincer-tft.csv",
    system="snomed",
    column="code",
)

# Used in A, B, C, E, F
ulcer_healing_drugs_codelist = codelist_from_csv(
    "codelists/pincer-ppi.csv",
    system="snomed",
    column="id",
)

# Used in A, B, D, I, K
oral_nsaid_codelist = codelist_from_csv(
    "codelists/pincer-nsaid.csv",
    system="snomed",
    column="id",
)

# Used in B, C
peptic_ulcer_codelist = codelist_from_csv(
    "codelists/pincer-pep.csv",
    system="snomed",
    column="code",
)

# Used in B, C
gi_bleed_codelist = codelist_from_csv(
    "codelists/pincer-gi_bleed.csv",
    system="snomed",
    column="code",
)

# Used in C
antiplatelet_excluding_aspirin_codelist = codelist_from_csv(
    "codelists/pincer-non_asp_antiplate.csv",
    system="snomed",
    column="id",
)

# Used in C, F
aspirin_codelist = codelist_from_csv(
    "codelists/pincer-aspirin.csv",
    system="snomed",
    column="id",
)

# Used in D, E
anticoagulant_codelist = codelist_from_csv(
    "codelists/pincer-anticoag.csv",
    system="snomed",
    column="id",
)

# Used in G
asthma_codelist = codelist_from_csv(
    "codelists/pincer-ast.csv",
    system="snomed",
    column="code",
)

# Used in G
asthma_resolved_codelist = codelist_from_csv(
    "codelists/pincer-ast_res.csv",
    system="snomed",
    column="code",
)

# Used in G
non_selective_bb_codelist = codelist_from_csv(
    "codelists/pincer-nsbb.csv",
    system="snomed",
    column="id",
)

# Used in I
heart_failure_codelist = codelist_from_csv(
    "codelists/pincer-hf.csv",
    system="snomed",
    column="code",
)

# Used in K
egfr_codelist = codelist_from_csv(
    "codelists/pincer-egfr.csv",
    system="snomed",
    column="code",
)

# Used in E, F
antiplatelet_including_aspirin_codelist = codelist_from_csv(
    "codelists/pincer-antiplat.csv",
    system="snomed",
    column="id",
)
