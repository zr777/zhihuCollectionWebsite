import os
import json
from bs4 import BeautifulSoup
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
# 参考 http://stackoverflow.com/questions/27981545/suppress-insecurerequestwarning-unverified-https-request-is-being-made-in-pytho
import requests_cache
requests_cache.install_cache('demo_cache')


Cookie_FilePlace = r'.'
Default_Header = {'User-Agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36",
                   'Host': "www.zhihu.com",
                   'Origin': "http://www.zhihu.com",
                   'Pragma': "no-cache",
                   'Referer': "http://www.zhihu.com/"}
Zhihu_URL = 'https://www.zhihu.com'
Login_URL = Zhihu_URL + '/login/email'
Profile_URL = 'https://www.zhihu.com/settings/profile'
Collection_URL = 'https://www.zhihu.com/collection/%d'
Cookie_Name = 'cookies.json'

os.chdir(Cookie_FilePlace)

r = requests.Session()

#--------------------Prepare--------------------------------#
r.headers.update(Default_Header)
if os.path.isfile(Cookie_Name):
    with open(Cookie_Name, 'r') as f:
        cookies = json.load(f)
        r.cookies.update(cookies)

def login(r):
    print('====== zhihu login =====')
    email = input('email: ')
    password = input("password: ")
    print('====== logging.... =====')
    data = {'email': email, 'password': password, 'remember_me': 'true'}
    value = r.post(Login_URL, data=data).json()
    print('====== result:', value['r'], '-', value['msg'])
    if int(value['r']) == 0:
        with open(Cookie_Name, 'w') as f:
            json.dump(r.cookies.get_dict(), f)

def isLogin(r):
    url = Profile_URL
    value = r.get(url, allow_redirects=False, verify=False)
    status_code = int(value.status_code)
    if status_code == 301 or status_code == 302:
        print("未登录")
        return False
    elif status_code == 200:
        return True
    else:
        print(u"网络故障")
        return False
        
if not isLogin(r):
    login(r)
    

#---------------------------------------------------------------------#
url_answer_dict= {}
# 单独生成一个答案的url和答案文本之间的字典，便于后台提供api服务，与123行相关

#-----------------------get collections-------------------------------#
def getCollectionsList():
    collections_list = []
    content = r.get(Profile_URL).content
    soup = BeautifulSoup(content, 'lxml')
    own_collections_url = 'http://' + soup.select('#js-url-preview')[0].text + '/collections'
    page_num = 0
    while True:
        page_num += 1
        url = own_collections_url + '?page=%d'% page_num
        content = r.get(url).content
        soup = BeautifulSoup(content, 'lxml')
        data = soup.select_one('#data').attrs['data-state']
        collections_dict_raw = json.loads(data)['entities']['favlists'].values()
        if not collections_dict_raw: 
        # if len(collections_dict_raw) == 0:
            break
        for i in collections_dict_raw:
            # print(i['id'],' -- ', i['title'])
            collections_list.append({
                'title': i['title'], 
                'url': Collection_URL % i['id'],
            })
    print('====== prepare Collections Done =====')
    return collections_list

#-------------------------
def getQaDictListFromOneCollection(collection_url = 'https://www.zhihu.com/collection/71534108'):
    qa_dict_list = []
    page_num = 0
    while True:
        page_num += 1
        url = collection_url + '?page=%d'% page_num
        content = r.get(url).content
        soup = BeautifulSoup(content, 'lxml')
        titles = soup.select('.zm-item-title a') # .text ; ['href']
        if len(titles) == 0:
            break
        votes = soup.select('.js-vote-count') # .text 
        answer_urls = soup.select('.toggle-expand') # ['href']
        answers = soup.select('textarea') # .text
        authors = soup.select('.author-link-line .author-link') # .text ; ['href']
        for title, vote, answer_url, answer, author \
        in zip(titles, votes, answer_urls, answers, authors):
            author_img = getAthorImage(author['href'])
            qa_dict_list.append({
                'title': title.text,
                'question_url': title['href'],
                'answer_vote': vote.text,
                'answer_url': answer_url['href'],
                #'answer': answer.text,
                'author': author.text,
                'author_url': author['href'],
                'author_img': author_img,
            })
            url_answer_dict[ 
                answer_url['href'][1:] 
            ] = answer.text
            # print(title.text, ' - ', author.text)
    return qa_dict_list

def getAthorImage(author_url):
    url = Zhihu_URL+author_url
    content = r.get(url).content
    soup = BeautifulSoup(content, 'lxml')
    return soup.select_one('.AuthorInfo-avatar')['src']

def getAllQaDictList():
    ''' 最终结果要是列表和字典的嵌套形式，以便前端解析'''
    all_qa_dict_list = []
    collections_list = getCollectionsList()
    for collection in collections_list:
        all_qa_dict_list.append({
            'ctitle': collection['title'],
            'clist': getQaDictListFromOneCollection(collection['url'])
        })
        print('====== getQa from %s Done =====' % collection['title'])
    return all_qa_dict_list


with open(u'知乎收藏文章.json', 'w', encoding='utf-8') as f:
    json.dump(getAllQaDictList(), f)

with open(u'url_answer.json', 'w', encoding='utf-8') as f:
    json.dump(url_answer_dict, f)
#---------------------utils------------------------------#
# with open('1.html', 'w', encoding='utf-8') as f:
    # f.write(soup.prettify())
# import os
# Cookie_FilePlace = r'E:\python\2017_2_15\zhihu'
# os.chdir(Cookie_FilePlace)
# import json
# dict_ = {}
# with open(u'知乎收藏文章.json', 'r', encoding='utf-8') as f:
#     dict_ = json.load(f)