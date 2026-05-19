# -*- coding: utf-8 -*-

import os
import requests
import json
import random

from datetime import datetime, date, timedelta
from lunar_python import Solar


# ==========================================
# GitHub Secrets 环境变量
# ==========================================

# GitHub Actions:
# env:
#   WX_WEBHOOK: ${{ secrets.WX_YONGSHENG }}

WEBHOOK_URL = os.getenv("WX_WEBHOOK")

COMMUNITY_NAME = os.getenv(
    "COMMUNITY_NAME",
    "铂宸府物业服务中心"
)

CITY_CODE = os.getenv(
    "CITY_CODE",
    "101070101"
)


# ==========================================
# 自动农历
# ==========================================

def get_lunar():
    """获取明天农历"""

    tomorrow = date.today() + timedelta(days=1)

    solar = Solar.fromYmd(
        tomorrow.year,
        tomorrow.month,
        tomorrow.day
    )

    lunar = solar.getLunar()

    lunar_month = lunar.getMonthInChinese()

    lunar_day = lunar.getDayInChinese()

    return f"农历 {lunar_month}月{lunar_day}"


# ==========================================
# Day编号
# ==========================================

def get_day_number():

    start_date = date(2026, 1, 1)

    tomorrow = date.today() + timedelta(days=1)

    delta = tomorrow - start_date

    return delta.days + 1


# ==========================================
# 天气图标
# ==========================================

def get_weather_icon(weather_type):

    if "晴" in weather_type:
        return "☀️"

    elif "多云" in weather_type:
        return "⛅"

    elif "阴" in weather_type:
        return "☁️"

    elif "雨" in weather_type:
        return "🌧️"

    elif "雪" in weather_type:
        return "❄️"

    elif "雾" in weather_type or "霾" in weather_type:
        return "🌫️"

    else:
        return "🌤️"


# ==========================================
# 周一 / 周五 / 周末文案
# ==========================================

def get_morning_message():

    weekday = datetime.now().weekday()

    monday_msgs = [

        "☀️ 新的一周开启，愿您今日顺遂平安，开启元气满满的一天。",

        "🌿 周一早安，愿好心情伴随您开启崭新的一周。",

        "🍀 新的一周如约而至，愿生活明朗，万事顺意。",

        "🌞 周一的晨光已经抵达，愿您带着微笑开启新的征程。",

    ]

    friday_msgs = [

        "🍃 周五愉快，愿您带着轻松心情迎接周末。",

        "🌇 忙碌一周辛苦了，愿今晚有温暖与放松。",

        "✨ 周末将近，愿您今日工作顺利，生活舒心。",

        "☕ 愿这个周五，为您带来一天的好心情。",

    ]

    weekend_msgs = [

        "🌸 周末愉快，愿您与家人共享惬意时光。",

        "☀️ 愿这个周末，有阳光、有陪伴、有好心情。",

        "🍵 周末时光开启，愿生活温柔而美好。",

        "🌿 愿您在周末收获轻松与愉悦，享受生活的小美好。",

    ]

    normal_msgs = [

        "🌞 每一个清晨都是新的开始，愿您今天收获满满幸福。",

        "🍀 愿您眼里有光，心中有爱，今天也是美好的一天。",

        "🌅 晨曦微露，万物复苏，愿您的生活如诗般美好。",

        "💐 把昨日烦恼留给昨天，用微笑迎接今天的阳光。",

        "✨ 心存美好，万物皆美，愿您今天遇见所有温暖。",

        "🍃 清风拂面，阳光正好，愿今日心情如晨光般明媚。",

    ]

    if weekday == 0:
        return random.choice(monday_msgs)

    elif weekday == 4:
        return random.choice(friday_msgs)

    elif weekday in [5, 6]:
        return random.choice(weekend_msgs)

    else:
        return random.choice(normal_msgs)


# ==========================================
# 获取天气
# ==========================================

def get_weather():

    url = f'http://t.weather.itboy.net/api/weather/city/{CITY_CODE}'

    try:

        response = requests.get(url, timeout=10)

        d = response.json()

        if d['status'] == 200:

            tomorrow_weather = d['data']['forecast'][1]

            weather_type = tomorrow_weather['type']

            high_temp = tomorrow_weather['high'].replace(
                '高温 ',
                ''
            ).replace('℃', '')

            low_temp = tomorrow_weather['low'].replace(
                '低温 ',
                ''
            ).replace('℃', '')

            tomorrow = datetime.now() + timedelta(days=1)

            weekdays = [

                "星期一",
                "星期二",
                "星期三",
                "星期四",
                "星期五",
                "星期六",
                "星期日"

            ]

            weekday = weekdays[tomorrow.weekday()]

            date_str = tomorrow.strftime("%Y年%m月%d日")

            lunar_str = get_lunar()

            day_num = get_day_number()

            weather_icon = get_weather_icon(weather_type)

            morning_msg = get_morning_message()

            message = (

                f"【永升早安语录·Day{day_num}】\n"
                f"今天是{date_str} {weekday}\n"
                f"{lunar_str}\n"
                f"天气 {weather_type}{weather_icon}\n"
                f"气温 {low_temp}℃ ~ {high_temp}℃\n\n"
                f"{morning_msg}\n\n"
                f"🌈 {COMMUNITY_NAME} 祝各位业主朋友生活愉快，出行顺利。"

            )

            return message, True

        else:

            return f"天气接口错误: {d['status']}", False

    except Exception as e:

        return f"获取天气失败: {e}", False


# ==========================================
# 企业微信发送
# ==========================================

def send_to_wechat(content):

    print("===== 开始检测Webhook =====")

    print("WEBHOOK_URL:", WEBHOOK_URL)

    if not WEBHOOK_URL:

        print("❌ 未检测到 WX_WEBHOOK 环境变量")

        return False

    headers = {

        'Content-Type': 'application/json'

    }

    data = {

        "msgtype": "text",

        "text": {

            "content": content,

            "mentioned_list": [],

            "mentioned_mobile_list": []

        }

    }

    try:

        response = requests.post(
            WEBHOOK_URL,
            headers=headers,
            data=json.dumps(data),
            timeout=10
        )

        print("HTTP状态码:", response.status_code)

        result = response.json()

        print("企业微信返回:", result)

        if result.get('errcode') == 0:

            print("✅ 企业微信发送成功")

            return True

        else:

            print(f"❌ 企业微信发送失败: {result}")

            return False

    except Exception as e:

        print(f"❌ 发送异常: {e}")

        return False


# ==========================================
# 主程序
# ==========================================

def main():

    print("🚀 开始执行永升天气推送...")

    message, success = get_weather()

    print("===== 天气内容 =====")

    print(message)

    if success:

        send_to_wechat(message)

    else:

        send_to_wechat(
            f"【天气获取失败】\n{message}"
        )

    print("✅ 执行结束")


# ==========================================
# 本地运行
# ==========================================

if __name__ == '__main__':

    main()
