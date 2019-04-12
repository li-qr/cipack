#!/usr/local/env python
# _*_ coding: utf-8 _*_
from sys import argv
import requests
import base64
from string import Template
from lxml import etree
import sys  

reload(sys)  
sys.setdefaultencoding('utf8')
__author__ = "quan.li"

login_url = '**'
editions_url = '**'
alert_url = Template('**tos=$user&content=$content')
compile_url = '**'
compile_info_url = '**='
progress_url= Template('**/$module/compile/$compile')

def enpasswd(password):
    '''
    针对于登陆中心密码采用转义传输。
    '''
    key = "**"
    keylength = 10
    code = ""
    for i in range(len(password)):
        keyindex = i % keylength
        code += chr(ord(password[i])^ord(key[keyindex]))
    return base64.b64encode(code)

def get_token(user_name,pass_word):
    '''
    获取token，调用接口时用token证明身份。
    '''
    param = {"user": user_name, "password": enpasswd(
        pass_word), "subsystem": "vela", "autologin": "false"}
    response = requests.post(login_url, data = param)
    return response.cookies.get_dict()['utoken']

def compile_edition_wapper(token,conf):
    '''
    对module_edition版本进行打包
    '''
    def compile_edition(module_edition):
        if conf['progress']:
            version = get_compile_version(module_edition['edition'])
            push_alert(conf['user'],"正在打包："+module_edition['module']['module']+" 四位版本号："+version)
        cookie = requests.cookies.RequestsCookieJar()
        cookie.set('utoken',token,domain='.elong.com',path='/')
        data = {"step[]": ["pull","build"],
                "buildExec": "",
                "buildType": "shell",
                "moduleId": module_edition['module']['module_id'],
                "editionId": module_edition['edition']}
        re = requests.post(compile_url,data=data,cookies=cookie).json()
        return {'module':module_edition['module']['module_id'],'complite':re['data']['id']}
    return compile_edition

def fetch_progress(module,compile,token):
    '''
    获取打包进度，‘编译中’，‘编译成功’，‘编译失败’
    '''
    cookie = requests.cookies.RequestsCookieJar()
    cookie.set('utoken',token,domain='.elong.com',path='/')
    response = requests.get(progress_url.substitute(module=module,compile=compile),cookies=cookie)
    selector = etree.HTML(response.text)
    status = selector.xpath('/html/body/div[1]/div[2]/div/div[1]/div[2]/p[1]/span/text()')
    info = selector.xpath('//*[@id="log-wrapper"]/a')
    return {"status":status[0],"info":info[0].attrib['href'] if len(info) != 0 else "等待ci返回"}

def fetch_errors(info_url):
    '''
    从ci中获取打包详情，提取异常日志
    '''
    response = requests.get(info_url)
    result = ""
    index = 0
    for line in response.text.splitlines():
        if index > 3:
            break
        if(line.startswith("[ERROR]")):
            index += 1
            result = result + line + "\n"
    return result

def get_editions(module_id,token):
    '''
    获取所有版本号
    '''
    cookie = requests.cookies.RequestsCookieJar()
    cookie.set('utoken',token,domain='.elong.com',path='/')
    reponse_json = requests.get(editions_url+str(module_id),cookies=cookie).json()
    return reponse_json['data']['data']

def get_compile_version(edition):
    '''
    获取打包生成的四位版本号.
    '''
    reponse_json = requests.get(compile_info_url+str(edition)).json()
    return reponse_json['data']['version']

def push_alert(user,content):
    '''
    调用ops-robot通知
    '''
    requests.get(alert_url.substitute(user=user,content=content))
