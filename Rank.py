
from PixivException import PixivExceptionError
import requests
from bs4 import BeautifulSoup
import os
import datetime
import openpyxl
import openpyxl.styles

import  time
from ArtWork import Artwork

class Ranking:
    def __init__(self,save_path,myheader,mode='',date=''):
        if mode!='':
            mode = 'mode='+mode
        if date!='':
            date = 'date='+date
        self.mode = mode
        self.date = date
        self.save_path = save_path.rstrip('\\')+'\\'+self.get_ModeDateName()
        self.my_header = myheader
        self.rankingInfoList={}

    def get_ModeDateName(self):
        date = self.date
        if date == '':
            i = datetime.datetime.now()
            date = str(i.year) + str(i.month) + str(i.day)
        mode = self.mode
        if mode == '':
            mode = 'daily'
        return  date + '_' + mode

    def get_rankingInfoList(self,num = 50):
        page_count = int((num-1)/50)+1
        n=0
        errornum=0
        print("开始拉取排行榜作品信息")
        for i in range(page_count):

            url = 'https://www.pixiv.net/ranking.php?'+self.mode+'&'+self.date+'&p='+str(i+1)
            rank_resp = requests.get(url,headers=self.my_header)

            soup = BeautifulSoup(rank_resp.text, 'html.parser')
            if rank_resp.status_code!=200:
                raise PixivExceptionError('排行榜页面异常')
            rank_resp.close()
            item = soup.find_all('section', attrs={'class': "ranking-item"})


            for j in item:
                try:
                    itemID = j.get('data-id')
                    self.rankingInfoList[int(j.get('data-rank'))] = Artwork(artwork_id=itemID,save_path=self.save_path,my_header=self.my_header)
                    time.sleep(0.3)
                    n+=1
                    if n == num:
                        break
                except Exception as e:
                    print(e)
                    errornum+=1
        if errornum!=0:
            print('获取排行榜作品信息时出现'+str(errornum)+'个错误')
        print("拉取排行榜作品信息完毕")

    def DownloadRanking(self,num):
        if not os.path.exists(self.save_path):
            os.mkdir(self.save_path)
        if self.rankingInfoList == {}:
            self.get_rankingInfoList(num=num)
        errorNum = 0
        for i,j in self.rankingInfoList.items():
            try:
                j.DownloadArtwork(No='No'+str(i)+'_')
            except Exception as e:
                errorNum+=1
                print(e)
        if errorNum!=0:
            print('下载排行榜作品时出现'+str(errorNum)+'个错误')
        print('排行榜作品下载完毕')

    def Write_RankingInfo(self,num=100):
        # 把排行榜作品信息存储进excel
        if self.rankingInfoList == {} or len(self.rankingInfoList)<num:
            self.get_rankingInfoList(num)
        date = self.date
        if date =='':
            i = datetime.datetime.now()
            date = str(i.year) + str(i.month) + str(i.day)
        mode = self.mode
        if mode == '':
            mode = 'daily'
        namestr=date+'_'+mode+'_前'+str(num)
        print('开始写入排行榜作品')
        if os.path.exists(self.save_path + '\\' + namestr + '.xlsx'):
            workbook = openpyxl.load_workbook(self.save_path + '\\' + namestr + '.xlsx')
        else:
            workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet.title = 'one'
        sheet['A1'] = '排名'
        sheet['B1'] = '作品ID'
        sheet.column_dimensions['B'].width = 10
        sheet['C1'] = '作品标题'
        sheet.column_dimensions['C'].width = 23
        sheet['D1'] = '画师名'
        sheet.column_dimensions['D'].width = 18
        sheet['E1'] = '画师ID'
        sheet.column_dimensions['E'].width = 9
        sheet['F1'] = '图片页数'
        sheet.column_dimensions['F'].width = 8
        sheet['G1'] = '浏览数量'
        sheet.column_dimensions['G'].width = 8
        sheet['H1'] = '点赞数量'
        sheet['I1'] = '收藏数量'
        sheet['J1'] = '收藏率'
        sheet.column_dimensions['I'].width = 13
        sheet['K1'] = '是否为R-18'
        sheet.column_dimensions['J'].width = 10
        sheet['L1'] = '原图文件链接'
        sheet.column_dimensions['K'].width = 12
        sheet['M1'] = '标签'
        sheet.column_dimensions['M'].width = 95

        for rank,work in self.rankingInfoList.items():
            list = []
            tags = ', '.join(work.artwork_info['tags'])

            list = [rank,work.artwork_info['work_ID'], work.artwork_info['work_title'], work.artwork_info['artist_name'],
                    work.artwork_info['artist_ID'], work.artwork_info['page_count'], work.artwork_info['view_count'],
                    work.artwork_info['like_count'], work.artwork_info['bookmark_count'], work.artwork_info['bookmark_rate'],
                    str(work.artwork_info['isR-18']), work.artwork_info['urls']['original'], tags]
            sheet.append(list)
        for i in sheet['M']:
            i.alignment = openpyxl.styles.Alignment(text_rotation=0, wrap_text=True)
        if not os.path.exists(self.save_path):
            os.mkdir(self.save_path)
        workbook.save(self.save_path + '\\' + namestr + '.xlsx')

        print('排行榜作品写入完毕')
