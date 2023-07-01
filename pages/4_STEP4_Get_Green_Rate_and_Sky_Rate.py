import os
from PIL import Image
import streamlit as st
import mxnet as mx
from mxnet import image
import gluoncv
import matplotlib.pyplot as plt
from gluoncv.data.transforms.presets.segmentation import test_transform
from gluoncv.utils.viz import get_color_pallete,plot_image
import matplotlib.image as mpimg
import numpy as np
import pandas as pd
import geopandas as gpd
# using cpu
ctx = mx.cpu()

def check_steps():
    if 'input_data' not in st.session_state.keys():
        warning = st.title(':warning:请先在STEP1 Upload Data页面\n# 上传采样点数据！')
        return False, warning
    elif 'draw_map' not in st.session_state.keys():
        warning = st.title(':warning:请先浏览STEP2页面\n# 确认采样点位置！')
        return False, warning
    elif 'images' not in st.session_state.keys():
        warning = st.title(':warning:请先浏览STEP3页面\n# 获取街景图像！')
        return False, warning
    else:
        return True, None

def generate_model(model_path='./model'):
    # model = gluoncv.model_zoo.get_model('deeplab_resnet101_citys', pretrained=True, root=model_path)
    model = gluoncv.model_zoo.get_model('deeplab_resnet101_citys', pretrained=True)
    return model

def first_segementation(model):
    '''
    :param img_path:
    :param model: a pre-defined model
    :return:
    '''
    st.session_state.green_rate = []
    for r, d, files in os.walk(st.session_state.images.name):
        for file in files:
            img = image.imread(os.path.join(r, file))
            img = test_transform(img, ctx)
            output = model.predict(img)
            predict = mx.nd.squeeze(mx.nd.argmax(output, 1)).asnumpy()
            green_rate = (predict==8)
            sky_rate = (predict==10)


def segment_single_pic(img_path, model):
    img = image.imread(img_path)
    img = test_transform(img, ctx)
    output = model.predict(img)
    predict = mx.nd.squeeze(mx.nd.argmax(output, 1)).asnumpy()
    green = (predict == 8)
    green_rate = len(predict[green]) / (predict.shape[0] * predict.shape[1])
    sky= (predict == 10)
    sky_rate = len(predict[sky]) / (predict.shape[0] * predict.shape[1])

    mask = get_color_pallete(predict, 'citys')
    st.image(mask, use_column_width=True)
    return mask, green_rate, sky_rate




if __name__ == '__main__':
    check = check_steps()
    # 本页面中用到的session_state如下：
    # image_dataset: 用于存储街景图像的文件夹，从STEP3中获取
    # file_name_list: 用于存储街景图像的文件名，从STEP3中获取
        # 如果没有这个key，说明没有获取过，需要获取

    # model_loaded: 用于标记是否已经读取过model
        # 如果没有读取过，那么session_staet中没有这个key
        # 如果读取过，就有这个key，并且value为读取的模型

    # step4_selectbox_result: 用于存储上一次选择的街景图像的文件名
        # 数据类型为 tuple (img_file, mask, green_rate, sky_rate)
        # 如果没有选择过，那么session_state中没有这个key，就需要读取第一张街景图像，并创建这个key
        # 如果选择过，那么就有这个key，并且value为上一次选择的计算结果
    # 所以页面显示的逻辑是：

    if check[0]:
        st.title('STEP4: 获取绿视率和天空率')

        # 先获取街景图像的文件名列表
        if 'file_name_list' not in st.session_state.keys():
            st.session_state.file_name_list = []
            for r, d, files in os.walk(st.session_state.image_dataset.name):
                for file in files:
                    if file.endswith('.png'):
                        st.session_state.file_name_list.append(file)

        # 如果没有街景图像，说明没有成功获取
        if len(st.session_state.file_name_list) == 0:
            st.title(':warning: 不好意思！未能成功获取街景图像！无法计算绿视率和天空率！')

        # 如果有街景图像，那么就继续
        else:
            # 如果没有加载过模型，那么就加载模型
            if 'model_loaded' not in st.session_state.keys():
                st.session_state.model_loaded = generate_model()

            file_name_list = st.session_state.file_name_list
            st.subheader('请在下拉框中选择一张街景图像')

            option = st.selectbox(
                "默认显示第一张街景图像的语义分割结果，并计算绿视率和天空率",
                file_name_list
            )

            # 如果没有选择过，那么就读取第一张街景图像，并创建这个key
            if ('step4_selectbox_result' not in st.session_state.keys()) or (option != st.session_state.step4_selectbox_result[0]):
                img_path = os.path.join(st.session_state.image_dataset.name, option)
                img_temp = Image.open(img_path)

                col1, col2 = st.columns(2)
                with col1:
                    st.markdown('#### :point_down:街景图像', )
                    st.image(img_temp, use_column_width=True)
                with col2:
                    st.markdown('#### :point_down:语义分割结果')
                    mask, green_rate, sky_rate = segment_single_pic(img_path, st.session_state.model_loaded)

                st.markdown('#### :deciduous_tree: 绿视率: {:.2f}%'.format(green_rate * 100))
                st.markdown('#### :sunrise: 天空率: {:.2f}%'.format(sky_rate * 100))

                st.session_state.step4_selectbox_result = (option, mask, green_rate, sky_rate)
                st.markdown('')

                img_temp.close()
                mask = None

                st.markdown('##### 如果您想获取所有街景图像的语义分割结果、绿视率和天空率')
                st.markdown('#### :point_down: 请点击下方按钮')

            else:
                img_path, mask, green_rate, sky_rate = st.session_state.step4_selectbox_result
                img_path = os.path.join(st.session_state.image_dataset.name, img_path)
                img_temp = Image.open(img_path)
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown('#### :point_down:街景图像', )
                    st.image(img_temp, use_column_width=True)
                with col2:
                    st.markdown('#### :point_down:语义分割结果')
                    st.image(mask, use_column_width=True)

                img_temp.close()
                mask = None

                st.markdown('#### :deciduous_tree: 绿视率: {:.2f}%'.format(green_rate * 100))
                st.markdown('#### :sunrise: 天空率: {:.2f}%'.format(sky_rate * 100))

                st.markdown('')

                st.markdown('##### 如果您想获取所有街景图像的语义分割结果、绿视率和天空率')
                st.markdown('#### :point_down: 请点击下方按钮')


