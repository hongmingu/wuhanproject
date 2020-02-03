from bs4 import BeautifulSoup
from django.shortcuts import render, redirect, reverse
from django.db.models import Q
from django.db import transaction
import uuid

from django.utils.timezone import now, timedelta

# Create your views here.
from baseapp.models import *

from django.urls import reverse
from django.shortcuts import render
from paypal.standard.forms import PayPalPaymentsForm

from django.views.decorators.http import require_GET
from django.views.decorators.csrf import csrf_exempt
import requests
#from isodata import parse_duration
from django.conf import settings

import pandas as pd
from bs4 import BeautifulSoup
import time
from selenium import webdriver
import ast
import json
from pyvirtualdisplay import Display
import os

def home(request):
    if request.method == "GET":
        from django.utils.timezone import localdate
        from django.utils.dateparse import parse_date
        from datetime import datetime, timedelta

        countries = CountryTranslation.objects.filter(chinese__icontains="尼泊尔")
        for country in countries:
            print(country.english)

        from ipware import get_client_ip
        client_ip, is_routable = get_client_ip(request)
        if client_ip is None:
            pass
        # Unable to get the client's IP address
        else:
            print(get_client_ip(request))

            from geoip import geolite2
            match = geolite2.lookup(client_ip)
            if match is not None:
                print(match.country)
                # 'US'
                print(match.continent)
                # 'NA'
                print(match.timezone)
                # 'America/Los_Angeles'
                print(match.subdivisions)
                print(frozenset(['CA']))
            # We got the client's IP address
            if is_routable:
                pass
            # The client's IP address is publicly routable on the Internet
            else:
                pass
        # The client's IP address is private

        return render(request, 'baseapp/home.html', {'day': 'day'})


YOUTUBE_DATA_API_KEY = 'AIzaSyDAOuwrMiVMDaRxcKBGATckFTjrYlgHSGA' # youtube api key. 민구야 발급 받는 게 좋을 듯?


def update_youtube(request):
    if request.method == "GET":
        search_url = 'https://www.googleapis.com/youtube/v3/search'
        video_url = 'https://www.googleapis.com/youtube/v3/videos'

        search_params = {
            'part': 'snippet',
            'q': 'corona',  # 검색어: corona
            'key': settings.YOUTUBE_DATA_API_KEY,
            'maxResults': 5,  # 불러올 비디오 갯수: 5개
            'type': 'video'
        }

        video_ids = []
        r = requests.get(search_url, params=search_params)

        results = r.json()['items']

        for result in results:
            video_ids.append(result['id']['videoId'])

        video_params = {
            'key': settings.YOUTUBE_DATA_API_KEY,
            'part': 'snippet,contentDetails',
            'id': ','.join(video_ids),
            'maxResults': 5,
        }

        r = requests.get(video_url, params=video_params)

        results = r.json()['items']

        videos = []
        for result in results:
            video_data = {
                'id': result['id'],
                'url': f'https://www.youtube.com/watch?v={ result["id"] }',
                # 'duration' : int(parse_duration(result['contentDetails']['duration']).total_seconds() // 60)
                'title': result['snippet']['title'],  # 제목
                'channel_title': result['snippet']['channelTitle'],
            # 채널 명 https://developers.google.com/youtube/v3/docs/videos
                'description': result['snippet']['description'],
            # 내용 설명 https://developers.google.com/youtube/v3/docs/videos
                'published_date': result['snippet']['publishedAt'],
            # 공개 날짜 https://developers.google.com/youtube/v3/docs/videos
                'viewcount': result['statistics']['viewCount'],
            # 조회수 https://developers.google.com/youtube/v3/docs/videos
                'thumbnail': result['snippet']['thumbnails']['high']['url']  # 썸네일
                ####################################################################### 언어 설정을 무조건 영어로 할지 어떨지 결정해야 한다.
            }



        context = {
            'videos': videos
        }

        return render(request, 'baseapp/home.html')


def test_linux(request):
    if request.method == "GET":
        print("heheh")
        return render(request, 'baseapp/home.html')

def crawl_on_linux(request):
    if request.method == "GET":

        webdriver_path = r'chromedriver_linux64\chromedriver'  # path
        os.environ['webdriver.chrome.driver'] = webdriver_path
        display = Display(visible=0, size=(800, 600))
        display.start()

        with open('language_dict.txt', 'r', encoding='utf-8') as f:  # language_dict.txt에 저장된 {언어: {중국어: 영어}} 불러오기.
            language_dict = json.loads(f.read())

        #while True:
        #    time.sleep(60 * 30)  # 30분 쉰다
        '''
        중국 자료를 크롤링
        '''
        china_url = r'https://3g.dxy.cn/newh5/view/pneumonia?scene=2&clicktime=1579582238&enterid=1579582238&from=singlemessage&isappinstalled=0'
        # browser = webdriver.Chrome(executable_path=webdriver_path, options=chrome_options,
        #                           service_args=['--verbose', '--log-path=/tmp/chromedriver.log'])
        browser = webdriver.Chrome(executable_path=webdriver_path)

        browser.get(china_url)
        time.sleep(5)
        soup_china = BeautifulSoup(browser.page_source, 'html.parser')

        ####### 중국을 제외한 나라들의 데이터
        out_china_text = soup_china.find('script', id='getListByCountryTypeService2').text
        json_start = out_china_text.find('[')
        json_end = out_china_text.rfind(']')

        out_china = ast.literal_eval(out_china_text[json_start:json_end + 1])
        out_china = pd.DataFrame(out_china)
        out_china = out_china[['provinceName', 'confirmedCount', 'deadCount', 'curedCount']]
        #######

        ####### 대만, 홍콩, 마카오의 데이터
        in_china_text = soup_china.find('script', id='getListByCountryTypeService1').text
        json_start = in_china_text.find('[')
        json_end = in_china_text.rfind(']')

        in_china = ast.literal_eval(in_china_text[json_start:json_end + 1])
        in_china = pd.DataFrame(in_china)
        in_china = in_china[['provinceName', 'confirmedCount', 'deadCount', 'curedCount']]

        in_but_out_china = ['香港', '台湾', '澳门']  # 홍콩, 대만, 마카오
        in_but_out_china = in_china[in_china['provinceName'].isin(in_but_out_china)]  # 홍콩, 대만, 마카오 데이터만 추출
        #######

        ####### 중국 본토 데이터
        china_text = soup_china.find('script', id='getStatisticsService').text
        json_start = china_text.find('id')
        json_end = china_text.rfind('}catch')

        china = json.loads(china_text[json_start - 2:json_end])
        china = pd.DataFrame([china])
        china = china[['confirmedCount', 'deadCount', 'curedCount']]

        main_china = china - in_but_out_china[['confirmedCount', 'deadCount', 'curedCount']].sum()
        main_china['provinceName'] = '中国'
        main_china = main_china[['provinceName', 'confirmedCount', 'deadCount', 'curedCount']]
        #######

        data = pd.concat([out_china, in_but_out_china, main_china])
        data = data.rename(
            columns={'provinceName': 'Country/Region', 'confirmedCount': 'Confirmed Cases', 'deadCount': 'Deaths',
                     'curedCount': 'Recovered'})  # column name을 존스홉스킨스와 동일하게 변경
        data.sort_values(by='Confirmed Cases', ascending=False, inplace=True)
        data.reset_index(drop=True, inplace=True)

        '''
        영어로 번역. language_dict에 있는지 확인한 후에, 없으면 파파고를 이용하자
        '''
        country = []
        papa_url = r'https://papago.naver.com/?sk=zh-CN&tk=en&st='
        for c in data['Country/Region'].to_list():
            if c in list(language_dict['English'].keys()):
                country.append(language_dict['English'][c])
            else:
                browser.get(papa_url)
                time.sleep(2)
                browser.find_element_by_css_selector('#sourceEditArea textarea').send_keys(c)
                time.sleep(4)
                papa_soup = BeautifulSoup(browser.page_source, 'html.parser')
                country.append(papa_soup.find('div', id='txtTarget').text)

        language_dict['English'] = {}  # language_dict['English']에 새로운 번역 추가
        for c, e in zip(data['Country/Region'].to_list(), country):
            language_dict['English'][c] = e

        language_dict = json.dumps(language_dict, ensure_ascii=False)
        with open('language_dict.txt', 'w', encoding='utf-8') as f:
            print(language_dict, file=f)

        data['Country/Region'] = country

        browser.close()

        #### 서버에서 처리할 데이터 ####
        Country = data['Country/Region'].to_list()  # 열 이름: Country/Region
        Confirmed = data['Confirmed Cases'].to_list()  # 열 이름: Confirmed Cases
        Deaths = data['Deaths'].to_list()  # 열 이름: Deaths
        Recovered = data['Recovered'].to_list()  # 열 이름: Recovered

        return render(request, 'baseapp/home.html')
