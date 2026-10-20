# -*- coding: utf-8 -*-
"""
Author: 章豹
Date: 2026/9/18 13:30
LastEditors: Do not edit
LastEditTime: 2026/9/18 13:30
"""
import base64
import hashlib
import hmac
import json
import random
import time
import uuid
from urllib.parse import urlparse

import requests

try:
    from utils.log_print import get_logger  # 从项目根目录运行时
except ImportError:
    from log_print import get_logger  # 在 utils 目录内直接运行时

logger = get_logger()

# 接口地址：正式环境 / 沙箱环境
URL_OFFICIAL = "https://sdk.nuonuo.com/open/v1/services"
URL_SANDBOX = "https://sandbox.nuonuocs.cn/open/v1/services"

# 接口固定参数（对接时分配的凭据）
# 注意：senid 是每次请求的唯一标识（防重放），必须每次随机生成，不要写死！
# 【重要】appSecret 不是 78607195！78607195 是 appKey。
#   开发项目(NuoShuiTongServiceImpl)的日志把 appSecret 也打成了 appKey（log 占位符传参错误），
#   真实 appSecret 存在系统数据字典表 MgmtDataDictionary 中（dtype='sdk_nuonuo_config' 的 appSecret 键），
#   用真实值传入 request_nuonuo_invoice(app_secret=...) 或改此处默认值。
#   用错误的 appSecret 签名，网关一律返回 070601「签名不匹配」。
DEFAULT_SENID = None                                  # None = 每次请求自动生成 32 位随机码
DEFAULT_APP_KEY = "78607195"                          # 平台分配的 appKey
DEFAULT_APP_SECRET = "26A860C451744A21"                             # 真实 appSecret 从数据字典 sdk_nuonuo_config 获取后填入
DEFAULT_TOKEN = "77f21f617f87135fcd97ef1ueud3dxdi"    # accessToken 授权码
DEFAULT_USER_TAX = "339901999999199"                  # 授权商户税号（须与 order.salerTaxNum 一致，否则报 E9302）
DEFAULT_METHOD = "nuonuo.OpeMplatform.requestBillingNew"  # API 方法名


TOKEN_URL = "https://open.nuonuo.com/accessToken"  # 自用型应用获取令牌地址


def get_merchant_token(app_key=DEFAULT_APP_KEY, app_secret=DEFAULT_APP_SECRET, timeout=30):
    """
    自用型应用获取 accessToken（对应官方 SDK 的 getMerchantToken）。
    响应示例：{"code":"200","describe":"成功","result":{"accessToken":"...","refreshToken":"..."}}
    该方法同时可用于诊断 appKey/appSecret 是否正确。
    """
    data = {
        "grant_type": "client_credentials",
        "client_id": app_key,
        "client_secret": app_secret,
    }
    logger.info(f"诺诺获取token请求: {TOKEN_URL} client_id={app_key}")
    resp = requests.post(TOKEN_URL, data=data, timeout=timeout)
    logger.info(f"诺诺获取token响应 [{resp.status_code}]: {resp.text}")
    resp.raise_for_status()
    return resp.json()


def get_isv_token(code, tax_num, redirect_uri, app_key=DEFAULT_APP_KEY,
                  app_secret=DEFAULT_APP_SECRET, timeout=30):
    """
    第三方（ISV）应用通过授权码获取 accessToken（对应官方 SDK 的 getISVToken）。
    注：本项目的 appKey 为 ISV 类型（自用型获取会报 070307 Incorrect appType[ISV]）。
    """
    data = {
        "client_id": app_key,
        "client_secret": app_secret,
        "grant_type": "authorization_code",
        "redirect_uri": redirect_uri,
        "code": code,
        "taxNum": tax_num,
    }
    logger.info(f"诺诺ISV获取token请求: {TOKEN_URL} client_id={app_key} taxNum={tax_num}")
    resp = requests.post(TOKEN_URL, data=data, timeout=timeout)
    logger.info(f"诺诺ISV获取token响应 [{resp.status_code}]: {resp.text}")
    resp.raise_for_status()
    return resp.json()


def refresh_isv_token(refresh_token, app_key=DEFAULT_APP_KEY,
                      app_secret=DEFAULT_APP_SECRET, timeout=30):
    """第三方（ISV）应用刷新 accessToken（对应官方 SDK 的 refreshISVToken）。"""
    data = {
        "refresh_token": refresh_token,
        "client_id": app_key,
        "client_secret": app_secret,
        "grant_type": "refresh_token",
    }
    logger.info(f"诺诺刷新token请求: {TOKEN_URL} client_id={app_key}")
    resp = requests.post(TOKEN_URL, data=data, timeout=timeout)
    logger.info(f"诺诺刷新token响应 [{resp.status_code}]: {resp.text}")
    resp.raise_for_status()
    return resp.json()


def _get_sign_hmac_sha1(url, senid, app_key, app_secret, content, nonce, timestamp):
    """新版 Maven SDK (com.nuonuo:open-sdk:1.0.5.2) 的签名算法（HMAC-SHA1 + Base64）。"""
    path = urlparse(url).path
    parts = path.split("/")
    base_string = (
        f"a={parts[3]}&l={parts[2]}&p={parts[1]}"
        f"&k={app_key}&i={senid}&n={nonce}&t={timestamp}&f={content}"
    )
    sign = base64.b64encode(
        hmac.new(app_secret.encode("utf-8"), base_string.encode("utf-8"), hashlib.sha1).digest()
    ).decode("utf-8")
    logger.info(f"诺诺签名串(hmac_sha1): {base_string}")
    logger.info(f"诺诺签名值(hmac_sha1): {sign}")
    return sign


def _get_sign_sha256(senid, app_secret, nonce, timestamp, token, method, content):
    """
    老版 NNOpenSDK 的签名算法（诺诺网关 070601 签名不匹配时用这种）：
    SHA256(appSecret + senid + nonce + timestamp + token + method + content)，32位大写hex。
    """
    sign_str = f"{app_secret}{senid}{nonce}{timestamp}{token}{method}{content}"
    sign = hashlib.sha256(sign_str.encode("utf-8")).hexdigest().upper()
    logger.info(f"诺诺签名串(sha256): {sign_str}")
    logger.info(f"诺诺签名值(sha256): {sign}")
    return sign


def request_nuonuo_invoice(order=None, content=None, url=URL_OFFICIAL,
                           senid=DEFAULT_SENID, app_key=DEFAULT_APP_KEY,
                           app_secret=DEFAULT_APP_SECRET, token=DEFAULT_TOKEN,
                           user_tax=DEFAULT_USER_TAX, method=DEFAULT_METHOD,
                           sign_algo="hmac_sha1", timeout=30):
    """
    请求开具发票（对应官方 SDK 的 sendPostSyncRequest）。

    :param order:    开票请求体 dict（含 buyerName/invoiceDetail 等），与 content 二选一
    :param content:  开票请求体 JSON 字符串，与 order 二选一（同时传时优先 content）
    :param url:      接口地址，默认正式环境；沙箱测试传 URL_SANDBOX
    :param senid:    唯一标识，32位随机码
    :param app_key:  平台分配的 appKey
    :param app_secret: 平台分配的 appSecret
    :param token:    accessToken 授权码
    :param user_tax: 授权商户税号（必须与 order.salerTaxNum 一致）
    :param method:   API 方法名
    :param sign_algo: 签名算法："hmac_sha1"（官方 Maven open-sdk 算法，已实测通过，默认）或 "sha256"（老版拼串）
    :param timeout:  请求超时秒数
    :return:         接口响应 dict，如 {"code": "E0000", "describe": "开票提交成功",
                     "result": {"invoiceSerialNum": "..."}}

    【报文勾稽校验（网关强校验，不满足会被拒）】
    1. 不含税金额 + 税额 = 含税金额        (E9130)
    2. |不含税金额 × 税率 - 税额| ≤ 0.06   (E9131)
    示例（税率 0.13，含税 1200）：taxExcludedAmount=1061.95, tax=138.05, taxIncludedAmount=1200.00
    """
    if content is None:
        if order is None:
            raise ValueError("order 和 content 至少传一个")
        # ensure_ascii=False 保持中文原文参与签名（官方 SDK 即原文参与，UTF-8 编码）
        content = json.dumps(order, ensure_ascii=False)

    # 公共参数：senid 每次请求唯一（防重放）、nonce 随机正整数、timestamp 秒级时间戳
    if not senid:
        senid = uuid.uuid4().hex
    nonce = str(random.randint(10000, 999999999))
    timestamp = str(int(time.time()))

    # 公共参数拼接在 URL query 上（官方 SDK 行为），请求体就是 content 本身
    # 【保险】网关只认 hmac_sha1（官方 Maven SDK 算法），sha256 一定返回 070601，
    #         故无论调用方传什么，一律强制走 hmac_sha1。
    if sign_algo != "hmac_sha1":
        logger.warning(f"签名算法收到 {sign_algo!r}，诺诺网关仅支持 hmac_sha1，已强制修正")
    sign = _get_sign_hmac_sha1(url, senid, app_key, app_secret, content, nonce, timestamp)
    request_url = (
        f"{url}?senid={senid}&nonce={nonce}&timestamp={timestamp}&appkey={app_key}"
    )
    headers = {
        "Content-Type": "application/json",
        "X-Nuonuo-Sign": sign,
        "accessToken": token,
        "userTax": user_tax,
        "method": method,
        "sdkVer": "1.0.5.2",
    }

    logger.info(f"诺诺开票请求 URL: {request_url}")
    logger.info(f"诺诺开票请求体: {content}")
    resp = requests.post(request_url, headers=headers, data=content.encode("utf-8"), timeout=timeout)
    logger.info(f"诺诺开票响应 [{resp.status_code}]: {resp.text}")
    resp.raise_for_status()
    return resp.json()


def query_invoice_result(serial_no=None, order_no=None, is_offer_invoice_detail="1",
                         url=URL_OFFICIAL, app_key=DEFAULT_APP_KEY,
                         app_secret=DEFAULT_APP_SECRET, token=DEFAULT_TOKEN,
                         user_tax=DEFAULT_USER_TAX, timeout=30):
    """
    查询发票详情（nuonuo.OpeMplatform.queryInvoiceResult，接口文档 V2.0）。

    开票提交成功（E0000）后，发票需要经过 开票中(20) -> 成功签章中(21) -> 开票完成(2) 的异步流程，
    开票完成(status=2)后才会返回 pdfUrl / ofdUrl 等版式文件地址。

    :param serial_no: 发票流水号（开票成功响应里的 invoiceSerialNum），与 order_no 二选一，同时传以流水号为准
    :param order_no:  开票时的订单编号，与 serial_no 二选一
    :param is_offer_invoice_detail: 是否需要提供明细 1-是 0-否（默认 1）
    :param url:       接口地址，默认正式环境
    :param timeout:   请求超时秒数
    :return:          接口响应 dict。主要字段：status（2=开票完成）、pdfUrl、ofdUrl、
                      invoiceNo、allElectronicInvoiceNumber、orderAmount 等；
                      异常码：E9500 发票不存在 / E9611 流水号订单号全为空
    """
    if not serial_no and not order_no:
        raise ValueError("serial_no 和 order_no 至少传一个")
    body = {"isOfferInvoiceDetail": is_offer_invoice_detail}
    if serial_no:
        body["serialNos"] = [serial_no]
    if order_no:
        body["orderNos"] = [order_no]
    content = json.dumps(body, ensure_ascii=False)

    method = "nuonuo.OpeMplatform.queryInvoiceResult"
    senid = uuid.uuid4().hex
    nonce = str(random.randint(10000, 999999999))
    timestamp = str(int(time.time()))
    sign = _get_sign_hmac_sha1(url, senid, app_key, app_secret, content, nonce, timestamp)

    request_url = f"{url}?senid={senid}&nonce={nonce}&timestamp={timestamp}&appkey={app_key}"
    headers = {
        "Content-Type": "application/json",
        "X-Nuonuo-Sign": sign,
        "accessToken": token,
        "userTax": user_tax,
        "method": method,
        "sdkVer": "1.0.5.2",
    }
    logger.info(f"诺诺查询发票请求 URL: {request_url}")
    logger.info(f"诺诺查询发票请求体: {content}")
    resp = requests.post(request_url, headers=headers, data=content.encode("utf-8"), timeout=timeout)
    logger.info(f"诺诺查询发票响应 [{resp.status_code}]: {resp.text}")
    resp.raise_for_status()
    return resp.json()


# if __name__ == "__main__":
#     开票请求体示例（沙箱/测试数据，orderNo 每个企业唯一，不可重复）
#     test_order = {
#         "order": {
#             "buyerAccount": "455555 45",
#             "buyerAddress": "45665",
#             "buyerName": "北大方正物产集团有限公司",
#             "buyerTaxNum": "913212007965055488",
#             "buyerTel": "456",
#             "ccEmail": "1228575415@qq.com",
#             "clerk": "ceshizb",
#             "email": "zhangbao_it@galaxyderivatives.com",
#             "invoiceDate": "2026-09-18 09:40:28",
#             "invoiceDetail": [
#                 {
#                     "categoryId": 16,
#                     "goodsCode": "1080208",
#                     "goodsName": "金属硅",
#                     "num": "1.0000",
#                     "specName": "3303",
#                     "specType": "3303",
#                     # "tax": "139.0500",
#                     # "taxExcludedAmount": "1061.95000000",
#                     "taxIncludedAmount": "1200.0000",
#                     "taxRate": "0.1300",
#                     "unit": "吨",
#                     # "price": "1200.0000",
#                     "varietyId": 7,
#                     "withTaxFlag": "1",
#                 }
#             ],
#             "invoiceLine": "bs",
#             "invoiceType": "1",
#             "orderNo": "11112212212",
#             "pushMode": "0",
#             "remark": "",
#             "salerAddress": "上海市虹口区东长治路359号1601室",
#             "salerTaxNum": "339901999999199",
#         }
#     }
#     result = request_nuonuo_invoice(order=test_order)
#     print(json.dumps(result, ensure_ascii=False, indent=2))
