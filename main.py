import json

import yaml
from Rank import Ranking
from ArtWork import Artwork
from  Artist import Artist
import requests
from bs4 import BeautifulSoup
import os
import re
from multiprocessing import Process
import time

import lxml
from  lxml import etree
import pprint
import os
import openpyxl
import datetime
from Login import login_pixiv

def menu():
    print('\n--------=> 主菜单 <=--------')
    print('请选择功能：')
    print('1. 下载单个作品')
    print('2. 下载指定画师全部或近期作品')
    print('3. 下载排行榜前部分或全部作品')
    print('4. 把指定画师的所有作品的信息写入Excel')
    print('5. 把排行榜部分或全部作品信息写入Excel')
    print('6. 查看说明书')
    print('7. 退出','\n')

if __name__ == "__main__":

    print('\n','----------------》欢迎使用Pixiv绘画网站作品下载分析器,首次使用请先设置配置文件！《----------------')
    print('！！！！！！》注意，由于Pixiv网站服务器位于境外，使用本软件时请确保自己的网络环境可访问外网《！！！！！！')
    print('！！！！！！  》   注意，首次使用该程序前请先设置配置文件config.yml   《   ！！！！！！')
    try:
        myheader = login_pixiv()
    except Exception as e:
        print('登录出错')
        print(e)
    try:
        with open('config.yml', 'r') as f:
            myheader["Cookie"] = yaml.load(f, Loader=yaml.SafeLoader)['Myheader']['cookie']
        with open('config.yml', 'r') as f:
            save_path = yaml.load(f, Loader=yaml.SafeLoader)['Setting']['Save_Path'].rstrip('\\')
    except Exception as e:
        print('读取配置文件出错')
        print(e)
    if not os.path.exists(save_path):
        os.mkdir(save_path)

    choice=0
    while choice!='7':
        menu()
        choice = input('请输入功能号码：')
        if int(choice) not in range(1,8):
            print('输入错误')
        #下载单个作品
        elif choice=='1':
            one_artwork_ID = input('请输入作品的pid, 输入0返回主菜单：')
            if one_artwork_ID !='0':
                try:
                    one_artwork = Artwork(artwork_id=one_artwork_ID,save_path=save_path,my_header=myheader)
                    one_artwork.DownloadArtwork()
                except Exception as e:
                    print('下载失败')
                    print(e)

        #下载指定画师全部或近期作品
        elif choice=='2':
            one_artist_ID = input('请输入画师的id, 输入0返回主菜单：')
            if one_artist_ID !='0':
                try:
                    one_artist = Artist(user_ID=one_artist_ID,save_path=save_path,my_header=myheader)
                except Exception as e:
                    print('获取画师信息出现问题')
                    print(e)
                try:
                    num = input('输入需要下载的近期作品数，直接回车默认为全部:')
                    if num=='':
                        one_artist.DownLoadArtworkList()
                    else:
                        one_artist.DownLoadArtworkList(num=int(num))
                except Exception as e:
                    print('下载失败')
                    print(e)
                print('画师作品下载完成')

        #3. 下载排行榜前部分或全部作品
        elif choice =='3':
            date = input('请输入排行榜日期，格式为8位数字，例如20221202，直接回车默认今日,输入0返回主菜单：')
            if date!='0':
                print('daily：日榜， weekly：周榜， monthly：月榜， rookie：新人榜， original：原创榜, daily_ai：AI生成日榜， male：受男性欢迎榜， female：受女性欢迎榜')
                mode = input('请输入排行榜模式，直接回车默认日榜，输入0返回主菜单：')
                '''while mode not in ['daily','weekly','monthly','rookie','original','daily_ai','male','female'] and mode != '':
                    mode = input('重新输入,接回车默认日榜:')'''
                if mode != '0':
                    try:
                        one_rank=Ranking(save_path=save_path,myheader=myheader,mode=mode,date=date)
                    except Exception as e:
                        print('获取排行榜信息出现问题')
                        print(e)
                    try:
                        num = input('输入需要下载排行榜前多少位，最大500，直接回车默认50：')
                        while True:
                            if num=='':
                                break
                            elif int(num) in range(1,501):
                                break
                            num = input('重新输入500以内的正整数，直接回车默认50:')
                        if num =='':
                            one_rank.DownloadRanking()
                        else:
                            one_rank.DownloadRanking(num=int(num))
                    except Exception as e:
                        print('下载失败')
                        print(e)
                    print('排行榜下载完成')

        #把指定画师的所有作品的信息写入Excel
        elif choice == '4':
            one_artist_ID = input('请输入画师的id, 输入0返回主菜单：')
            if one_artist_ID != '0':
                try:
                    one_artist = Artist(user_ID=one_artist_ID, save_path=save_path, my_header=myheader)
                except Exception as e:
                    print('获取画师信息出现问题')
                    print(e)
                try:
                    one_artist.Write_ArtworkInfo()
                except Exception as e:
                    print('写入失败')
                    print(e)
                print('画师作品信息写入完成')

        #把排行榜部分或全部作品信息写入Excel
        elif choice == '5':
            date = input('请输入排行榜日期，格式为8位数字，例如20221202，直接回车默认今日,输入0返回主菜单：')
            if date != '0':
                print(
                    'daily：日榜， weekly：周榜， monthly：月榜， rookie：新人榜， original：原创榜, daily_ai：AI生成日榜， male：受男性欢迎榜， female：受女性欢迎榜')
                mode = input('请输入排行榜模式，直接回车默认日榜，输入0返回主菜单：')
                '''while mode not in ['daily', 'weekly', 'monthly', 'rookie', 'original', 'daily_ai', 'male',
                                   'female'] and mode != '':
                    mode = input('重新输入,接回车默认日榜:')'''
                if mode != '0':
                    try:
                        one_rank = Ranking(save_path=save_path, myheader=myheader, mode=mode, date=date)
                    except Exception as e:
                        print('获取排行榜信息出现问题')
                        print(e)
                    try:
                        num = input('输入需要写入排行榜前多少位，最大500，直接回车默认100：')
                        while True:
                            if num == '':
                                break
                            elif int(num) in range(1, 501):
                                break
                            num = input('重新输入500以内的正整数，直接回车默认50:')
                        if num == '':
                            one_rank.Write_RankingInfo()
                        else:
                            one_rank.Write_RankingInfo(num=int(num))
                    except Exception as e:
                        print('写入失败')
                        print(e)
                    print('排行榜写入完成')
        #查看说明书
        elif choice == '6':
            print('Pixiv，俗称P站，是一个以插图、漫画和小说、艺术为中心的社交网络服务里的虚拟社区网站，你可以使用本下载器下载里面画师与排行榜的作品与信息')
            print('在使用前，您需要设置config.yml配置文件，设置你的Pixiv账号密码与cookie，存储路径save_path等')
            print('根据菜单提示进行选择吧')









