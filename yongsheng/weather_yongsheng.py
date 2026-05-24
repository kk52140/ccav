# -*- coding: utf-8 -*-

import os
import requests
import json
import random

from datetime import datetime, date, timedelta
from lunar_python import Solar


WEBHOOK_URL = os.getenv("WX_YONGSHENG")

CITY_CODE = os.getenv(
    "CITY_CODE",
    "101070101"
)

COMMUNITY_NAME = os.getenv(
    "COMMUNITY_NAME",
    "铂宸府物业服务中心"
)


# ==========================================
# 明日日期
# ==========================================

def get_target_date():
    return date.today() + timedelta(days=1)


def get_target_datetime():
    return datetime.now() + timedelta(days=1)


# ==========================================
# 获取农历 + 节气
# ==========================================

def get_lunar_info():

    target = get_target_date()

    solar = Solar.fromYmd(
        target.year,
        target.month,
        target.day
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
    target = get_target_date()
    delta = target - start_date

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
# 天气描述增强
# ==========================================

def get_weather_life_desc(weather_type):

    if "晴" in weather_type:
        return "☀️ 天气晴好，适宜出行，也请注意防晒。"
    elif "多云" in weather_type:
        return "⛅ 多云天气，体感较舒适，适合日常出行。"
    elif "阴" in weather_type:
        return "☁️ 阴天为主，外出请留意天气变化。"
    elif "雷" in weather_type:
        return "⚡ 可能出现雷电天气，请尽量减少户外停留。"
    elif "暴雨" in weather_type:
        return "⛈️ 暴雨天气，请提前规划行程，注意出行安全。"
    elif "大雨" in weather_type:
        return "🌧️ 降雨明显，请携带雨具，注意道路湿滑。"
    elif "雨" in weather_type:
        return "☔ 有降雨可能，出门建议随身携带雨具。"
    elif "雪" in weather_type:
        return "❄️ 有降雪天气，请注意防寒保暖及出行安全。"
    elif "雾" in weather_type:
        return "🌫️ 能见度较低，驾车请减速慢行。"
    elif "霾" in weather_type:
        return "😷 空气质量可能受影响，敏感人群请做好防护。"
    else:
        return ""


# ==========================================
# 中国节日专属文案
# ==========================================

def get_festival_message(lunar):

    solar_target = get_target_datetime().strftime("%m-%d")

    lunar_month = lunar.getMonth()
    lunar_day = lunar.getDay()

    solar_festivals = {
        "01-01": "🎉 元旦快乐，愿新的一年平安顺遂。",
        "05-01": "🛠️ 劳动节快乐，致敬每一位奋斗者。",
        "10-01": "🇨🇳 国庆节快乐，祝祖国繁荣昌盛。",
    }

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

    if solar_target in solar_festivals:
        return solar_festivals[solar_target]

    return ""


# ==========================================
# 节日前安全提醒
# ==========================================

def get_holiday_safety_notice(lunar):

    solar_target = get_target_datetime().strftime("%m-%d")
    lunar_month = lunar.getMonth()
    lunar_day = lunar.getDay()

    notices = {
        "04-30": "🚗 五一假期临近，如有出行安排，请提前规划路线并注意家中水电安全。",
        "09-30": "🇨🇳 国庆假期临近，请合理安排出行，离家前注意关闭门窗、水电及燃气。",
        "12-31": "🎆 元旦假期临近，外出请注意交通安全，居家请做好防火防盗。",
    }

    lunar_notices = {
        (12, 29): "🧨 春节临近，请注意用火用电安全，外出前检查门窗、水电及燃气。",
        (12, 30): "🧧 除夕将至，愿您阖家团圆，也请注意居家用火用电安全。",
        (5, 4): "🚣 端午将至，请注意饮食卫生，出行注意交通安全。",
        (8, 14): "🌕 中秋将至，愿团圆相伴，外出请注意行程与安全。",
    }

    if solar_target in notices:
        return notices[solar_target]

    if (lunar_month, lunar_day) in lunar_notices:
        return lunar_notices[(lunar_month, lunar_day)]

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
        return jieqi_dict.get(jieqi, f"🌿 今日节气：{jieqi}")

    return ""


# ==========================================
# PM2.5描述
# ==========================================

def get_pm25_desc(aqi):

    try:
        aqi_num = int(float(aqi))

        if aqi_num <= 35:
            return f"{aqi}（空气清新）"
        elif aqi_num <= 75:
            return f"{aqi}（空气良好）"
        elif aqi_num <= 115:
            return f"{aqi}（轻度污染）"
        elif aqi_num <= 150:
            return f"{aqi}（中度污染）"
        else:
            return f"{aqi}（污染较重）"

    except:
        return str(aqi)


# ==========================================
# 空气质量提醒
# ==========================================

def get_air_quality_notice(aqi):

    try:
        aqi = int(float(aqi))

        if aqi <= 35:
            return "🌿 空气质量较好，适宜户外活动。"
        elif aqi <= 75:
            return "🍃 空气质量良好，可正常外出。"
        elif aqi <= 115:
            return "🌫️ 空气轻度污染，敏感人群请注意防护。"
        elif aqi <= 150:
            return "⚠️ 空气中度污染，建议减少长时间户外活动。"
        else:
            return "🚨 空气污染较重，请注意健康防护。"

    except:
        return ""


# ==========================================
# 极端天气预警
# ==========================================

def get_weather_warning(weather_type, high_temp, low_temp):

    warnings = []

    try:
        high = int(float(high_temp))
    except:
        high = 25

    try:
        low = int(float(low_temp))
    except:
        low = 15

    if high >= 35:
        warnings.append("🔥 高温天气，请注意防暑降温，避免长时间户外活动。")
    elif high >= 30:
        warnings.append("🥤 气温较高，外出请注意防晒并及时补充水分。")

    if low <= 0:
        warnings.append("🧣 气温较低，请注意添衣保暖。")
    elif high - low >= 10:
        warnings.append("🧥 昼夜温差较大，早晚出行建议适当添衣。")

    if "暴雨" in weather_type:
        warnings.append("⛈️ 暴雨天气，请注意出行安全，避开低洼积水路段。")
    elif "大雨" in weather_type:
        warnings.append("🌧️ 降雨明显，请携带雨具，注意道路湿滑。")
    elif "雨" in weather_type:
        warnings.append("☔ 有降雨天气，出门建议备好雨具。")

    if "雷" in weather_type:
        warnings.append("⚡ 雷电天气，请减少户外停留。")

    if "雪" in weather_type:
        warnings.append("❄️ 降雪天气，道路湿滑，请注意慢行。")

    if "大风" in weather_type or "狂风" in weather_type:
        warnings.append("💨 风力较大，请注意关闭门窗，并妥善安置阳台物品。")

    return "\n".join(warnings)


# ==========================================
# 每日语录：按日期轮换，避免连续随机重复
# ==========================================

def pick_by_day(messages):

    day_num = get_day_number()
    index = day_num % len(messages)

    return messages[index]


def get_daily_message():

    target = get_target_datetime()
    weekday = target.weekday()

    monday_msgs = [
        "💼 新的一周开启，愿您工作顺利、心情愉快。",
        "☀️ 周一早安，愿好心情伴随您开启新的一周。",
        "🌿 新周启程，愿今日顺遂，万事从容。",
    ]

    friday_msgs = [
        "🌇 周末将至，愿疲惫渐散，好运开启。",
        "🍃 周五愉快，愿您带着轻松心情迎接周末。",
        "✨ 忙碌一周辛苦了，愿今晚有温暖与放松。",
    ]

    weekend_msgs = [
        "🌸 周末愉快，愿您与家人共享惬意时光。",
        "☀️ 愿这个周末，有阳光、有陪伴、有好心情。",
        "🍵 周末已至，愿生活慢下来，心情亮起来。",
    ]

    normal_msgs = [
        "🌞 每一个清晨都是新的开始，愿您今日幸福满满。",
        "🍀 愿您眼里有光，心中有爱，今日皆美好。",
        "🌅 晨曦微露，愿生活如诗般温暖。",
        "💐 把昨日烦恼留给昨天，用笑容迎接今天。",
        "✨ 心存美好，万物皆美。",
    ]

    if weekday == 0:
        return pick_by_day(monday_msgs)
    elif weekday == 4:
        return pick_by_day(friday_msgs)
    elif weekday in [5, 6]:
        return pick_by_day(weekend_msgs)
    else:
        return pick_by_day(normal_msgs)


# ==========================================
# 物业结尾语
# ==========================================

def get_property_message():

    messages = [
        f"🏡 {COMMUNITY_NAME} 祝您生活愉快，出行顺利。",
        f"🏡 {COMMUNITY_NAME} 愿您与家人平安顺遂，天天好心情。",
        f"🏡 {COMMUNITY_NAME} 愿您今日万事顺意，归家一路安心。",
        f"🏡 {COMMUNITY_NAME} 感谢您的理解与支持，祝您生活愉快。",
        f"🏡 {COMMUNITY_NAME} 愿美好常伴左右，幸福如期而至。",
        f"🏡 {COMMUNITY_NAME} 愿您今日工作顺利，生活舒心。",
        f"🏡 {COMMUNITY_NAME} 祝您与家人平安健康，阖家幸福。",
        f"🏡 {COMMUNITY_NAME} 愿每一天都有温暖与好心情。",
        f"🏡 {COMMUNITY_NAME} 愿您出行平安，归家有暖。",
        f"🏡 {COMMUNITY_NAME} 祝您今日顺顺利利，生活愉快。",
    ]

    return pick_by_day(messages)


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

            target = get_target_datetime()

            weekdays = [
                "星期一",
                "星期二",
                "星期三",
                "星期四",
                "星期五",
                "星期六",
                "星期日"
            ]

            weekday = weekdays[target.weekday()]
            date_str = target.strftime("%Y年%m月%d日")

            lunar_text, jieqi, lunar = get_lunar_info()

            jieqi_msg = get_jieqi_message(jieqi)
            festival_msg = get_festival_message(lunar)
            holiday_notice = get_holiday_safety_notice(lunar)
            weather_life_desc = get_weather_life_desc(weather_type)
            daily_msg = get_daily_message()

            day_num = get_day_number()
            aqi = d['data'].get('pm25', 0)

            pm25_text = get_pm25_desc(aqi)
            air_notice = get_air_quality_notice(aqi)

            warning_msg = get_weather_warning(
                weather_type,
                high_temp,
                low_temp
            )

            property_msg = get_property_message()

            message_parts = [
                f"【永升早安语录·Day{day_num}】",
                f"📅 {date_str} {weekday}",
                f"🌙 {lunar_text}",
            ]

            if festival_msg:
                message_parts.append(festival_msg)

            if jieqi_msg:
                message_parts.append(jieqi_msg)

            if holiday_notice:
                message_parts.append(holiday_notice)

            message_parts.extend([
                f"{weather_icon} 天气：{weather_type}",
                f"🌡️ 气温：{low_temp}℃ ~ {high_temp}℃",
                f"🌿 PM2.5：{pm25_text}",
            ])

            if weather_life_desc:
                message_parts.append(weather_life_desc)

            if air_notice:
                message_parts.append(air_notice)

            if warning_msg:
                message_parts.append(warning_msg)

            if daily_msg:
                message_parts.append(daily_msg)

            message_parts.append(property_msg)

            message = "\n".join(message_parts)

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

    headers = {'Content-Type': 'application/json'}

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
        send_to_wechat(f"【天气获取失败】\n{message}")

    print("✅ 执行结束")


if __name__ == '__main__':
    main()
