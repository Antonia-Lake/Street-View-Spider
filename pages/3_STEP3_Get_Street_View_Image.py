import streamlit as st
import subprocess
import time
import os
import glob
import tempfile
import zipfile
import sys

sys.path.append('..')
import GetBaiduStreetView as gbsv


def check_steps():
    if 'input_data' not in st.session_state.keys():
        warning = st.title(':warning:请先在STEP1 Upload Data页面\n# 上传采样点数据！')
        return False, warning
    elif 'draw_map' not in st.session_state.keys():
        warning = st.title(':warning:请先浏览STEP2页面\n# 确认采样点位置！')
        return False, warning
    else:
        return True, None


def get_baidu_sv_image():
    '''
    :return: tempfile.TemporaryDirectory(), st.progress(), list, list
    '''
    if 'image_dataset' in st.session_state:
        del st.session_state['image_dataset']
    st.session_state.image_dataset = None

    my_bar = st.progress(0, text='### 开始爬取...')
    st.experimental_set_query_params(disabled=True)
    root = tempfile.TemporaryDirectory()

    img_error_fn = 'error_road_intersection.csv'
    svid_error_fn = 'svid_none.csv'

    data = None
    if st.session_state.input_type == 'geojson' or st.session_state.input_type == 'shp':
        data = st.session_state.input_data[0]
    else:
        data = st.session_state.input_data

    header = data.columns.tolist()

    error_img = []
    svid_none = []

    directions = []
    pitchs = '0'
    count = 1

    for key in st.session_state.direction.keys():
        if key == "north" and st.session_state.direction[key]:
            directions.append('0')
        if key == "east" and st.session_state.direction[key]:
            directions.append('90')
        if key == "south" and st.session_state.direction[key]:
            directions.append('180')
        if key == "west" and st.session_state.direction[key]:
            directions.append('270')

    for i in range(len(data)):
        progress_text = '### 正在爬取第{}个采样点...'.format(i + 1)
        progress_float = round(i / len(data), 3)
        my_bar.progress(progress_float, text=progress_text)
        # st.write('爬取Point No. {}...'.format(i + 1))
        wgs_x, wgs_y = data.iloc[i, 0], data.iloc[i, 1]

        try:
            bd09mc_x, bd09mc_y = gbsv.wgs_to_bd09mc(wgs_x, wgs_y)
        except Exception as e:
            st.write(str(e))
        flag = True

        # 设置不重复爬取
        # for k in range(len(directions)):
        #     flag = flag and "%s_%s_%s_%s.png" % (wgs_x, wgs_y, directions[k], pitchs) in filenames_exist
        # if flag:
        #     st.write('\t所有图片已存在，不进行重复爬取。'.format(i + 1))
        #     continue

        svid = gbsv.get_svid(bd09mc_x, bd09mc_y)
        if svid is None:
            # st.write('\t获取svid失败！')
            svid_none.append([wgs_x, wgs_y])
        # else:
        #     st.write('\tsvid: {}'.format(svid))

        for h in range(len(directions)):
            # save_fn = os.path.join(root, img_dir, '%s_%s_%s_%s.png' % (wgs_x, wgs_y, directions[h], pitchs))
            url = 'https://mapsv0.bdimg.com/'
            params = {
                'qt': 'pr3d',
                'fovy': 90,
                'quality': 100,
                'panoid': svid,
                'heading': directions[h],
                'pitch': 0,
                'width': 480,
                'height': 320
            }
            img = gbsv.get_street_view_image(url, params)

            if img is None:
                error_data = data.iloc[i, :].tolist()
                error_data.append(directions[h])
                error_img.append(error_data)

            if img is not None:
                # 在本地请用这个代码
                with open(os.path.join(root.name) + r'\%s_%s_%s_%s.png' % (wgs_x, wgs_y, directions[h], pitchs),
                          "wb") as f:
                    f.write(img)
                ## 在服务器上请用这个代码
                # with open(os.path.join(root.name,r'\%s_%s_%s_%s.png' % (wgs_x, wgs_y, directions[h], pitchs)),
                #           "wb") as f:
                #     f.write(img)

            progress_float = round((i * len(directions) + h + 1) / (len(data) * len(directions)), 3)
            progress_text = '### 爬取进度：{:.2f}%'.format(progress_float * 100)
            my_bar.progress(progress_float, text=progress_text)
        time.sleep(st.session_state.interval)
        count += 1
    if len(svid_none) > 0:
        gbsv.write_csv(os.path.join(root.name, svid_error_fn), svid_none, header)
    if len(error_img) > 0:
        gbsv.write_csv(os.path.join(root.name, img_error_fn), error_img, header)
    st.session_state.submitted = True

    st.experimental_set_query_params(disabled=False)
    st.session_state.image_dataset = root
    # TODO 这里的st.session_state.image_dataset保存的是所有图片的路径，可以通过Image.read()读取图片
    return my_bar, svid_none, error_img



if __name__ == '__main__':
    check = check_steps()
    if check[0]:
        st.title("Step:three: 获取街景图片")
        with st.form(key='my_form'):
            st.markdown("#### 选择需要获取的街景图像拍摄方位（默认全部获取）")
            if 'direction' not in st.session_state.keys():
                st.session_state.direction = {
                    'north': True,
                    'south': True,
                    'east': True,
                    'west': True
                }
                st.session_state.interval = 6
            if 'submitted' not in st.session_state.keys():
                st.session_state.submitted = False

            directions = st.session_state.direction
            north = st.checkbox("正北", value=directions['north'])
            south = st.checkbox("正南", value=directions['south'])
            east = st.checkbox("正东", value=directions['east'])
            west = st.checkbox("正西", value=directions['west'])
            interval = st.slider("#### 选择采样间隔（默认6s，最低3s），间隔过小可能采样失败", 3, 30, 6)
            if not (True in st.session_state.direction.values()):
                submitted = st.form_submit_button("请重新提交数据，至少选择一个方向，点击后开始采集数据")
            else:
                submitted = st.form_submit_button("点击提交数据，开始采集数据")  # 用于提交表单

        # 当提交按钮被点击时
        if submitted:
            # 将checkbox的状态保存到st.session_state中的一个键值对中
            st.session_state.direction = {
                'north': north,
                'south': south,
                'east': east,
                'west': west
            }
            st.session_state.interval = interval

        if 'direction' in st.session_state.keys():
            dir = st.session_state.direction
            st.session_state.direction = dir
            intv = st.session_state.interval
            st.session_state.interval = intv

        if not (True in st.session_state.direction.values()):
            st.subheader(":warning:请至少选择一个方位！")
            st.session_state.submitted = False
        elif submitted:
            # 删除之前的数据
            st.subheader("数据已提交，开始采集数据...")
            st.subheader(":exclamation:请耐心等待，采集过程中请勿切换界面...")
            st.experimental_set_query_params(disabled=True)
            # 在后台运行程序
            st.session_state.mybar, st.session_state.svid_none, st.session_state.erro_img = get_baidu_sv_image()

        if st.session_state.submitted:
            svid_none = st.session_state.svid_none
            erro_img = st.session_state.erro_img
            if st.session_state.input_type == 'csv':
                count = len(st.session_state.input_data)
            elif st.session_state.input_type == 'geojson':
                count = len(st.session_state.input_data[0])
            st.markdown('数据采集完成！共爬取{}个点，其中{}个点获取svid失败，{}个点获取图片失败。'
                         .format(count, len(svid_none), len(erro_img)))
            st.subheader(":point_left:请点击左侧菜单栏的STEP4，进行下一步操作")
