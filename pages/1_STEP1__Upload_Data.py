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


def display_data(_data):
    # 展示文件信息
    total_lines = len(_data)
    if total_lines > 5:
        header = st.subheader("文件预览（前5行），共{}行".format(total_lines))
    else:
        header = st.subheader("文件预览，共{}行".format(total_lines))
    df = st.dataframe(_data.head(5))
    return header, df


def check_csv(csv_df):
    if len(csv_df) == 0:
        warning = ':warning: 请勿上传空文件！'
        return False, warning
    elif (type(csv_df.iloc[0, 0]) != np.float64) or (type(csv_df.iloc[0, 1]) != np.float64):
        warning = ':warning:请保证csv文件的经纬度数据处于第1列和第2列！'
        return False, warning
    return True, None


def check_geojson_shp(geo_df):
    if len(geo_df) == 0:
        warning = ':warning: 请勿上传空文件！'
        return False, warning
    elif geo_df.geom_type[0] != 'Point':
        warning = ':warning: 请上传点数据！'
        return False, warning
    return True, None


# 上传数据页面需要用到的session_state
# input_data: 上传的数据 这个不要变了，后面会用到
# input_type: 上传的数据类型，csv/geojson
# step1_upload_pressed: 上传按钮是否被按下
# 如果没有被按下过，就创建这个key，设置值为None, 然后初始化页面, 在里面设置这个键值
# 之后检查上传数据的类型 flag
# 如果是csv，用check_csv()函数检查是否符合要求
# 如果是geojson，用check_geojson()函数检查是否符合要求

def init_page():
    subheader = st.subheader("您可以选择使用示例数据，或上传自己的数据，文件类型为CSV/GeoJSON")
    radio = st.radio("*默认使用示例数据", ['使用示例数据', '不，我要上传自己的数据'],horizontal=True)
    if radio == '使用示例数据':
        csv_data_path = './example_data/point.csv'
        geojson_data_path = './example_data/pointjson.geojson'
        radio2 = st.radio("请选择要使用的示例数据", ['CSV', 'GeoJSON'])
        if radio2 == 'CSV':
            data = pd.read_csv(csv_data_path)
            header, df = display_data(data)
            button = st.button(":exclamation: :exclamation: :exclamation: 点击确认使用该数据")
            if button:
                st.session_state.input_type = 'csv'
                st.session_state.input_data = data
        elif radio2 == 'GeoJSON':
            gdf = gpd.read_file(geojson_data_path)
            data = trans_gdf_to_df(gdf)
            header, df = display_data(data)
            button = st.button(":exclamation: :exclamation: :exclamation: 点击确认使用该数据")
            if button:
                st.session_state.input_data = (data, gdf)
                st.session_state.input_type = 'geojson'
    else:
        file = st.file_uploader(':grey_exclamation: 如果上传CSV文件，请保证经纬度数据处于第1列和第2列',
                                type=["csv", "geojson"])
        if file != st.session_state['step1_previous_file']:
            st.session_state.step1_upload_pressed = True
            if file.name.endswith('.csv'):
                st.session_state.input_type = 'csv'
                data = pd.read_csv(file)

                col = data.columns.tolist()
                col.remove(col[0])
                col.insert(0, 'lng')
                col.remove(col[1])
                col.insert(1, 'lat')
                data = pd.DataFrame(data, columns=col)

                # 检查csv文件
                flag, warning = check_csv(data)
                if (not flag) and ('空' in warning):
                    st.subheader(warning)
                    st.subheader(":point_up: 请重新上传文件")
                elif not flag:
                    display_data(data)
                    st.subheader(warning)
                    st.subheader(":point_up: 请重新上传文件")
                else:
                    header, df = display_data(data)
                    st.session_state.input_data = data
                    st.session_state.input_type = 'csv'
                    subheader.subheader("文件上传成功！")


            elif file.name.endswith('.geojson'):
                gdf = gpd.read_file(file)
                # 检查矢量数据是否为点数据
                flag, warning = check_geojson_shp(gdf)

                if not flag:
                    display_data(trans_gdf_to_df(gdf))
                    st.subheader(warning)
                    st.subheader(":point_up: 请重新上传文件")
                    # 如果点击了重新上传按钮，就清空页面

                else:
                    data = trans_gdf_to_df(gdf)
                    header, df = display_data(data)
                    st.session_state.input_data = (data, gdf)
                    st.session_state.input_type = 'geojson'
                    subheader.subheader("文件上传成功！")

            else:
                st.subheader(':warning:文件格式错误，请重新选择。')


#

if __name__ == '__main__':
    st.title("Step:one: 上传街景采样点数据")
    if 'step1_previous_file' not in st.session_state:
        st.session_state.step1_previous_file = None

    if 'input_data' not in st.session_state.keys():
        init_page()  # 这里创建了session_state.input_data
        # 如果点击了重新上传按钮，就清空页面
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
                st.session_state.step1_previous_file = None
                init_page()
    if 'input_data' in st.session_state.keys():
        if st.session_state.input_data is not None:
            st.subheader(":point_left:请点击左侧菜单栏的STEP2，进行下一步操作")
