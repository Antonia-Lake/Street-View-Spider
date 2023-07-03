import streamlit as st
import base64

st.set_page_config(page_title="百度街景数据采集+街景语义分割工具", page_icon=":house_with_garden:")
text = """
# :house_with_garden: 这是一个百度街景数据采集工具
## :one: 作者信息
<b><font size=4>姓名：来陈璐</font></b>\\
<b><font size=4>班级：21级地理科学拔尖班</font></b>
## :two: 项目简介
随着城市化进程的不断推进，城市宜居性越来越受到人们的重视，越来越多的科学证据表明，城市建成环境在影响人类健康上发挥着重要作用。街道作为城市的基础单元，受到了众多研究者的关注；其中，
<b><font color=#186cb0>街景图像（Street View Image）</font> </b>
是研究街道品质的重要数据来源，可以直观反映街道提供的视觉信息。\\
<br>
<b>但是，对于缺乏编程经验的研究者而言，获取街景图像，并从图像中获取街道评价指标具有一定的难度。</b>
首先需要熟悉网络爬虫方法；其次，为了从图像中获取准确的语义信息（也就是街景数据中主要包含的视觉信息），需要在本地部署深度学习框架，并学习相应的代码文档。\\
<br>
因此，本项目针对该痛点，开发了一个<b><font color=#186cb0>交互式网页</font></b>，
便于研究者获取<b><font color=#186cb0>街景图像</font></b>，
并根据街景图像得到常用的街道评价指标（<b><font color=#186cb0>绿视率和天空率</font></b>）。最重要的是，交互式网页<b>避免了繁琐的代码部署过程</b>，使得数据获取更加简单快捷。
"""
st.markdown(text, unsafe_allow_html=True)

text_envi = """
## :three: 环境依赖-技术路线
项目语言为:snake: **Python** 
"""
st.markdown(text_envi, unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown("""
        #### 网页部署
        - Streamlit
        - Streamlit-folium
        """)
with col2:
    st.markdown("""
        #### 数据处理
        - GeoPandas
        - Pandas
        - Folium
        """)
with col3:
    st.markdown("""
        #### 街景数据采集
        - Requests
        - Pillow
        """)
with col4:
    st.markdown("""
        #### 语义分割
        - NumPy 1.23.5
        - MXNet
        - GluonCV
        """)


st.markdown("""
## :four: 项目功能
### 4.1 使用说明
- 用户可以使用示例数据；如果想使用个人数据，需要上传街景图像的<b>经纬度位置（点数据）</b>，文件格式为
<b><font color=#478e68>CSV</font></b> 或 <b><font color=#478e68>GeoJSON</font></b>
""", unsafe_allow_html=True)

file = open(r"./gif/step1.gif", 'rb')
contents = file.read()
data_url = base64.b64encode(contents).decode('utf-8-sig')
file.close()
st.markdown(f'<img src=data:image/gif;base64,{data_url} width=500>', unsafe_allow_html=True)

st.markdown('')

st.markdown("""
- 上传数据后，需要在Step2页面确认采样点信息
""", unsafe_allow_html=True)


file = open(r"./gif/step2.gif", 'rb')
contents = file.read()
data_url = base64.b64encode(contents).decode('utf-8-sig')
file.close()
st.markdown(f'<img src=data:image/gif;base64,{data_url} width=500>', unsafe_allow_html=True)

st.markdown('')

st.markdown("""
- 之后用户可以选择需要采集的街景方位，并设置采样间隔，获取街景图像
""", unsafe_allow_html=True)

file = open(r"./gif/step3.gif", 'rb')
contents = file.read()
data_url = base64.b64encode(contents).decode('utf-8-sig')
file.close()
st.markdown(f'<img src=data:image/gif;base64,{data_url} width=500>', unsafe_allow_html=True)

st.markdown('')

st.markdown("""
- 采集数据后，使用<b>语义分割模型</b>对街景图像进行分割，得到街景中的语义内容，并<b>计算绿视率和天空率</b>
""", unsafe_allow_html=True)


file = open(r"./gif/step4_1.gif", 'rb')
contents = file.read()
data_url = base64.b64encode(contents).decode('utf-8-sig')
file.close()
st.markdown(f'<img src=data:image/gif;base64,{data_url} width=500>', unsafe_allow_html=True)

st.markdown('')

st.markdown("""
- 最后，用户可以<b>点击下载</b>采集的街景数据、语义分割结果、绿视率和天空率
""", unsafe_allow_html=True)


file = open(r"./gif/step4_2.gif", 'rb')
contents = file.read()
data_url = base64.b64encode(contents).decode('utf-8-sig')
file.close()
st.markdown(f'<img src=data:image/gif;base64,{data_url} width=500>', unsafe_allow_html=True)

st.markdown('')

st.markdown("""
- 下图为获得的街景和语义分割图像
""", unsafe_allow_html=True)

st.markdown('![image](https://github.com/Antonia-Lake/Street-View-AOI-Spider/blob/main/gif/download.png)')
st.markdown('')

st.markdown("""
### 4.2 项目稳定性

""")


st.markdown("""
## :five: 如果您对该项目感兴趣
- 您可以访问我的[项目仓库](https://github.com/Antonia-Lake/Street-View-AOI-Spider)，查看源代码
- 如果您希望对该项目进行改进，欢迎fork项目并提交pull request
- 如果您希望将项目部署到本地
    - 建议使用`conda`创建虚拟环境，建议Python版本为3.9
    - 您可以使用以下命令安装创建虚拟环境，并安装项目所需的依赖包
    ```cmd
    conda create -n streetview python=3.9
    pip install -r requirements.txt
    ```
""")
