#!/usr/bin/python3
# coding=utf-8

import os
import requests
import json
import random
import sys
from datetime import datetime

# ==============================
# 环境变量配置（避免明文）
# ==============================

WX_WEBHOOK = os.getenv("WX_WEBHOOK")
COMMUNITY_NAME = os.getenv("COMMUNITY_NAME", "铂宸府物业服务中心")
CITY_CODE = os.getenv("CITY_CODE", "101070101")  # 默认沈阳


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
# 天气提醒
# ==============================

def get_weather_warning(weather_type, high_temp, low_temp):
    """根据天气生成出行提醒"""

    try:
        high = int(''.join(filter(str.isdigit, high_temp)))
    except:
        high = 20

    reminders = []

    if high >= 35:
        reminders.append("天气炎热，建议尽量减少午后长时间户外停留，注意做好防暑降温。")
    elif high >= 30:
        reminders.append("气温较高，外出请注意防晒，并及时补充水分。")
    elif high <= 0:
        reminders.append("气温较低，外出请注意添衣保暖。")
    elif high <= 10:
        reminders.append("早晚温差较明显，建议适当增添外套。")

    if "暴雨" in weather_type:
        reminders.append("暴雨天气，请提前规划出行，注意避开低洼积水路段。")
    elif "大雨" in weather_type:
        reminders.append("降雨较明显，出门请携带雨具，注意道路湿滑。")
    elif "中雨" in weather_type:
        reminders.append("有降雨天气，建议随身携带雨具，出行注意安全。")
    elif "小雨" in weather_type or "雨" in weather_type:
        reminders.append("出门建议备好雨具，注意脚下安全。")
    elif "暴雪" in weather_type or "大雪" in weather_type:
        reminders.append("降雪天气，路面湿滑，请注意慢行，谨慎出行。")
    elif "中雪" in weather_type or "小雪" in weather_type or "雪" in weather_type:
        reminders.append("有降雪天气，请注意防寒保暖及出行安全。")
    elif "大风" in weather_type or "狂风" in weather_type:
        reminders.append("风力较大，请留意门窗关闭，并妥善安置阳台物品。")
    elif "雾" in weather_type:
        reminders.append("能见度较低，驾车出行请减速慢行，注意安全。")
    elif "霾" in weather_type:
        reminders.append("空气质量一般，敏感人群外出请做好防护。")

    return " ".join(reminders)


# ==============================
# 穿衣建议
# ==============================

def get_dress_advice(weather_type, high_temp, low_temp, is_today=False):
    """根据天气生成穿衣建议"""

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

    warning = get_weather_warning(weather_type, high_temp, low_temp)

    if warning:
        advice += "\n📌 出行提醒：" + warning

    return advice


# ==============================
# 物业结尾提示
# ==============================

def get_property_message():
    """物业结束语"""

    base_messages = [

        f"\n🏢 【{COMMUNITY_NAME}】\n感谢您的关注，物业服务中心将持续为您提供细致、安心的服务。",

        f"\n🏢 【{COMMUNITY_NAME}】\n如您在生活服务、设施报修或出行协助方面需要帮助，欢迎随时联系物业服务中心。",

        f"\n🏢 【{COMMUNITY_NAME}】\n天气变化请您留意，物业服务中心将与您一同守护家人与生活的安心。",

        f"\n🏢 【{COMMUNITY_NAME}】\n愿您今日出行顺利、居家舒心，物业服务中心始终在岗守护。",

        f"\n🏢 【{COMMUNITY_NAME}】\n感谢您对物业服务工作的理解与支持，祝您与家人生活愉快。"

    ]

    friday_messages = [

        f"\n🏢 【{COMMUNITY_NAME}】\n周末将至，愿您在忙碌之余收获一份从容与惬意。",

        f"\n🏢 【{COMMUNITY_NAME}】\n周末临近，祝您与家人度过一个轻松愉快的美好时光。",

        f"\n🏢 【{COMMUNITY_NAME}】\n忙碌一周辛苦了，愿您以舒适心情迎接周末生活。",

        f"\n🏢 【{COMMUNITY_NAME}】\n周末在即，祝您归家有暖意，生活有从容。",

        f"\n🏢 【{COMMUNITY_NAME}】\n愿您以愉悦心情开启周末，物业服务中心将持续守护您的安心生活。"

    ]

    monday_messages = [

        f"\n🏢 【{COMMUNITY_NAME}】\n新的一周已经开启，愿您工作顺遂、生活安然。",

        f"\n🏢 【{COMMUNITY_NAME}】\n周一早安，愿您以从容与好心情开启新一周。",

        f"\n🏢 【{COMMUNITY_NAME}】\n新的一周，物业服务中心继续与您共同守护美好生活。",

        f"\n🏢 【{COMMUNITY_NAME}】\n愿您本周诸事顺意，出入平安，生活舒心。",

        f"\n🏢 【{COMMUNITY_NAME}】\n新周启程，愿美好如常相伴，安心始终相随。"

    ]

    weekday = datetime.now().weekday()

    if weekday == 4:
        return random.choice(friday_messages)
    elif weekday == 0:
        return random.choice(monday_messages)
    else:
        return random.choice(base_messages)


# ==============================
# 获取天气
# ==============================

def get_weather(weather_type='tomorrow'):

    api = 'http://t.weather.itboy.net/api/weather/city/'
    tqurl = api + CITY_CODE

    try:

        response = requests.get(tqurl, timeout=10)
        d = response.json()

        if d['status'] == 200:

            if weather_type == 'today':
                index = 0
                title = "【今日天气预报】"
            else:
                index = 1
                title = "【明日天气预报】"

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

            weather_info = (

                f"{title}\n"
                f"尊敬的业主您好，以下为{COMMUNITY_NAME}{'今日' if weather_type == 'today' else '明日'}天气提醒：\n\n"

                f"🏙️ 所在城市：{d['cityInfo']['parent']} {d['cityInfo']['city']}\n"
                f"📅 日期：{weather_data['ymd']} {weather_data['week']}\n"
                f"☁️ 天气情况：{weather_type_str}\n"
                f"🌡️ 气温范围：{low_temp} ~ {high_temp}\n"
                f"💧 空气湿度：{d['data']['shidu']}\n"
                f"🌿 空气质量：{d['data']['quality']}（PM2.5：{d['data']['pm25']}）\n"
                f"💨 风向风力：{weather_data['fx']} {weather_data['fl']}\n"
                f"🩺 健康提示：{d['data']['ganmao']}\n"
                f"📢 天气提示：{weather_data['notice']}\n\n"

                f"{dress_advice}"

                f"{property_message}"

            )

            return weather_info, True

        else:
            return f"天气接口返回错误: {d['status']}", False

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
