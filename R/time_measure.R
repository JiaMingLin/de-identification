TimeMeasure <- setRefClass(
   "TimeMeasure",
   fields = list(
     ptm = "ANY",
     start.time = "ANY",
     function.name = "ANY",
     procedure = "ANY",
     debug = "logical"
   ),
   methods = list(
     initialize = function(procedure ,flag.debug=TRUE){
       .self$procedure = procedure
       .self$debug <- flag.debug
     },

     start = function(function.name){
       if(.self$debug){
         .self$function.name<-function.name
         .self$start.time<-Sys.time()
         .self$ptm <- proc.time() 
       }
     },

     check = function(){
       if(.self$debug){
         cat(blue(paste("======================", .self$procedure ,"=========================\n", sep=" ")))
	 cat( red(paste(.self$start.time, ": Function starting.....:", .self$function.name, "\n", sep=" ")) )
	 print(proc.time() - ptm)
       }
     }
   )
)