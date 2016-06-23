import pandas as pd
import rpy2.robjects as robjects
import pandas.rpy.common as com
from rpy2.robjects.methods import RS4


class ExpressionSet(RS4):
    pass

r=robjects.r
r.source("dep-graph.R")
r_dep_edges = r['get_dep_edges']
df = pd.read_csv('/workspace/de_identification/desktop/static/testing_row_data.csv')
domain = dict((pair[0], list(set(pair[1]))) for pair in dict(df).items())

r_dataframe = com.convert_to_r_dataframe(df)
rdomain = robjects.ListVector(domain)

res = r_dep_edges(r_dataframe, rdomain)
print [list(rls) for rls in list(res)]

"""
res_myclass = ExpressionSet(res)
print res['edges']
print type(res_myclass)

print type(r_dep)
print tuple(res.slotnames())
print(tuple(res.slots.keys()))
print res.slots['.xData']
"""
