import urllib.request
import urllib.error
import urllib.parse
import json
import copy
import re



def d_Course_Name(c):
    res=c.split(' ')
    return res[0]+res[1]

def d_session(s):
    return s.split(' ')[0]

def d_time(time_set):
    converted_time=[]
    if re.search('<br>',str(time_set)):
        return 'error'
    if time_set[0]=='TBA':
        return 'TBA'
    for time in time_set:
        result=re.search('([A-Za-z]*) (\d+):(\d+)([A-Z]*) - (\d+):(\d+)([A-Z]*)',time)
        t=[]
        if result.group(4)=='PM' and result.group(2)!='12':
            t.append(str(int(result.group(2))+12)+':'+result.group(3))
        else:
            t.append(result.group(2)+':'+result.group(3))
        if result.group(7) == 'PM' and result.group(5) != '12':
            t.append(str(int(result.group(5)) + 12) + ':' + result.group(6))
        else:
            t.append(result.group(5) + ':' + result.group(6))
        date=result.group(1)
        for i in range(int(len(result.group(1))/2)):
            if i>0:
                t.append(t[0])
                t.append(t[1])
            if date[i*2]== 'M':
                t.append(1)
            elif date[i*2]=='T':
                if date[i*2+1]=='u':
                    t.append(2)
                else:
                    t.append(4)
            elif date[i*2]=='W':
                t.append(3)
            elif date[i*2]=='F':
                t.append(5)
            elif date[i*2]=='S':
                if date[i*2+1]=='a':
                    t.append(6)
                else:
                    t.append(7)
        for element in t:
            converted_time.append(element)
    return converted_time

def spider(url):
    lib = urllib.request
    school_web = lib.Request(url)
    try :
        resp = lib.urlopen(school_web)
    except urllib.error.HTTPError as e:
        print(e.code())
        #print(1)
    except urllib.error.URLError as b:
        print(b.reason)
    else:
        patt = re.compile(r'<div class="course">.*?<h2>(.*?)</h2>.*?<table.*?>.*?<tr>.*?</tr>(.*?)</table>',re.S)
        item=re.findall(patt,str(resp.read()))
        patt = re.compile(r'<tr class="newsect.*?'
                          r'<td.*?>(.*?)</td>'#session
                          r'.*?<td>(.*?)</td>'#date and time
                          r'.*?<td>(.*?)</td>'#room
                          r'.*?<td>(?:<a .*?>)*(.*?)(?:</a>)*?</td>'#instructor
                          r'.*?<td .*?>.*?(\d+).*?</td>'#quota
                          r'.*?<td .*?>.*?(\d+).*?</td>'#enroll
                          r'.*?<td .*?>.*?(\d+).*?</td>'#avail
                          r'.*?<td .*?>.*?(\d+).*?</td>'#wait
                          r'|'
                          r'<tr class="sect'
                          r'.*?<td>(.*?)</td>'  # date and time
                          r'.*?<td>(.*?)</td>'  # Room
                          r'.*?<td>(?:<a .*?>)*(.*?)(?:</a>)*?</td>.*?</tr>'  # instructor
                          ,re.S)
        temp_all_courses=[]
        for a in item:
            b = []
            b.append(a[0])
            b.append(re.findall(patt, str(a[1])))
            temp_all_courses.append(b)
            #print(b)
        all_courses=[]
        for course in temp_all_courses:
            b=[]
            b.append(course[0])
            b.append([])
            infs=course[1]
            i=-1
            for inf in infs:
                if inf[0]!='':
                    c=[]
                    for j in range(len(inf)-3):
                        c.append([inf[j]])
                    b[1].append(c)
                    i=i+1
                else:
                    for j in range(1,4):
                        if inf[j+7]!=b[1][i][j][-1]:
                            b[1][i][j].append(inf[j+7])
            all_courses.append(b)

        values_set=[]
        for course in all_courses:
            #print(course)
            #print(d_session(course[1][0][0][0]))
            values={}
            values['Lname']=d_Course_Name(course[0])
            for situation in course[1]:

                values['session']=d_session(situation[0][0])
                #处理time
                t=d_time(situation[1])
                if t=='TBA' or t=='error':
                    continue
                post_t=[]
                for t_element in t:
                    post_t.append(t_element)
                if len(t)==6:
                    for i in range(6,9):
                        post_t.append(0)
                elif len(t)==3:
                    for i in range(3,9):
                        post_t.append(0)
                #处理完毕
                values['f1']=post_t[0]
                values['t1']=post_t[1]
                values['d1']=post_t[2]
                values['f2']=post_t[3]
                values['t2']=post_t[4]
                values['d2']=post_t[5]
                values['f3']=post_t[6]
                values['t3']=post_t[7]
                values['d3']=post_t[8]
                values_set.append(copy.copy(values))

        params = json.dumps(values_set).encode('utf8')
        data_request = urllib.request.Request("localhost/datadeal.php",params,{'content-type': 'application/json'})
        print(urllib.request.urlopen(data_request, params).read())

'''code
'''
lib = urllib.request
school_web = lib.Request('https://ust.hk/')
patt=re.compile(r'<div id="navigator".*?<div class="depts">(.*?)</div>',re.S)
resp = lib.urlopen(school_web)
hrefs=re.search(patt,str(resp.read()))
hrefs=hrefs.group(1)
patt=re.compile(r'href="(.*?)">')
hrefs=re.findall(patt,hrefs)
for href in hrefs:
    spider(r'https://w5.ab.ust.hk'+href)
'''code end
'''