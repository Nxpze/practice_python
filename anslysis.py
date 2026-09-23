import pandas as pd

df1 = pd.read_csv('Dataset/netflix_user_behavior_dataset.csv')
df2 = pd.read_csv('Dataset/credits.csv')
df3 = pd.read_csv('Dataset/titles.csv')

print(df1.shape)
print(df2.shape)
print(df3.shape)