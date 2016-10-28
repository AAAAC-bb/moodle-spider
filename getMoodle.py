# -*- coding:utf-8 -*-
import requests,re,pymysql
from bs4 import BeautifulSoup
# define value
sess = requests.Session()
headers = {
		"Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
		"Accept-Encoding":"gzip, deflate",
		"Cache-Control":"max-age=0",
		"Connection":"keep-alive",
		"Content-Type":"application/x-www-form-urlencoded",
		"Upgrade-Insecure-Requests":"1",
		"User-Agent":"Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36"
	}
# login function
def Login():
	# define login value
	login_true = True
	# logi
	login_url = "http://*.*.*.*/moodle/login/index.php"
	while login_true:
		Username = str(input("请输入用户名:"))
		Password = str(input("请输入密  码:"))
		login_payload = {
			"username":Username,
			"password":Password
		}
		# login into moodel
		login_res = sess.post(login_url,data = login_payload,headers = headers,verify=False).text
		if login_res.find("我的主页") != -1:
			print("登录成功")
			login_true = False
		else:
			print("登录失败")
# get question & answer
def getData(url,page):
	url = url + "&page=" + str(page)
	print("正在抓取:" + url)
	datasource = sess.get(url,headers = headers).text
	soup = BeautifulSoup(datasource,'html.parser')
	qList = soup.find_all('div',class_='formulation clearfix')
	sList = soup.find_all('div',class_='rightanswer')
	qList = converData(qList)
	sList = converData(sList)
	allList = []
	listCount = len(qList)
	for i in range(0,listCount):
		allList.append({'question':qList[i],'answer':sList[i]})
	return allList
# converData
def converData(listData):
	datalist = []
	for unit in listData:
		unit = unit.get_text()
		unit = unit.replace("题干","")
		datalist.append(unit)
	return datalist
# insert mysql
def insertQS(datalist):
	#define value
	count = 0
	fail = 0
	repeat = 0
	#database connection
	conn = pymysql.connect(host = '127.0.0.1', port = 3306,	user = 'root', passwd = '', db = 'moodle_data', charset = 'utf8')
	cur = conn.cursor()
	#insert question&answer
	for index in datalist:
		question = index['question']
		answer = index['answer']
		question = checkInject(question)
		answer = checkInject(answer)
		if checkQS(question,"中级网络管理员"):
			if cur.execute('insert into tk_qs(question,answer,category) values (%s,%s,%s)', (question, answer,"中级网络管理员")):
				count += 1
			else:
				fail += 1
		else:
			repeat += 1
		conn.commit()
	cur.close()
	conn.close()
	return(count,fail,repeat)
# check repeat
def checkQS(question,category):
	#database connection
	conn = pymysql.connect(host = '127.0.0.1', port = 3306,	user = 'root', passwd = '', db = 'moodle_data', charset = 'utf8')
	cur = conn.cursor()
	cur.execute("select question from tk_qs where question = %s and category = %s",(question,category))
	if cur.fetchone():
		cur.close()
		conn.close
		return False
	else:
		cur.close()
		conn.close
		return True
# check inject
def checkInject(q):  
	dirty_stuff = ["\"", "\\", "/", "*", "'", "=", "-", "#", ";", "<", ">", "+", "%"]  
	for stuff in dirty_stuff:
		q = q.replace(stuff,"")
	return(q)
# Main program
def getUrl():
	# course URL
	html = sess.get("http://*.*.*.*/moodle/mod/quiz/view.php?id=13710",headers = headers).text
	reg = r'="attempt.*?value="(.*?)"'
	data = re.findall(reg,html)
	return(data)
def main():
	# Login
	Login()
	# get url
	urlList = getUrl()
	for url in urlList:
		# 
		url = "http://*.*.*.*/moodle/mod/quiz/review.php?attempt=%s" %url
		Datalist = []
		for page in range(0,10):
			Datalist.extend(getData(url, page))
		count,fail,repeat =  insertQS(Datalist)
		print("成功抓取%s条记录,过滤%s条数据,其中%s条记录插入数据库失败" %(count,repeat,fail))
	print("抓取结束")
# ****enter****
if __name__ == "__main__":
	main()