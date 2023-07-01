import streamlit as st
import pandas as pd
import geopandas as gpd
import numpy as np

st.set_page_config(page_title="上传采样点数据", page_icon=":one:")

def trans_gdf_to_df(gdf):
    geom = gdf.geometry.apply(lambda x: x.wkt.replace('POINT (', '').replace(')', '').split(' '))
    geom = pd.DataFrame(geom.tolist(), columns=['lng', 'lat'])
    _data = pd.DataFrame(gdf.iloc[:, :-1])
    _data['geometry'] = geom['lng'].astype(str) + ',' + geom['lat'].astype(str)
    return _data



def init_page():
    # 添加一个文件选择器，并在选择后读取文件，获取文件的绝对路径
    subheader = st.subheader("请选择街景采样点数据，文件类型为CSV/GeoJSON")
    file = st.file_uploader(':grey_exclamation: 如果上传CSV文件，请保证经纬度数据处于第1列和第2列',type=["csv", "geojson"])
    # 读取文件，并显示在页面上，限制显示10行

    if file is not None:
        if file.name.endswith('.csv'):
            st.session_state.input_type = 'csv'
            subheader.subheader("文件上传成功！")
            data = pd.read_csv(file)
            st.session_state.input_data = data
            total_lines = len(data)
            header = st.subheader("文件预览（前5行），共{}行".format(total_lines))
            df = st.dataframe(data.head(5))
            if type(data.iloc[0,0]) != np.float64 or type(data.iloc[0,1]) != np.float64:
                st.subheader(':warning:请保证csv文件的经纬度数据处于第1列和第2列！')

        elif file.name.endswith('.geojson'):
            gdf = gpd.read_file(file)
            # 检查矢量数据是否为点数据
            if gdf.geom_type[0] != 'Point':
                st.subheader(':warning:矢量数据不是点数据，请重新选择！')
            else:
                st.session_state.input_type = 'geojson'
                subheader.subheader("文件上传成功！")
                data = trans_gdf_to_df(gdf)
                st.session_state.input_data = (data, gdf)
                total_lines = len(data)
                header = st.subheader("文件预览（前5行），共{}行".format(total_lines))
                df = st.dataframe(data.head(5))
        ## TODO 有空的话再加上shp文件的读取
        else:
            st.subheader(':warning:文件格式错误，请重新选择。')

def display_data(_data):
    # 展示文件信息
    total_lines = len(_data)
    header = st.subheader("文件预览（前5行），共{}行".format(total_lines))
    df = st.dataframe(_data.head(5))
    return header, df

if __name__ == '__main__':
    st.title("Step1: 上传街景采样点数据")
    if 'input_data' not in st.session_state.keys():
        init_page() # 这里创建了session_state.input_data
    # 当切换页面的时候
    else:
        if st.session_state is not None:
            subheader = st.subheader(":exclamation:文件已上传，如需重新上传，请点击下方按钮")
            display_input = None
            if st.session_state.input_type == 'csv':
                display_input = st.session_state.input_data
            else:
                display_input = st.session_state.input_data[0]
            header, df = display_data(display_input)
            reload = st.button("重新上传", key='reload')
            # 如果点击了重新上传按钮，就清空页面
            if reload:
                subheader.empty()
                header.empty()
                df.empty()
                for key in st.session_state.keys():
                    del st.session_state[key]
                init_page()
    if 'input_data' in st.session_state.keys():
        if st.session_state.input_data is not None:
            st.subheader(":point_left:请点击左侧菜单栏的STEP2，进行下一步操作")
