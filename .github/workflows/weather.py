#!/usr/bin/python3
# coding=utf-8

import os
import requests
import json
import random
import sys
from datetime import datetime


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
# 企业微信发送
# ==============================

def send_to_wechat(content):

    if not WX_WEBHOOK:
        raise RuntimeError("未配置 WX_WEBHOOK 环境变量")

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
            data=json.dumps(data),
            timeout=10
        )

        result = response.json()

        if result.get('errcode') == 0:
            print("✅ 消息发送成功")
        else:
            print(f"❌ 消息发送失败: {result}")

    except Exception as e:

        print(f"❌ 发送异常: {e}")


# ==============================
# 出行提醒
# ==============================

def get_weather_warning(weather_type, high_temp, low_temp):

    try:
        high = int(''.join(filter(str.isdigit, high_temp)))
    except:
        high = 20

    reminders = []

    if high >= 35:
        reminders.append("🔥 天气炎热，请注意防暑降温，尽量减少午后长时间户外停留。")
    elif high >= 30:
        reminders.append("🥤 气温较高，外出请注意防晒，并及时补充水分。")
    elif high <= 0:
        reminders.append("🧣 气温较低，外出请注意添衣保暖。")
    elif high <= 10:
        reminders.append("🧥 早晚温差较明显，建议适当增添外套。")

    if "暴雨" in weather_type:
        reminders.append("⛈️ 暴雨天气，请提前规划出行，注意避开低洼积水路段。")
    elif "大雨" in weather_type:
        reminders.append("🌧️ 降雨较明显，出门请携带雨具，注意道路湿滑。")
    elif "中雨" in weather_type:
        reminders.append("☔ 有降雨天气，建议随身携带雨具，出行注意安全。")
    elif "小雨" in weather_type or "雨" in weather_type:
        reminders.append("☂️ 出门建议备好雨具，注意脚下安全。")
    elif "暴雪" in weather_type or "大雪" in weather_type:
        reminders.append("❄️ 降雪天气，路面湿滑，请注意慢行，谨慎出行。")
    elif "中雪" in weather_type or "小雪" in weather_type or "雪" in weather_type:
        reminders.append("🌨️ 有降雪天气，请注意防寒保暖及出行安全。")
    elif "大风" in weather_type or "狂风" in weather_type:
        reminders.append("💨 风力较大，请留意门窗关闭，并妥善安置阳台物品。")
    elif "雾" in weather_type:
        reminders.append("🌫️ 能见度较低，驾车出行请减速慢行，注意安全。")
    elif "霾" in weather_type:
        reminders.append("😷 空气质量一般，敏感人群外出请做好防护。")

    return "\n".join(reminders)


# ==============================
# 着装建议
# ==============================

def get_dress_advice(weather_type, high_temp, low_temp, is_today=False):

    try:
        high = int(''.join(filter(str.isdigit, high_temp)))
    except:
        high = 20

    time_desc = "今日" if is_today else "明日"

    advice = f"👔 【{time_desc}着装建议】\n"

    if high >= 30:
        advice += f"{time_desc}气温偏高，建议选择轻薄透气衣物，外出注意防晒。"
    elif high >= 25:
        advice += f"{time_desc}体感较为舒适，建议着轻便服装，早晚可酌情搭配薄外套。"
    elif high >= 20:
        advice += f"{time_desc}气温适宜，建议着长袖上衣或薄外套，出行较为舒适。"
    elif high >= 15:
        advice += f"{time_desc}天气偏凉，建议着针织衫、卫衣或外套，注意早晚保暖。"
    elif high >= 5:
        advice += f"{time_desc}气温较低，建议着保暖外套，适当做好防寒准备。"
    else:
        advice += f"{time_desc}天气寒冷，建议着羽绒服、大衣等保暖衣物，注意防寒保暖。"

    warning = get_weather_warning(
        weather_type,
        high_temp,
        low_temp
    )

    if warning:
        advice += "\n📌 出行提醒：\n" + warning

    return advice


# ==============================
# H1号楼专属物业结尾
# ==============================

def get_property_message():

    weekday = datetime.now().weekday()

    normal_messages = [

        f"🏡 {BUILDING_NAME}专属提醒｜我是管家{STAFF_NAME}，{COMMUNITY_NAME}祝您生活愉快，出行顺利。",

        f"🏡 {BUILDING_NAME}业主朋友您好，我是管家{STAFF_NAME}，愿您与家人平安顺遂，天天好心情。",

        f"🏡 {BUILDING_NAME}管家{STAFF_NAME}温馨提醒：愿您出行平安，归家有暖。",

        f"🏡 来自{COMMUNITY_NAME} · {BUILDING_NAME}管家{STAFF_NAME}的天气提醒，祝您生活舒心、万事顺意。",

        f"🏡 {BUILDING_NAME}业主专属服务｜管家{STAFF_NAME}愿您今日好心情，生活更从容。",

        f"🏡 {BUILDING_NAME}管家{STAFF_NAME}提醒您：天气变化请留意，愿您与家人平安健康。",

        f"🏡 {COMMUNITY_NAME} · {BUILDING_NAME}管家{STAFF_NAME} 感谢您的理解与支持，祝您生活愉快。",

        f"🏡 {BUILDING_NAME}专属天气提醒由管家{STAFF_NAME}为您送达，愿您出行顺利、居家安心。"
    ]

    friday_messages = [

        f"🌇 周末将至，{BUILDING_NAME}管家{STAFF_NAME}愿您卸下一周疲惫，迎接轻松时光。",

        f"🏡 {BUILDING_NAME}管家{STAFF_NAME}提前祝您周末愉快，愿归家皆有温暖。",

        f"✨ 周末即将开启，{COMMUNITY_NAME} · {BUILDING_NAME}管家{STAFF_NAME}祝您生活惬意、心情舒畅。"
    ]

    monday_messages = [

        f"☀️ 新的一周开始啦，{BUILDING_NAME}管家{STAFF_NAME}愿您工作顺利、万事顺心。",

        f"💼 周一早安，{COMMUNITY_NAME} · {BUILDING_NAME}管家{STAFF_NAME}愿您开启元气满满的一周。",

        f"🌿 新周启程，{BUILDING_NAME}管家{STAFF_NAME}祝您生活舒心、出行平安。"
    ]

    if weekday == 4:
        return random.choice(friday_messages)
    elif weekday == 0:
        return random.choice(monday_messages)
    else:
        return random.choice(normal_messages)


# ==============================
# 获取天气
# ==============================

def get_weather(weather_type='tomorrow'):

    api = 'http://t.weather.itboy.net/api/weather/city/'
    tqurl = api + CITY_CODE

    try:

        response = requests.get(
            tqurl,
            timeout=10
        )

        d = response.json()

        if d['status'] == 200:

            if weather_type == 'today':
                index = 0
                title = "【今日天气提醒】"
                time_desc = "今日"
            else:
                index = 1
                title = "【明日天气提醒】"
                time_desc = "明日"

            weather_data = d['data']['forecast'][index]

            weather_type_str = weather_data['type']
            high_temp = weather_data['high']
            low_temp = weather_data['low']

            dress_advice = get_dress_advice(
                weather_type_str,
                high_temp,
                low_temp,
                is_today=(weather_type == 'today')
            )

            property_message = get_property_message()

            message_parts = [

                title,

                f"尊敬的{BUILDING_NAME}业主您好，以下为{time_desc}天气提醒：",

                f"🏙️ 所在城市：{d['cityInfo']['parent']} {d['cityInfo']['city']}",

                f"📅 日期：{weather_data['ymd']} {weather_data['week']}",

                f"☁️ 天气情况：{weather_type_str}",

                f"🌡️ 气温范围：{low_temp} ~ {high_temp}",

                f"💧 空气湿度：{d['data']['shidu']}",

                f"🌿 空气质量：{d['data']['quality']}（PM2.5：{d['data']['pm25']}）",

                f"💨 风向风力：{weather_data['fx']} {weather_data['fl']}",

                f"🩺 健康提示：{d['data']['ganmao']}",

                f"📢 天气提示：{weather_data['notice']}",

                "",

                dress_advice,

                "",

                property_message
            ]

            weather_info = "\n".join(message_parts)

            return weather_info, True

        else:
            return (
                f"天气接口返回错误: {d['status']}",
                False
            )

    except Exception as e:
        return (
            f"获取天气失败: {e}",
            False
        )


# ==============================
# 主程序
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

    print(f"🚀 开始执行{type_desc}天气推送...")

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
