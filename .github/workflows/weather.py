#!/usr/bin/python3
#coding=utf-8

import requests
import json
import random
import sys
from datetime import datetime, timedelta

# 企业微信机器人 Webhook 地址
WX_WEBHOOK = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=68910e58-fcfc-4a50-96b5-df810275aba1'

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

def get_property_message():
    """生成物业管家专属结束语"""
    messages = [
        f"\n🏢 【{COMMUNITY_NAME}物业温馨提示】\n无论天气如何变化，我们始终在您身边。如需帮助，请致电物业服务中心：XXXX-XXXXXXXX",
        f"\n🏢 【{COMMUNITY_NAME}物业暖心提醒】\n出门记得查看天气，带好雨具/做好防晒。您的满意是我们最大的动力！",
        f"\n🏢 【{COMMUNITY_NAME}物业管家服务】\n我是您的专属管家小X，有任何需求随时找我。祝您今日心情愉快！",
        f"\n🏢 【{COMMUNITY_NAME}物业】\n天气多变，注意身体。我们将继续努力，为您创造更舒适的居住环境。",
        f"\n🏢 【{COMMUNITY_NAME}物业提醒您】\n明日天气预报已送达，出行请注意安全。如需帮助，请联系物业。",
        f"\n🏢 【{COMMUNITY_NAME}物业】\n美好的一天从天气预报开始！如有报修或咨询，欢迎联系物业。",
    ]
    
    weekday = datetime.now().weekday()
    if weekday == 4:  # 周五
        messages.append(f"\n🏢 【{COMMUNITY_NAME}物业祝您周末愉快】\n提前祝您周末快乐！如需帮助，我们随时在线。")
    elif weekday == 0:  # 周一
        messages.append(f"\n🏢 【{COMMUNITY_NAME}物业】\n新的一周开始啦！出门前别忘了看天气哦~")
    
    return random.choice(messages)

def get_dress_advice(weather_type, high_temp, low_temp, is_today=False):
    """根据天气和温度生成穿衣建议"""
    try:
        high = int(''.join(filter(str.isdigit, high_temp)))
        low = int(''.join(filter(str.isdigit, low_temp)))
    except:
        high, low = 20, 10
    
    time_desc = "今天" if is_today else "明天"
    advice = f"👔 【{time_desc}穿衣指南】\n"
    
    if high >= 30:
        advice += f"{time_desc}高温，建议穿短袖、短裤、裙子等清凉衣物，注意防晒，多补充水分。"
    elif high >= 25:
        advice += f"{time_desc}温度适中偏热，建议穿短袖、薄长裤，可携带薄外套以防空调房温差。"
    elif high >= 20:
        advice += f"{time_desc}温度舒适，建议穿长袖T恤、薄外套、牛仔裤等。"
    elif high >= 15:
        advice += f"{time_desc}温度偏凉，建议穿毛衣、卫衣、夹克，注意保暖。"
    elif high >= 5:
        advice += f"{time_desc}温度较低，建议穿厚外套、毛衣、羽绒服，注意防寒保暖。"
    else:
        advice += f"{time_desc}温度寒冷，建议穿羽绒服、厚棉衣、围巾手套，注意防寒保暖。"
    
    if "雨" in weather_type:
        advice += f" {time_desc}有雨，出门记得带伞，注意路面湿滑。"
    elif "雪" in weather_type:
        advice += f" {time_desc}有雪，路面湿滑，请注意出行安全。"
    elif "风" in weather_type or weather_type in ["大风", "沙尘"]:
        advice += f" {time_desc}风大，注意关好门窗，收好阳台物品。"
    elif "雾" in weather_type or "霾" in weather_type:
        advice += f" {time_desc}空气质量不佳，建议减少户外活动，佩戴口罩。"
    
    return advice

def get_weather(weather_type='tomorrow'):
    """
    获取天气信息
    weather_type: 'today' 或 'tomorrow'
    """
    api = 'http://t.weather.itboy.net/api/weather/city/'
    city_code = '101070101'
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
            
            dress_advice = get_dress_advice(weather_type_str, high_temp, low_temp, is_today=(weather_type=='today'))
            property_message = get_property_message()
            
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
