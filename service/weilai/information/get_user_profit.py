import asyncio
import aiohttp
from decimal import Decimal, InvalidOperation
from utils.logger import get_logger
from utils.request import generate_random_ipv4, DATA_BODY, DATA_BODY1, DATA_BODY2, DATA_BODY3
from utils import request as request_util

loggers = get_logger()
profit_logger = loggers['profit']


def build_headers(token: str) -> dict:
    ip = generate_random_ipv4()
    headers = request_util.headers.copy()
    headers.update({
        "Authorization": token,
        "X-Token": token,
        "X-Forwarded-For": ip,
        "CLIENT_IP": ip,
        "REMOTE_ADDR": ip,
        "Via": ip
    })
    return headers


async def post_with_retry(session, url: str, json_data, headers: dict, phone: str, max_retries=3):
    for attempt in range(1, max_retries + 1):
        try:
            async with session.post(url, json=json_data, headers=headers, timeout=5) as resp:
                resp_json = await resp.json()
                if resp_json.get('code') == '200':
                    return 100, resp_json.get("data", {})
                else:
                    profit_logger.warning(f"[{phone}] 响应失败（第 {attempt} 次）: {resp_json}")
                    return -1, None
        except Exception as e:
            profit_logger.error(f"[{phone}] 请求异常（第 {attempt} 次）: {e}")
            if attempt == max_retries:
                return -2, None
    return -2, None


async def get_user_profit(phone: str, token: str):
    headers = build_headers(token)
    url = "https://api-sc.weilaiqiyuan.com/core/collection/page_person_front"

    async with aiohttp.ClientSession() as session:
        status, data = await post_with_retry(session, url, DATA_BODY, headers, phone)
        if status != 100:
            return status, None

        tasks = []
        for item in data.get("list", []):
            collection_id = item.get("id")
            tasks.append(get_user_profit1(session, phone, token, collection_id))

        results = await asyncio.gather(*tasks)

        total_profit = Decimal("0")
        total_price = Decimal("0")
        total_no_fee_price=Decimal("0")

        for result in results:
            s, p, c,d = result
            if s == 100:
                total_profit += p
                total_price += c
                total_no_fee_price+=d

        msg = (
            f"[{phone}] 今日收益: {total_profit} 元（已去掉手续费）\n"
            f"未去掉提现手续费的收益: {total_no_fee_price} 元\n"
            f"今日持仓: {total_price} 元"
        )

        profit_logger.info(msg)
        return 100, msg


async def get_user_profit1(session, phone: str, token: str, collection_id: str):
    headers = build_headers(token)
    url = "https://api-sc.weilaiqiyuan.com/core/collection_detail/page_front"
    data_body = DATA_BODY1.copy()
    data_body.update({"collectionId": collection_id})

    status, data = await post_with_retry(session, url, data_body, headers, phone)
    if status != 100:
        return status, Decimal("0"), Decimal("0"), Decimal("0")

    tasks = []
    for item in data.get("list", []):
        item_id = item.get("id")
        tasks.append(get_user_profit2(session, phone, token, item_id))

    results = await asyncio.gather(*tasks)

    profit_sum = Decimal("0")
    price_sum = Decimal("0")
    no_fee_profit_sum = Decimal("0")

    for result in results:
        s, p, cp,cpc = result
        if s == 100:
            profit_sum += p
            price_sum += cp
            no_fee_profit_sum+= cpc

    return 100, profit_sum, price_sum,no_fee_profit_sum


async def get_user_profit2(session, phone: str, token: str, id2: str):
    headers = build_headers(token)
    url = f"https://api-sc.weilaiqiyuan.com/core/collection_detail/public/detail_front/{id2}"
    data_body = DATA_BODY2.copy()
    data_body.update({"id": id2})

    status, data = await post_with_retry(session, url, data_body, headers, phone)
    if status != 100:
        return status, Decimal("0"), Decimal("0")

    try:
        trade_price = Decimal(str(data.get("tradePrice", "0")))
        current_price = Decimal(str(data.get("currentPrice", "0")))
    except (InvalidOperation, TypeError, ValueError):
        trade_price = Decimal("0")
        current_price = Decimal("0")

    item_id = data.get("id")
    status, fee = await get_user_profit3(session, phone, token, item_id, current_price)
    if status != 100:
        return status, Decimal("0"), Decimal("0")

    profit = current_price - trade_price - fee
    no_fee_profit=current_price - trade_price
    return 100, profit, current_price,no_fee_profit


async def get_user_profit3(session, phone: str, token: str, id3: str, price: Decimal):
    headers = build_headers(token)
    url = "https://api-sc.weilaiqiyuan.com/core/buyout_products/pay/getTradeFee/batch"
    data_body = [dict(item) for item in DATA_BODY3]
    data_body[0].update({
        "collectionDetailId": id3,
        "price": float(price)
    })

    status, data = await post_with_retry(session, url, data_body, headers, phone)
    if status != 100:
        return status, Decimal("0")

    try:
        fee = Decimal(str(data.get("fee", "0")))
        return 100, fee
    except (InvalidOperation, TypeError, ValueError):
        return -1, Decimal("0")
