#coding=utf-8
import requests
import re
import sys
import MySQLdb

reload(sys)
sys.setdefaultencoding("utf-8")
conn = None

class Spider:
	def __init__(self):
		print 'Start scrawling infos'
		self.user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'#init user_agent 
		self.headers = { 'User-Agent' : self.user_agent}#init headers

	#获取源代码
	def getSource(self, url):
		html = requests.get(url)
		return html.text
	#获取每个课程块信息
	def getLessons(self, source):
		lessons = re.findall('deg="0" >(.*?)</li>', source, re.S)
		return lessons
	#获取课程信息，课程名称，课程介绍，课程时间，课程等级，学习人数
	def getLessonInfo(self, lesson):
		info = {}
		info['title'] = re.search('<h2 class="lesson-info-h2"><a(.*?)>(.*?)</a></h2>', lesson, re.S).group(2).strip()
		info['desc'] = re.search('<p style="height: 0px; opacity: 0; display: none;">(.*?)</p>', lesson, re.S).group(1).strip()
		timeandlevel = re.findall('<em>(.*?)</em>', lesson, re.S)
		info['time'] = timeandlevel[0].strip().replace("\n","").replace("     ","")
		info['level'] = timeandlevel[1].strip()
		info['learnNumber'] = re.search('"learn-number">(.*?)</em>',lesson, re.S).group(1).strip()
		return info

	#保存课程信息到数据库
	def saveLessonInfos(self, lessonInfos):
		dbTable = 'jikexueyuan'
		conn = MySQLdb.connect(host='localhost', user = 'root', passwd= 'root', db= 'db_jikexueyuan', charset='utf8')
		cur = conn.cursor()
		cur.execute("SET NAMES utf8")
		cur.execute("SET CHARACTER_SET_CLIENT=utf8")
		cur.execute("SET CHARACTER_SET_RESULTS=utf8")
		str_selectTable = "SELECT * FROM %s"%dbTable
		cur.execute(str_selectTable)
		i = 1

		for each in lessonInfos:
			str_insertValue = "INSERT INTO jikexueyuan VALUES ('%s','%s','%s','%s','%s','%s')"%(str(i),each['title'],each['desc'],each['time'],each['level'],each['learnNumber'])
			cur.execute(str_insertValue)
			conn.commit()
			i += 1
		

#这个部分的主要意义是定义要爬取的页面范围，然后把爬取的内容放进整个一个列表中，再把列表中的内容保存到数据库
if __name__ == '__main__':
	#定义课程信息数组
	lessonInfos=[]
	#课程信息页面url
	url = 'http://www.jikexueyuan.com/course/'
	#实例化爬虫
	spider = Spider()
	#取1-10页的信息
	for i in range(1,10):
		#构建分页url
		pageUrl = url + '?pageNum=' + str(i)
		print '正在处理页面：' + pageUrl
		html = spider.getSource(pageUrl)
		lessons = spider.getLessons(html)
		for each in lessons:
			lessoninfo = spider.getLessonInfo(each)
			lessonInfos.append(lessoninfo)
		print '已处理' + str(lessons.__len__()) + '个课程信息。'
	print '极客学院课程信息爬取完毕，正在保存课程信息。。。'
	spider.saveLessonInfos(lessonInfos)
	if conn:
		conn.close()
	print '极客学院课程信息保存完毕。'