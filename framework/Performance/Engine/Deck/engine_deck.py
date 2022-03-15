'''
This script loads an Excel spreadsheet using the pandas package, uses the numpy
package to find trends and plots with the matplotlib package
'''

# Imports
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.offsetbox import AnchoredText


# 'De (m)' 'BPR' 'FPR' 'OPR' 'TIT (K)' 'T (N)' 'FC (kg/hr)'
df = pd.read_pickle("engines.pkl")
print(df.head())
print(df.shape[0])


