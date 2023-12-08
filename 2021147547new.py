import pandas as pd
df=pd.read_csv("/WorldCupMatches.csv")
df.shape
# (852, 19)
 
df[df.duplicated()] 
df=df.drop_duplicates() 
df.shape
#(836, 19)

# Home Team Goals
data1 = pd.DataFrame(df.groupby("Home Team Name")["Home Team Goals"].agg(["count", 'sum']).sort_values('sum', ascending=False).reset_index())
data1.rename(columns={'Home Team Name': 'Team', 'count': 'Matches', 'sum': 'Goals'}, inplace=True)

# Away Team Goals
data2 = pd.DataFrame(df.groupby("Away Team Name")["Away Team Goals"].agg(["count", 'sum']).sort_values('sum', ascending=False).reset_index())
data2.rename(columns={'Away Team Name': 'Team', 'count': 'Matches', 'sum': 'Goals'}, inplace=True)

# Merge
data3 = data1.merge(data2, on="Team", how="outer")
data3 = data3.fillna(0)  # Some teams may not have played as the home team, so NaN values are filled with 0
data3

data3["TotalMatches"] = data3["Matches_x"] + data3["Matches_y"]
data3["TotalGoals"] = data3["Goals_x"] + data3["Goals_y"]
data3["GoalRate"] = (data3["TotalGoals"] / data3["TotalMatches"]).round(2)
data3.sort_values("GoalRate", ascending=False)[:10]

# Home Team Goals Conceded
data4 = pd.DataFrame(df.groupby("Home Team Name")["Away Team Goals"].agg(["count", 'sum']).sort_values('sum', ascending=False).reset_index())
data4.rename(columns={'Home Team Name': 'Team', 'count': 'Matches', 'sum': 'GoalsConceded'}, inplace=True)

# Away Team Goals Conceded
data5 = pd.DataFrame(df.groupby("Away Team Name")["Home Team Goals"].agg(["count", 'sum']).sort_values('sum', ascending=False).reset_index())
data5.rename(columns={'Away Team Name': 'Team', 'count': 'Matches', 'sum': 'GoalsConceded'}, inplace=True)

# Merge and fill missing values
data6 = data4.merge(data5, on="Team", how="outer")
data6 = data6.fillna(0)

# Calculate total matches, total goals conceded, and goals conceded rate
data6["TotalMatches"] = data6["Matches_x"] + data6["Matches_y"]
data6["TotalGoalsConceded"] = data6["GoalsConceded_x"] + data6["GoalsConceded_y"]
data6["GoalsConcededRate"] = (data6["TotalGoalsConceded"] / data6["TotalMatches"]).round(2)
data6.sort_values("GoalsConcededRate", ascending=True)[:10]

# Merge data tables
data7 = data3.merge(data6, on="Team", how="outer")
data7 = data7[['Team', 'TotalMatches_x', 'TotalGoals', 'GoalRate', 'TotalGoalsConceded', 'GoalsConcededRate']]
data7.rename(columns={'TotalMatches_x': 'TotalMatches'}, inplace=True)

# Plotting
import numpy as np
col = ["Brazil", "Italy", "Germany FR", "Argentina", "France", "Uruguay", "England", "Germany", "Spain"]
result = []
for i in col:
    result.append(data7[data7["Team"] == i])

result = np.array(result)
result = result.reshape(9, 6)
result = pd.DataFrame(result, index=col, columns=data7.columns)
result = result.iloc[:, 1:].astype('float')

import matplotlib.pyplot as plt
import matplotlib as mpl
mpl.rcParams['font.family'] = 'sans-serif'
mpl.rcParams['font.sans-serif'] = [u'SimHei']
mpl.rcParams['axes.unicode_minus'] = False

# Define plot range
minx = min(result["GoalsConcededRate"])
maxx = max(result["GoalsConcededRate"])
miny = min(result["GoalRate"])
maxy = max(result["GoalRate"])

# Create scatter plot
plt.figure(figsize=(8, 8), dpi=100)
for i in range(result.shape[0]):
    plt.scatter(x=result["GoalsConcededRate"][i], y=result["GoalRate"][i], s=result["TotalMatches"][i] * 20, alpha=0.65, cmap='viridis')

# Set axis limits and draw average lines
plt.xlim(xmin=maxx + 0.1, xmax=minx - 0.1)
plt.vlines(x=result['GoalsConcededRate'].mean(), ymin=miny - 0.1, ymax=maxy + 0.1, colors='black', linewidth=1)
plt.hlines(y=result['GoalRate'].mean(), xmin=minx - 0.1, xmax=maxx + 0.1, colors='black', linewidth=1)

# Add team names to the points
for x, y, z in zip(result["GoalsConcededRate"], result["GoalRate"], col):
    plt.text(x, y, z, ha='center', fontsize=10)

plt.xlabel("High<—————— GoalsConcededRate(%) ——————>Low", fontsize=15)
plt.ylabel("Low<—————— GoalRate(%) ——————>High", fontsize=15)
plt.title("Goal and Goals Conceded Rates of Championship Teams - Boston Matrix", fontsize=20)
plt.show()

# Calculate goal differences
df["Half-Goal-difference"] = df["Half-time Home Goals"] - df["Half-time Away Goals"]  # Half-time goal difference
df["Away-Half-Goal-difference"] = df["Half-time Away Goals"] - df["Half-time Home Goals"]  # Away team's half-time goal difference
df["Goal-difference"] = df["Home Team Goals"] - df["Away Team Goals"]  # Full-time goal difference
df["Away-Goal-difference"] = df["Away Team Goals"] - df["Home Team Goals"]  # Away team's full-time goal difference

df.loc[df["Half-Goal-difference"] > 0, 'Half-result'] = '6'
df.loc[df["Half-Goal-difference"] == 0, 'Half-result'] = '0'
df.loc[df["Half-Goal-difference"] < 0, 'Half-result'] = '-3'
df.loc[df["Away-Half-Goal-difference"] > 0, 'Away-Half-result'] = '6'
df.loc[df["Away-Half-Goal-difference"] == 0, 'Away-Half-result'] = '0'
df.loc[df["Away-Half-Goal-difference"] < 0, 'Away-Half-result'] = '-3'

# Assign results for full-time
df.loc[df["Goal-difference"] > 0, 'result'] = '1'
df.loc[df["Goal-difference"] == 0, 'result'] = '0'
df.loc[df["Goal-difference"] < 0, 'result'] = '-1'

# Assign results for away team's full-time
df.loc[df["Away-Goal-difference"] > 0, 'Away-result'] = '1'
df.loc[df["Away-Goal-difference"] == 0, 'Away-result'] = '0'
df.loc[df["Away-Goal-difference"] < 0, 'Away-result'] = '-1'

# Convert string results to integers
df["Half-result"] = df["Half-result"].astype("int32")
df["result"] = df["result"].astype("int32")
df["Away-Half-result"] = df["Away-Half-result"].astype("int32")
df["Away-result"] = df["Away-result"].astype("int32")


df["v1"] = df["Half-result"] - df["result"]
df["v2"] = df["Away-Half-result"] - df["Away-result"]
print(df["v1"].value_counts())
print(df["v2"].value_counts())

import matplotlib.pyplot as plt
import matplotlib as mpl
import warnings
warnings.filterwarnings("ignore")
mpl.rcParams["font.sans-serif"] = ["SimHei"]
mpl.rcParams["axes.unicode_minus"] = False
df1 = pd.DataFrame(df["v1"].value_counts() / df["v1"].count())
df2 = pd.DataFrame(df["v2"].value_counts() / df["v2"].count())
g = ["5", "-1", "0", "-2", "1", "-4", "-3", "6", "7"]
g1 = ["-2", "1", "0", "5", "-1", "7", "6", "-3", "-4"]
c = ["red", "yellow", "violet", "cyan", "lightseagreen", "silver", "orange", "olive", "green"]
c1 = ["cyan", "lightseagreen", "violet", "red", "yellow", "green", "olive", "orange", "silver"]
wedgeprops = {'width': 0.3}
explode = (0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.15)
fig = plt.figure(figsize=(15, 15))
plt.subplot(121)
plt.pie(df1.loc[:, 'count'], explode=explode, labels=g, autopct="%3.1f%%", startangle=60, colors=c, wedgeprops=wedgeprops)

plt.title("Home Team Half and Full Match Result Distribution")
plt.subplot(122)
plt.pie(df2.loc[:, 'count'], explode=explode, labels=g1, autopct="%3.1f%%", startangle=60, colors=c1, wedgeprops=wedgeprops)
plt.title("Away Team Half and Full Match Result Distribution")
plt.show()


df3 = df[df['v1'] == 5]  
df3_away = df[df["v2"] == 5]  # Favorable conditions as the away team
df4 = df[(df["v1"] == -3) | (df["v1"] == -4)]  # Unfavorable conditions as the home team
df4_away = df[(df["v2"] == -3) | (df["v2"] == -4)]  # Unfavorable conditions as the away team
fig = plt.figure(figsize=(12, 8))
plt.subplot(221)
df3["Home Team Name"].value_counts().sort_values(ascending=True)[-10:].plot(kind='barh')
plt.title("Top 10 Teams as Home in Favorable Conditions")

plt.subplot(222)
df3_away["Away Team Name"].value_counts().sort_values(ascending=True)[-10:].plot(kind='barh')
plt.title("Top 10 Teams as Away in Favorable Conditions")

plt.subplot(223)
df4["Home Team Name"].value_counts().sort_values(ascending=True)[-10:].plot(kind='barh')
plt.title("Top 10 Teams as Home in Unfavorable Conditions")

plt.subplot(224)
df4_away["Away Team Name"].value_counts().sort_values(ascending=True)[-10:].plot(kind='barh')
plt.title("Top 10 Teams as Away in Unfavorable Conditions")

plt.subplots_adjust(wspace=0.5, hspace=0.3)

plt.show()

plt.figure(figsize=(20,20))
for i, j in enumerate(col):
    df_home=df[df["Home Team Name"]==j]
    data=pd.DataFrame(df_home.loc[:,"v1"].value_counts()/df_home.loc[:,"v1"].count())
    plt.subplot(3,3,i+1)  
    plt.pie(data.loc[:, 'count'],labels=data.index,autopct="%3.1f%%",startangle=60,colors=c,\
              textprops={'fontsize': 15},wedgeprops={'width':0.3},pctdistance=0.7)
    plt.title(j, fontsize=18)
plt.show()

