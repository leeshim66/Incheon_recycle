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
from sklearn.model_selection import train_test_split, GridSearchCV
from xgboost import XGBRegressor

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
rf1 = RandomForestRegressor()
rf1.fit(X,y1)
rf1_pred = rf1.predict(X)

rf2 = RandomForestRegressor()
rf2.fit(X,y2)
rf2_pred = rf2.predict(X)

rf3 = RandomForestRegressor()
rf3.fit(X,y3)
rf3_pred = rf3.predict(X)

features = X.columns.values
a,b = (list(a) for a in zip(*sorted(zip(rf1.feature_importances_, features), reverse=False)))

trace = go.Bar(x=a, y=b, marker=dict(color=a, colorscale='Viridis', reversescale=True),
               name = 'RF feature importance', orientation='h')
layout = dict(width=800, height=500,
              yaxis=dict(showgrid=True,showline=False, showticklabels=True, domain=[0,1]))

fig = go.Figure(data=[trace])
fig['layout'].update(layout)
py.iplot(fig, filename='plotss')


# Gridsearch를 통한 파라미터 설정
param_grid = {
    'learning_rate' : [0.001,0.005,0.01,0.05],
    'booster' : ['gbtree', 'gblinear'],
    'n_estimators': [100, 150, 200],
    'max_depth': [1,2,3],
    'min_samples_split': [0,1,2],
    'min_samples_leaf' : [0,1,2],
    'max_leaf_node' : [1,2,3]
}

a1,b1 = (list(a) for a in zip(*sorted(zip(rf1.feature_importances_, features), reverse=True)))
a2,b2 = (list(a) for a in zip(*sorted(zip(rf2.feature_importances_, features), reverse=True)))
a3,b3 = (list(a) for a in zip(*sorted(zip(rf3.feature_importances_, features), reverse=True)))
feature1 = b1[:6]
feature2 = b2[:6]
feature3 = b3[:6]
X1 = X[feature1]# RF변수중요도로 변수 선택
X2 = X[feature2]
X3 = X[feature3]

xgb = XGBRegressor()

grid_search1 = GridSearchCV(estimator=xgb, param_grid=param_grid, cv=10, n_jobs=-1)
grid_search2 = GridSearchCV(estimator=xgb, param_grid=param_grid, cv=10, n_jobs=-1)
grid_search3 = GridSearchCV(estimator=xgb, param_grid=param_grid, cv=10, n_jobs=-1)

grid_search1.fit(X1,y1)
grid_search2.fit(X2,y2)
grid_search3.fit(X3,y3)

# 셀별 y 예측
XGB1 = XGBRegressor(booster='gbtree', learning_rate=0.01, max_depth=1, n_estimators=200, max_leaf_node=2)
XGB2 = XGBRegressor(booster='gbtree', learning_rate=0.005, max_depth=1, n_estimators=150, max_leaf_node=2)
XGB3 = XGBRegressor(booster='gbtree', learning_rate=0.005, max_depth=2, n_estimators=150, max_leaf_node=2)
XGB1.fit(X1,y1)
XGB2.fit(X2,y2)
XGB3.fit(X3,y3)

predict_df = pd.read_csv('data/final/pred_df.csv')

X_pred1 = predict_df[feature1]
X_pred2 = predict_df[feature2]
X_pred3 = predict_df[feature3]

XGB_pred1 = XGB1.predict(X_pred1)
XGB_pred2 = XGB2.predict(X_pred2)
XGB_pred3 = XGB3.predict(X_pred3)

