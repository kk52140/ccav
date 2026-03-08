#!/usr/bin/python3
#coding=utf-8

import requests
import json
import random
import sys
from datetime import datetime

# 企业微信机器人 Webhook 地址
WX_WEBHOOK = ''

# 小区名称
COMMUNITY_NAME = "铂宸府物业服务中心"

def send_to_wechat(content):
    """发送消息到企业微信机器人"""
    url = WX_WEBHOOK
    headers = {'Content-Type': 'application/json'}
    
    data = {
        "msgtype": "text",
        "text": {
            "content": content
        }
    }
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        result = response.json()
        if result.get('errcode') == 0:
            print("✅ 消息发送成功")
        else:
            print(f"❌ 消息发送失败: {result}")
    except Exception as e:
        print(f"❌ 发送异常: {e}")

def get_weather_warning(weather_type, high_temp, low_temp):
    """根据天气生成预警信息（用于穿衣指南）"""
    try:
        high = int(''.join(filter(str.isdigit, high_temp)))
    except:
        high = 20
    
    warning = ""
    
    # 温度预警（用于穿衣指南）
    if high >= 35:
        warning += "🔥 极端高温，注意防暑降温，尽量避免午后户外活动。"
    elif high >= 30:
        warning += "☀️ 高温天气，注意防晒，多补充水分。"
    elif high <= -10:
        warning += "❄️ 极端寒冷，注意防寒保暖，预防冻伤。"
    elif high <= 0:
        warning += "⛄ 严寒天气，注意保暖，预防感冒。"
    
    # 天气现象预警（用于穿衣指南）
    if "暴雨" in weather_type:
        warning += " 🌧️ 暴雨天气，注意防雨防雷，避开低洼路段。"
    elif "大雨" in weather_type:
        warning += " 🌧️ 大雨天气，出门带好雨具，注意交通安全。"
    elif "雨" in weather_type:
        warning += " ☔ 降雨天气，出门记得带伞。"
    elif "暴雪" in weather_type:
        warning += " 🌨️ 暴雪天气，注意防滑保暖，减少外出。"
    elif "大雪" in weather_type:
        warning += " 🌨️ 大雪天气，注意防滑，小心慢行。"
    elif "雪" in weather_type:
        warning += " ❄️ 降雪天气，路面湿滑，注意安全。"
    elif "大风" in weather_type or "狂风" in weather_type:
        warning += " 💨 大风天气，注意关好门窗，收好阳台物品。"
    elif "沙尘" in weather_type:
        warning += " 🏜️ 沙尘天气，佩戴口罩，减少户外活动。"
    elif "雾" in weather_type or "霾" in weather_type:
        warning += " 🌫️ 雾霾天气，佩戴口罩，注意行车安全。"
    
    return warning

def get_dress_advice(weather_type, high_temp, low_temp, is_today=False):
    """根据天气和温度生成穿衣建议"""
    try:
        high = int(''.join(filter(str.isdigit, high_temp)))
        low = int(''.join(filter(str.isdigit, low_temp)))
    except:
        high, low = 20, 10
    
    time_desc = "今天" if is_today else "明天"
    advice = f"👔 【{time_desc}穿衣指南】\n"
    
    # 基础穿衣建议
    if high >= 30:
        advice += f"{time_desc}高温，建议穿短袖、短裤、裙子等清凉衣物，注意防晒。"
    elif high >= 25:
        advice += f"{time_desc}温度适中偏热，建议穿短袖、薄长裤，可携带薄外套。"
    elif high >= 20:
        advice += f"{time_desc}温度舒适，建议穿长袖T恤、薄外套、牛仔裤等。"
    elif high >= 15:
        advice += f"{time_desc}温度偏凉，建议穿毛衣、卫衣、夹克，注意保暖。"
    elif high >= 5:
        advice += f"{time_desc}温度较低，建议穿厚外套、毛衣，注意防寒保暖。"
    else:
        advice += f"{time_desc}温度寒冷，建议穿羽绒服、厚棉衣、围巾手套，注意防寒保暖。"
    
    # 获取天气预警信息（添加到穿衣指南）
    warning = get_weather_warning(weather_type, high_temp, low_temp)
    if warning:
        advice += " " + warning
    
    return advice

def get_property_message(weather_type=None):
    """生成物业管家专属结束语（根据天气情况选择不同的暖心提示）"""
    
    # 基础暖心提示池
    base_messages = [
        f"\n🏢 【{COMMUNITY_NAME}物业温馨提示】\n无论天气如何变化，我们始终在您身边。如需帮助，请致电物业服务中心：XXXX-XXXXXXXX",
        
        f"\n🏢 【{COMMUNITY_NAME}物业暖心提醒】\n美好的一天从天气预报开始！如有报修或咨询，欢迎联系物业。",
        
        f"\n🏢 【{COMMUNITY_NAME}物业管家服务】\n我是您的专属管家，有任何需求随时找我。祝您今日心情愉快！",
        
        f"\n🏢 【{COMMUNITY_NAME}物业】\n天气多变，注意身体。我们将继续努力，为您创造更舒适的居住环境。",
        
        f"\n🏢 【{COMMUNITY_NAME}物业】\n您的满意是我们最大的动力！"
    ]
    
    # 根据天气情况选择特定的暖心提示
    weather_messages = []
    
    if weather_type:
        if "雨" in weather_type:
            weather_messages.append(
                f"\n🏢 【{COMMUNITY_NAME}物业雨天提醒】\n雨天路滑，出行请注意安全。如需帮助，请随时联系我们。"
            )
        elif "雪" in weather_type:
            weather_messages.append(
                f"\n🏢 【{COMMUNITY_NAME}物业雪天提醒】\n雪天路滑，请注意出行安全，老人小孩尽量减少外出。"
            )
        elif "大风" in weather_type or "狂风" in weather_type:
            weather_messages.append(
                f"\n🏢 【{COMMUNITY_NAME}物业大风提醒】\n大风天气，请关好门窗，收好阳台物品，注意高空坠物。"
            )
        elif "雾" in weather_type or "霾" in weather_type:
            weather_messages.append(
                f"\n🏢 【{COMMUNITY_NAME}物业雾霾提醒】\n雾霾天气，建议佩戴口罩，减少户外活动，注意行车安全。"
            )
        elif "晴" in weather_type and int(''.join(filter(str.isdigit, high_temp)) if 'high_temp' in locals() else 20) >= 30:
            weather_messages.append(
                f"\n🏢 【{COMMUNITY_NAME}物业高温提醒】\n高温天气，请注意防暑降温，多补充水分，避免长时间日晒。"
            )
        elif "晴" in weather_type:
            weather_messages.append(
                f"\n🏢 【{COMMUNITY_NAME}物业】\n天气晴朗，适合晾晒和户外活动，祝您心情愉快！"
            )
    
    # 周末特定提醒
    weekday = datetime.now().weekday()
    if weekday == 4:  # 周五
        weather_messages.append(f"\n🏢 【{COMMUNITY_NAME}物业祝您周末愉快】\n提前祝您周末快乐！如需帮助，我们随时在线。")
    elif weekday == 0:  # 周一
        weather_messages.append(f"\n🏢 【{COMMUNITY_NAME}物业】\n新的一周开始啦！祝您工作顺利，心情愉快！")
    
    # 合并所有消息池
    all_messages = weather_messages + base_messages
    
    return random.choice(all_messages) if all_messages else random.choice(base_messages)

def get_weather(weather_type='tomorrow'):
    """
    获取天气信息
    weather_type: 'today' 或 'tomorrow'
    """
    api = 'http://t.weather.itboy.net/api/weather/city/'
    city_code = '101070101'  # 沈阳
    tqurl = api + city_code
    
    try:
        response = requests.get(tqurl)
        d = response.json()
        
        if d['status'] == 200:
            # 选择今天或明天的数据
            if weather_type == 'today':
                index = 0  # 今天
                title = "【今日天气预报】"
            else:
                index = 1  # 明天
                title = "【明日天气预报】"
            
            weather_data = d['data']['forecast'][index]
            weather_type_str = weather_data['type']
            high_temp = weather_data['high']
            low_temp = weather_data['low']
            
            # 生成穿衣建议（包含天气预警）
            dress_advice = get_dress_advice(weather_type_str, high_temp, low_temp, is_today=(weather_type=='today'))
            
            # 生成物业暖心提示（根据天气情况）
            property_message = get_property_message(weather_type_str)
            
            weather_info = (
                f"{title}\n"
                f"🏙️ 城市：{d['cityInfo']['parent']} {d['cityInfo']['city']}\n"
                f"📅 日期：{weather_data['ymd']} {weather_data['week']}\n"
                f"☁️ 天气：{weather_type_str}\n"
                f"🌡️ 温度：{high_temp} {low_temp}\n"
                f"💧 湿度：{d['data']['shidu']}\n"
                f"🍃 空气质量：{d['data']['quality']} (PM2.5:{d['data']['pm25']})\n"
                f"💨 风力风向：{weather_data['fx']} {weather_data['fl']}\n"
                f"🤧 感冒指数：{d['data']['ganmao']}\n"
                f"📢 温馨提示：{weather_data['notice']}\n"
                f"\n{dress_advice}\n"
                f"{property_message}"
            )
            return weather_info, True
        else:
            return f"【天气接口返回错误】状态码：{d['status']}", False
    except Exception as e:
        return f"【获取天气失败】{e}", False

def main():
    """主函数"""
    # 获取命令行参数
    weather_type = 'tomorrow'  # 默认明天
    if len(sys.argv) > 1:
        weather_type = sys.argv[1]
    
    type_desc = "今日" if weather_type == 'today' else "明日"
    print(f"🚀 开始执行{type_desc}天气推送...")
    
    weather_msg, success = get_weather(weather_type)
    
    if success:
        print(f"📤 正在发送{type_desc}天气信息到企业微信...")
        send_to_wechat(weather_msg)
    else:
        print(f"📤 正在发送错误信息到企业微信...")
        error_msg = f"【{type_desc}天气推送失败】\n{weather_msg}"
        send_to_wechat(error_msg)
    
    print("✅ 执行完成")
    return "执行完成"

if __name__ == '__main__':
    main()
