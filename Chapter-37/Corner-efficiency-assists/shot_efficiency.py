import numpy as np
import scipy as sp
import matplotlib.pyplot as plt
import pandas as pd
import time
import geopandas as gpd
import descartes
from PIL import Image
from statsmodels.stats.proportion import proportions_ztest
from matplotlib.patches import Circle, Rectangle, Arc
from matplotlib import pyplot
from scipy import stats

# adjusted from Savvas Tjortjoglou code: http://savvastjortjoglou.com/nba-shot-sharts.html
# plotting function

def draw_court(ax=None, color='black', lw=2):
    # If an axes object isn't provided to plot onto, just get current one
    if ax is None:
        ax = plt.gca()

    # Create the various parts of an NBA basketball court

    # Create the basketball hoop
    # Diameter of a hoop is 18" so it has a radius of 9", which is a value
    # 7.5 in our coordinate system
    hoop = Circle((25, 4), radius=7.5/10.0, linewidth=lw, color=color, fill=False)

    # Create backboard
    backboard = Rectangle((23, 3), 4, -1, linewidth=lw, color=color)

    # The paint
    # Create the outer box 0f the paint, width=16ft, height=19ft
    outer_box = Rectangle((17, 0), 160/10.0, 190/10.0, linewidth=lw, color=color,
                          fill=False)
    # Create the inner box of the paint, width=12ft, height=19ft
    inner_box = Rectangle((19, 0), 120/10.0, 190/10.0, linewidth=lw, color=color,
                          fill=False)

    # Create free throw top arc
    top_free_throw = Arc((25, 19), 12, 12, theta1=0, theta2=180,
                         linewidth=lw, color=color, fill=False)
    # Create free throw bottom arc
    bottom_free_throw = Arc((25, 19), 12, 12, theta1=180, theta2=0,
                            linewidth=lw, color=color, linestyle='dashed')
    # Restricted Zone, it is an arc with 4ft radius from center of the hoop
    restricted = Arc((25, 4.5), 8, 8.5, theta1=0, theta2=180, linewidth=lw,
                     color=color)

    # Three point line
    # Create the side 3pt lines, they are 14ft long before they begin to arc
    corner_three_a = Rectangle((3, 0), 0, 14, linewidth=lw,
                               color=color)
    corner_three_b = Rectangle((47,0), 0, 14, linewidth=lw, color=color)
    # 3pt arc - center of arc will be the hoop, arc is 23'9" away from hoop
    # I just played around with the theta values until they lined up with the 
    # threes
    three_arc = Arc((25, 4.5), 47.5, 48.5, theta1=22, theta2=158, linewidth=lw,
                    color=color)

    # List of the court elements to be plotted onto the axes
    court_elements = [hoop, backboard, outer_box, inner_box, top_free_throw,
                      bottom_free_throw, restricted, corner_three_a,
                      corner_three_b, three_arc]

    # Add the court elements onto the axes
    for element in court_elements:
        ax.add_patch(element)

    return ax


data13 = pd.read_csv("https://raw.githubusercontent.com/hwchase17/sportvu/master/joined_shots_2013.csv")
data14 = pd.read_csv("https://raw.githubusercontent.com/hwchase17/sportvu/master/joined_shots_2014.csv")
data = pd.concat([data13,data14],ignore_index=True)
data = data[data["TOUCH_TIME"] >= 0]

n, bins, patches = plt.hist(x=data["TOUCH_TIME"], bins='auto', color='#0504aa', alpha=0.7, rwidth=0.85)
plt.grid(axis='y', alpha=0.75)
plt.xlabel('Touch time (sec)')
plt.ylabel('Frequency')
maxfreq = n.max()
plt.ylim(ymax=np.ceil(maxfreq / 10) * 10 if maxfreq % 10 else maxfreq + 10)
plt.show()

# We will explore the FG% for a specific zone for (potentially) assisted and unassisted shots. 
#We will define assisted shot one where the touch time is less than 1 second (this might be restrictive; we will come back to it later).
#We will then calculate the league-average expected points per shot for assisted and non-assisted shots from each zone.

# create a new column that will say whether the shot was "assisted"

data['assisted'] = data.apply(lambda row: int((row.TOUCH_TIME <= 1.5) & (row.DRIBBLES < 2)), axis=1)

# create a new column that has the mapping between ZONE_BASIC and ZONE_AREA to the court zones in the shapefile 

d = np.array(["xxxxxxxxxxxxx"] * len(data))

d[data["SHOT_ZONE_BASIC"] == "Restricted Area"] = "Deep Paint"
d[data["SHOT_ZONE_BASIC"] == "In The Paint (Non-RA)"] = "BasketArea"
d[(data["SHOT_ZONE_BASIC"] == "Mid-Range") & (data["SHOT_ZONE_AREA"] == "Center(C)")] = "MidrangeSlot"
d[(data["SHOT_ZONE_BASIC"] == "Mid-Range") & (data["SHOT_ZONE_AREA"] == "Left Side(L)")] = "LeftBaseline"
d[(data["SHOT_ZONE_BASIC"] == "Mid-Range") & (data["SHOT_ZONE_AREA"] == "Right Side(R)")] = "RightBaseline"
d[(data["SHOT_ZONE_BASIC"] == "Above the Break 3") & (data["SHOT_ZONE_AREA"] == "Center(C)")] = "TopOfArc"
d[(data["SHOT_ZONE_BASIC"] == "Right Corner 3")] = "RightCorner3"
d[(data["SHOT_ZONE_BASIC"] == "Left Corner 3")] = "LeftCorner"
d[(data["SHOT_ZONE_BASIC"] == "Above the Break 3") & (data["SHOT_ZONE_AREA"] == "Right Side Center(RC)")] = "RightWing3"
d[(data["SHOT_ZONE_BASIC"] == "Above the Break 3") & (data["SHOT_ZONE_AREA"] == "Left Side Center(LC)")] = "LeftWing3"
d[(data["SHOT_ZONE_BASIC"] == "Mid-Range") & (data["SHOT_ZONE_AREA"] == "Right Side Center(RC)")] = "RightWing2"
d[(data["SHOT_ZONE_BASIC"] == "Mid-Range") & (data["SHOT_ZONE_AREA"] == "Left Side Center(LC)")] = "LeftWing2"

data['ZoneName'] = d
data = data[data["ZoneName"] != "xxxxxxxxxxxxx"]

# Next we find the fraction of (potentially) assisted shots in every zone. This will give us some high-level idea on how these shots are generated.

df = pd.DataFrame(columns=['ZoneName','assisted'])
for z, tmp in data.groupby('ZoneName'):
    df = df.append({'ZoneName' : z, 'assisted' : len(tmp[tmp["assisted"]==1])/float(len(tmp))},ignore_index=True)


court = gpd.read_file("CourtZones.shx")

court = court.merge(df,on="ZoneName")

fig, ax = plt.subplots(figsize  = (12, 8))

court.plot(column="assisted",cmap="Purples",legend=True,edgecolors="white",ax=ax)
ax.set_title("Percentage of assisted shots (made and missed) per zone", fontsize=25)
draw_court()

#histogram for the closest defender distance for assisted and unassisted shots
from matplotlib import pyplot
from scipy import stats

assisted = data[data['assisted'] == 1].CLOSE_DEF_DIST
unassisted = data[data['assisted'] == 0].CLOSE_DEF_DIST

bins = np.linspace(0, max(data["CLOSE_DEF_DIST"]), 100)

pyplot.hist(assisted, bins, alpha=0.5, label='Assisted')
pyplot.hist(unassisted, bins, alpha=0.5, label='Unassisted')
pyplot.xlabel("Closest defender distance (feet)")
pyplot.ylabel("Frequence")
pyplot.legend(loc='upper right')
pyplot.show()

# perform t-test and ks-test

tt, pt = stats.ttest_ind(assisted,unassisted)

tks, pks = stats.ks_2samp(assisted,unassisted)

#FG% for each zone with an assisted-non assisted split. 
#This will allow us to eventually see how much value an assist provides to each zone.

dffg = pd.DataFrame(columns=['ZoneName','assistedFG','unassistedFG','ppsDiffAss','pval']) # ppsDiffAss is the expected point per shot differential between assistes and unassisted shots

for z, tmp in data.groupby('ZoneName'):
    stats, pval = proportions_ztest(count = [len(tmp[(tmp["assisted"] == 1) & (tmp['SHOT_MADE_FLAG'] == 1)]),len(tmp[(tmp["assisted"] == 0) & (tmp['SHOT_MADE_FLAG'] == 1)])], nobs = [len(tmp[tmp['assisted']==1]), len(tmp[tmp['assisted']==0])])
    dffg = dffg.append({'ZoneName' : z, 'assistedFG' : len(tmp[(tmp["assisted"] == 1) & (tmp['SHOT_MADE_FLAG'] == 1)])/float(len(tmp[tmp['assisted']==1])), 'unassistedFG' : len(tmp[(tmp["assisted"]==0) & (tmp["SHOT_MADE_FLAG"] == 1)])/float(len(tmp[tmp['assisted']==0])), 'ppsDiffAss' : max(2,float(court[court['ZoneName'] == z].Range))*((len(tmp[(tmp["assisted"] == 1) & (tmp['SHOT_MADE_FLAG'] == 1)])/float(len(tmp[tmp['assisted']==1])))-(len(tmp[(tmp["assisted"] == 0) & (tmp['SHOT_MADE_FLAG'] == 1)])/float(len(tmp[tmp['assisted']==0])))), 'pval' : pval },ignore_index=True)
    
df1 = dffg[['ZoneName','assistedFG','unassistedFG','pval']]
df1.round(3)

# expected points above unassisted shot 

court = court.merge(dffg,on="ZoneName")

fig, ax = plt.subplots(figsize = (12,8))

court.plot(ax=ax,column="ppsDiffAss",legend=True,cmap="Purples")
ax.set_title("Expected points added per assisted shot", fontsize=25)
draw_court()


dffgp = pd.DataFrame(columns=['ZoneName','Player','assistedFG','unassistedFG'])

for z, tmpz in data.groupby('ZoneName'):
    for p, tmp in tmpz.groupby('PLAYER_NAME'):
        if (len(tmp[tmp['assisted'] == 1]) > 0) & (len(tmp[tmp['assisted'] == 0]) > 0) & (len(tmp)>50):
            dffgp = dffgp.append({'ZoneName' : z, 'Player' : p, 'assistedFG' : len(tmp[(tmp["assisted"] == 1) & (tmp['SHOT_MADE_FLAG'] == 1)])/float(len(tmp[tmp['assisted']==1])), 'unassistedFG' : len(tmp[(tmp["assisted"]==0) & (tmp["SHOT_MADE_FLAG"] == 1)])/float(len(tmp[tmp['assisted']==0]))},ignore_index=True)
            
dffgp.head()
