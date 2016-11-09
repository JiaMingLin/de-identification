# -*- coding: utf-8 -*-

import sys
import pandas as pd


print sys.stdout.encoding
pd.options.display.encoding =sys.stdout.encoding
df = pd.read_csv('test_chinese.csv', encoding='utf-8')
print df

df2 = pd.DataFrame({ '日期' : ['2015-01-07', '2014-12-17', '2015-01-21', '2014-11-19', '2015-01-17', '2015-02-26', '2015-01-04', '2014-12-20', '2014-12-07', '2015-01-06'],
                    '股票代码': ['600795', '600268', '002428', '600031', '002736', '600216', '000799', '601600', '601939', '000898']
                    })

print df2
