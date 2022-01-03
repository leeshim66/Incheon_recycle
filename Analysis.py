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
