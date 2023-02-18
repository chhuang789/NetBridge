# -*- coding: utf-8 -*-
# Build Version Information: 230201-1

# ---------Imports---------
import os
import ssl
import time
import json
import http.client
import requests

import logging.config
# ---------End of imports---------


class RMAApi:
    def __init__(self, logger):
        # ------------Avoid SSL error and ignore SSL Warning-------------
        requests.packages.urllib3.disable_warnings()
        ssl._create_default_https_context = ssl._create_unverified_context
        # ---------End of Avoid SSL error and ignore SSL Warning---------

        # ---------Proxy---------
        self.proxy_enable = False
        # ---------End of Proxy---------

        self.session = requests.Session()
        self.theTimeout = 10
        self.connection = None
        #self.logger = logger
        self.SerialNumber = None
        self.URL = None

        # create logger
        #if not os.path.exists("log"):
        #    os.makedirs("log")

        # Load logging.conf
        #logging.config.fileConfig('logging.conf')
        #console_handler = logging.StreamHandler()
        #self.logger = logging.getLogger('NetBridgeRMA')
        self.logger = logger

    # RMA http request

    def RMARequest(self, strURL):
        response = None
        try:
            self.connection = http.client.HTTPConnection(
                "141.147.180.0", 80, timeout=self.theTimeout)

            if (self.connection):
                response = self.session.get(strURL, verify=False)
            else:
                self.logger.error("http(s) connection failed")
        except Exception as e:
            self.logger.error(e)
            return response

        self.logger.debug("response code=%d", response.status_code)
        return response

    # getRMAStats http request
    def getRMAStats(self, strSerialNumber):
        self.SerialNumber = strSerialNumber
        self.URL = "http://141.147.180.0/rma2/public/api/r_require/" + self.SerialNumber
        self.logger.debug(
            "Call RMA API=%s", self.URL)

        response = self.RMARequest(self.URL)
        if (response == None):
            self.logger.warning("response=None")
        else:
            if response.status_code == 200 or response.status_code == 404:
                json_Body = json.loads(response.text)
        return response.status_code, json_Body


'''
def isValidSN(strSN):
    if len(strSN) != 13:
        return 3  # 長度需為13碼
    for ch in strSN:
        if not (ord(ch) in range(97, 122) or ord(ch) in range(65, 90) or ch.isdigit()):
            if ch.isspace():
                return 1  # 序號有空白
            else:
                return 2  # 序號不為英數字
    return 0


def main():
    # create logger
    if not os.path.exists("log"):
        os.makedirs("log")

    # Load logging.conf
    logging.config.fileConfig('logging.conf')
    console_handler = logging.StreamHandler()
    logger = logging.getLogger('NetBridgeRMA')

    myRMAApi = RMAApi()
    strSN = "abc0123456789"
    status = isValidSN(strSN)
    strReply = None
    if status > 0:
        strReply = "請回覆維修產品的序號\n序號為大寫英文字母及數字組合\n長度為13碼\n中間不能有空格"
        logger.debug(strReply)
    else:
        try:
            status, json_workers = myRMAApi.getRMAStats(strSN.upper())
            if status == 200:
                if len(json_workers) > 0:
                    logger.debug("Serial Number=%s", json_workers[0]['Serial'])
                    logger.debug("Status=%s", json_workers[0]['Status'])
                    logger.debug("Repair Order=%s",
                                 json_workers[0]['Repair_Order'])
            elif status == 404:
                if len(json_workers) > 0:
                    logger.debug("Status=%s", json_workers[0]['Status'])
            else:
                logger.error("status = %d", status)
        except Exception as e:
            logger.error(e)

    exit


if __name__ == "__main__":
    main()
'''
