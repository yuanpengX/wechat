
#coding=gb2312
from django.shortcuts import render
from django.http import HttpResponse
import time
import hashlib
import os
# python django 提供的良好处理中文的库
from django.utils.encoding import smart_str
from django.views.decorators.csrf import csrf_exempt
import sys, urllib, urllib2, json
# 加在一个XML的解析库
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET
# Create your views here.

TOKEN = "diaoxiong"
APP_ID = "wx45779b96e3d17b91"
API_STORE_KEY = "7aa30ddb083f3f3c4c6e09bc084f57a4"
#禁用DJANGo提供的跨站脚本攻击服务
@csrf_exempt
def process(request):
	if request.method == 'GET':
		return HttpResponse(checkSignature(request))
	elif request.method == "POST":
		x = reply(request)
		return HttpResponse(x,content_type="application/xml")

#用GET方法做签名验证
def checkSignature(request):
	global TOKEN
	#获得服务器GET的内容
	signature = request.GET.get("signature",None)
	timestamp = request.GET.get("timestamp",None)
	nonce = request.GET.get("nonce",None)
	echoStr = request.GET.get("echostr",None)
	#取得自己的token
	token = TOKEN
	#对数据排序
	tmpList = [token,nonce,timestamp]
	tmpList.sort()
	tmpStr = "%s%s%s"% tuple(tmpList)
	#计算SHA1信息摘要
	tmpStr = hashlib.sha1(tmpStr).hexdigest()
	if tmpStr == signature:
		#摘要与签名一致
		return echoStr
	else:
		return "Hello World"

#针对服务器POST的数据做回复处理
def reply(request):
	# 将获得的XML数据进行一次解析
	xml = smart_str(request.body)
	msg = parse_msg(xml)
	#将获得的数据原样返回给服务器
	content = msg["Content"]
	#从微信服务器里传过来的是UNICODE中文编码方式
	if type(content).__name__ == "unicode":
		content = content.encode('UTF-8') # 通过这个把他编码成str
	content = weather(content)
	return render(request,'reply_text.xml',
				{'toUser':msg["FromUserName"],
				'fromUser':msg["ToUserName"],
				'createTime':str(int(time.time())),
				'msgType':msg["MsgType"],
				'content':content,
				},
				content_type = "application/xml")

#将消息解析成字典类型
def parse_msg(rawStr):
	root = ET.fromstring(rawStr)
	msg = {}
	for child in root:
		msg[child.tag] = child.text
	return msg

def weather(city):
	global API_STORE_KEY
	BASIC_SERVICE = "HeWeather data service 3.0"
	# 构造网址
	city = urllib2.quote(city)
	url = 'http://apis.baidu.com/heweather/weather/free?city='+city
	apikey = API_STORE_KEY
	req = urllib2.Request(url)
	req.add_header("apikey", apikey)
	#利用API请求天气
	content = urllib2.urlopen(req).read() # 从服务器给定的字符串会是一个str
	#content = content.decode("utf-8") #将其转化成utf-8编码后可以正常显示
	if content:
		data = json.loads(content)
		base = data[BASIC_SERVICE][0]
		if base['status'] is not "ok":
			return u"抱歉，无法查询到你输入的城市"
		CITY = base["basic"]["city"]
		WEATHER = base["now"]["cond"]["txt"]
		TEMPRATURE = base["now"]["tmp"]
		QUALITY = base["aqi"]["city"]["aqi"]
		PM25 = base["aqi"]["city"]["pm25"]
		SPORT = base["suggestion"]["sport"]['txt']
		TRAVEL = base["suggestion"]["uv"]['txt']
		content = u"查询到的天气如下:\n城市：" + CITY + u"\n天气："+ WEATHER
		content = content + u"\n温度："+ TEMPRATURE+u"C\n空气质量指数:"+QUALITY+u"\nPM2.5:"+PM25
		content = content + u"\n运动建议:" + SPORT +u"\n户外建议：" +TRAVEL
	else:
		content = u"对不起，无法得到有效的信息"
	return content