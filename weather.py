#!/usr/bin/python3
# coding=utf-8

import os
import requests
import json
import random
import sys
import re
from datetime import datetime, timedelta

# ==============================
# 环境变量配置（避免明文）
# ==============================

WX_WEBHOOK = os.getenv("WX_WEBHOOK")
COMMUNITY_NAME = os.getenv("COMMUNITY_NAME", "铂宸府物业服务中心")
CITY_CODE = os.getenv("CITY_CODE", "101070101")  # 默认沈阳


# ==============================
# 通用工具
# ==============================

def extract_temp(temp_text, default=20):
    """从 '高温 5℃' / '低温 -4℃' 中提取整数温度"""
    try:
        match = re.search(r'-?\d+', str(temp_text))
        return int(match.group()) if match else default
    except Exception:
        return default


def format_pm25(pm25_value):
    """格式化 PM2.5 数值"""
    try:
        return str(int(float(pm25_value)))
    except Exception:
        return str(pm25_value)


# ==============================
# 发送企业微信消息
# ==============================

def send_to_wechat(content):
    """发送消息到企业微信机器人"""
    if not WX_WEBHOOK:
        raise RuntimeError("未配置 WX_WEBHOOK 环境变量")

    headers = {'Content-Type': 'application/json'}
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
            data=json.dumps(data, ensure_ascii=False),
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
# 天气分级判断
# ==============================

def get_weather_level(weather_type, high_temp, low_temp, wind_level_text):
    """
    天气模板级别：
    normal  = 普通天气
    rain    = 降雨加强提醒
    severe  = 恶劣天气安全提醒
    """
    high = extract_temp(high_temp, 20)
    low = extract_temp(low_temp, 10)

    # 提取风力等级中的数字
    wind_level_num = 0
    try:
        match = re.search(r'(\d+)', str(wind_level_text))
        if match:
            wind_level_num = int(match.group(1))
    except Exception:
        wind_level_num = 0

    # 恶劣天气条件
    severe_keywords = ["暴雨", "大暴雨", "暴雪", "大雪", "中雪", "冰雹", "沙尘暴", "雷暴", "强对流"]
    if any(k in weather_type for k in severe_keywords):
        return "severe"

    if wind_level_num >= 6:
        return "severe"

    if high <= -10 or low <= -10:
        return "severe"

    # 降雨加强提醒
    rain_keywords = ["小雨", "中雨", "大雨", "阵雨", "雷阵雨", "雨夹雪"]
    if any(k in weather_type for k in rain_keywords):
        return "rain"

    return "normal"


# ==============================
# 出行提醒
# ==============================

def get_weather_warning(weather_type, high_temp, low_temp, weather_level):
    """根据天气生成出行提醒"""
    high = extract_temp(high_temp, 20)
    low = extract_temp(low_temp, 10)

    # 恶劣天气
    if weather_level == "severe":
        if "雪" in weather_type:
            return "降雪天气路面可能结冰，请注意出行安全，行走及驾车时请减速慢行。"
        elif "风" in weather_type:
            return "风力较大，请留意高空坠物，尽量避免在树木、广告牌附近停留。"
        elif "雨" in weather_type:
            return "强降雨天气请提前规划出行，注意避开低洼积水路段，确保出行安全。"
        elif high <= -10 or low <= -10:
            return "气温持续偏低，请注意防寒保暖，谨防低温天气对出行带来的不便。"
        else:
            return "天气情况较为复杂，请留意安全，合理安排出行。"

    # 降雨天气
    if weather_level == "rain":
        return "降雨天气道路湿滑，步行及驾车请注意安全，尽量预留充足出行时间。"

    # 普通天气
    if high <= 5 or low <= 0:
        return "早晚气温偏低，建议适当增添衣物，合理安排出行时间。"
    elif high - low >= 8:
        return "昼夜温差较明显，请注意适时增减衣物。"
    else:
        return "天气较为平稳，适宜日常出行。"


# ==============================
# 着装建议
# ==============================

def get_dress_advice(weather_type, high_temp, low_temp, is_today=False):
    """根据天气生成着装建议"""
    high = extract_temp(high_temp, 20)
    low = extract_temp(low_temp, 10)

    time_desc = "今日" if is_today else "明日"
    advice = f"👔 {time_desc}着装建议\n"

    if high >= 30:
        advice += "建议选择轻薄透气衣物，外出注意防晒。"
    elif high >= 25:
        advice += "建议着轻便服装，早晚可酌情搭配薄外套。"
    elif high >= 20:
        advice += "建议着长袖上衣或薄外套，出行较为舒适。"
    elif high >= 15:
        advice += "建议着针织衫、卫衣或外套，注意早晚保暖。"
    elif high >= 5:
        advice += "建议着保暖外套，适当做好防寒准备。"
    else:
        advice += "建议穿着羽绒服、大衣等保暖衣物，并注意防寒保暖。"

    return advice


# ==============================
# 天气提示
# ==============================

def build_weather_notice(weather_type, high_temp, low_temp, quality, weather_level):
    """生成不同级别天气提示"""
    high = extract_temp(high_temp, 20)
    low = extract_temp(low_temp, 10)
    notices = []

    if weather_level == "severe":
        if "雪" in weather_type:
            notices.append("今日有降雪天气，气温较低，请注意防寒保暖。")
        elif "风" in weather_type:
            notices.append("今日风力较大，请注意关好门窗，并留意阳台物品固定情况。")
        elif "雨" in weather_type:
            notices.append("今日有明显降雨天气，请提前做好出行安排并注意防范积水。")
        elif high <= -10 or low <= -10:
            notices.append("今日气温较低，请注意做好防寒保暖措施。")
        else:
            notices.append("今日天气变化较明显，请及时关注天气情况并做好防护。")

    elif weather_level == "rain":
        notices.append("今日有降雨天气，外出建议随身携带雨具。")

    else:
        if "晴" in weather_type:
            notices.append("天气晴好，适宜出行。")
        elif "多云" in weather_type:
            notices.append("天气较为平稳，适宜日常出行。")
        elif "阴" in weather_type:
            notices.append("天气以阴天为主，请注意及时增减衣物。")
        else:
            notices.append("请根据天气变化合理安排出行与生活。")

    if weather_level == "normal":
        if low <= 0:
            notices.append("早晚气温偏低，请注意防寒保暖。")
        elif high - low >= 8:
            notices.append("昼夜温差较明显，请注意适时增减衣物。")

    if str(quality) in ["轻度", "中度", "重度", "严重"]:
        notices.append("空气质量一般，敏感人群建议减少长时间户外活动。")

    return "".join(notices)


def optimize_ganmao_text(raw_text):
    """健康提示轻度润色"""
    if not raw_text:
        return "请根据天气变化注意日常健康防护。"

    text = str(raw_text).strip()
    text = text.replace("儿童、老年人及心脏、呼吸系统疾病患者人群", "儿童、老年人及心肺敏感人群")
    return text


# ==============================
# 物业结尾提示（周一 / 周五特殊版）
# ==============================

def get_property_message():
    """物业结束语"""

    normal_messages = [
        f"🏢 {COMMUNITY_NAME}\n感谢您的关注，物业服务中心将持续为您提供细致、安心的服务。",
        f"🏢 {COMMUNITY_NAME}\n如您在生活服务、设施报修或出行协助方面需要帮助，欢迎随时联系物业服务中心。",
        f"🏢 {COMMUNITY_NAME}\n天气变化请您留意，物业服务中心将与您一同守护家人与生活的安心。"
    ]

    monday_messages = [
        f"🏢 {COMMUNITY_NAME}\n新的一周已经开启，愿您工作顺遂、生活安然。\n物业服务中心将持续为您守护安心生活。",
        f"🏢 {COMMUNITY_NAME}\n周一早安，愿您以从容与好心情开启新一周。\n如您有生活服务需求，欢迎随时联系物业服务中心。"
    ]

    friday_messages = [
        f"🏢 {COMMUNITY_NAME}\n周末将至，祝您与家人度过一个轻松愉快的美好时光。\n如您有生活服务需求，物业服务中心随时为您提供协助。",
        f"🏢 {COMMUNITY_NAME}\n忙碌一周辛苦了，愿您以舒适心情迎接周末生活。\n物业服务中心将持续守护您的安心与便利。"
    ]

    beijing_time = datetime.utcnow() + timedelta(hours=8)
    weekday = beijing_time.weekday()

    if weekday == 0:
        return random.choice(monday_messages)
    elif weekday == 4:
        return random.choice(friday_messages)
    else:
        return random.choice(normal_messages)


# ==============================
# 获取天气
# ==============================

def get_weather(weather_type='tomorrow'):
    api = 'http://t.weather.itboy.net/api/weather/city/'
    tqurl = api + CITY_CODE

    try:
        response = requests.get(tqurl, timeout=10)
        d = response.json()

        if d['status'] != 200:
            return f"天气接口返回错误: {d['status']}", False

        if weather_type == 'today':
            index = 0
            title_prefix = "今日"
        else:
            index = 1
            title_prefix = "明日"

        weather_data = d['data']['forecast'][index]

        weather_type_str = weather_data['type']
        high_temp_raw = weather_data['high']
        low_temp_raw = weather_data['low']
        wind_text = weather_data['fl']

        high_temp = extract_temp(high_temp_raw, 20)
        low_temp = extract_temp(low_temp_raw, 10)

        air_quality = str(d['data'].get('quality', '未知'))
        pm25 = format_pm25(d['data'].get('pm25', '未知'))
        ganmao_text = optimize_ganmao_text(d['data'].get('ganmao', ''))

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
            air_quality,
            weather_level
        )

        dress_advice = get_dress_advice(
            weather_type_str,
            high_temp,
            low_temp,
            is_today=(weather_type == 'today')
        )

        travel_warning = get_weather_warning(
            weather_type_str,
            high_temp,
            low_temp,
            weather_level
        )

        property_message = get_property_message()

        # 标题根据天气级别切换
        if weather_level == "severe":
            title = "【天气安全提醒】"
        else:
            title = f"【{title_prefix}天气提醒】"

        # 普通天气模板
        if weather_level == "normal":
            weather_info = (
                f"{title}\n\n"
                f"尊敬的业主您好，以下为{COMMUNITY_NAME}{title_prefix}天气提醒：\n\n"
                f"🏙️ 所在城市：{d['cityInfo']['parent']} {d['cityInfo']['city']}\n"
                f"📅 日期：{weather_data['ymd']} {weather_data['week']}\n"
                f"☁️ 天气情况：{weather_type_str}\n"
                f"🌡️ 预计气温：{low_temp}℃ ~ {high_temp}℃\n"
                f"💧 空气湿度：{d['data']['shidu']}\n"
                f"🌿 空气质量：{air_quality}（PM2.5：{pm25}）\n"
                f"💨 风向风力：{weather_data['fx']} {weather_data['fl']}\n\n"
                f"📢 {title_prefix}天气提示\n"
                f"{weather_notice}\n\n"
                f"{dress_advice}\n\n"
                f"🚶 出行提醒\n"
                f"{travel_warning}\n\n"
                f"{property_message}"
            )

        # 降雨天气模板
        elif weather_level == "rain":
            weather_info = (
                f"{title}\n\n"
                f"尊敬的业主您好，以下为{COMMUNITY_NAME}{title_prefix}天气提醒：\n\n"
                f"🏙️ 所在城市：{d['cityInfo']['parent']} {d['cityInfo']['city']}\n"
                f"📅 日期：{weather_data['ymd']} {weather_data['week']}\n"
                f"🌧 天气情况：{weather_type_str}\n"
                f"🌡️ 预计气温：{low_temp}℃ ~ {high_temp}℃\n"
                f"💧 空气湿度：{d['data']['shidu']}\n"
                f"🌿 空气质量：{air_quality}（PM2.5：{pm25}）\n"
                f"💨 风向风力：{weather_data['fx']} {weather_data['fl']}\n\n"
                f"📢 {title_prefix}天气提示\n"
                f"{weather_notice}\n\n"
                f"{dress_advice}\n\n"
                f"🚶 出行提醒\n"
                f"{travel_warning}\n\n"
                f"{property_message}"
            )

        # 恶劣天气模板
        else:
            severe_home_tip = ""
            if "风" in weather_type_str or extract_temp(weather_data['fl'], 0) >= 6:
                severe_home_tip = "🏠 居家提示\n请留意关好门窗，并检查阳台物品是否固定。\n\n"

            weather_info = (
                f"{title}\n\n"
                f"尊敬的业主您好，以下为{COMMUNITY_NAME}天气提醒：\n\n"
                f"🏙️ 所在城市：{d['cityInfo']['parent']} {d['cityInfo']['city']}\n"
                f"📅 日期：{weather_data['ymd']} {weather_data['week']}\n"
                f"❄️ 天气情况：{weather_type_str}\n"
                f"🌡️ 预计气温：{low_temp}℃ ~ {high_temp}℃\n"
                f"💧 空气湿度：{d['data']['shidu']}\n"
                f"🌿 空气质量：{air_quality}（PM2.5：{pm25}）\n"
                f"💨 风向风力：{weather_data['fx']} {weather_data['fl']}\n"
                f"🩺 健康提示：{ganmao_text}\n\n"
                f"📢 天气提示\n"
                f"{weather_notice}\n\n"
                f"⚠️ 安全提醒\n"
                f"{travel_warning}\n\n"
                f"{severe_home_tip}"
                f"{dress_advice}\n\n"
                f"{property_message}"
            )

        return weather_info, True

    except Exception as e:
        return f"获取天气失败: {e}", False


# ==============================
# 主函数
# ==============================

def main():
    weather_type = 'tomorrow'

    if len(sys.argv) > 1:
        weather_type = sys.argv[1]

    type_desc = "今日" if weather_type == 'today' else "明日"
    print(f"🚀 开始执行{type_desc}天气推送...")

    weather_msg, success = get_weather(weather_type)

    if success:
        print("📤 正在发送天气信息...")
        send_to_wechat(weather_msg)
    else:
        error_msg = f"【天气推送失败】\n{weather_msg}"
        send_to_wechat(error_msg)

    print("✅ 执行完成")


if __name__ == '__main__':
    main()
