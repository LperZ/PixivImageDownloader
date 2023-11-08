import yaml
from PixivException import PixivExceptionError
import requests
import os
import re
import time
import imageio
import zipfile

class Artwork:
    def __init__(self, artwork_id, save_path, my_header):
        self.artwork_id = artwork_id
        self.save_path = save_path.rstrip('\\')
        self.MyHeader = my_header
        self.artwork_info = self.getArtworkInfo()
    #获取作品的标题，画师ID，画师名，画师
    def getArtworkInfo(self):
        artwork_resp = requests.get('https://www.pixiv.net/ajax/illust/'+self.artwork_id,headers=self.MyHeader)
        if artwork_resp.status_code != 200:
            raise PixivExceptionError('获取作品信息页面出错或作品不存在')

        proto_info = artwork_resp.json()['body']
        artwork_resp.close()
        info = {}
        info['work_ID'] = self.artwork_id
        info['work_title'] = proto_info['title']
        info['artist_ID'] = proto_info['userId']
        info['artist_name'] = proto_info['userName']
        info['urls'] = proto_info['urls']
        info['tags'] = [i['tag'] for i in proto_info['tags']['tags']]
        info['page_count']=int(proto_info['pageCount'])
        info['view_count'] = int(proto_info['viewCount'])
        info['like_count'] = int(proto_info['likeCount'])
        info['bookmark_count'] = int(proto_info['bookmarkCount'])
        info['bookmark_rate'] = float(info['bookmark_count']/info['view_count'])
        if 'R-18' in info['tags']:
            info['isR-18'] = True
        else:
            info['isR-18'] = False

        if 'ugoira' in info['urls']['original']:
            info['file_type'] = 'dynamic'
        else:
            info['file_type'] = "static"
            part_url = re.search('https://i\.pximg\.net/.*?(?P<part>[/\d]*)_p0\.', info['urls']['original']).group(
                'part')
            info['part_url'] = part_url
        return info


    #检查作品名称是否符合文件命名规范
    def CheckWorkName(self,str):
        reStr = ''
        for i in str:
            st = i
            if i in ['\\', '/', '?', ':', '*', '<', '>', '|', '"']:
                st = '_'
            reStr += st
        return reStr
    #下载该作品
    def DownloadStaticArtwork(self,url, work_title, file_type, save_path):
        work_title=self.CheckWorkName(work_title)
        if self.artwork_info['page_count']==1:
            pic = requests.get(url,headers=self.MyHeader,stream=True)
            #处理作品重名的情况
            if os.path.exists(save_path + '\\' + work_title+ '.' + file_type):
                n = 0
                while os.path.exists(save_path + '\\' + work_title+ '.' + file_type):
                    n += 1
                    work_title = work_title + '(' + str(n) + ')'

            with open(save_path + "\\" + work_title + '.' + file_type, 'wb') as f2:
                f2.write(pic.content)
            pic.close()
        else:
            # 处理作品重名的情况
            if not os.path.exists(save_path + '\\' + work_title):
                os.mkdir(save_path + '\\' + work_title)
            else:
                n=0
                while os.path.exists(save_path + '\\' + work_title):
                    n+=1
                    work_title= work_title+'('+str(n)+')'
                os.mkdir(save_path + '\\' + work_title)
            for i in range(self.artwork_info['page_count']):
                pic = requests.get('https://i.pximg.net/img-original/img/' + self.artwork_info['part_url'] + '_p' + str(i) +'.' + file_type,
                                   headers=self.MyHeader,stream=True)
                with open(save_path + '\\'  +work_title + '\\' + str(i+1)+'_'+work_title  +  '.' + file_type, mode='wb') as f2:
                    f2.write(pic.content)
                pic.close()
                time.sleep(0.4)
        print(work_title + ' 下载成功')
        time.sleep(0.6)
        return

    #对动图作品进行解密
    def DownloadDynamicArtwork(self,ID,work_title,save_path,headers):
        file_path = save_path
        # 获取gif信息，提取zip url
        gifIn = requests.get('https://www.pixiv.net/ajax/illust/' + ID + '/ugoira_meta', headers=headers)
        gif_info = gifIn.json()
        gifIn.close()
        delay = [item["delay"] for item in gif_info["body"]["frames"]]
        delay = sum(delay) / len(delay)
        zip_url = gif_info["body"]["originalSrc"]

        # 下载压缩包
        gif = requests.get(zip_url, headers=headers)
        gif_data = gif.content
        gif.close()
        try:
            os.mkdir(file_path)
        except Exception:
            pass
        zip_path = os.path.join(file_path, "temp"+"_"+work_title+".zip")
        with open(zip_path, "wb") as fp:
            fp.write(gif_data)
        # 生成文件
        temp_file_list = []
        zipo = zipfile.ZipFile(zip_path, "r")
        for file in zipo.namelist():
            temp_file_list.append(os.path.join(file_path, file))
            zipo.extract(file, file_path)
        zipo.close()
        # 读取所有静态图片，合成gif
        image_data = []
        for file in temp_file_list:
            image_data.append(imageio.imread(file))
        imageio.mimsave(os.path.join(file_path, work_title + ".gif"), image_data, "GIF", duration=delay / 1000)
        # 清除所有中间文件。
        for file in temp_file_list:
            os.remove(file)
        os.remove(zip_path)
        print(work_title + ' 下载成功')

    #判断该作品图片格式
    def DownloadArtwork(self,No='',mode = 'original'):
        #根据配置阻止用户下载R-18内容
        with open('config.yml', 'r') as f:
            allow= yaml.load(f, Loader=yaml.SafeLoader)['Setting']['Allow_R-18']
        if self.artwork_info['isR-18'] and not allow:
            print('不可下载R-18作品')
        else:
            work_title = No+self.artwork_info['work_title']
            if self.artwork_info['file_type'] =='static':
                url = self.artwork_info['urls'][mode]
                file_type = url.split('.')[-1]
                self.DownloadStaticArtwork(url, work_title, file_type, self.save_path)
            else:
                self.DownloadDynamicArtwork(self.artwork_id,work_title,self.save_path,self.MyHeader)

