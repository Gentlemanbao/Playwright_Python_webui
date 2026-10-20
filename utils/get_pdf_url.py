import sys, time
sys.path.insert(0, r'D:\期现项目资料\ui_auto_project')
from utils.nuonuo_invoice import request_nuonuo_invoice, query_invoice_result

test_order = {
        "order": {
            "buyerAccount": "455555 45",
            "buyerAddress": "45665",
            "buyerName": "北大方正物产集团有限公司",
            "buyerTaxNum": "913212007965055488",
            "buyerTel": "456",
            "ccEmail": "1228575415@qq.com",
            "clerk": "ceshizb",
            "email": "zhangbao_it@galaxyderivatives.com",
            "invoiceDate": "2026-09-18 09:40:28",
            "invoiceDetail": [
                {
                    "categoryId": 16,
                    "goodsCode": "1080208",
                    "goodsName": "金属硅",
                    "num": "869.4825",
                    "specName": "3303",
                    "specType": "3303",
                    "tax": "2425702.27",
                    "taxExcludedAmount": "18659248.43",
                    "taxIncludedAmount": "21084950.70",
                    "taxRate": "0.1300",
                    "unit": "吨",
                    # "price": "1200.0000",
                    "varietyId": 7,
                    "withTaxFlag": "1",
                }
            ],
            "invoiceLine": "bs",
            "invoiceType": "1",
            "orderNo": "1111221222412",
            "pushMode": "0",
            "remark": "",
            "salerAddress": "上海市虹口区东长治路359号1601室",
            "salerTaxNum": "339901999999199",
        }
    }
# 1. 开票（凭据全有默认值，orderNo 记得每次换新）
r = request_nuonuo_invoice(order=test_order)
serial_no = r["result"]["invoiceSerialNum"]

# 2. 轮询查询拿 pdfUrl（status=2 开票完成才返回）
while True:
    q = query_invoice_result(serial_no=serial_no)
    info = q["result"][0]
    if info["status"] == "2":
        print(info["pdfUrl"])   # 发票 PDF 地址
        break
    time.sleep(3)
