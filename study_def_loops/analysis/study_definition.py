# Creates study population with no restirctions but include indicators for
# mental health and CVD where clinical monitoring is diagnosis specific
from cohortextractor import (
    StudyDefinition,
    Measure,
    patients,
)
from codelists import *

############################################
### Function 1: create separate variables for primary diagnoses/diagnoses for specified variable and codelist
############################################

def make_variable(variable_name, with_these_codes=None):
    return {
        f"{variable_name}_primary_admission": (
            patients.admitted_to_hospital(
                with_these_primary_diagnoses = with_these_codes,
                between=["index_date", "last_day_of_month(index_date)"],
                returning="binary_flag",
                return_expectations={"incidence": 0.1}
            )
        ),
        f"{variable_name}_admission": (
            patients.admitted_to_hospital(
                with_these_diagnoses = with_these_codes,
                between=["index_date", "last_day_of_month(index_date)"],
                returning="binary_flag",
                return_expectations={"incidence": 0.1}
                )
        ),
    }

############################################
### Function 2: run a loop of a list of variable names and codelists
############################################

def loop_over_variables():
    # list of variable names and corresponding codelists (NOTE: must be in the same order!)
    var_name_list = ["heart_failure", "vte", "depression", "anxiety", "smi"]
    codelist_list = [heart_failure_icd_codes, vte_icd_codes, depression_icd_codes, anxiety_icd_codes, severe_mental_illness_icd_codes]
    
    variables = {}
    for i in range(1,len(var_name_list)):
        # call make_variable function for each item in turn
        variables.update(make_variable(var_name_list[i],codelist_list[i]))
    return variables



############################################
### Create study cohort
############################################

study = StudyDefinition(
    default_expectations={
        "date": {"earliest": "1980-01-01", "latest": "today"},
        "rate": "uniform",
        "incidence": 0.05,
    },
    # Update index date to 2018-03-01 when ready to run on full dataset
    index_date="2018-03-01",
    population=patients.satisfying(
        """
        has_follow_up AND
        (age >=18 AND age <= 110) AND
        (NOT died) AND
        (sex = 'M' OR sex = 'F') AND
        (stp != 'missing') AND
        (household <=15)
        """,
        has_follow_up=patients.registered_with_one_practice_between(
            "index_date - 3 months", "index_date"
        ),
        died=patients.died_from_any_cause(
            on_or_before="index_date"
        ),
        age=patients.age_as_of(
            "index_date",
            return_expectations={
                "rate": "universal",
                "int": {"distribution": "population_ages"},
            },
        ),
        
        stp=patients.registered_practice_as_of(
            "index_date",
            returning="stp_code",
            return_expectations={
               "category": {"ratios": {"STP1": 0.3, "STP2": 0.2, "STP3": 0.5}},
            },
        ),
        household=patients.household_as_of(
            "2020-02-01",
            returning="household_size",
        ),
    ),
    sex=patients.sex(
            return_expectations={
                "rate": "universal",
                "category": {"ratios": {"M": 0.49, "F": 0.5, "U": 0.01}},
            }
        ),
    
    ####################################################
    ### Original coding without loop
    ####################################################

    # Heart failure
    heart_failure_primary_admission=patients.admitted_to_hospital( # specify variable
        with_these_primary_diagnoses=heart_failure_icd_codes, # specify primary or not; specify code list
        between=["index_date", "last_day_of_month(index_date)"],
        returning="binary_flag",
        return_expectations={"incidence": 0.1},
    ),
    
    # Heart failure
    heart_failure_admission=patients.admitted_to_hospital(
        with_these_diagnoses=heart_failure_icd_codes,
        between=["index_date", "last_day_of_month(index_date)"],
        returning="binary_flag",
        return_expectations={"incidence": 0.1},
    ),
    
    ####################################################
    ### New coding for single variable or loop
    ### ** required for these to function
    ####################################################

    ## call make_variable to specify a single variable
    **make_variable(
        variable_name="heart_failure_test",
        with_these_codes=heart_failure_icd_codes
    ),
   
    ## call loop function to generate complete variable list
    **loop_over_variables()
    
)
