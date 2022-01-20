library(dplyr)
library(magrittr)
library(glue)
library(lubridate)
library(readr)
library(stringr)
library(ggplot2)

### <%> pwd
### To run on the command line:
### <%> Rscript analysis/ISPO_get-sim-data-info.R output "measure_indicator_(.*)_rate.csv" output/indicator_saturation
### /Users/lisahopcroft/Work/Projects/PINCER/pincer-measures-change-detection

##### Retrive arguments from Python command
arguments <- commandArgs(trailingOnly = TRUE)

### For testing
# arguments[1] = "output"
# arguments[2] = "measure_indicator_(.*)_rate.csv"
# arguments[3] = "output/indicator_saturation/simulated-data"

input_dir  = arguments[1]
output_dir = arguments[2]

input_file = "measure_indicator_(.*)_rate.csv"

measure_data = tibble()

for ( f in dir( input_dir, pattern=input_file ) ) {
  cat( sprintf("Reading input file: %s/%s\n", input_dir, f) )

  if ( ! ( f %>% str_detect("alternative") ) ) {
    this_measure = (f %>% str_match( input_file ))[,2]

    d_in = read_csv( glue("{input_dir}/{f}") ) %>% 
      mutate( date = as.Date( date ) ) %>%
      mutate( value = as.numeric(value) ) %>%
      mutate( indicator = this_measure ) %>%
      select( indicator, practice, value, date )

    measure_data = measure_data %>% bind_rows(d_in)
  } 
}

measure_data = measure_data %>% 
  mutate( q = lubridate::quarter( date ) )  %>% 
  mutate( year = format(date, format="%Y") )  %>% 
  mutate( q_date = glue("Q{q} {year}"))  %>% 
  mutate( value = replace(value, is.infinite(value), NA) ) %>%
  select( -q )

measure_monthly_summary = measure_data %>% 
  group_by( indicator, date ) %>% 
  summarise(  min = min( value, na.rm = TRUE ),
              max = max( value, na.rm = TRUE ),
              mean = mean( value, na.rm = TRUE ),
              median = median( value, na.rm = TRUE ),
              n_missing = sum(is.na(value)),
              n_total = n() )

measure_quarterly_summary = measure_data %>% 
  group_by( indicator, q_date ) %>% 
  summarise(  min = min( value, na.rm = TRUE ),
              max = max( value, na.rm = TRUE ),
              mean = mean( value, na.rm = TRUE ),
              median = median( value, na.rm = TRUE ),
              sd = sd( value, na.rm = TRUE ),
              n_missing = sum(is.na(value)),
              n_total = n() )


if ( !dir.exists( output_dir ) ) {
  cat(sprintf("Creating directory: %s", output_dir))
  dir.create(output_dir, showWarnings = FALSE)
}

write.csv(measure_monthly_summary  , file=glue("{output_dir}/ISPO_simdata_monthly.csv"  ))
write.csv(measure_quarterly_summary, file=glue("{output_dir}/ISPO_simdata_quarterly.csv"))
