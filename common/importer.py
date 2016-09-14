from pyspark import SparkConf, SparkContext, SQLContext
conf = SparkConf().setMaster("local").setAppName("de_identification")
sc = SparkContext(conf = conf)
sqlContext = SQLContext(sc)
partition_num = 40