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
from tqdm import tqdm
import sys
import pyarrow.csv as pacsv
import time
import warnings

# sys.setrecursionlimit(10**6)
warnings.filterwarnings('ignore')

plt.rcParams['font.family'] = 'NanumGothic'
plt.rc("axes", unicode_minus = False)
plt.rcParams['figure.figsize'] = (16,12)

dic = {'2814051000':'만석동','2814052500':'화수1·화평동','2814053000':'화수2동','2814055500':'송현1·2동',
       '2814057000':'송현3동','2814058000':'송림1동','2814059000':'송림2동','2814060500':'송림3·5동',
       '2814061000':'송림4동','2814063000':'송림6동','2814064000':'금창동'}
# pd.options.display.float_format = '{:.10f}'.format

incheon_pcell_sex_age = pd.read_csv('D:/인천재활용/data/SK생활인구데이터셋/2019/01/incheon_service_pcell_sex_age_pop_201901.csv', delimiter='|')
incheon_pcell_sex_age['X_COORD'] = round(incheon_pcell_sex_age['X_COORD'],6)
incheon_pcell_sex_age['Y_COORD'] = round(incheon_pcell_sex_age['Y_COORD'],6)
# 인천시 동구 법정동코드 : 28140
pcell_sex_age_donggu = incheon_pcell_sex_age[(2814000000<incheon_pcell_sex_age['HCODE']) & (incheon_pcell_sex_age['HCODE']<2815000000)].reset_index(drop=True)

# 현실적으로 재활용 수거가 불가능한 섬지역 제외
pcell_sex_age_donggu = pcell_sex_age_donggu[pcell_sex_age_donggu['X_COORD']>921000]

# 동구 인근 지역 500m까지의 X,Y좌표
min_X = min(pcell_sex_age_donggu['X_COORD']-500)
max_X = max(pcell_sex_age_donggu['X_COORD'])
min_Y = min(pcell_sex_age_donggu['Y_COORD']-500)
max_Y = max(pcell_sex_age_donggu['Y_COORD'])

# 동구 인근 500m 격자까지 사용
pcell_sex_age = incheon_pcell_sex_age[(incheon_pcell_sex_age['X_COORD']>min_X)&(incheon_pcell_sex_age['X_COORD']<max_X)&(incheon_pcell_sex_age['Y_COORD']>min_Y)&(incheon_pcell_sex_age['Y_COORD']<max_Y)].reset_index(drop=True)
pcell_sex_age = pcell_sex_age.iloc[:,:46]



inProj = Proj('+proj=tmerc +lat_0=38 +lon_0=127.5 +k=0.9996 +x_0=1000000 +y_0=2000000 +ellps=GRS80 +units=m +no_defs')
outProj = Proj(init='epsg:4326')
transformer = Transformer.from_proj(inProj,outProj)

points = []
for index, item in pcell_sex_age_donggu[['X_COORD','Y_COORD']].iterrows():
       points.append((item.X_COORD, item.Y_COORD))

latlist, lnglist = [], []
for pt in transformer.itransform(points):
       latlist.append(pt[1])
       lnglist.append(pt[0])

pcell_sex_age_donggu['longitude'] = lnglist
pcell_sex_age_donggu['latitude'] = latlist

points = []
for index, item in pcell_sex_age[['X_COORD','Y_COORD']].iterrows():
       points.append((item.X_COORD, item.Y_COORD))

latlist, lnglist = [], []
for pt in transformer.itransform(points):
       latlist.append(pt[1])
       lnglist.append(pt[0])

pcell_sex_age['longitude'] = lnglist
pcell_sex_age['latitude'] = latlist

# geometry 데이터타입 생성
pcell_sex_age['geometry'] = pcell_sex_age.apply(lambda row : Point([row['X_COORD'], row['Y_COORD']]), axis=1)
pcell_sex_age = gpd.GeoDataFrame(pcell_sex_age, geometry='geometry')



melt_sex_age_donggu = pd.melt(pcell_sex_age_donggu, id_vars=['STD_YMD','HCODE','X_COORD','Y_COORD','longitude','latitude'], var_name='age')
melt_sex_age_donggu.sort_values(['STD_YMD','HCODE','X_COORD','Y_COORD'], inplace=True)

def purpose(x):
       if x[0] == 'H': return 'HOME'
       elif x[0] == 'W': return 'WORK'
       elif x[0] == 'V': return 'VISIT'

def sex(x):
       return x[2]

def age(x):
       return x[4:]

melt_sex_age_donggu['purpose'] = melt_sex_age_donggu['age'].apply(lambda x: purpose(x))
melt_sex_age_donggu['sex'] = melt_sex_age_donggu['age'].apply(lambda x: sex(x))
melt_sex_age_donggu['age'] = melt_sex_age_donggu['age'].apply(lambda x: age(x))
melt_sex_age_donggu['pop'] = melt_sex_age_donggu['value']
sex_age_total_donggu = melt_sex_age_donggu.drop('value', axis=1).reset_index(drop=True)


melt_sex_age = pd.melt(pcell_sex_age, id_vars=['STD_YMD','HCODE','X_COORD','Y_COORD','geometry','longitude','latitude'], var_name='age')
melt_sex_age.sort_values(['STD_YMD','HCODE','X_COORD','Y_COORD'], inplace=True)

melt_sex_age['purpose'] = melt_sex_age['age'].apply(lambda x: purpose(x))
melt_sex_age['sex'] = melt_sex_age['age'].apply(lambda x: sex(x))
melt_sex_age['age'] = melt_sex_age['age'].apply(lambda x: age(x))
melt_sex_age['pop'] = melt_sex_age['value']
sex_age_total = melt_sex_age.drop('value', axis=1).reset_index(drop=True)



all_dong = ['도원동','동인천동','북성동','송월동','신포동','신흥동','율목동','도화동','숭의1.3동','숭의2동','숭의4동','도화1동','용현2동','용현3동','가좌1동','가좌2동','가좌3동','가좌4동','석남2동','도화2.3동']
korea = gpd.read_file('D:/인천재활용/data/메타데이터/행정동데이터/HDONGP.shp', encoding='euc-kr')
donggu = korea[(korea['DO_NAME']=='인천광역시')&((korea['GU_NAME']=='동구')|(korea['HDONG_NAME'].isin(all_dong)))].reset_index(drop=True)
donggu.crs = '+proj=tmerc +lat_0=38 +lon_0=127.5 +k=0.9996 +x_0=1000000 +y_0=2000000 +ellps=GRS80 +units=m +no_defs'
# donggu.to_crs(epsg=4326, inplace=True)
donggu['HCODE'] = donggu['HCODE'].astype(np.int64)

donggu_geojson = donggu.to_crs(epsg=4326).to_json()




center = [37.48323,126.63000]
admin_center = [[37.48323,126.62550],[37.48154,126.62990],[37.48434,126.63017],[37.47844,126.63335],
                [37.48245,126.64264],[37.47623,126.64026],[37.47578,126.64270],[37.47473,126.64883],
                [37.47815,126.64992],[37.47731,126.64798],[37.47251,126.63984]]

m = folium.Map(location=center, zoom_start=14)
folium.Choropleth(geo_data = donggu_geojson, fill_color='BuPu', fill_opacity=0).add_to(m)

for i in range(11):
       folium.Circle(admin_center[i], radius=25, color='blue').add_to(m)
m



