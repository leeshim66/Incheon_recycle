import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objs as go
import plotly.offline as py
import geopandas as gpd
import folium
from folium import plugins
import branca
from shapely.geometry import Polygon, LineString, Point
from shapely import wkt
from pyproj import Proj, transform, Transformer
import geojsoncontour
from scipy.interpolate import griddata
import scipy as sp
import scipy.ndimage
from plotnine import *
import sys
import warnings
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split

# sys.setrecursionlimit(10**6)
warnings.filterwarnings('ignore')

plt.rcParams['font.family'] = 'NanumGothic'
plt.rc("axes", unicode_minus = False)
plt.rcParams['figure.figsize'] = (16,12)

dic = {'2814051000':'만석동','2814052500':'화수1·화평동','2814053000':'화수2동','2814055500':'송현1·2동',
       '2814057000':'송현3동','2814058000':'송림1동','2814059000':'송림2동','2814060500':'송림3·5동',
       '2814061000':'송림4동','2814063000':'송림6동','2814064000':'금창동'}


# 최종 데이터셋 로드
data = pd.read_csv('data/final/final_dataset.csv')
X = data[['pop_50','pop_100','pop_250','pop_500','card_50','card_100','card_250','card_500']]
y1 = data['value']
y2 = data['mean_value']
y3 = data['real_mean_value']

# random forest 변수중요도 시각화
rf = RandomForestRegressor()
rf.fit(X,y1)
rf_pred = rf.predict(X)

features = X.columns.values
a,b = (list(a) for a in zip(*sorted(zip(rf.feature_importances_, features), reverse=False)))

trace = go.Bar(x=a, y=b, marker=dict(color=a, colorscale='Viridis', reversescale=True),
               name = 'RF feature importance', orientation='h')
layout = dict(width=800, height=500,
              yaxis=dict(showgrid=True,showline=False, showticklabels=True, domain=[0,1]))

fig = go.Figure(data=[trace])
fig['layout'].update(layout)
py.iplot(fig, filename='plotss')

