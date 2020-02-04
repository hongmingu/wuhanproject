import feedparser
from bs4 import BeautifulSoup
from django.http import JsonResponse
from django.shortcuts import render, redirect, reverse
from django.db.models import Q
from django.db import transaction, IntegrityError
import uuid

from django.utils.timezone import now, timedelta

# Create your views here.
from baseapp.models import *

from django.urls import reverse
from django.shortcuts import render

from django.views.decorators.http import require_GET
from django.views.decorators.csrf import csrf_exempt
import requests
# from isodata import parse_duration
from django.conf import settings

import pandas as pd
from bs4 import BeautifulSoup
import time
from selenium import webdriver
import ast
import json
from pyvirtualdisplay import Display
import os

from django.utils.timezone import localdate
from django.utils.dateparse import parse_date
from datetime import datetime, timedelta
from ipware import get_client_ip
from geoip import geolite2


def home(request):
    if request.method == "GET":
        client_ip, is_routable = get_client_ip(request)
        country_code = None
        if client_ip is None:
            pass
        # Unable to get the client's IP address
        else:
            # print(get_client_ip(request))
            match = geolite2.lookup(client_ip)
            if match is not None:
                get_code = match.country
                try:
                    country_code = CountryCode.objects.get(code=get_code)
                except Exception as e:
                    print(e)
                    pass

                # print(match.country)# 'US'
                # print(match.continent)# 'NA'
                # print(match.timezone)# 'America/Los_Angeles'
                # print(match.subdivisions)
                # print(frozenset(['CA']))
            # We got the client's IP address
            # if is_routable:
            #     pass
            # # The client's IP address is publicly routable on the Internet
            # else:
            #     pass
        # The client's IP address is private

        date_flag = DateFlag.objects.last()
        country_item = None
        world_item = None
        all_country_item = CountryItem.objects.filter(date_flag=date_flag).order_by('-confirmed', '-death',
                                                                                    'country_code__english')

        cnn_item = CnnItem.objects.all().order_by('-created')[:5]

        youtube_item = YoutubeItem.objects.all().order_by('-created')[:5]

        if country_code is not None:
            try:
                country_item = CountryItem.objects.get(country_code=country_code, date_flag=date_flag)
            except Exception as e:
                print(e)

        try:
            world_item = WorldItem.objects.get(date_flag=date_flag)
        except Exception as e:
            print(e)

        return render(request, 'baseapp/home.html', {'country_item': country_item,
                                                     'all_country_item': all_country_item,
                                                     'world_item': world_item,
                                                     'cnn_item': cnn_item,
                                                     'youtube_item': youtube_item})
    else:
        return render(request, 'baseapp/home.html')


YOUTUBE_DATA_API_KEY = 'AIzaSyDAOuwrMiVMDaRxcKBGATckFTjrYlgHSGA'  # youtube api key. 민구야 발급 받는 게 좋을 듯?


@csrf_exempt
def update_cnn(request):
    if request.method == "POST":

        payload = json.loads(
            request.body.decode('utf-8'))

        token = payload["token"]
        if not token == settings.OXIBUG_TOKEN:
            return JsonResponse({"data": "failed"}, safe=False)

        url = "http://feeds.bbci.co.uk/news/rss.xml"  # Getting URL
        feed = feedparser.parse(url)  # Parsing XML data
        try:
            with transaction.atomic():

                for item in feed["entries"]:
                    if 'Corona' in str(item["title"]):
                        try:

                            a = str(item["description"])[:str(item["description"]).find("<img src=")]
                            cnn_item = CnnItem.objects.create(title=item["title"],
                                                              published_date=item["published"],
                                                              content=a,
                                                              url=item['link'])
                        except IntegrityError as e:
                            print(e)
                            pass
        except Exception as e:
            print(e)
            return JsonResponse({"data": "failed"}, safe=False)

        return JsonResponse({"data": "success"}, safe=False)

    else:
        return render(request, 'baseapp/home.html')


@csrf_exempt
def update_country(request):
    if request.method == "POST":
        # print("data: "+str(request.POST.form))
        # get_data = request.POST.get("oxibug1905", None)
        # print(get_data)

        # type(get_data)
        # print(request.POST.get("haha", None))
        # print(request.POST)
        # print(request.POST.dict())
        # print(str(request.POST.dict()))

        payload = json.loads(
            request.body.decode('utf-8'))
        # print(str(payload) + "gogo")
        token = payload["token"]
        if not token == settings.OXIBUG_TOKEN:
            return JsonResponse({"data": "token failed"}, safe=False)

        import pandas as pd
        data = pd.DataFrame(payload)

        country = data['Country/Region'].to_list()  # 열 이름: Country/Region
        confirmed = data['Confirmed Cases'].to_list()  # 열 이름: Confirmed Cases
        deaths = data['Deaths'].to_list()  # 열 이름: Deaths
        recovered = data['Recovered'].to_list()  # 열 이름: Recovered
        iso = data['ISO'].to_list()  # 열 이름: ISO

        try:
            with transaction.atomic():

                date_flag_create = DateFlag.objects.create()

                confirmed_count = 0
                deaths_count = 0
                recovered_count = 0

                for item in range(len(country)):
                    confirmed_count = confirmed_count + int(confirmed[item])
                    deaths_count = deaths_count + int(deaths[item])
                    recovered_count = recovered_count + int(recovered[item])

                    country_code, created = CountryCode.objects.get_or_create(code=iso[item])
                    country_code.english = country[item]
                    country_code.save()

                    country_item_create = CountryItem.objects.create(date_flag=date_flag_create,
                                                                     country_code=country_code,
                                                                     confirmed=int(confirmed[item]),
                                                                     death=int(deaths[item]),
                                                                     recovered=int(recovered[item]),
                                                                     death_rate=round(
                                                                         deaths[item] / confirmed[item] * 100,
                                                                         2))

                world_item_create = WorldItem.objects.create(date_flag=date_flag_create,
                                                             country_count=int(str(len(country))),
                                                             confirmed=int(str(confirmed_count)),
                                                             death=int(str(deaths_count)),
                                                             recovered=int(str(recovered_count)),
                                                             death_rate=round(deaths_count / confirmed_count * 100, 2))
        except Exception as e:
            print(e)
            return JsonResponse({"data": "failed"}, safe=False)

        return JsonResponse({"data": "success"}, safe=False)
    else:
        return render(request, 'baseapp/home.html')


@csrf_exempt
def update_youtube(request):
    if request.method == "POST":
        # print("data: "+str(request.POST.form))
        # get_data = request.POST.get("oxibug1905", None)
        # print(get_data)

        # type(get_data)
        # print(request.POST.get("haha", None))
        # print(request.POST)
        # print(request.POST.dict())
        # print(str(request.POST.dict()))

        payload = json.loads(
            request.body.decode('utf-8'))
        # print(str(payload) + "gogo")
        token = payload["token"]
        if not token == settings.OXIBUG_TOKEN:
            return JsonResponse({"data": "token failed"}, safe=False)

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
        print("video_ids:" + str(video_ids))

        video_params = {
            'key': settings.YOUTUBE_DATA_API_KEY,
            'part': 'snippet,contentDetails',
            'id': ','.join(video_ids),
            'maxResults': 5,
        }
        print("video_params:" + str(video_params))
        r = requests.get(video_url, params=video_params)

        results = r.json()['items']
        print("results:" + str(results))

        videos = []

        try:
            with transaction.atomic():

                for result in results:
                    print("result" + str(result))
                    try:

                        youtube_item_created = YoutubeItem.objects.create(video_id=result['id'],
                                                                          url=f'https://www.youtube.com/watch?v={ result["id"] }',
                                                                          title=result['snippet']['title'],
                                                                          channel_title=result['snippet'][
                                                                              'channelTitle'],
                                                                          description=result['snippet']['description'],
                                                                          published_date=result['snippet'][
                                                                              'publishedAt'],
                                                                          published_date_raw=result['snippet'][
                                                                              'publishedAt'],
                                                                          thumbnail=
                                                                          result['snippet']['thumbnails']['high'][
                                                                              'url'])
                    except IntegrityError as e:
                        print(e)
                        pass
                return JsonResponse({"data": "success"}, safe=False)
        except Exception as e:
            print(e)
            return JsonResponse({"data": "failed"}, safe=False)

    else:
        return render(request, 'baseapp/home.html')


#
# [{'kind': 'youtube#video', 'etag': '"Fznwjl6JEQdo1MGvHOGaz_YanRU/WE5mwVTiBEhtJxuzVu5Vy4vrZ24"', 'id': 'MLkzh_fhrnI',
#   'snippet': {'publishedAt': '2020-02-04T08:02:21.000Z', 'channelId': 'UC7723FqVehXq2zeRb3tP0hQ',
#               'title': 'Tin tức dịch corona mới nhất ngày hôm nay 4/2/2020 | Tin tức tổng hợp',
#               'description': 'FBNC TV - Tin tức dịch corona mới nhất ngày hôm nay 4/2/2020\n\nTheo Bộ Y tế, đến 11h ngày hôm nay (4/2), thế giới có 20.628 ca nhiễm virus corona, 427 người tử vong. Việt Nam có 360 trường hợp nghi ngờ nhiễm và 9 trường hợp đã được xách định nhiễm nCoV, trong đó có 2 trường hợp đã điều trị khỏi và được ra viện.\n\nNgoài ra, Việt Nam vừa tiếp nhận được mồi đặc hiệu chuẩn thức của Tổ chức Y tế Thế giới (WHO) để xét nghiệm virus corona. Nếu như trước đây phải mất tới 3-4 ngày mới có kết quả thì nay với kỹ thuật mới này, từ 1-2 ngày đã có thể cho kết quả. \n\nĐể sẵn sàng các phương án phòng chống và điều trị, TP.HCM cũng đang gấp rút triển khai 2 bệnh viện dã chiến quy mô 500 giường bệnh đặt tại huyện Củ Chi và Nhà Bè. Dự kiến hoàn thành vào ngày 15/2. \n\nBên cạnh đó, Thủ tướng và Bộ Công thương vừa đưa ra các chỉ thị về việc cách ly tuyệt đối trường hợp nghi nhiễm nCoV, dừng nhận lao động từ vùng dịch về Việt Nam.\n\nĐồng thời, Bộ VHTT&DL cũng chỉ thị dừng tất cả các lễ hội kể cả lễ hội đã khai mạc tại các tỉnh đã công bố dịch.\n--------------------\nFBNC (Financial Business News Channel) là kênh truyền hình của HTVC  dành cho giới kinh doanh, thông tin chuyên sâu về  kinh tế Việt Nam, bất động sản,  tài chính ngân hàng,  chứng khoán và cổ phiếu, giá vàng và khởi nghiệp,… Nếu bạn đã, đang và sẽ định giá doanh nghiệp. Hãy đồng hành cùng FBNC TV!\n\nKênh truyền thông FBNC:\nFanpage https://www.facebook.com/KinhTeTaiChi...\nZalo https://zalo.me/fbncvn\nYoutube http://www.youtube.com/FBNCVietnam\nWebsite fbnc.vn\nFBNC Live\nhttp://popsww.com/FBNC\n---------------\nFBNC\nĐỒNG TIỀN THÔNG MINH - CUỘC SỐNG THÔNG MINH\n#FBNCTV  #viruscorona #tintuctonghop',
#               'thumbnails': {
#                   'default': {'url': 'https://i.ytimg.com/vi/MLkzh_fhrnI/default.jpg', 'width': 120, 'height': 90},
#                   'medium': {'url': 'https://i.ytimg.com/vi/MLkzh_fhrnI/mqdefault.jpg', 'width': 320, 'height': 180},
#                   'high': {'url': 'https://i.ytimg.com/vi/MLkzh_fhrnI/hqdefault.jpg', 'width': 480, 'height': 360},
#                   'standard': {'url': 'https://i.ytimg.com/vi/MLkzh_fhrnI/sddefault.jpg', 'width': 640, 'height': 480},
#                   'maxres': {'url': 'https://i.ytimg.com/vi/MLkzh_fhrnI/maxresdefault.jpg', 'width': 1280,
#                              'height': 720}}, 'channelTitle': 'FBNC Vietnam',
#               'tags': ['fbnc vietnam', 'tin hot', 'tin nong', 'fbnc tv', 'coronavirus', 'corona',
#                        'diễn biến dịch corona ở Việt Nam', 'dịch virus corona',
#                        'Tin tức dịch corona mới nhất ngày hôm nay 4/2/2020', 'tin tức tổng hợp ngày 4/2/2020',
#                        'tin tức ngày 4/2/2020', 'thoi su 24h', 'virus corona', 'corona vũ hán', 'corona việt nam',
#                        'phòng chống corona', 'người việt nhiễm corona', 'số người chết corona',
#                        'virus corona tại việt nam', 'dịch bệnh corona', 'dịch corona',
#                        'cập nhật tình hình virus corona', 'dịch corona ở việt nam'], 'categoryId': '25',
#               'liveBroadcastContent': 'none',
#               'localized': {'title': 'Tin tức dịch corona mới nhất ngày hôm nay 4/2/2020 | Tin tức tổng hợp',
#                             'description': 'FBNC TV - Tin tức dịch corona mới nhất ngày hôm nay 4/2/2020\n\nTheo Bộ Y tế, đến 11h ngày hôm nay (4/2), thế giới có 20.628 ca nhiễm virus corona, 427 người tử vong. Việt Nam có 360 trường hợp nghi ngờ nhiễm và 9 trường hợp đã được xách định nhiễm nCoV, trong đó có 2 trường hợp đã điều trị khỏi và được ra viện.\n\nNgoài ra, Việt Nam vừa tiếp nhận được mồi đặc hiệu chuẩn thức của Tổ chức Y tế Thế giới (WHO) để xét nghiệm virus corona. Nếu như trước đây phải mất tới 3-4 ngày mới có kết quả thì nay với kỹ thuật mới này, từ 1-2 ngày đã có thể cho kết quả. \n\nĐể sẵn sàng các phương án phòng chống và điều trị, TP.HCM cũng đang gấp rút triển khai 2 bệnh viện dã chiến quy mô 500 giường bệnh đặt tại huyện Củ Chi và Nhà Bè. Dự kiến hoàn thành vào ngày 15/2. \n\nBên cạnh đó, Thủ tướng và Bộ Công thương vừa đưa ra các chỉ thị về việc cách ly tuyệt đối trường hợp nghi nhiễm nCoV, dừng nhận lao động từ vùng dịch về Việt Nam.\n\nĐồng thời, Bộ VHTT&DL cũng chỉ thị dừng tất cả các lễ hội kể cả lễ hội đã khai mạc tại các tỉnh đã công bố dịch.\n--------------------\nFBNC (Financial Business News Channel) là kênh truyền hình của HTVC  dành cho giới kinh doanh, thông tin chuyên sâu về  kinh tế Việt Nam, bất động sản,  tài chính ngân hàng,  chứng khoán và cổ phiếu, giá vàng và khởi nghiệp,… Nếu bạn đã, đang và sẽ định giá doanh nghiệp. Hãy đồng hành cùng FBNC TV!\n\nKênh truyền thông FBNC:\nFanpage https://www.facebook.com/KinhTeTaiChi...\nZalo https://zalo.me/fbncvn\nYoutube http://www.youtube.com/FBNCVietnam\nWebsite fbnc.vn\nFBNC Live\nhttp://popsww.com/FBNC\n---------------\nFBNC\nĐỒNG TIỀN THÔNG MINH - CUỘC SỐNG THÔNG MINH\n#FBNCTV  #viruscorona #tintuctonghop'},
#               'defaultAudioLanguage': 'vi'},
#   'contentDetails': {'duration': 'PT5M29S', 'dimension': '2d', 'definition': 'hd', 'caption': 'false',
#                      'licensedContent': True, 'projection': 'rectangular'}},
#  {'kind': 'youtube#video', 'etag': '"Fznwjl6JEQdo1MGvHOGaz_YanRU/nHBXl2fatxtf7VidDoCoc34UvcY"', 'id': 'In9oKF-OfmE',
#   'snippet': {'publishedAt': '2020-02-03T22:15:34.000Z', 'channelId': 'UC5BMIWZe9isJXLZZWPWvBlg',
#               'title': 'Ini Dia, Penampakan Rumah Sakit Khusus Virus Corona yang Dibangun Hanya Dalam 10 Hari',
#               'description': 'WUHAN, KOMPAS.TV - Rumah sakit khusus penanganan virus corona akhirnya sudah selesai dibangun.\r\n\r\nPemerintah China menamainya RS. Huoshenshan yang bertugas untuk menangani virus corona.\r\n\r\nRumah sakit dibangun di atas lahan tanah seluas 33.900 meter persegi.\r\n\r\nRumah sakit ini terletak di Wuhan, China.\r\n\r\n7.000 pekerja bekerja untuk membangun rumah sakit ini selama 24 jam.\r\n\r\nRumah sakit ini dibangun pada tanggal 23 Januari 2020 dan tanggal 3 Februari, rumah sakit sudah siap untuk beroperasi.\r\n\r\nTotal keseluruhan waktu yang dihabiskan adalah 10 hari.\r\n\r\nMetode pembangunan yang sangat singkat ini di Indonesia terkenal sebagai proyek Roro Jonggrang.\r\n\r\n1.400 staf medis berasal dari tentara China dan mereka sudah siap ditugas di rumah sakit baru tersebut.\r\nRumah sakit ini juga memiliki 10.000 tempat tidur, sehingga diharapkan cukup untuk menampung dan mengatasi kasus-kasus yang diduga virus corona saat ini. \r\n\r\nDilansir dari Kompas.com melalui Global Times, rumah sakit ini mirip dengan kasus pembangunan RS. Xiaotangshan yang dibangun pada tahun 2003 lalu.\r\n\r\nRS tersebut dibangun sebagai pusat medis untuk pasien SARS.',
#               'thumbnails': {
#                   'default': {'url': 'https://i.ytimg.com/vi/In9oKF-OfmE/default.jpg', 'width': 120, 'height': 90},
#                   'medium': {'url': 'https://i.ytimg.com/vi/In9oKF-OfmE/mqdefault.jpg', 'width': 320, 'height': 180},
#                   'high': {'url': 'https://i.ytimg.com/vi/In9oKF-OfmE/hqdefault.jpg', 'width': 480, 'height': 360},
#                   'standard': {'url': 'https://i.ytimg.com/vi/In9oKF-OfmE/sddefault.jpg', 'width': 640, 'height': 480},
#                   'maxres': {'url': 'https://i.ytimg.com/vi/In9oKF-OfmE/maxresdefault.jpg', 'width': 1280,
#                              'height': 720}}, 'channelTitle': 'KOMPASTV',
#               'tags': ['virus corona', 'wuhan', 'china', 'rumah sakit khusus', 'cerita indonesia'], 'categoryId': '25',
#               'liveBroadcastContent': 'none', 'localized': {
#           'title': 'Ini Dia, Penampakan Rumah Sakit Khusus Virus Corona yang Dibangun Hanya Dalam 10 Hari',
#           'description': 'WUHAN, KOMPAS.TV - Rumah sakit khusus penanganan virus corona akhirnya sudah selesai dibangun.\r\n\r\nPemerintah China menamainya RS. Huoshenshan yang bertugas untuk menangani virus corona.\r\n\r\nRumah sakit dibangun di atas lahan tanah seluas 33.900 meter persegi.\r\n\r\nRumah sakit ini terletak di Wuhan, China.\r\n\r\n7.000 pekerja bekerja untuk membangun rumah sakit ini selama 24 jam.\r\n\r\nRumah sakit ini dibangun pada tanggal 23 Januari 2020 dan tanggal 3 Februari, rumah sakit sudah siap untuk beroperasi.\r\n\r\nTotal keseluruhan waktu yang dihabiskan adalah 10 hari.\r\n\r\nMetode pembangunan yang sangat singkat ini di Indonesia terkenal sebagai proyek Roro Jonggrang.\r\n\r\n1.400 staf medis berasal dari tentara China dan mereka sudah siap ditugas di rumah sakit baru tersebut.\r\nRumah sakit ini juga memiliki 10.000 tempat tidur, sehingga diharapkan cukup untuk menampung dan mengatasi kasus-kasus yang diduga virus corona saat ini. \r\n\r\nDilansir dari Kompas.com melalui Global Times, rumah sakit ini mirip dengan kasus pembangunan RS. Xiaotangshan yang dibangun pada tahun 2003 lalu.\r\n\r\nRS tersebut dibangun sebagai pusat medis untuk pasien SARS.'}},
#   'contentDetails': {'duration': 'PT1M', 'dimension': '2d', 'definition': 'hd', 'caption': 'false',
#                      'licensedContent': True, 'projection': 'rectangular'}},
#  {'kind': 'youtube#video', 'etag': '"Fznwjl6JEQdo1MGvHOGaz_YanRU/mEnL_XTV7f-gX1h-2_HMk7xPWpk"', 'id': 'mO4P2PB7wjA',
#   'snippet': {'publishedAt': '2020-02-04T07:35:32.000Z', 'channelId': 'UCabsTV34JwALXKGMqHpvUiA',
#               'title': 'Việt Nam rút ngắn thời gian xét nghiệm virus corona mới | VTV24',
#               'description': 'Thay vì phải đợi tới 3 - 10 ngày, nhờ mồi đặc hiệu từ WHO, thời gian xét nghiệm virus corona tại Việt Nam rút ngắn xuống còn 24 -28 giờ.\n\n► Kênh Youtube Chính Thức của Trung tâm Tin tức VTV24 - Đài Truyền Hình Việt Nam\n►Subscribe kênh ngay: http://bit.ly/VTV24Subscribe\n►Đồng hành cùng VTV24 tại:\nFanpage chính thức      : fb.com/tintucvtv24\nChuyên trang Tài Chính: fb.com/vtv24money\nZalo                                  : zalo.me/1571891271885013375\nInstagram                       : instagram.com/vtv24news/\nYoutube Channel           : youtube.com/vtv24',
#               'thumbnails': {
#                   'default': {'url': 'https://i.ytimg.com/vi/mO4P2PB7wjA/default.jpg', 'width': 120, 'height': 90},
#                   'medium': {'url': 'https://i.ytimg.com/vi/mO4P2PB7wjA/mqdefault.jpg', 'width': 320, 'height': 180},
#                   'high': {'url': 'https://i.ytimg.com/vi/mO4P2PB7wjA/hqdefault.jpg', 'width': 480, 'height': 360},
#                   'standard': {'url': 'https://i.ytimg.com/vi/mO4P2PB7wjA/sddefault.jpg', 'width': 640, 'height': 480},
#                   'maxres': {'url': 'https://i.ytimg.com/vi/mO4P2PB7wjA/maxresdefault.jpg', 'width': 1280,
#                              'height': 720}}, 'channelTitle': 'VTV24',
#               'tags': ['chuyển động 24h', 'tin tức vtv24', 'thời sự vtv24', 'tin tức', 'VTV24', 'Tin tức mới nhất',
#                        'tin tức trong ngày', 'tin tức VTV1', 'virus corona mới', 'nCoV', 'thời gian xét nghiệm',
#                        'mồi đặc hiệu', 'WHO'], 'categoryId': '25', 'liveBroadcastContent': 'none',
#               'localized': {'title': 'Việt Nam rút ngắn thời gian xét nghiệm virus corona mới | VTV24',
#                             'description': 'Thay vì phải đợi tới 3 - 10 ngày, nhờ mồi đặc hiệu từ WHO, thời gian xét nghiệm virus corona tại Việt Nam rút ngắn xuống còn 24 -28 giờ.\n\n► Kênh Youtube Chính Thức của Trung tâm Tin tức VTV24 - Đài Truyền Hình Việt Nam\n►Subscribe kênh ngay: http://bit.ly/VTV24Subscribe\n►Đồng hành cùng VTV24 tại:\nFanpage chính thức      : fb.com/tintucvtv24\nChuyên trang Tài Chính: fb.com/vtv24money\nZalo                                  : zalo.me/1571891271885013375\nInstagram                       : instagram.com/vtv24news/\nYoutube Channel           : youtube.com/vtv24'},
#               'defaultAudioLanguage': 'vi'},
#   'contentDetails': {'duration': 'PT5M3S', 'dimension': '2d', 'definition': 'hd', 'caption': 'false',
#                      'licensedContent': True, 'projection': 'rectangular'}},
#  {'kind': 'youtube#video', 'etag': '"Fznwjl6JEQdo1MGvHOGaz_YanRU/qO7b1sRKPYCN3Nchr4qfozgk8QY"', 'id': 'p5zobT0A0Sk',
#   'snippet': {'publishedAt': '2020-02-03T07:29:59.000Z', 'channelId': 'UCN7B-QD0Qgn2boVH5Q0pOWg',
#               'title': 'China ने Corona Virus से लड़ने के लिए दस दिन में बनाया 1000 बेड का अस्पताल',
#               'description': 'चीन का वुहान शहर कोरोना वायरस से जूझ रहा है और इससे लड़ने के लिए उसने दस दिनों में एक हज़ार बेड का अस्पताल बनाकर दिखा दिया है.\n\n#China #Wuhan #CoronaVirus\n\nऐसे ही और दिलचस्प वीडियो देखने के लिए चैनल सब्सक्राइब ज़रूर करें-\nhttps://www.youtube.com/channel/UCN7B-QD0Qgn2boVH5Q0pOWg?disable_polymer=true\n\nबीबीसी हिंदी से आप इन सोशल मीडिया चैनल्स पर भी जुड़ सकते हैं-\n\nफ़ेसबुक- https://www.facebook.com/BBCnewsHindi\nट्विटर- https://twitter.com/BBCHindi\nइंस्टाग्राम- https://www.instagram.com/bbchindi/\n\nबीबीसी हिंदी का एंड्रॉयड ऐप डाउनलोड करने के लिए क्लिक करें- https://play.google.com/store/apps/details?id=uk.co.bbc.hindi',
#               'thumbnails': {
#                   'default': {'url': 'https://i.ytimg.com/vi/p5zobT0A0Sk/default.jpg', 'width': 120, 'height': 90},
#                   'medium': {'url': 'https://i.ytimg.com/vi/p5zobT0A0Sk/mqdefault.jpg', 'width': 320, 'height': 180},
#                   'high': {'url': 'https://i.ytimg.com/vi/p5zobT0A0Sk/hqdefault.jpg', 'width': 480, 'height': 360},
#                   'standard': {'url': 'https://i.ytimg.com/vi/p5zobT0A0Sk/sddefault.jpg', 'width': 640, 'height': 480}},
#               'channelTitle': 'BBC News Hindi',
#               'tags': ['BBC Hindi', 'hindi news', 'news in hindi', 'China', 'CHina Wuhan', 'CHina Hospital',
#                        'Wuhan Hospital', 'Corona Virus', 'बीबीसी हिन्दी', 'हिन्दी समाचार', 'हिन्दी ख़बर', 'चीन',
#                        'वुहान', 'चीनी शहर वुहान', 'कोरोना वायरस', 'वुहान अस्पताल', 'बीजिंग'], 'categoryId': '25',
#               'liveBroadcastContent': 'none',
#               'localized': {'title': 'China ने Corona Virus से लड़ने के लिए दस दिन में बनाया 1000 बेड का अस्पताल',
#                             'description': 'चीन का वुहान शहर कोरोना वायरस से जूझ रहा है और इससे लड़ने के लिए उसने दस दिनों में एक हज़ार बेड का अस्पताल बनाकर दिखा दिया है.\n\n#China #Wuhan #CoronaVirus\n\nऐसे ही और दिलचस्प वीडियो देखने के लिए चैनल सब्सक्राइब ज़रूर करें-\nhttps://www.youtube.com/channel/UCN7B-QD0Qgn2boVH5Q0pOWg?disable_polymer=true\n\nबीबीसी हिंदी से आप इन सोशल मीडिया चैनल्स पर भी जुड़ सकते हैं-\n\nफ़ेसबुक- https://www.facebook.com/BBCnewsHindi\nट्विटर- https://twitter.com/BBCHindi\nइंस्टाग्राम- https://www.instagram.com/bbchindi/\n\nबीबीसी हिंदी का एंड्रॉयड ऐप डाउनलोड करने के लिए क्लिक करें- https://play.google.com/store/apps/details?id=uk.co.bbc.hindi'},
#               'defaultAudioLanguage': 'hi'},
#   'contentDetails': {'duration': 'PT1M23S', 'dimension': '2d', 'definition': 'hd', 'caption': 'false',
#                      'licensedContent': True, 'projection': 'rectangular'}},
#  {'kind': 'youtube#video', 'etag': '"Fznwjl6JEQdo1MGvHOGaz_YanRU/2M0nq1jwgrMCNiKUWt3bGHNCniY"', 'id': 'vX_Au3XeTz0',
#   'snippet': {'publishedAt': '2020-02-04T08:44:03.000Z', 'channelId': 'UCIW9cGgoRuGJnky3K3tbzNg',
#               'title': 'Bản tin về virus corona mới ngày 4.2.2020: Người Việt mắc viêm phổi Vũ Hán tiếp tục tăng',
#               'description': '#thoisuthanhnien #tinnongthanhnien #phongsuthanhnien\nBản tin về virus Corona số ngày 4.2.2020 của Báo Thanh Niên phát vào lúc 19 giờ tại địa chỉ thanhnien.vn và kênh YouTube Báo Thanh Niên. Nội dung là những thông tin mới nhất, đầy đủ nhất về diễn biến của dịch bệnh viêm phổi Vũ Hán do chủng mới của virus Corona gây ra tại Việt Nam và cả trên thế giới.\n\n#viruscorona #bảntincorona #BảntinvirusCorona #BáoThanhNiên #viêmphổicorona #khẩutrang #thiếukhẩutrang #virútcorona #viêmphổiTrungQuốc #viêmphổiVũVán #VũHán #virusviêmphổi\n\n--------\nĐăng kí theo dõi kênh để xem những tin tức mới nhất: \n\nhttp://popsww.com/BaoThanhNien\n\nTin tức báo Thanh Niên - Đọc tin mới online - tin nhanh - tin 24h - thời sự\nKênh YouTube chính thức của Báo Thanh Niên. Đăng kí theo dõi kênh để xem những tin tức mới nhất: \n\nhttp://popsww.com/BaoThanhNien\n\nWebsite: http://thanhnien.vn/\nFanpage: https://www.facebook.com/thanhnien\n\nYoutube Channel: http://popsww.com/BaoThanhNien\n\n268 - 270 Nguyễn Đình Chiểu, Phường 6, Q.3, TP HCM \nĐT: (+84.8) 39302302 \nFax: (+84.8) 39309939 \nEmail: tnmedia@thanhnien.vn',
#               'thumbnails': {
#                   'default': {'url': 'https://i.ytimg.com/vi/vX_Au3XeTz0/default_live.jpg', 'width': 120, 'height': 90},
#                   'medium': {'url': 'https://i.ytimg.com/vi/vX_Au3XeTz0/mqdefault_live.jpg', 'width': 320,
#                              'height': 180},
#                   'high': {'url': 'https://i.ytimg.com/vi/vX_Au3XeTz0/hqdefault_live.jpg', 'width': 480, 'height': 360},
#                   'standard': {'url': 'https://i.ytimg.com/vi/vX_Au3XeTz0/sddefault_live.jpg', 'width': 640,
#                                'height': 480},
#                   'maxres': {'url': 'https://i.ytimg.com/vi/vX_Au3XeTz0/maxresdefault_live.jpg', 'width': 1280,
#                              'height': 720}}, 'channelTitle': 'Báo Thanh Niên',
#               'tags': ['virus corona', 'bản tin corona', 'Bản tin virus Corona', 'Báo Thanh Niên', 'viêm phổi corona',
#                        'khẩu trang', 'thiếu khẩu trang', 'vi rút corona', 'viêm phổi Trung Quốc', 'viêm phổi Vũ Ván',
#                        'Vũ Hán', 'virus viêm phổi'], 'categoryId': '25', 'liveBroadcastContent': 'live', 'localized': {
#           'title': 'Bản tin về virus corona mới ngày 4.2.2020: Người Việt mắc viêm phổi Vũ Hán tiếp tục tăng',
#           'description': '#thoisuthanhnien #tinnongthanhnien #phongsuthanhnien\nBản tin về virus Corona số ngày 4.2.2020 của Báo Thanh Niên phát vào lúc 19 giờ tại địa chỉ thanhnien.vn và kênh YouTube Báo Thanh Niên. Nội dung là những thông tin mới nhất, đầy đủ nhất về diễn biến của dịch bệnh viêm phổi Vũ Hán do chủng mới của virus Corona gây ra tại Việt Nam và cả trên thế giới.\n\n#viruscorona #bảntincorona #BảntinvirusCorona #BáoThanhNiên #viêmphổicorona #khẩutrang #thiếukhẩutrang #virútcorona #viêmphổiTrungQuốc #viêmphổiVũVán #VũHán #virusviêmphổi\n\n--------\nĐăng kí theo dõi kênh để xem những tin tức mới nhất: \n\nhttp://popsww.com/BaoThanhNien\n\nTin tức báo Thanh Niên - Đọc tin mới online - tin nhanh - tin 24h - thời sự\nKênh YouTube chính thức của Báo Thanh Niên. Đăng kí theo dõi kênh để xem những tin tức mới nhất: \n\nhttp://popsww.com/BaoThanhNien\n\nWebsite: http://thanhnien.vn/\nFanpage: https://www.facebook.com/thanhnien\n\nYoutube Channel: http://popsww.com/BaoThanhNien\n\n268 - 270 Nguyễn Đình Chiểu, Phường 6, Q.3, TP HCM \nĐT: (+84.8) 39302302 \nFax: (+84.8) 39309939 \nEmail: tnmedia@thanhnien.vn'}},
#   'contentDetails': {'duration': 'PT0S', 'dimension': '2d', 'definition': 'sd', 'caption': 'false',
#                      'licensedContent': True, 'projection': 'rectangular'}}]
#

def crawl_on_linux(request):
    if request.method == "GET":

        webdriver_path = r'chromedriver_linux64\chromedriver'  # path
        os.environ['webdriver.chrome.driver'] = webdriver_path
        display = Display(visible=0, size=(800, 600))
        display.start()

        with open('language_dict.txt', 'r', encoding='utf-8') as f:  # language_dict.txt에 저장된 {언어: {중국어: 영어}} 불러오기.
            language_dict = json.loads(f.read())

        # while True:
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
