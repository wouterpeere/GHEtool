import pandas as pd
from GHEtool.gui.translations import TrClass

tr = TrClass()

column = ['name',	'English',	'German',	'Dutch', 	'Italian', 	'French', 	'Spanish', 'Galician']
values = []
for trans in tr.__slots__:
    values.append([trans])
for i in range(len(column) - 1):
    tr.changeLanguage(i)
    for idx, trans in enumerate(tr.__slots__):
        val = getattr(tr, trans)
        values[idx].append(val.replace('\n', '@') if isinstance(val, str) else val)

df = pd.DataFrame(values, columns=column)
df = df.set_index('name')
df.to_csv('trsns.csv', sep=';', encoding='utf-16')
