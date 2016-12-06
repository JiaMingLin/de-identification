from enum import Enum

class EvalMethods(Enum):
	use_original_data = "Use Original Data"
	cv = "Cross-validation Folds|param"
	percent_split = "Percentage split|param"

	


class MLAlgorithms(Enum):
	pass