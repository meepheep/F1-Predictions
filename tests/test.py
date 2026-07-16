import pandas as pd
#from tabulate import tabulate

obj = pd.read_pickle("data\\raw\\fastf1_cache\\2024\\2024-03-02_Bahrain_Grand_Prix\\2024-03-02_Race\\driver_info.ff1pkl")

dfs = obj['data']

#print(dfs)
#for item in dfs:
    #print(dfs[item])

dfs['1'].loc[:, ['Time', 'SessionTime', 'Date']]