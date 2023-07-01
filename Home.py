import os

def default_proj_lib():
    proj_lib = os.getenv('PROJ_LIB')
    if proj_lib not in (None, 'PROJ_LIB'):
        return proj_lib
    try:
        import conda
    except ImportError:
        conda = None
    if conda is not None or os.getenv('CONDA_PREFIX') is None:
        conda_file_dir = conda.__file__
        conda_dir = conda_file_dir.split('lib')[0]
        proj_lib = os.path.join(os.path.join(conda_dir, 'share'), 'proj')
        if os.path.exists(proj_lib):
            return proj_lib
        return None
    return None

default_proj_lib()

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


