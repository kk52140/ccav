#!/usr/bin/python3
# coding=utf-8

import os
import requests
import json
import sys
import re


# ==============================
# 环境变量配置
# ==============================

WX_WEBHOOK = os.getenv("WX_WEBHOOK")

COMMUNITY_NAME = os.getenv(
    "COMMUNITY_NAME",
    "铂宸府物业服务中心"
)

BUILDING_NAME = os.getenv(
    "BUILDING_NAME",
    "H1号楼"
)

STAFF_NAME = os.getenv(
    "STAFF_NAME",
    "考拉"
)

CITY_CODE = os.getenv(
    "CITY_CODE",
    "101070101"
)


# ==============================
# 温度提取
# ==============================

def extract_temp(temp_text, default=20):

    try:

        match = re.search(
            r'-?\d+',
            str(temp_text)
        )

        return (
            int(match.group())
            if match
            else default
        )

    except Exception:

        return default


# ==============================
# PM2.5格式化
# ==============================

def format_pm25(pm25_value):

    try:

        return str(
            int(float(pm25_value))
        )

    except Exception:

        return str(pm25_value)


# ==============================
# 企业微信发送
# ==============================

def send_to_wechat(content):

    if not WX_WEBHOOK:

        raise RuntimeError(
            "未配置 WX_WEBHOOK 环境变量"
        )

    headers = {
        'Content-Type': 'application/json'
    }

    data = {
        "msgtype": "text",
        "text": {
            "content": content
        }
    }

    try:

        response = requests.post(
            WX_WEBHOOK,
            headers=headers,
            data=json.dumps(
                data,
                ensure_ascii=False
            ),
            timeout=10
        )

        result = response.json()

        if result.get('errcode') == 0:

            print("✅ 消息发送成功")

        else:

            print(
                f"❌ 消息发送失败: {result}"
            )

    except Exception as e:

        print(f"❌ 发送异常: {e}")


# ==============================
# 天气等级判断
# ==============================

def get_weather_level(
    weather_type,
    high_temp,
    low_temp,
    wind_level_text
):

    wind_level_num = 0

    try:

        match = re.search(
            r'(\d+)',
            str(wind_level_text)
        )

        if match:

            wind_level_num = int(
                match.group(1)
            )

    except Exception:

        wind_level_num = 0

    severe_keywords = [
        "暴雨",
        "大暴雨",
        "暴雪",
        "大雪",
        "中雪",
        "冰雹",
        "沙尘暴",
        "雷暴",
        "强对流"
    ]

    if any(
        k in weather_type
        for k in severe_keywords
    ):

        return "severe"

    if wind_level_num >= 6:

        return "severe"

    rain_keywords = [
        "小雨",
        "中雨",
        "大雨",
        "阵雨",
        "雷阵雨",
        "雨夹雪"
    ]

    if any(
        k in weather_type
        for k in rain_keywords
    ):

        return "rain"

    return "normal"


# ==============================
# 出行提醒
# ==============================

def get_weather_warning(
    weather_type,
    high_temp,
    low_temp,
    weather_level
):

    high = extract_temp(high_temp, 20)

    low = extract_temp(low_temp, 10)

    if weather_level == "severe":

        if "雪" in weather_type:

            return (
                "降雪天气道路湿滑，请注意减速慢行。"
            )

        elif "风" in weather_type:

            return (
                "风力较大，请注意高空坠物。"
            )

        elif "雨" in weather_type:

            return (
                "强降雨天气，请提前规划出行。"
            )

        else:

            return (
                "天气变化明显，请注意出行安全。"
            )

    if weather_level == "rain":

        return (
            "降雨天气道路湿滑，请注意出行安全。"
        )

    if high - low >= 8:

        return (
            "昼夜温差较大，请注意及时增减衣物。"
        )

    return (
        "天气较平稳，适宜日常出行。"
    )


# ==============================
# 着装建议
# ==============================

def get_dress_advice(
    high_temp,
    is_today=False
):

    high = extract_temp(high_temp, 20)

    if high >= 30:

        return (
            "建议穿着轻薄透气衣物，外出注意防晒。"
        )

    elif high >= 25:

        return (
            "建议着轻便服装，早晚可搭配薄外套。"
        )

    elif high >= 15:

        return (
            "建议穿着长袖或薄外套，注意早晚温差。"
        )

    else:

        return (
            "建议做好保暖措施，外出注意添衣。"
        )


# ==============================
# 天气提示
# ==============================

def build_weather_notice(
    weather_type,
    high_temp,
    low_temp,
    weather_level
):

    high = extract_temp(high_temp, 20)

    low = extract_temp(low_temp, 10)

    if weather_level == "severe":

        if "雨" in weather_type:

            return (
                "今日降雨较明显，请提前做好出行安排。"
            )

        elif "雪" in weather_type:

            return (
                "今日有降雪天气，请注意防寒保暖。"
            )

        else:

            return (
                "今日天气变化明显，请注意安全防护。"
            )

    elif weather_level == "rain":

        return (
            "今日有降雨天气，建议随身携带雨具。"
        )

    else:

        if "晴" in weather_type:

            return (
                "天气晴好，适宜出行。"
            )

        elif "阴" in weather_type:

            return (
                "天气以阴天为主，请注意及时增减衣物。"
            )

        elif high - low >= 8:

            return (
                "昼夜温差较明显，请注意及时增减衣物。"
            )

        else:

            return (
                "天气较平稳，适宜日常出行。"
            )


# ==============================
# 获取天气
# ==============================

def get_weather(weather_type='tomorrow'):

    api = (
        'http://t.weather.itboy.net/api/weather/city/'
    )

    tqurl = api + CITY_CODE

    try:

        response = requests.get(
            tqurl,
            timeout=10
        )

        d = response.json()

        if d['status'] != 200:

            return (
                f"天气接口返回错误: {d['status']}",
                False
            )

        if weather_type == 'today':

            index = 0

            title_prefix = "今日"

        else:

            index = 1

            title_prefix = "明日"

        weather_data = (
            d['data']['forecast'][index]
        )

        weather_type_str = weather_data['type']

        high_temp_raw = weather_data['high']

        low_temp_raw = weather_data['low']

        wind_text = weather_data['fl']

        high_temp = extract_temp(
            high_temp_raw,
            20
        )

        low_temp = extract_temp(
            low_temp_raw,
            10
        )

        pm25 = format_pm25(
            d['data'].get('pm25', '未知')
        )

        weather_level = get_weather_level(
            weather_type_str,
            high_temp,
            low_temp,
            wind_text
        )

        weather_notice = build_weather_notice(
            weather_type_str,
            high_temp,
            low_temp,
            weather_level
        )

        dress_advice = get_dress_advice(
            high_temp,
            is_today=(
                weather_type == 'today'
            )
        )

        travel_warning = get_weather_warning(
            weather_type_str,
            high_temp,
            low_temp,
            weather_level
        )

        if weather_level == "severe":

            title = "【天气安全提醒】"

        else:

            title = (
                f"【{title_prefix}天气提醒】"
            )

        weather_info = (

            f"{title}\n\n"

            f"尊敬的{BUILDING_NAME}业主您好，"
            f"以下为{title_prefix}天气提醒：\n\n"

            f"📅 {weather_data['ymd']} "
            f"{weather_data['week']}\n"

            f"☁️ 天气：{weather_type_str}\n"

            f"🌡️ 气温："
            f"{low_temp}℃ ~ {high_temp}℃\n"

            f"🌿 PM2.5：{pm25}\n"

            f"💨 风力："
            f"{weather_data['fx']} "
            f"{weather_data['fl']}\n\n"

            f"📢 {weather_notice}\n"

            f"👔 {dress_advice}\n"

            f"🚶 {travel_warning}\n\n"

            f"🏡 {BUILDING_NAME}管家{STAFF_NAME}\n"
            f"祝您生活愉快，出行顺利。"

        )

        return weather_info, True

    except Exception as e:

        return (
            f"获取天气失败: {e}",
            False
        )


# ==============================
# 主函数
# ==============================

def main():

    weather_type = 'tomorrow'

    if len(sys.argv) > 1:

        weather_type = sys.argv[1]

    type_desc = (
        "今日"
        if weather_type == 'today'
        else "明日"
    )

    print(
        f"🚀 开始执行{type_desc}天气推送..."
    )

    weather_msg, success = get_weather(
        weather_type
    )

    if success:

        print("📤 正在发送天气信息...")

        send_to_wechat(weather_msg)

    else:

        error_msg = (
            f"【天气推送失败】\n"
            f"{weather_msg}"
        )

        send_to_wechat(error_msg)

    print("✅ 执行完成")


if __name__ == '__main__':

    main()
