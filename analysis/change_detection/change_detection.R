print("Change detection running...")

##### Retrive arguments from Python command
arguments <- commandArgs(trailingOnly = TRUE)

# if ( FALSE ) {
#   arguments[1] = "output/indicator_saturation/indicator_saturation_down_a"
#   arguments[2] = "r_input_2.csv"
#   arguments[3] = "r_intermediate_2.RData"
#   arguments[4] = "/workspace/analysis/change_detection"
# }

#rm(list = ls())  #clear the workspace
setwd(arguments[1]) ### Set working directory

########################
####### Load required packages (install needed first time)
#######################
library(caTools)
library(gets) ### main package for break detection - see Pretis, Reade, and Sucarrat, Journal of Stat. Software, in press.

##########################
####### Parameters
#########################

plot_show <- FALSE ###show plots during break detection

#### Break detection calibration
# p_alpha <- 0.000001 ## level of significance for the detection of breaks (main calibration choice)
p_alpha <- 0.001 ## level of significance for the detection of breaks (main calibration choice)


### Computational
parallel <- NULL ### set as integer (=number of cores-1) if selection should run in parallel (may increase speed for longer time series)
# recommended to set to "NULL" unless datasets are very large.

######### Input Data
variable <- "ratio_quantity" ###choose relevant variable name in the sample
data.pick <- read.csv(arguments[2], header=TRUE)   #load raw input data

#############################################
############################################

pick.rel <- grep(variable , names(data.pick)) 
data_names = names(data.pick)[pick.rel]

month.c  <-  as.POSIXct(as.numeric(as.character(data.pick$month)),origin="1970-01-01",tz="GMT")

data.pick <- data.frame(month.c, data.pick[,pick.rel])
colnames(data.pick)[2:ncol(data.pick)] = data_names

names.rel <- names(data.pick)[pick.rel]
vars <- length(pick.rel)


#############################################################################
################################################
###################### A: Break Detection Loop
################################################
##############################################################################

result.list <- list()

withCallingHandlers({
  for (i in 1:vars) 
    
  {
    
    #print(names.rel[i])
    print(paste(round((i / vars)*100,1), "%"))
    y <- as.matrix(data.pick[names.rel[i]])
    
    ###############################################
    ###Main Break Detection Function (tis=TRUE searches for trend breaks) - called from "gets" package
    if (sum(is.na(y))==0){ ## if there are no missing values
      islstr.res <- isat(y,
                         t.pval=p_alpha,
                         sis = FALSE,
                         tis = TRUE,
                         iis = FALSE,
                         plot=plot_show,
                         parallel.options = parallel,
                         ratio.threshold = 0.3,
                         max.block.size = 15
                         )
    } else {
      ### Create missing value indicator
      m <- is.na(y)
      m <- m * 1
      ### Fill in missing values with arbitrary number
      y[is.na(y)] <- -1
      
      islstr.res <- isat(y,
                         t.pval=p_alpha,
                         sis = FALSE,
                         tis = TRUE,
                         iis = FALSE,
                         plot=plot_show,
                         parallel.options = parallel,
                         ratio.threshold = 0.3,
                         max.block.size = 12,
                         mxreg = m)
    }
    ##########################################
    
    result.list[i] <- list(islstr.res)
    names(result.list)[i] <- names.rel[i]
    
  }  
}, warning = function(w){
  results$warn[i] <<- w$message
  invokeRestart("muffleWarning")
  
}) ###withCalling closed

#save(result.list, file=arguments[3])
save.image(file=arguments[3])

print("Break detection done")