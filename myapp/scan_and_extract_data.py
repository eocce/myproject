import os
import py7zr
from .serializers import RemoteSensingDataSerializer
import xml.etree.ElementTree as ET
def extract_details(element):
    details = {}
    for child in element:
        if child.tag == 'Cloud':
            details['CloudPercent'] = child.attrib['CloudPercent']
        elif child.tag == 'GeodeticInfo':
            details[child.tag] = {grandchild.tag: grandchild.text for grandchild in child}
        elif len(child) > 0:
            details[child.tag] = extract_details(child)
        else:
            details[child.tag] = child.text
    return details


def scan_and_extract_data(directory):
    for filename in os.listdir(directory):
        if filename.endswith(".7z"):  # 假设遥感数据是 7z 文件
            filepath = os.path.join(directory, filename)
            name, extension = os.path.splitext(filename)
            # 解压 7z 文件
            with py7zr.SevenZipFile(filepath, mode='r') as z:
                z.extractall(path=directory+'\\'+name)
                print("解压成功")
            # 获取源数据信息
            data_name = filename
            data_path = filepath
            multispectral_data = {}
            panchromatic_data = {}
            for GFname in os.listdir(directory+'\\'+name):
                # 如果文件是tif文件，并且文件名中包含"MS"
                if GFname.endswith(".tif") and "MS" in GFname and "mask" not in GFname:
                    # 提取tif文件的路径
                    MStif_path = os.path.join(directory+'\\'+name, GFname)
                    # 提取相应的xml文件的路径
                    xml_path = MStif_path.replace(".tif", ".meta.xml")
                    # 如果xml文件存在
                    if os.path.exists(xml_path):
                        # 解析xml文件
                        tree = ET.parse(xml_path)
                        root = tree.getroot()
                        # 从xml文件中提取详细信息
                        details = extract_details(root)
                        # 将详细信息添加到多光谱数据字典中
                        multispectral_data[MStif_path] = details

                # 如果文件是tif文件，并且文件名中包含"PA"
                elif GFname.endswith(".tif") and "PA" in GFname and "mask" not in GFname:
                    # 提取tif文件的路径
                    PAtif_path = os.path.join(directory+'\\'+name, GFname)
                    # 提取相应的xml文件的路径
                    xml_path = PAtif_path.replace(".tif", ".meta.xml")
                    # 如果xml文件存在
                    if os.path.exists(xml_path):
                        # 解析xml文件
                        tree = ET.parse(xml_path)
                        root = tree.getroot()
                        # 从xml文件中提取详细信息
                        details = extract_details(root)
                        # 将详细信息添加到全色数据字典中
                        panchromatic_data[PAtif_path] = details
                        # 如果文件是tif文件，并且文件名中包含"PA"
                elif GFname.endswith(".jpg") and ("MS" in GFname) and ("browse" in GFname) and ("mask" not in GFname):
                    # 提取tif文件的路径
                    browsejpgpath = os.path.join(directory + '\\' + name, GFname)
                    print(browsejpgpath)

            # 创建一个新的 RemoteSensingData 对象并保存到数据库中
            serializer = RemoteSensingDataSerializer(data={
                'zname': data_name,
                'zpath': data_path,
                'MSname': data_path,
                'MSpath': MStif_path,
                'PAname': data_path,
                'PApath': PAtif_path,
                'CloudPercent': multispectral_data[MStif_path]['SceneInfo']['CloudPercent'],
                'GeodeticInfo': multispectral_data[MStif_path]['GeodeticInfo'],
                'ProductTime': multispectral_data[MStif_path]['ProductInfo']['ProductTime'],
                'browsejpgpath': browsejpgpath,
            })
            # print(multispectral_data)
            if serializer.is_valid():
                serializer.save()
            else:
                print(serializer.errors)