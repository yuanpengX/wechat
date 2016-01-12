from django.shortcuts import render
from django.http import HttpResponse
import time
import os
# python django 提供的良好处理中文的库
from django.utils.encoding import smart_str
from django.views.decorators.csrf import csrf_exempt  
# 加在一个XML的解析库
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET
# Create your views here.

TOKEN = "diaoxiong"
APP_ID = "wx45779b96e3d17b91"
#禁用DJANGo提供的跨站脚本攻击服务
@csrf_exempt  
def process(request):
	if request.method == 'GET':
		return HttpResponse(checkSignature(request))
	elif request.method == "POST":
		return reply(request)

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
	tmpStr = "%s%s%s"%tuple(tmpList)
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
	return render(request,'reply_text.xml',
				{'toUser':msg["fromUserName"],
				'fromUser':msg["toUserName"],
				'createTime':time.time(),
				'msgType':msg["MsgType"],
				'content':msg["Content"],
				},
				content_type = "application/xml")

#将消息解析成字典类型
def parse_msg(rawStr):
	root = ET.fromstring(rawStr)
	msg = {}
	for child in root:
		msg[child.tag] = child.text
	return msg

