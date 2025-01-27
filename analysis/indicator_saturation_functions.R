library(optparse , quietly=T, warn.conflicts = FALSE)
library(glue     , quietly=T, warn.conflicts = FALSE)
library(parallel , quietly=T, warn.conflicts = FALSE)
library(magrittr , quietly=T, warn.conflicts = FALSE)
library(stringr  , quietly=T, warn.conflicts = FALSE)
library(readr    , quietly=T, warn.conflicts = FALSE)
library(dplyr    , quietly=T, warn.conflicts = FALSE)
library(tidyr    , quietly=T, warn.conflicts = FALSE)
library(tibble   , quietly=T, warn.conflicts = FALSE)
library(purrr    , quietly=T, warn.conflicts = FALSE)
library(lubridate, quietly=T, warn.conflicts = FALSE)

setClass("ChangeDetection",
         representation(
             name = 'character',
             verbose = 'logical',
             sample='logical',
             measure='logical',
             custom_measure='logical',
             numcores = 'numeric',
             code_variable = 'character',
             numerator_variable = 'character',
             denominator_variable = 'character',
             date_variable = 'character',
             date_format = "character",
             indir = 'character',
             outdir = 'character',
             direction='character',
             use_cache='logical',
             csv_name='character',
             overwrite='logical',
             draw_figures='logical',
             bq_folder='character',
             expected_columns = 'list',
             working_dir = 'character',
             code_tag = 'character',
             min_NA_proportion = 'numeric',
             r_command = 'character',
             reverse = 'logical',
             change_detection_location = 'character',
             change_detection_script = 'character',
             results_extract_location = 'character',
             results_extract_script = 'character',
             test_number = 'numeric'
         ),
         prototype(name = NA_character_,
                   verbose = FALSE,
                   sample = FALSE,
                   measure = FALSE,
                   custom_measure=FALSE,
                   numcores = detectCores()-1,
                   code_variable = 'code',
                   numerator_variable = NA_character_,
                   denominator_variable = NA_character_,
                   date_variable = 'month',
                   date_format = "%Y-%m-%d",
                   indir = getwd(),
                   outdir = 'output',
                   direction='both',
                   use_cache=TRUE,
                   csv_name='bq_cache.csv',
                   overwrite=FALSE,
                   draw_figures=FALSE,
                   bq_folder='measures',
                   expected_columns=list(),
                   working_dir = NA_character_,
                   code_tag = 'ratio_quantity.',
                   min_NA_proportion = 0.5,
                   r_command = 'Rscript',
                   reverse = FALSE,
                   change_detection_location = glue("{getwd()}/analysis/change_detection"),
                   change_detection_script = 'change_detection.R',
                   results_extract_location = glue("{getwd()}/analysis/change_detection"),
                   results_extract_script = 'results_extract.R',
                   test_number = NA_integer_ )
         )

ChangeDetection <- function(...) {
    a = new("ChangeDetection", ...)

    a@expected_columns = list(
        code = a@code_variable,
        month = a@date_variable,
        numerator = a@numerator_variable,
        denominator = a@denominator_variable
    )

    return( a )
}


create_test_cd = function() {
    cd = ChangeDetection(
        name = glue('indicator_saturation_a'),
        code_variable = "practice",
        numerator_variable = "indicator_a_numerator",
        denominator_variable = "indicator_a_denominator",
        date_variable = "date",
        date_format = unlist("%Y-%m-%d"),
        indir = "../output",
        outdir = "../output/indicator_saturation/test",
        direction = "both",
        overwrite = TRUE,
        draw_figures = TRUE,
        verbose = TRUE,
        csv_name = "measure_indicator_a_rate.csv",
        numcores = 7
    )
    
    return( cd )
}


report_info = function(cd, m) {
    if ( cd@verbose )  cat( sprintf( "[INFO::%s] %s\n", cd@name, m ) )
}

report_error = function(cd, m) {
    tag = ifelse( is.na(cd@name), "", sprintf("::%s",cd@name) )
    return( glue( "[ERROR{tag}] {m}\n" ) )
}

get_working_dir = function(cd) {
    folder_name = cd@name %>% str_replace( '%', '' )
    return( glue("{cd@outdir}/{folder_name}") )
}

create_dirs = function(cd, wd) {
    dir.create(wd, showWarnings = FALSE)
    dir.create(glue("{wd}/figures"), showWarnings = FALSE)
    report_info( cd, glue("creating working directory [{wd}]") )
} 

identify_missing_column_names = function(required_fields,df) {
    return( setdiff( required_fields, colnames(df) ) %>% unlist )
}

amend_column_names = function(cd,df) {
    return( df %>% rename( !!!syms(cd@expected_columns) ) )
}

date_to_epoch = function( x=today() ) {
    return( difftime( x,ymd("1970-01-01"),unit="secs") %>% as.numeric )
}

shape_dataframe = function(cd) {
    input_file = glue( "{cd@indir}/{cd@csv_name}" ) 
    input_data = read_csv( input_file, col_types = cols() )

    ### Check that all the expected columns exist in the data
    missing_columns = identify_missing_column_names( cd@expected_columns, input_data )
    if ( length(missing_columns)>0 ) {
        stop( report_error( cd, glue( "Expected column missing: '{missing_columns}'" ) ) )
    }

    ### Amend column names as required to produce expected format
    input_data = amend_column_names( cd, input_data )

    ### Check that the date is in the expected format
    input_data = input_data %>% mutate( month = as.Date(as.character(month),format=cd@date_format) )
    if ( any( is.na(input_data %>% pull(month)) ) ) {
        stop( report_error( cd, c( glue("Field '{cd@date_variable}' is not of the format '{cd@date_format}'"),
                                   glue("Try using the -Y flag to specify the date format used in the input file") ) )
        )
    }
    input_data = input_data %>% mutate( month = as.Date(month, format="%Y-%m-%d"))

    ### Retain only those data that we're expecting
    input_data = input_data %>% select( !!!syms(cd@expected_columns %>% names) )
    
    ### Calculation of new variables
    input_data = input_data %>% arrange( code, month ) %>% 
        ### Calculate the ratio
        mutate( ratio = numerator/denominator ) %>% 
        ### Modify the 'code' variable as expected
        mutate( code = glue({"{cd@code_tag}{code}"})) %>% 
        ### Remove the numerator and denominator columns
        select( -numerator, -denominator ) %>% 
        ### Replace values of +/-infinity to NA
        mutate( ratio = ifelse(is.infinite(ratio), NA, ratio ) )
    
    input_data = input_data  %>% 
        ### Convert to wide format
        pivot_wider( names_from = "code", values_from = "ratio" ) %>%
        ### Add a code variable and reorder for ease of reading
        mutate( code = 1:n() ) %>%
        select( code, month, everything() ) 
    
    ### Python script seems to remove the bottom 5 rows - but have left
    ### this out here

    ### Drop columns with identical values
    ratio_variability = input_data %>% ungroup() %>% select( -month, -code ) %>%
        map( ~sd(.,na.rm=T) )
    
    columns_to_keep = ratio_variability %>%
        discard( ~is.na(.) ) %>%
        discard( . == 0 ) %>% 
        names
    
    columns_to_drop = setdiff( ratio_variability %>% names, columns_to_keep)
    
    report_info( cd, glue( "Removing data for item \\
                           '{columns_to_drop %>% str_remove(cd@code_tag)}' \\
                           due to lack of variability data" ))
    
    input_data = input_data %>%
        select( code, month, !!!syms(columns_to_keep) )
    
    ### Drop columns with high proportion of NAs
    NA_proportion = input_data %>% ungroup() %>% select( -month, -code ) %>%
        map(~sum(is.na(.))) 
    
    NA_threshold = cd@min_NA_proportion * nrow(input_data)
    columns_to_keep = NA_proportion %>%
        discard( . > NA_threshold ) %>%
        names
    
    columns_to_drop = setdiff( NA_proportion %>% names, columns_to_keep)
    
    report_info( cd, glue( "Removing data for item \\
                           '{columns_to_drop %>% str_remove(cd@code_tag)}' \\
                           due to >{cd@min_NA_proportion*100}% NA values" ))
    
    input_data = input_data %>%
        select( code, month, !!!syms(columns_to_keep) )
    
    ### Add column (index) to represent number of seconds from 1970-01-01
    input_data = input_data %>% 
        mutate( index = date_to_epoch(month) ) %>% 
        select( month, index, everything())
    
    # if ( cd@sample ) {
    #     input_data = input_data %>% sample_n(df, 100, seed=1234)
    # }
    
    if ( !is.na( cd@test_number ) ) {
        
        data_columns = input_data %>% colnames %>% keep( ~str_detect(.x, cd@code_tag) )
        
        if (  cd@test_number > length(data_columns) ) {
            cd@test_number = length(data_columns)
            report_info( cd, glue( "{cd@test_number} samples requested to test, \\
                            but only {length(data_columns)} exist in the dataset. \\
                           Testing will continue on {length(data_columns)} samples." ))
        }
        
        report_info( cd, glue( "Running analysis on first {cd@test_number} samples" ))
        report_info( cd, glue( "-{1:cd@test_number}- {data_columns[1:cd@test_number]} ") )
        
        input_data = input_data %>% select( month, index, code, data_columns[1:cd@test_number] )
    }
    
    return(input_data)
    
}

check_input_file_exists = function(cd) {

    if ( file.exists( glue( "{cd@indir}/{cd@csv_name}" ) ) ) {
        
        ### Create working directory
        working_dir = get_working_dir(cd)
        create_dirs( cd, working_dir )
        return( working_dir )

    } else {
        stop( report_error( cd, glue( "input file does not exist: {cd@indir}/{cd@csv_name}" ) ) )
    }
}


check_output_dir_exists = function(cd) {
    if ( !dir.exists(cd@outdir) ) {
        report_info( cd, glue("creating output directory: {cd@outdir}") )
        dir.create(cd@outdir)
    } 
}



divide_data_frame = function( cd, df ) {
    df = df %>% pivot_longer( starts_with(cd@code_tag ),
                                           names_to = "id",
                                           values_to = "value" )
    
    num_measurements = df %>% pull( id ) %>% unique %>% length

    if ( cd@numcores > num_measurements ) {
        report_info( cd, glue("data requested to be split into\\
                              {cd@numcores} groups but there are only\\
                              {num_measurements} measurements" ) )
        report_info( cd, glue("data will be split into\\
                              {num_measurements} groups instead") )
        cd@numcores = min( num_measurements, cd@numcores )
    }
    
    
    group_mapping = df %>%
        select( id ) %>% unique %>% 
        mutate( assignment = rep(1:cd@numcores, length.out=n()))
    
    split_grouping = df %>% 
        left_join( group_mapping, by="id" ) %>% 
        group_by( assignment ) %>% 
        group_split()
        
    split_list = vector("list",
                        group_mapping %>%
                            pull( assignment ) %>%
                            max )

    for ( i in 1:length(split_grouping) ) {
        split_list[[i]] = split_grouping[[i]] %>%
            select( -assignment ) %>% 
            pivot_wider( names_from = id,
                         values_from = value )
    }

    return( split_list )
}

run_r_script = function(cd, i, script_name, input_name, output_name, module_folder, ... ) {
    ## Define R command
    args = ""
    if ( length(list(...)) > 0 ) {
        args = paste( list(...), collapse=" " )
    }
    
    cmd = glue("{cd@r_command} {module_folder}/{script_name} {cd@working_dir} {input_name} {output_name} {module_folder} {args}")

    report_info( cd, glue( "Executing: [{cmd}]" ))

    system( cmd, wait=TRUE )
}

### Function which reverses the timeseries
reverse_timeseries = function( m ) {

    origin_objects = m %>% unique
    mapping = vector( mode = "character", length = length(origin_objects) )
    
    mapping = rev( origin_objects )
    names( mapping ) = origin_objects

    return( mapping[as.character(m)] )    
} 

### THIS RUNS THE change_detection.R SCRIPT
r_detect = function( cd ) {
    
    df = shape_dataframe( cd )
    
    df_list = divide_data_frame(cd, df)

    ### Launch an R process for each of these split dataframes
    ## Initiate a separate R process for each sub-DataFrame
    for ( i in 1:length(df_list) ) {
        
        this_df = df_list[[i]] %>% 
            ungroup() %>% 
            select( -month, -code ) %>% 
            rename( month = index )
        
        if ( cd@reverse ) {
            report_info( cd, "NB. Time series will be reversed" )
        
            reversed_months = this_df %>% pull( month ) %>% rev
            this_df = this_df %>% 
                mutate( month_original = month ) %>% 
                mutate( month = reversed_months ) %>% 
                arrange( month )
        }
        
        # Using i-1 so as to match the existing Python methodology
        input_file_name = glue("r_input_{i-1}.csv")
        output_file_name = glue("r_intermediate_{i-1}.RData")
        
        write_csv( this_df, glue("{cd@working_dir}/{input_file_name}") )
        
        run_r_script( cd=cd,
                      i=i,
                      script_name  =cd@change_detection_script,
                      input_name   =input_file_name,
                      output_name  =output_file_name,
                      module_folder=cd@change_detection_location
                      )
    }
}

### THIS RUNS THE results_extract.R SCRIPT
r_extract = function( cd ) {
    
    ### Launch an R process for each of the sets of data (defined
    ### by the number of cores)
    for ( i in 1:cd@numcores) {
        input_file_name = glue("r_intermediate_{i-1}.RData")
        output_file_name = glue("summary_output.csv")
        
        run_r_script( cd=cd,
                      i =i,
                      script_name=cd@results_extract_script,
                      input_name =input_file_name,
                      output_name=output_file_name,
                      module_folder=cd@results_extract_location,
                      cd@direction,
                      ifelse( cd@draw_figures, "yes", "no" )
        )
    }
    
    
}



run = function(cd) {
    report_info( cd, "Running new change detection..." )

    check_output_dir_exists( cd )
    
    cd@working_dir = check_input_file_exists( cd )
    
    report_info( cd, glue("working directory set to: {cd@working_dir}") )
    
    r_detect( cd )
    r_extract( cd )

    report_info( cd, "change detection analysis complete")

}

default_values = new( "ChangeDetection" )

option_list = list(
    ### Parameters that define the analysis
    make_option(c("-I", "--indicator"), type="character", default=NULL,
                help="indicator name (required)", metavar="character"),
    make_option(c("-C", "--code"), type="character", default=default_values@code_variable,
                help="code column name", metavar="character"),
    make_option(c("-A", "--numerator"), type="character", default=NULL, 
                help="numerator column name", metavar="character"),
    make_option(c("-B", "--denominator"), type="character", default=NULL, 
                help="output directory name", metavar="character"),
    make_option(c("-T", "--date"), type="character", default=default_values@date_variable,
                help="date column name [default=%default]", metavar="character"),
    make_option(c("-Y", "--ymd"), type="character", default=default_values@date_format,
                help="date format of input file [default=%default]", metavar="character"),
    make_option(c("-D", "--direction"), type="character", default=default_values@direction,
                help="direction (up/down/both) of change to identify [default=%default]", metavar="character"),
    make_option(c("-Z", "--numcores"), type="numeric", default=default_values@numcores,
                help="number of cores to use [default=%default]", metavar="numeric"),
    make_option(c("-N", "--test"), type="numeric", default=default_values@test_number,
                help="number of samples to run to test [default=%default]", metavar="numeric"),
    make_option(c("-Q", "--reverse"), action="store_true", default=default_values@reverse,
                help="Reverse timeseries [default=%default]" ),
    
    ### Parameters that define the input/output/reporting
    make_option(c("-v", "--verbose"), action="store_true", default=default_values@verbose,
                help="Print extra output [default]"),
    make_option(c("-i", "--indir"), type="character", default=default_values@indir, 
                help="output directory name [default=%default]", metavar="character"),
    make_option(c("-o", "--outdir"), type="character", default=default_values@outdir, 
                help="output directory name [default=%default]", metavar="character"),
    make_option(c("-x", "--overwrite"), action="store_true", default=default_values@overwrite,
                help="overwrite existing content? [default=%default]", metavar="character"),
    make_option(c("-f", "--figures"), action="store_true", default=default_values@draw_figures,
                help="generate figures? [default=%default]", metavar="character")
)
