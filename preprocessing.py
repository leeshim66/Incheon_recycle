import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
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

# sys.setrecursionlimit(10**6)
warnings.filterwarnings('ignore')

plt.rcParams['font.family'] = 'NanumGothic'
plt.rc("axes", unicode_minus = False)
plt.rcParams['figure.figsize'] = (16,12)

dic = {'2814051000':'만석동','2814052500':'화수1·화평동','2814053000':'화수2동','2814055500':'송현1·2동',
       '2814057000':'송현3동','2814058000':'송림1동','2814059000':'송림2동','2814060500':'송림3·5동',
       '2814061000':'송림4동','2814063000':'송림6동','2814064000':'금창동'}


sk = pd.read_csv('data/sk.csv')
card = pd.read_csv('data/신한카드.csv')

final_data = pd.merge(sk, card, how='left', on=['FID','STD_YMD'])
final_data = final_data.fillna(0)


### 적분을 통한 각 행정복지센터 기준 거리별 인구
# 적분 함수
def integrity(case, lat, lon, xmin_vec, xmax_vec, ymin_vec, ymax_vec, r, k):
       N = len(case)
       perc = [0]*N
       for j in range(N):
              pre = case[j]
              xmin = xmin_vec[j]
              xmax = xmax_vec[j]
              ymin = ymin_vec[j]
              ymax = ymax_vec[j]

              if pre=='1':
                     rg = np.arange(lon - np.sqrt(r**2-(ymax-lat)**2), xmax, k)
                     def f(x):
                            return ymax - lat + np.sqrt(r**2-(x-lon)**2)
              elif pre=='2':
                     rg = np.arange(xmin, lon + np.sqrt(r**2-(ymax-lat)**2), k)
                     def f(x):
                            return ymax - lat + np.sqrt(r**2-(x-lon)**2)
              elif pre=='3':
                     rg = np.arange(xmin, lon + np.sqrt(r**2-(ymin-lat)**2), k)
                     def f(x):
                            return lat + np.sqrt(r**2-(x-lon)**2) - ymin
              elif pre=='4':
                     rg = np.arange(lon - np.sqrt(r**2-(ymin-lat)**2), xmax, k)
                     def f(x):
                            return lat + np.sqrt(r**2-(x-lon)**2) - ymin
              elif pre=='12':
                     rg = np.arange(xmin, xmax, k)
                     def f(x):
                            return ymax - lat + np.sqrt(r**2-(x-lon)**2)
              elif pre=='23':
                     rg = np.arange(ymin, ymax, k)
                     def f(x):
                            return ymax - lon + np.sqrt(r**2-(x-lat)**2)
              elif pre=='34':
                     rg = np.arange(xmin, xmax, k)
                     def f(x):
                            return lat + np.sqrt(r**2-(x-lon)**2) - ymin
              elif pre=='14':
                     rg = np.arange(ymin, ymax, k)
                     def f(x):
                            return xmax - lon + np.sqrt(r**2-(x-lat)**2)
              elif pre=='123':
                     rg = np.arange(lon + np.sqrt(r**2-(ymin-lat)**2), xmax, k)
                     sq = (lon + np.sqrt(r**2-(ymin-lat)**2) - xmin)*50
                     def f(x):
                            return ymax - lat + np.sqrt(r**2-(x-lon)**2)
              elif pre=='124':
                     rg = np.arange(xmin, lon + np.sqrt(r**2-(ymin-lat)**2), k)
                     sq = (xmax - lon + np.sqrt(r**2-(ymin-lat)**2))*50
                     def f(x):
                            return ymax - lat + np.sqrt(r**2-(x-lon)**2)
              elif pre=='134':
                     rg = np.arange(xmin, lon + np.sqrt(r**2-(ymax-lat)**2), k)
                     sq = (xmax - lon + np.sqrt(r**2-(ymax-lat)**2))*50
                     def f(x):
                            return lat + np.sqrt(r**2-(x-lon)**2) - ymin
              elif pre=='234':
                     rg = np.arange(lon + np.sqrt(r**2-(ymax-lat)**2), xmax, k)
                     sq = (lon + np.sqrt(r**2-(ymax-lat)**2) - xmin)*50
                     def f(x):
                            return lat + np.sqrt(r**2-(x-lon)**2) - ymin

              int_pre = int(pre)
              if int_pre==0:
                     perc[j] = 0
              elif int_pre<100 :
                     summ = 0
                     for i in range(k):
                            if i==0 or i==k-1:
                                   summ = summ + (rg[-1]-rg[0]) / (n-1)/2*f(rg[i])
                            else :
                                   summ = summ + (rg[-1]-rg[0]) / (n-1)*f(rg[i])
                     perc[j] = summ / 50**2
              elif int_pre<1000 :
                     summ = 0
                     for i in range(k):
                            if i==0 or i==k-1:
                                   summ = summ + (rg[-1]-rg[0]) / (n-1)/2*f(rg[i])
                            else :
                                   summ = summ + (rg[-1]-rg[0])/(n-1)*f(rg[i])
                     perc[j] = (summ+sq) / 50**2
              else :
                     perc[j] = 1

       return perc