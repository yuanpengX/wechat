
#coding=gb2312
from django.shortcuts import render
from django.http import HttpResponse
import time
import hashlib
import os
# python django �ṩ�����ô������ĵĿ�
from django.utils.encoding import smart_str
from django.views.decorators.csrf import csrf_exempt  
# ����һ��XML�Ľ�����
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET
# Create your views here.

TOKEN = "diaoxiong"
APP_ID = "wx45779b96e3d17b91"
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
	return render(request,'reply_text.xml',
				{'toUser':msg["FromUserName"],
				'fromUser':msg["ToUserName"],
				'createTime':str(int(time.time())),
				'msgType':msg["MsgType"],
				'content':msg["Content"],
				},
				content_type = "application/xml")

#����Ϣ�������ֵ�����
def parse_msg(rawStr):
	root = ET.fromstring(rawStr)
	msg = {}
	for child in root:
		msg[child.tag] = child.text
	return msg

