from pyspark import SparkConf, SparkContext
conf = SparkConf().setMaster("local").setAppName("de_identification")
sc = SparkContext(conf = conf)