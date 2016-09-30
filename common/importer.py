try:

	from pyspark import SparkConf, SparkContext, SQLContext
	conf = (SparkConf()
        	.setMaster("yarn-client")
        	.setAppName("de_identification")
        	.set("spark.executor.memory", "1G")
        	.set("spark.driver.memory", "1G")
        	.set("spark.executor.cores", 1)
        	.set("spark.executor.instances", 40)
	)	
	sc = SparkContext(conf = conf)
	sqlContext = SQLContext(sc)
	partition_num = 400

except:
	print "run on local"
