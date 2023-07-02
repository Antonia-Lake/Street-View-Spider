import streamlit as st
import pandas as pd
import geopandas as gpd

st.set_page_config(page_title="百度街景数据采集工具", page_icon=":house_with_garden:")
text = """
# :house_with_garden: 这是一个百度街景数据采集工具
## 作者信息
姓名：来陈璐\\
班级：21级地理科学拔尖班
## 项目简介
- 本项目是一个百度街景数据采集工具。用户可以上传一个点数据文件（**CSV/GeoJSON**），自动采集该点附近四个方向（东南西北）的街景数据。
- 采集数据后，会使用语义分割模型对街景图像进行分割，得到街景中的语义内容，并计算绿视率和天空率。
- 最后，用户可以下载采集的街景数据、语义分割结果、绿视率和天空率。

## 环境依赖
- Anaconda
- Python 建议3.7以上
- Streamlit
- Streamlit-folium
- Folium
- Geopandas
- Requests
- Pandas
## 使用方法

"""

st.markdown(text)
