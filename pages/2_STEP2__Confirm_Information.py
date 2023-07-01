import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
import streamlit as st
from streamlit_folium import st_folium


def draw_map(_data):
    '''
    绘制地图
    :param _data: pd.Dataframe
    :return: st_folium
    '''
    m = folium.Map()
    lnglat_lists = []
    for i in range(len(_data)):
        lnglat_lists.append([_data.iloc[i, 1], _data.iloc[i, 0]])
        folium.Marker(
            lnglat_lists[-1],
            tooltip="lng: {}, lat: {}".format(_data.iloc[i, 0], _data.iloc[i, 1])
        ).add_to(m)
    m.fit_bounds(lnglat_lists)
    # call to render Folium map in Streamlit
    st_data = st_folium(m, width=725, height=350)
    return st_data


def trans_gdf_to_df(gdf):
    geom = gdf.geometry.apply(lambda x: x.wkt.replace('POINT (', '').replace(')', '').split(' '))
    geom = pd.DataFrame(geom.tolist(), columns=['lng', 'lat'])
    _data = pd.DataFrame(gdf.iloc[:, :-1])
    _data['geometry'] = geom['lng'].astype(str) + ',' + geom['lat'].astype(str)
    return _data


if __name__ == '__main__':
    st.set_page_config(page_title="确认采样点位置", page_icon=":two:")
    if 'input_data' not in st.session_state.keys():
        st.title(":warning:请先在STEP1 Upload Data页面\n# 上传采样点数据！")
    else:
        if st.session_state.input_data is None:
            st.title(":warning:请先在STEP1 Upload Data页面\n# 上传采样点数据！")
        else:
            if 'draw_map' not in st.session_state.keys():
                st.session_state.draw_map = False
            else:
                st.session_state.draw_map = True
            st.title("Step:two: 确认采样点位置")
            st.subheader(":point_down:下图为采样点位置分布图")
            if st.session_state.input_type == 'geojson':
                text = """
                - 上传的文件类型为`GeoJSON`，如果下方地图无法显示，请打开**VPN**
                - :grey_exclamation: 已自动设置数据的地理坐标系为`WGS84`，请检查采样点位置是否正确 
                """
                st.markdown(text)
                if st.session_state.draw_map:
                    st_data = draw_map(st.session_state.input_data[0])
                else:
                    gdf = st.session_state.input_data[1]
                    gdf = gdf.to_crs(epsg=4326)
                    data = trans_gdf_to_df(gdf)
                    st.session_state.input_data = (data, gdf)
                    st_data = draw_map(data)

            if st.session_state.input_type == 'csv':
                text = """
                - 上传的文件类型为`CSV`，如果下方地图无法显示，请打开**VPN**
                - :grey_exclamation: 请再次确认点数据的地理坐标系为`WGS84`，请检查采样点位置是否正确 
                """
                st.markdown(text)
                data = st.session_state.input_data
                st_data = draw_map(data)
                # TODO 有空的话，可以加一个转换坐标系的功能
            st.subheader(':point_left:请点击左侧菜单栏的STEP3，进行下一步操作')
