
#coding=gb2312
from django.shortcuts import render
from django.http import HttpResponse
import time
import hashlib
import os
# python django �ṩ�����ô������ĵĿ�
from django.utils.encoding import smart_str
from django.views.decorators.csrf import csrf_exempt
import sys, urllib, urllib2, json
# ����һ��XML�Ľ�����
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET
# Create your views here.

TOKEN = "diaoxiong"
APP_ID = "wx45779b96e3d17b91"
API_STORE_KEY = "7aa30ddb083f3f3c4c6e09bc084f57a4"
#����DJANGo�ṩ�Ŀ�վ�ű���������
@csrf_exempt
def process(request):
	if request.method == 'GET':
		return HttpResponse(checkSignature(request))
	elif request.method == "POST":
		x = reply(request)
		return HttpResponse(x,content_type="application/xml")

#��GET������ǩ����֤
def checkSignature(request):
	global TOKEN
	#��÷�����GET������
	signature = request.GET.get("signature",None)
	timestamp = request.GET.get("timestamp",None)
	nonce = request.GET.get("nonce",None)
	echoStr = request.GET.get("echostr",None)
	#ȡ���Լ���token
	token = TOKEN
	#����������
	tmpList = [token,nonce,timestamp]
	tmpList.sort()
	tmpStr = "%s%s%s"% tuple(tmpList)
	#����SHA1��ϢժҪ
	tmpStr = hashlib.sha1(tmpStr).hexdigest()
	if tmpStr == signature:
		#ժҪ��ǩ��һ��
		return echoStr
	else:
		return "Hello World"

#��Է�����POST���������ظ�����
def reply(request):
	# ����õ�XML���ݽ���һ�ν���
	xml = smart_str(request.body)
	msg = parse_msg(xml)
	#����õ�����ԭ�����ظ�������
	content = msg["Content"]
	#��΢�ŷ������ﴫ��������UNICODE���ı��뷽ʽ
	if type(content).__name__ == "unicode":
		content = content.encode('UTF-8') # ͨ��������������str
	content = weather(content)
	return render(request,'reply_text.xml',
				{'toUser':msg["FromUserName"],
				'fromUser':msg["ToUserName"],
				'createTime':str(int(time.time())),
				'msgType':msg["MsgType"],
				'content':content,
				},
				content_type = "application/xml")

#����Ϣ�������ֵ�����
def parse_msg(rawStr):
	root = ET.fromstring(rawStr)
	msg = {}
	for child in root:
		msg[child.tag] = child.text
	return msg

def weather(city):
	global API_STORE_KEY
	BASIC_SERVICE = "HeWeather data service 3.0"
	# ������ַ
	city = urllib2.quote(city)
	url = 'http://apis.baidu.com/heweather/weather/free?city='+city
	apikey = API_STORE_KEY
	req = urllib2.Request(url)
	req.add_header("apikey", apikey)
	#����API��������
	content = urllib2.urlopen(req).read() # �ӷ������������ַ�������һ��str
	#content = content.decode("utf-8") #����ת����utf-8��������������ʾ
	if content:
		data = json.loads(content)
		base = data[BASIC_SERVICE][0]
		CITY = base["basic"]["city"]
		WEATHER = base["now"]["cond"]["txt"]
		TEMPRATURE = base["now"]["tmp"]
		QUALITY = base["aqi"]["city"]["aqi"]
		PM25 = base["aqi"]["city"]["pm25"]
		SPORT = base["suggestion"]["sport"]['txt']
		TRAVEL = base["suggestion"]["uv"]['txt']
		content = u"��ѯ������������:\n���У�" + CITY + u"\n������"+ WEATHER
		content = content + u"\n�¶ȣ�"+ TEMPRATURE+u"C\n��������ָ��:"+QUALITY+u"\nPM2.5:"+PM25
		content = content + u"\n�˶�����:" + SPORT +u"\n���⽨�飺" +TRAVEL
	else:
		content = u"�Բ����޷��õ���Ч����Ϣ"
	return content