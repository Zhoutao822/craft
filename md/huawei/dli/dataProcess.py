
#%%
import pandas as pd

df = pd.read_csv('./train.csv')

df.head(10)
#%%
columns = df.columns.values.tolist()

print(columns)

#%%
na_series = df.isnull().sum()
for col_name in na_series.index:
    if na_series[col_name] > 200:
        df = df.drop(columns=col_name, axis=1)
        print(col_name)
#%%
df.isnull().sum()

df_without_na = df.dropna(axis=0)

print(df_without_na.isnull().sum())

#%%
df_without_na.describe()

df_without_na.to_csv('./result.csv', index=False)

