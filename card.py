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




### data load
shinhan_19 = pd.DataFrame()

for i in range(1,13):
       month = str(i).zfill(2)
       path = 'data/신한카드데이터셋/2019/{}/'.format(month)
       data = pd.read_csv(path+'인천시내국인업종별블록별_19{}.csv'.format(month))
       data.rename(columns={'일별':'STD_YMD','블록코드':'FID'}, inplace=True)
       shinhan_19 = pd.concat([shinhan_19,data])

shinhan_19['FID'] = shinhan_19['FID'].astype(int)
shinhan_19.reset_index(drop=True, inplace=True)



### 셀별 ID 부여
all_dong = ['도원동','동인천동','북성동','송월동','신포동','신흥동','율목동','도화동','숭의1.3동','숭의2동','숭의4동','도화1동','용현2동','용현3동','가좌1동','가좌2동','가좌3동','가좌4동','석남2동','도화2.3동']
korea = gpd.read_file('data/메타데이터/행정동데이터/HDONGP.shp', encoding='euc-kr')
donggu = korea[(korea['DO_NAME']=='인천광역시')&((korea['GU_NAME']=='동구')|(korea['HDONG_NAME'].isin(all_dong)))].reset_index(drop=True)
donggu.crs = '+proj=tmerc +lat_0=38 +lon_0=127.5 +k=0.9996 +x_0=1000000 +y_0=2000000 +ellps=GRS80 +units=m +no_defs'
donggu['HCODE'] = donggu['HCODE'].astype(np.int64)

donggu_geojson = donggu.to_crs(epsg=4326).to_json()

sk_50m = gpd.read_file('data/메타데이터/sk_50_격자/sk_m50_grs80_utmk.shp', encoding='euc-kr')
sk_50m['HCODE'] = 0

# 목표 셀의 고유번호 리스트 추출
idx = []
for i in range(290000,len(sk_50m)):
       for j in range(len(donggu)):
              if (sk_50m['geometry'][i].intersects(donggu['geometry'][j])):
                     idx.append(i)
                     sk_50m['HCODE'][i] = donggu['HCODE'][j]
                     break

donggu_grid = sk_50m.iloc[idx,:].reset_index(drop=True)

center_point = donggu_grid.centroid
X_center = []
Y_center = []

for i in range(len(center_point)):
       coord = list(center_point[i].coords)
       X_center.append(coord[0][0])
       Y_center.append(coord[0][1])

donggu_grid['X_COORD'] = X_center
donggu_grid['Y_COORD'] = Y_center

# 신한카드 데이터에서 목표 셀만 추출
shinhan = gpd.GeoDataFrame(pd.merge(shinhan_19,donggu_grid,how='inner', on='FID'))
shinhan.drop(['월별','geometry','HCODE','X_COORD','Y_COORD'], axis=1, inplace=True)

