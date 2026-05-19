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

WEBHOOK_URL = os.getenv("WX_YONGSHENG")

COMMUNITY_NAME = os.getenv(
    "COMMUNITY_NAME",
    "铂宸府物业服务中心"
)

CITY_CODE = os.getenv(
    "CITY_CODE",
    "101070101"
)


# ==========================================
# 获取农历 + 节气
# ==========================================

def get_lunar_info():

    tomorrow = date.today() + timedelta(days=1)

    solar = Solar.fromYmd(
        tomorrow.year,
        tomorrow.month,
        tomorrow.day
    )

    lunar = solar.getLunar()

    lunar_text = (
        f"农历 {lunar.getMonthInChinese()}月"
        f"{lunar.getDayInChinese()}"
    )

    jieqi = lunar.getJieQi()

    return lunar_text, jieqi, lunar


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

    elif "雷" in weather_type:
        return "⛈️"

    elif "暴雨" in weather_type:
        return "🌧️"

    elif "雨" in weather_type:
        return "🌦️"

    elif "雪" in weather_type:
        return "❄️"

    elif "雾" in weather_type or "霾" in weather_type:
        return "🌫️"

    else:
        return "🌤️"


# ==========================================
# 中国节日专属文案
# ==========================================

def get_festival_message(lunar):

    solar_today = (
        datetime.now() + timedelta(days=1)
    ).strftime("%m-%d")

    lunar_month = lunar.getMonth()

    lunar_day = lunar.getDay()

    # ======================
    # 阳历节日
    # ======================

    solar_festivals = {

        "01-01": "🎉 元旦快乐，愿新的一年平安顺遂。",

        "05-01": "🛠️ 劳动节快乐，致敬每一位奋斗者。",

        "10-01": "🇨🇳 国庆节快乐，祝祖国繁荣昌盛。",

    }

    # ======================
    # 农历传统节日
    # ======================

    lunar_festivals = {

        (1, 1): "🧨 春节快乐，愿阖家幸福，万事如意。",

        (1, 15): "🏮 元宵节快乐，愿团圆常伴左右。",

        (5, 5): "🚣 端午安康，愿平安顺遂，幸福绵长。",

        (7, 7): "🌌 七夕快乐，愿世间美好如约而至。",

        (8, 15): "🌕 中秋快乐，愿人月两圆，阖家安康。",

        (9, 9): "🍂 重阳安康，愿长辈健康长寿。",

        (12, 8): "🥣 腊八节快乐，愿生活温暖有味。",

        (12, 23): "🏮 小年快乐，愿喜乐常伴人间。",

    }

    lunar_key = (lunar_month, lunar_day)

    if lunar_key in lunar_festivals:

        return lunar_festivals[lunar_key]

    if solar_today in solar_festivals:

        return solar_festivals[solar_today]

    return ""


# ==========================================
# 节气文案
# ==========================================

def get_jieqi_message(jieqi):

    jieqi_dict = {

        "立春": "🌱 立春已至，万物复苏。",

        "雨水": "🌧️ 雨水时节，润物无声。",

        "惊蛰": "🌿 惊蛰始鸣，万物生长。",

        "春分": "☀️ 春分时节，昼夜均分。",

        "清明": "🍃 清明风起，春和景明。",

        "谷雨": "🌾 谷雨春光晓，山川黛色青。",

        "立夏": "🌿 夏意初长，万物繁茂。",

        "小满": "🌾 小满未满，恰到好处。",

        "芒种": "🌱 芒种忙种，希望可期。",

        "夏至": "☀️ 夏至已至，盛夏开启。",

        "立秋": "🍂 秋意渐起，暑气未消。",

        "白露": "💧 白露凝珠，秋意渐浓。",

        "秋分": "🍁 秋分时节，天高气爽。",

        "寒露": "🌾 寒露已至，添衣保暖。",

        "霜降": "🍂 霜降时节，秋意更深。",

        "立冬": "❄️ 立冬已至，万物收藏。",

        "小雪": "🌨️ 小雪轻落，冬意渐浓。",

        "大雪": "❄️ 大雪纷飞，注意保暖。",

        "冬至": "🥟 冬至安康，愿人间团圆。",

    }

    if jieqi:

        return jieqi_dict.get(
            jieqi,
            f"🌿 今日节气：{jieqi}"
        )

    return ""


# ==========================================
# 空气质量提醒
# ==========================================

def get_air_quality_notice(aqi):

    try:

        aqi = int(aqi)

        if aqi <= 50:

            return "🌿 空气质量优，适宜户外活动。"

        elif aqi <= 100:

            return "🍃 空气质量良好，可正常外出。"

        elif aqi <= 150:

            return "🌫️ 空气轻度污染，敏感人群请注意防护。"

        elif aqi <= 200:

            return "⚠️ 空气中度污染，建议减少长时间户外活动。"

        else:

            return "🚨 空气污染较重，请注意健康防护。"

    except:

        return ""


# ==========================================
# 极端天气预警
# ==========================================

def get_weather_warning(weather_type, high_temp):

    warnings = []

    try:

        high = int(high_temp)

    except:

        high = 25

    if high >= 35:

        warnings.append(
            "🔥 高温天气，请注意防暑降温。"
        )

    if "暴雨" in weather_type:

        warnings.append(
            "⛈️ 暴雨天气，请注意出行安全。"
        )

    elif "大雨" in weather_type:

        warnings.append(
            "🌧️ 降雨明显，请携带雨具。"
        )

    if "雷" in weather_type:

        warnings.append(
            "⚡ 雷电天气，请减少户外停留。"
        )

    if "雪" in weather_type:

        warnings.append(
            "❄️ 降雪天气，道路湿滑请慢行。"
        )

    if "大风" in weather_type:

        warnings.append(
            "💨 风力较大，请注意高空坠物。"
        )

    return "\n".join(warnings)


# ==========================================
# 每日随机语录
# ==========================================

def get_daily_message():

    weekday = datetime.now().weekday()

    monday_msgs = [

        "☀️ 新的一周开启，愿您今日顺遂平安。",

        "🌿 周一早安，愿好心情伴随您开启新的一周。",

    ]

    friday_msgs = [

        "🍃 周五愉快，愿您带着轻松心情迎接周末。",

        "🌇 忙碌一周辛苦了，愿今晚有温暖与放松。",

    ]

    weekend_msgs = [

        "🌸 周末愉快，愿您与家人共享惬意时光。",

        "☀️ 愿这个周末，有阳光、有陪伴、有好心情。",

    ]

    normal_msgs = [

        "🌞 每一个清晨都是新的开始，愿您今日幸福满满。",

        "🍀 愿您眼里有光，心中有爱，今日皆美好。",

        "🌅 晨曦微露，愿生活如诗般温暖。",

        "💐 把昨日烦恼留给昨天，用笑容迎接今天。",

        "✨ 心存美好，万物皆美。",

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

    url = f"http://t.weather.itboy.net/api/weather/city/{CITY_CODE}"

    try:

        response = requests.get(url, timeout=10)

        d = response.json()

        if d['status'] == 200:

            tomorrow_weather = d['data']['forecast'][1]

            weather_type = tomorrow_weather['type']

            high_temp = (
                tomorrow_weather['high']
                .replace('高温 ', '')
                .replace('℃', '')
            )

            low_temp = (
                tomorrow_weather['low']
                .replace('低温 ', '')
                .replace('℃', '')
            )

            weather_icon = get_weather_icon(weather_type)

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

            lunar_text, jieqi, lunar = get_lunar_info()

            jieqi_msg = get_jieqi_message(jieqi)

            festival_msg = get_festival_message(lunar)

            daily_msg = get_daily_message()

            day_num = get_day_number()

            aqi = d['data'].get('pm25', 0)

            air_notice = get_air_quality_notice(aqi)

            warning_msg = get_weather_warning(
                weather_type,
                high_temp
            )

            message = (

                f"【永升早安语录·Day{day_num}】\n\n"

                f"📅 {date_str} {weekday}\n"

                f"🌙 {lunar_text}\n\n"

                f"{festival_msg}\n"

                f"{jieqi_msg}\n\n"

                f"{weather_icon} 天气：{weather_type}\n"

                f"🌡️ 气温：{low_temp}℃ ~ {high_temp}℃\n"

                f"🌿 PM2.5：{aqi}\n\n"

                f"{air_notice}\n\n"

                f"{warning_msg}\n\n"

                f"{daily_msg}\n\n"

                f"🏡 {COMMUNITY_NAME}\n"
                f"祝各位业主朋友生活愉快，出行顺利。"

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

    if not WEBHOOK_URL:

        print("❌ 未检测到 WX_YONGSHENG 环境变量")

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

        result = response.json()

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

    if success:

        send_to_wechat(message)

    else:

        send_to_wechat(
            f"【天气获取失败】\n{message}"
        )

    print("✅ 执行结束")


# ==========================================
# 启动
# ==========================================

if __name__ == '__main__':

    main()
