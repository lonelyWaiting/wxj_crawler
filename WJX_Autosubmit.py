import sys
import getopt
import requests
from bs4 import BeautifulSoup
import re
import random
import time
import datetime
import urllib.parse
import os
import fake_info
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

'''调查页面，获取相关参数'''
# 获取调查问卷的页面

def match_answer(label):
    if label.find('姓名') != -1:
        return '你的名字'
    elif label.find('名字') != -1:
        return '你的名字'
    elif label.find('学院') != -1:
        return '你的学院'
    elif label.find('专业') != -1:
        return '你的学科'
    elif label.find('年级') != -1:
        return '你的年级'
    elif label.find('电话') != -1:
        return '你的电话'
    elif label.find('号码') != -1:
        return '你的电话'
    elif label.find('联系方式') != -1:
        return '你的电话'
    elif label.find('学号') != -1:
        return '你的学号'

    print('Can not Find Match Answer')
    return ''


def get_fill_content(url, user_agent):
    headers = {
    'user-agent': user_agent,
    "Connection": "close"
    }
    r1 = requests.get(url, headers=headers,verify=False)
    setCookie = r1.headers['Set-Cookie']
    CookieText = re.findall(r'acw_tc=.*?;', setCookie)[0] + re.findall(r'\.ASP.*?;', setCookie)[0] + re.findall(r'jac.*?;', setCookie)[0] + re.findall(r'SERVERID=.*;',setCookie)[0]
    return r1.text,CookieText

# 从页面中获取curid,rn,jqnonce,starttime,同时构造ktimes用作提交调查问卷
def get_submit_query(content):
    curid = re.search(r'\d{8}',content).group()
    rn = re.search(r'\d{9,10}\.\d{8}',content).group()
    jqnonce= re.search(r'.{8}-.{4}-.{4}-.{4}-.{12}',content).group()
    ktimes = random.randint(5, 18)
    starttime = (datetime.datetime.now()-datetime.timedelta(minutes=1)).strftime("%Y/%m/%d %H:%M:%S")
    return curid, rn, jqnonce, ktimes, starttime

#通过ktimes,jqnonce构造jqsign	
def get_jqsign(ktimes, jqnonce):
    result = []
    b = ktimes % 10
    if b == 0:
        b = 1
    for char in list(jqnonce):
        f = ord(char) ^ b
        result.append(chr(f))
    return ''.join(result)
     

'''获取随机答案'''	

# 获取调查问卷的题目
def get_title_list(content):
    main_soup = BeautifulSoup(content, 'lxml')
    title_soup_list = main_soup.find_all(id=re.compile(r'div\d'))
    title_list = []
    for title_soup in title_soup_list:
        try:
            title_str = title_soup.find(class_='div_title_question').get_text().strip()
            title_dict = {
                'title': title_str,
            }
        except:
            title_str = title_soup.find(class_='field-label').get_text().strip()
            title_dict = {
                    'title': title_str,
                }
        title_list.append(title_dict)	 
    return title_list
        
# 随机选择
def match_allanswer(title_list):
    answer_list = []
    for title in title_list:
        answer_list.append(match_answer(title['title']))
    return answer_list
    
#构造符合样式的提交数据
def get_submit_data(title_list,answer_list):
    form_data = ''
    for num in range(len(title_list)):
        form_data += str(num+1) + '$' + str(answer_list[num]) + '}'
    return form_data[:-1]

def Auto_WjX():
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36"##UserAgent().random
    fill_content,cookies = get_fill_content(fill_url,user_agent)#网页源代码，cookies
    title_list = get_title_list(fill_content) #所有题目
    '''获取相关参数'''
    curid, rn, jqnonce, ktimes,starttime = get_submit_query(fill_content)
    jqsign = get_jqsign(ktimes,jqnonce)
    time_stamp = '{}{}'.format(int(time.time()), random.randint(100, 200))  # 生成一个时间戳，最后三位为随机数
    #curid, time_stamp, starttime, ktimes, rn, jqnonce, jqsign
    Parameters = {
            'curID': curid,
            'starttime': starttime,
            "source": "directphone",
            'submittype': '1',
            'ktimes':ktimes,
            'hlv': '1',
            'rn': rn,   
            't': time_stamp,
            'jqnonce':jqnonce,
            'jqsign':jqsign,
        }
    headers = {
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Connection": "keep-alive",
        "Content-Type": "application/x-www-form-urlencoded",
        "Cookie": cookies,
        "Host": root_url,
        "Origin": http_url,
        "Referer": fill_url,
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": user_agent,
        "X-Requested-With": "XMLHttpRequest"
    }

    if isCNSite == True:
        headers['Accept'] = "*/*"
    else:
        headers['Accept'] = "text/plain, */*; q=0.01"

    answer_data = match_allanswer(title_list)
    submit_data = get_submit_data(title_list,answer_data)
    data = {'submitdata':str(submit_data)}
    # 发送请求
    try:
        r = requests.post(url=submit_url, headers=headers, data=data, params=Parameters, verify=False, timeout=10)
        #通过测试返回数据中表示成功与否的关键数据（’10‘or '22s'）在开头,所以只需要提取返回数据中前两位元素
        result = r.text[0:2]  
        return result
    except requests.exceptions.ProxyError:
        print('request ProxyError')
    except requests.exceptions.ReadTimeout:
        print('request ReadTimeout')
    except requests.exceptions.BaseHTTPError:
        print('request BaseHTTPError')
    except requests.exceptions.ChunkedEncodingError:
        print('request ChunkedEncoding Error')
    except requests.exceptions.ConnectionError:
        print('request ConnectionError')
    except requests.exceptions.ConnectTimeout:
        print('request ConnnectTimeout')
    except requests.exceptions.FileModeWarning:
        print("request FileModeWarning")
    except requests.exceptions.HTTPError:
        print('request HTTPError')
    except requests.exceptions.InvalidHeader:
        print('request InvalidHeader')
    except requests.exceptions.InvalidProxyURL:
        print('request InvalideProxyURL')
    except requests.exceptions.InvalidSchema:
        print('request InvalidSchema')
    except requests.exceptions.InvalidURL:
        print('request InvalidURL')
    except requests.exceptions.MissingSchema:
        print('request MissingSchema')
    except requests.exceptions.RequestException:
        print('request RequestException')
    except requests.exceptions.RequestsDependencyWarning:
        print('request RequestDependencyWarning')
    except requests.exceptions.RequestsWarning:
        print('request RequestsWarning')
    except requests.exceptions.RetryError:
        print('request RetryError')
    except requests.exceptions.SSLError:
        print('request SSLError')
    except requests.exceptions.StreamConsumedError:
        print('request StreamConsumedError')
    except requests.exceptions.Timeout:
        print('request Timeout')
    except requests.exceptions.TooManyRedirects:
        print('request TooManyRedirects')
    except requests.exceptions.UnrewindableBodyError:
        print('request UnrewindableBodyError')
    except requests.exceptions.URLRequired:
        print('request URLRequired')


def main():
    success = False
    while success == False:
        try:
            result= Auto_WjX()
            if int(result) in [10]:
                print('[ Response : %s ]  ===> 提交成功！！！！' % result)
                success = True
            else:
                print('[ Response : %s ]  ===> 提交失败！！！！' % result)
        #捕获错误
        except(TypeError,IndexError,ValueError):
            continue

if __name__ == '__main__':
    # fill_url = 'https://www.wjx.top/m/94264221.aspx'
    # root_url = 'www.wjx.top'
    startTime   = datetime.datetime(2020, 10, 25, 20, 00, 6)
    while datetime.datetime.now() < startTime:
        time.sleep(1)

    fill_url = 'https://www.wjx.cn/jq/95035576.aspx'
    root_url = 'www.wjx.cn'
    http_url = 'https://' + root_url
    submit_url = http_url + '/joinnew/processjq.ashx'
    isCNSite  = True
    main()