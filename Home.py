import streamlit as st
import pandas as pd
import geopandas as gpd

st.set_page_config(page_title="百度街景数据采集工具", page_icon=":house_with_garden:")
text = """
# :house_with_garden: 这是一个百度街景数据采集工具
## 作者信息
姓名：来陈璐\\
学号：10202150412\\
班级：21级地理科学拔尖班
## 项目简介
本项目是一个百度街景数据采集工具，可以通过输入一个点数据文件，自动采集该点附近的街景数据，并将采集结果保存为一个csv文件。

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


