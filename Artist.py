import requests
from PixivException import  PixivExceptionError
from ArtWork import Artwork
import openpyxl
import openpyxl.styles
import os

class Artist:
    def __init__(self,user_ID,save_path,my_header):
        self.user_ID = user_ID
        self.save_path=save_path.rstrip('\\')+'\\'+str(user_ID)
        self.my_header = my_header
        self.artwork_list = []
        try:
            self.get_ArtWorkIDList()
        except Exception as e:
            print(e)
            raise  PixivExceptionError("获取画师作品出现问题 或 该账号不存在")
    def get_ArtWorkIDList(self):
        ArtList_page = requests.get("https://www.pixiv.net/ajax/user/"+ self.user_ID +"/profile/all",headers=self.my_header)
        artList_pageJson = ArtList_page.json()
        ArtList_page.close()
        self.artwork_IDlist = [i for i in artList_pageJson['body']['illusts'].keys()]

    def get_ArtworkList(self,num=-1,save_path=''):
        self.artwork_list=[]
        if len(self.artwork_IDlist)==0:
            print('该账号没有发布过作品')
            return
        if num>len(self.artwork_IDlist) or num ==-1:
            num=len(self.artwork_IDlist)

        n = 0
        print('正在拉取作品列表')
        for i in range(num):

            try:
                self.artwork_list.append(Artwork(self.artwork_IDlist[i],save_path,my_header=self.my_header))
            except Exception as e:
                n+=1
                print(e)
        if n!=0:
            print('拉取列表时出现'+str(n)+"个错误")
        print('拉取作品列表完成')

    def Write_ArtworkInfo(self):
        #把画师的作品存储进excel
        if self.artwork_list==[]:
            self.get_ArtworkList(save_path=self.save_path)
        print('开始写入画师作品')
        if os.path.exists(self.save_path+'\\'+str(self.user_ID)+'.xlsx'):
            workbook = openpyxl.load_workbook(self.save_path+'\\'+str(self.user_ID)+'.xlsx')
        else:
            workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet.title = 'one'
        sheet['A1'] = '作品ID'
        sheet.column_dimensions['A'].width = 10
        sheet['B1'] = '作品标题'
        sheet.column_dimensions['B'].width = 23
        sheet['C1'] = '画师名'
        sheet.column_dimensions['C'].width = 18
        sheet['D1'] = '画师ID'
        sheet.column_dimensions['D'].width = 9
        sheet['E1'] = '图片页数'
        sheet.column_dimensions['E'].width = 8
        sheet['F1'] = '浏览数量'
        sheet.column_dimensions['F'].width = 8
        sheet['G1'] = '点赞数量'
        sheet['H1'] = '收藏数量'
        sheet['I1'] = '收藏率'
        sheet.column_dimensions['I'].width = 13
        sheet['J1'] = '是否为R-18'
        sheet.column_dimensions['J'].width = 10
        sheet['K1'] = '原图文件链接'
        sheet.column_dimensions['K'].width = 12
        sheet['L1'] = '标签'

        sheet.column_dimensions['L'].width = 95

        for s in self.artwork_list:
            list = []
            tags = ', '.join(s.artwork_info['tags'])

            list = [s.artwork_info['work_ID'], s.artwork_info['work_title'], s.artwork_info['artist_name'],
                    s.artwork_info['artist_ID'], s.artwork_info['page_count'], s.artwork_info['view_count'],
                    s.artwork_info['like_count'], s.artwork_info['bookmark_count'], s.artwork_info['bookmark_rate'],
                    str(s.artwork_info['isR-18']), s.artwork_info['urls']['original'], tags]
            sheet.append(list)
        for i in sheet['L']:
            i.alignment = openpyxl.styles.Alignment(text_rotation=0, wrap_text=True)
        if not os.path.exists(self.save_path):
            os.mkdir(self.save_path)
        workbook.save(self.save_path+'\\'+str(self.user_ID)+'.xlsx')

        print('画师作品写入完毕')



    def DownLoadArtworkList(self,num=int(-1)):
        if not os.path.exists(self.save_path):
            os.mkdir(self.save_path)
        self.get_ArtworkList(num=num,save_path=self.save_path)
        n = 0
        print('开始下载')

        for i in self.artwork_list:
            try:
                i.DownloadArtwork()
            except Exception as e:
                n += 1
                print(e)
        if n != 0:
            print('下载作品时出现' + str(n) + "个错误")
        print('画师作品下载完毕')




