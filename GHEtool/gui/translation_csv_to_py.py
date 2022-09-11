from pandas import read_csv
from os import system
df1 = read_csv('Translations.csv', sep=';', encoding='utf-8')

file_name = 'translation_class.py'

with open(file_name, 'w', encoding='utf-8') as file:
    file.write('from typing import List\n')
    file.write('class Translations:\n')
    list_of_options = df1["name"].to_list()
    list_of_options.append('option_language')
    text = f'__slots__ = {tuple(list_of_options)}'
    file.write(f'   {text}\n')
    file.write('   def __init__(self):\n')
    file.write(f'      self.option_language: List[str] = {df1.columns[1:].to_list()}\n')
    for name, translations in zip(df1['name'], df1.iloc[:, 1:].to_numpy()):
        text = f'self.{name}: List[str] = {translations.tolist()}'
        file.write(f'      {text}\n')

system(f'py -m black --line-length 160 {file_name}')
