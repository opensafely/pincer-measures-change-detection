from cohortextractor import (
    StudyDefinition,
    patients,
    Measure
)

from codelists import *

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

)


    

measures = [
    Measure(
        id="dummmy",
        numerator="registered",
        denominator="population",
        group_by=["practice"]
    ),


]

