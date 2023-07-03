import os
from PIL import Image
import streamlit as st
import mxnet as mx
from mxnet import image
import gluoncv
import matplotlib.pyplot as plt
from gluoncv.data.transforms.presets.segmentation import test_transform
from gluoncv.utils.viz import get_color_pallete, plot_image
import matplotlib.image as mpimg
import numpy as np
import pandas as pd
import geopandas as gpd
import tempfile
import zipfile

# using cpu
ctx = mx.cpu()

st.set_page_config(page_title="获取绿视率和天空率", page_icon=":four:")


def check_steps():
    if 'input_data' not in st.session_state.keys():
        warning = st.title(':warning:请先在STEP1 Upload Data页面\n# 上传采样点数据！')
        return False, warning
    elif 'draw_map' not in st.session_state.keys():
        warning = st.title(':warning:请先浏览STEP2页面\n# 确认采样点位置！')
        return False, warning
    elif 'image_dataset' not in st.session_state.keys():
        warning = st.title(':warning:请先浏览STEP3页面\n# 获取街景图像！')
        return False, warning
    else:
        return True, None


@st.cache_resource
def generate_model(model_path='./model'):
    return gluoncv.model_zoo.get_model('deeplab_resnet101_citys', pretrained=True, root=model_path)


def calculate_green_sky(output, show=True):
    predict = mx.nd.squeeze(mx.nd.argmax(output, 1)).asnumpy()
    green = (predict == 8)
    green_rate = len(predict[green]) / (predict.shape[0] * predict.shape[1])
    sky = (predict == 10)
    sky_rate = len(predict[sky]) / (predict.shape[0] * predict.shape[1])

    mask = get_color_pallete(predict, 'citys')
    if show:
        st.image(mask, use_column_width=True)
    return mask, green_rate, sky_rate


def create_zip(temp_dir, zip_fn, include_csv):
    '''
    将temp_dir中的文件打包成zip文件, 记得要将zip_root.cleanup()
    :param temp_dir: TemporaryDirectory
    :param zip_fn: str
    :param include_csv: bool
    :return: zip_data, zip_root
    '''
    zip_root = tempfile.TemporaryDirectory()
    zip_file = os.path.join(zip_root.name, zip_fn)

    with zipfile.ZipFile(zip_file, 'w') as zipf:
        for r, d, files in os.walk(temp_dir.name):
            for file in files:
                if include_csv:
                    if file.endswith('.png') or file.endswith('.csv'):
                        file_path = os.path.join(r, file)  # 获取文件的绝对路径
                        arc_name = file_path[len(temp_dir.name) + 1:]
                        zipf.write(file_path, arcname=arc_name)
                else:
                    if file.endswith('.png'):
                        file_path = os.path.join(r, file)
                        arc_name = file_path[len(temp_dir.name) + 1:]
                        zipf.write(file_path, arcname=arc_name)

    with open(zip_file, 'rb') as f:
        zip_data = f.read()

    return zip_data, zip_root


def create_result(green_sky_df):
    '''
    将green_sky_df转换成csv或geojson文件, 记得要将temp_result_dir.cleanup()
    :param green_sky_df:
    :return:
    '''
    temp_result_dir = tempfile.TemporaryDirectory()

    if st.session_state.input_type == 'csv':
        green_sky_df.to_csv(os.path.join(temp_result_dir.name, 'green_sky_rate.csv'), index=False)
    elif st.session_state.input_type == 'geojson':
        gdf = trans_df_to_gdf(green_sky_df)
        gdf.to_file(os.path.join(temp_result_dir.name, 'green_sky_rate.geojson'), driver='GeoJSON')

    if st.session_state.input_type == 'csv':
        with open(os.path.join(temp_result_dir.name, 'green_sky_rate.csv'), 'rb') as f:
            result_data = f.read()
    elif st.session_state.input_type == 'geojson':
        with open(os.path.join(temp_result_dir.name, 'green_sky_rate.geojson'), 'rb') as f:
            result_data = f.read()

    return result_data, temp_result_dir


def create_mask_and_rate():
    '''

    :return: green_sky_df, img_mask_green_sky_df, mask_temp_dir
    '''

    # 这个是存mask的临时文件夹
    temp_dir = tempfile.TemporaryDirectory()

    img_mask_green_sky_df = pd.DataFrame(columns=['mask_path', 'green_rate', 'sky_rate'])

    if st.session_state.input_type == 'csv':
        green_sky_df = st.session_state.input_data
    else:
        green_sky_df = st.session_state.input_data[0]

    # 为dataframe创建空列
    for d in st.session_state.direction:
        if d == '0':
            green_sky_df['n_gre'] = np.nan
            green_sky_df['n_sky'] = np.nan
        elif d == '90':
            green_sky_df['e_gre'] = np.nan
            green_sky_df['e_sky'] = np.nan
        elif d == '180':
            green_sky_df['s_gre'] = np.nan
            green_sky_df['s_sky'] = np.nan
        elif d == '270':
            green_sky_df['w_gre'] = np.nan
            green_sky_df['w_sky'] = np.nan

    model = generate_model()

    for r, d, files in os.walk(st.session_state.image_dataset.name):
        for file in files:
            if file.endswith('.png'):
                img_path = os.path.join(r, file)
                img = image.imread(img_path)
                output = model.predict(test_transform(img, ctx))
                _mask, _green, _sky = calculate_green_sky(output, show=False)

                _mask_fn = file.split('.png')[0] + '_mask.png'
                _mask_pth = os.path.join(temp_dir.name, _mask_fn)
                img_mask_green_sky_df.loc[file.replace('\\','')] = [_mask_pth, _green, _sky]
                _mask.save(_mask_pth)
                lng, lat, dir = file.split('_')[:3]

                # lng = float(lng)
                # lat = float(lat)

                lng = float(lng.replace('\\', ''))
                lat = float(lat.replace('\\', ''))

                if dir == '0':
                    dir = 'n_'
                elif dir == '90':
                    dir = 'e_'
                elif dir == '180':
                    dir = 's_'
                elif dir == '270':
                    dir = 'w_'
                green_sky_df.loc[(green_sky_df['lng'] == lng) & (green_sky_df['lat'] == lat), dir + 'gre'] = _green
                green_sky_df.loc[(green_sky_df['lng'] == lng) & (green_sky_df['lat'] == lat), dir + 'sky'] = _sky

    return green_sky_df, img_mask_green_sky_df, temp_dir


def trans_df_to_gdf(df):
    df_ = df.drop(columns=['geometry'], inplace=False)
    gdf = gpd.GeoDataFrame(df_, geometry=gpd.points_from_xy(df_.lng, df_.lat))
    gdf.crs = 'EPSG:4326'
    return gdf


def mark_downloaded():
    if "download" not in st.session_state.keys():
        st.session_state.download = False
    else:
        st.session_state.download = True


if __name__ == '__main__':
    check = check_steps()
    # 本页面中用到的session_state如下：
    # image_dataset: 用于存储街景图像的文件夹，从STEP3中获取
    # file_name_list: 用于存储街景图像的文件名，从STEP3中获取
    # 如果没有这个key，说明没有获取过，需要获取

    # segment_completed: 用于标记是否已经读取过model
    # 如果没有读取过，那么session_state中没有这个key
    # 如果读取过，就有这个key

    # step4_selectbox_result: 用于存储上一次选择的街景图像的文件名
    # 数据类型为 tuple (img_file, mask, green_rate, sky_rate)
    # 如果没有选择过，那么session_state中没有这个key，就需要读取第一张街景图像，并创建这个key
    # 如果选择过，那么就有这个key，并且value为上一次选择的计算结果
    # 所以页面显示的逻辑是：

    if check[0]:
        st.title('Step:four: 获取绿视率和天空率')

        # 先获取街景图像的文件名列表
        
        if 'file_name_list' not in st.session_state.keys():
            st.session_state.file_name_list = []
            for r, d, files in os.walk(st.session_state.image_dataset.name):
                for file in files:
                    if file.endswith('.png'):
                        st.session_state.file_name_list.append(file)

        # 如果没有街景图像，说明没有成功获取
        if len(st.session_state.file_name_list) == 0:
            st.title(':warning: 抱歉！未能成功获取街景图像！无法计算绿视率和天空率！')
            st.subheader(
                '这可能是因为您曾经在STEP3未运行结束时切换了页面，导致程序中断。请您返回STEP1，重新上传采样点数据。')

        # 如果有街景图像，那么就继续
        else:
            # 先判断是否已经分割和计算过绿视率和天空率 segment_completed
            if 'step4_selectbox_result' not in st.session_state.keys():
                temp_notice = st.markdown(
                    '##### :exclamation: 语义分割结果、绿视率和天空率正在计算中，可能需要一些时间，请耐心等待...')

                st.session_state['green_sky_df'], st.session_state['mask'], st.session_state[
                    'mask_dataset'] = create_mask_and_rate()
                temp_notice.empty()

            file_name_list = st.session_state.file_name_list
            st.subheader('可下拉框中选择一张街景图像，预览结果')

            option = st.selectbox(
                "默认显示第一张街景图像的语义分割结果，并计算绿视率和天空率",
                file_name_list
            )

            img_path = os.path.join(st.session_state.image_dataset.name, option)
            img_temp = Image.open(img_path)

            col1, col2 = st.columns(2)
            with col1:
                st.markdown('#### :point_down:街景图像')
                st.image(img_temp, use_column_width=True)
            with col2:
                results = st.session_state.mask.loc[option.replace('\\', ''), :].values
                st.markdown('#### :point_down:语义分割结果')
                mask = Image.open(results[0])
                green_rate = results[1]
                sky_rate = results[2]
                st.image(mask, use_column_width=True)

            img_temp.close()
            mask.close()

            st.markdown('#### :deciduous_tree: 绿视率: {:.2f}%'.format(green_rate * 100))
            st.markdown('#### :sunrise: 天空率: {:.2f}%'.format(sky_rate * 100))

            st.session_state.step4_selectbox_result = True
            st.markdown('')


            st.markdown('#### 我们在原数据的基础上，添加了不同方向的绿视率、天空率字段')
            st.markdown('如： <b><font color=green>n_gre</font></b> 字段代表正北方向的绿视率， <b><font color=green>n_sky</font></b> 字段代表正北方向的天空率',unsafe_allow_html=True)
            st.dataframe(st.session_state.green_sky_df.head(5))

            st.markdown('#### 如果您想获取所有街景图像的语义分割结果、绿视率和天空率')
            st.markdown('#### :point_down: 请点击下方按钮')

            svdata = create_zip(st.session_state.image_dataset, 'street_view_data.zip', True)
            st.download_button(
                label="点击下载街景图片和错误信息压缩包(.zip)",
                data=svdata[0],
                file_name='street_view_data.zip',
                mime='application/zip',
                key='svdata'
            )

            segdata = create_zip(st.session_state.mask_dataset, 'segmentation_result.zip', False)
            st.download_button(
                label="点击下载语义分割图像(.zip)",
                data=segdata[0],
                file_name='segmentation_result.zip',
                mime='application/zip',
                key='segdata'
            )

            if st.session_state.input_type == 'geojson':
                mime_ = 'application/json'
            elif st.session_state.input_type == 'csv':
                mime_ = 'text/csv'

            ratedata = create_result(st.session_state['green_sky_df'])
            st.download_button(
                label="点击下载带有绿视率和天空率的原始信息(.{})".format(st.session_state.input_type),
                data=ratedata[0],
                file_name='original_data_with_rate.{}'.format(st.session_state.input_type),
                mime=mime_,
                key='rate'
            )

            st.markdown('#### 到这里，您已经完成了所有的步骤:sparkling_heart:')
            st.markdown(
                '#### 如果您喜欢这个项目，欢迎star:star:[我的GitHub仓库](https://github.com/Antonia-Lake/Street-View-AOI-Spider):hugging_face:')

            # st.session_state.model_loaded = None
