import os
import json
import requests
import time, glob
import csv
import pandas as pd
import geopandas as gpd


def check_library():
    try:
        import geopandas as gpd
        print("GeoPandas库已安装。")
    except ImportError:
        print("ERROR: GeoPandas库未安装。")
    try:
        import requests
        print("Requests库已安装。")
    except ImportError:
        print("ERROR: Requests库未安装。")
    try:
        import pandas as pd
        print("Pandas库已安装。")
    except ImportError:
        print("ERROR: Pandas库未安装。")


# write csv
def write_csv(filepath, data, head=None):
    if head:
        data = [head] + data
    with open(filepath, mode='w', encoding='UTF-8-sig', newline='') as f:
        writer = csv.writer(f)
        for i in data:
            writer.writerow(i)


# 读取文件（文件类型可以是csv, shp, geojson），返回dataframe
def read_data(filepath, encoding='utf-8', lng_col=0, lat_col=1, filename_col=None):
    data = None
    if os.path.exists(filepath):

        if filepath.endswith('.csv'):
            df = pd.read_csv(filepath, encoding=encoding)
            if filename_col is None:
                data = pd.DataFrame(df.iloc[:, [lng_col, lat_col]])
                data['filename'] = data.iloc[:,lng_col].astype(str) + ',' + data.iloc[:,lat_col].astype(str)
            else:
                data['filename'] = data.iloc[:, filename_col]
            return data

        elif filepath.endswith('.geojson') or filepath.endswith('.shp'):
            gdf = gpd.read_file(filepath, encoding=encoding)
            lng_lat = gdf.geometry.apply(lambda x: x.wkt.replace('POINT (', '').replace(')', '').split(' '))
            data = pd.DataFrame(lng_lat.tolist(), columns=['lng', 'lat'])
            if filename_col is None:
                data['filename'] = data['lng'].astype(str) + ',' + data['lat'].astype(str)
            else:
                data['filename'] = gdf.iloc[:, filename_col]
            return data
    else:
        print('文件路径错误：{}'.format(filepath))
        return data


def get_street_view_image(_url, _params, _headers=None):
    if _headers == None:
        # 设置请求头 request header
        headers = {
            "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="90", "Google Chrome";v="90"',
            "Referer": "https://map.baidu.com/",
            "sec-ch-ua-mobile": "?0",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36"
        }
    else:
        headers = _headers
    response = requests.get(_url, params=_params, headers=headers)

    if response.status_code == 200 and response.headers.get('Content-Type') == 'image/jpeg':
        return response.content
    else:
        return None


def open_url_with_head(_url, _params=None):
    # 设置请求头 request header
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36"
    }
    response = requests.get(_url, params=_params, headers=headers)
    if response.status_code == 200:  # 状态码为200，说明服务器成功处理请求
        return response.content
    else:
        return None

# 获取百度街景中的svid
def get_svid(_x, _y):
    url = "https://mapsv0.bdimg.com/"
    params = {
        'qt': 'qsdata',
        'x': _x,
        'y': _y,
        # 'l': 17.031000000000002, # 17.031000000000002代表百度街景的缩放级别
        'l': 18,
        'action': 0, # 0代表获取svid
        'mode': 'day', # day代表白天
        't': 1530956939770 # 时间戳，
    }
    response = open_url_with_head(url, params).decode("utf8")
    if (response == None):
        return None
    try:
        svid_json = json.loads(response)
        svid = svid_json['content']['id']
        return svid
    except:
        return None


# 将wgs84坐标转换为百度墨卡托投影bd09mc，因为百度街景获取时采用的是bd09mc
def wgs_to_bd09mc(wgs_x, wgs_y):
    url = 'http://api.map.baidu.com/geoconv/v1/'
    params = {
        'ak': 'Vz42KalZBiDzK5j53idbt1uUIv0uggus',
        'coords': str(wgs_x) + ',' + str(wgs_y),
        'from': 1, # 1代表wgs84坐标系
        'to': 6,   # 6代表bd09mc坐标系
        'output': 'json'
    }
    response = requests.get(url, params=params)
    temp = response.json()
    bd09mc_x = 0
    bd09mc_y = 0
    if temp['status'] == 0:
        bd09mc_x = temp['result'][0]['x']
        bd09mc_y = temp['result'][0]['y']
    return bd09mc_x, bd09mc_y

def GetBaiduStreetView(data_fn):
    root = './dir'
    img_error_fn = 'error_road_intersection.csv'
    svid_error_fn = 'svid_none.csv'
    img_dir = r'images'

    filenames_exist = glob.glob1(os.path.join(root, img_dir), "*.png")

    # 读取 csv 文件
    data = read_data(data_fn)
    # 记录 header
    header = data.columns.tolist()
    # 记录爬取失败的图片
    error_img = []
    # 记录没有svid的位置
    svid_none = []

    directions = ['0', '90', '180', '270']  # 方向，0代表正北，90代表正东，180代表正南，270代表正西
    pitchs = '0'

    count = 1

    print('开始爬取...')
    for i in range(len(data)):
        print('爬取Point No. {}...'.format(i + 1))
        wgs_x, wgs_y = data.iloc[i, 0], data.iloc[i, 1]

        try:
            bd09mc_x, bd09mc_y = wgs_to_bd09mc(wgs_x, wgs_y)
        except Exception as e:
            print(str(e))  # 抛出异常的原因
            continue
        flag = True

        # 设置不重复爬取，如果四个方向的图片都已经在./dir/image文件夹中，则跳过
        for k in range(len(directions)):
            flag = flag and "%s_%s_%s_%s.png" % (wgs_x, wgs_y, directions[k], pitchs) in filenames_exist

        # If all four files exist, skip
        if (flag):
            print('\t所有图片已存在，不进行重复爬取。'.format(i + 1))
            continue

        svid = get_svid(bd09mc_x, bd09mc_y)
        if svid is None:
            svid_none.append(data.iloc[:,i].tolist())
        print('\t svid:{}'.format(svid))

        for h in range(len(directions)):
            save_fn = os.path.join(root, img_dir, '%s_%s_%s_%s.png' % (wgs_x, wgs_y, directions[h], pitchs))
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
            img = get_street_view_image(url, params)

            if img == None:
                error_data = data.iloc[:, i].tolist()
                error_data.append(directions[h])
                error_img.append(error_data)

            if img != None:
                with open(os.path.join(root, img_dir) + r'\%s_%s_%s_%s.png' % (wgs_x, wgs_y, directions[h], pitchs),
                          "wb") as f:
                    f.write(img)

        # 睡眠6s，太快可能会被封
        time.sleep(6)
        count += 1

    # 说明没有svid的位置
    if len(svid_none) > 0:
        write_csv(os.path.join(root, svid_error_fn), svid_none, header)
        print('没有svid的位置共{}个,具体如下：\n{}'.format(len(svid_none), svid_none))
    else:
        print('所有位置均有svid！')
    # 说明保存失败的图片
    if len(error_img) > 0:
        write_csv(os.path.join(root, img_error_fn), error_img, header)
        print('保存失败的图片共{}张，具体如下：\n{}'.format(len(error_img), error_img))
    else:
        print('所有图片均保存成功！')

    print('爬取结束！图片保存在{}文件夹中。'.format(os.path.join(root, img_dir)))

if __name__ == "__main__":
    data_fn = './dir/point.csv'
    GetBaiduStreetView(data_fn)