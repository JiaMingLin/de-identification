from aenum import Enum

class EvalMethodEnums(Enum):
	use_original_data = 1
	cv = 2
	percent_split = 3

	@staticmethod
	def get_names():
		mapping = dict()
		mapping[EvalMethodEnums.use_original_data.value] = 'Use Original Data'
		mapping[EvalMethodEnums.cv.value] = 'Cross-Validation Folds|param'
		mapping[EvalMethodEnums.percent_split.value] = 'Percentage Split|param'
		return mapping

class MeasureEnums(Enum):
	score = 1

	@staticmethod
	def get_names():
		mapping = dict()
		mapping[MeasureEnums.score.value] = 'Score'
		return mapping

class MLAlgorithmEnums(Enum):
	logistic_regression = 1
	random_forest = 2
	naive_bayes = 3

	@staticmethod
	def get_names():
		mapping = dict()
		mapping[MLAlgorithmEnums.logistic_regression.value] = 'Logistic Regression'
		mapping[MLAlgorithmEnums.random_forest.value] = 'Random Forest'
		mapping[MLAlgorithmEnums.naive_bayes.value] = 'Naive Bayes'
		return mapping