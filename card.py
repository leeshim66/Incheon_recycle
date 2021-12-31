import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import geopandas as gpd
import folium
from folium import plugins
import branca
from shapely.geometry import Polygon, LineString, Point
from pyproj import Proj, transform, Transformer
import geojsoncontour
from scipy.interpolate import griddata
import scipy as sp
import scipy.ndimage
from plotnine import *

plt.rcParams['font.family'] = 'NanumGothic'
plt.rcParams['figure.figsize'] = (16,12)

dic = {'2814051000':'만석동','2814052500':'화수1·화평동','2814053000':'화수2동','2814055500':'송현1·2동',
       '2814057000':'송현3동','2814058000':'송림1동','2814059000':'송림2동','2814060500':'송림3·5동',
       '2814061000':'송림4동','2814063000':'송림6동','2814064000':'금창동'}




# data load
shinhan_19 = pd.DataFrame()

for i in range(1,13):
       month = str(i).zfill(2)
       path = 'data/신한카드데이터셋/2019/{}/'.format(month)
       data = pd.read_csv(path+'인천시내국인업종별블록별_19{}.csv'.format(month))
       data.rename(columns={'일별':'STD_YMD','블록코드':'FID'}, inplace=True)
       shinhan_19 = pd.concat([shinhan_19,data])

shinhan_19['FID'] = shinhan_19['FID'].astype(int)
shinhan_19.reset_index(drop=True, inplace=True)




