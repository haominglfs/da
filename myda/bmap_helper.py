import requests
import json
from myda.utils import get_logger
from myda.dbutils import select_geo,update_geo

logger = get_logger(__name__)

ak = 'Pl2os1FXl6bZT0zvl0WyUo3z0dGm49fu'
headers = {
  'Cookie': 'SameSite=None; Secure',
  'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.116 Safari/537.36',
}


def __get_http_session(pool_connections, pool_maxsize, max_retries):
    session = requests.Session()
    # 创建一个适配器，连接池的数量pool_connections, 最大数量pool_maxsize, 失败重试的次数max_retries
    adapter = requests.adapters.HTTPAdapter(pool_connections = pool_connections,
            pool_maxsize = pool_maxsize, max_retries = max_retries)
    # 告诉requests，http协议和https协议都使用这个适配器
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

def get_latlng(addresses):
    geo_coord_list = []
    geo_update_list = []
    for address in addresses:
        try:
            values = select_geo(address)
            if(values):
               geo_coord_list.append(values)
            else:
                url = 'http://api.map.baidu.com/geocoding/v3/?address={}&output=json&ak={}'.format(address, ak)
                s = __get_http_session(24,24,2)
                res = requests.get(url,headers=headers)
                json_data = json.loads(res.text)
                lat = json_data['result']['location']['lat']
                lng = json_data['result']['location']['lng']
                geo_update_list.append((address,lat,lng))
                geo_coord_list.append((address,lat,lng))
        except Exception as e:
            logger.error(e)
        finally:
            update_geo(geo_update_list)

    return geo_coord_list


def convert_data(data,geo_coord_map):
    res = []
    for i in range(len(data)):
        try:
            geo_coord = geo_coord_map[data[i][0]]
            geo_coord.append(data[i][1])
            res.append([data[i][0], geo_coord])
        except Exception as e:
            logger.error(e)
    return res

if __name__ == '__main__':
    geoCoordMap = get_latlng(['上海市上海市嘉定区曹安公路4800号B106'])
    print(geoCoordMap)

