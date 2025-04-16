import streamlit as st
import streamlit.components.v1 as components
import folium
from folium import plugins
import pandas as pd
from streamlit_folium import st_folium
import time
import json
from datetime import datetime
import numpy as np
import math
import os
from urllib.parse import quote, urlencode
import requests

# 从环境变量或 Streamlit Secrets 获取 API 密钥
def get_api_key():
    # 优先从 Streamlit Secrets 获取
    if 'AMAP_API_KEY' in st.secrets:
        return st.secrets['AMAP_API_KEY']
    # 否则从环境变量获取
    return os.environ.get('AMAP_API_KEY', '')

# 检查 API 密钥
api_key = get_api_key()
if not api_key:
    st.error('请设置高德地图 API 密钥！')
    st.stop()

# 设置页面标题和简介
st.set_page_config(layout="wide")
st.title('苏州两日精华游')
st.markdown("""
这是一份为期两天的苏州精华景点游览路线。每个景点都经过精心挑选，包含了苏州最具代表性的园林、古街、寺庙等景点。
路线设计考虑了景点之间的距离和游览时间，让您能够充分体验苏州的古典园林之美和江南水乡风情。
""")

# 添加自定义CSS和JavaScript
st.markdown("""
<style>
    /* 当处于规划模式时，将鼠标改为十字 */
    .planning-mode {
        cursor: crosshair !important;
    }
    
    /* 当鼠标悬停在途经点上时，将鼠标改为指针 */
    .waypoint-marker {
        cursor: pointer !important;
    }
</style>
""", unsafe_allow_html=True)

# 添加JavaScript代码以处理右键点击和鼠标样式
js_code = """
<script>
// 禁用默认的右键菜单
document.addEventListener('contextmenu', function(e) {
    if (e.target.closest('.folium-map')) {
        e.preventDefault();
    }
});

// 设置规划模式的鼠标样式
function setPlanningMode(enabled) {
    const map = document.querySelector('.folium-map');
    if (map) {
        if (enabled) {
            map.classList.add('planning-mode');
        } else {
            map.classList.remove('planning-mode');
        }
    }
}
</script>
"""
st.components.v1.html(js_code, height=0)

# 定义路线数据
ROUTES = {
    'day1': {
        'name': '第一天行程',
        'points': [
            {'name': '维也纳国际酒店', 'lat': 31.339867, 'lon': 120.617061, 'info': '酒店位置优越，交通便利', 'type': 'hotel'},
            {'name': '拙政园', 'lat': 31.330214, 'lon': 120.635739, 'info': '中国四大名园之一，UNESCO世界文化遗产', 'type': 'day1'},
            {'name': '苏州博物馆', 'lat': 31.329108, 'lon': 120.634235, 'info': '由著名建筑师贝聿铭设计，藏品丰富', 'type': 'day1'},
            {
                'name': '平江历史文化街区', 
                'lat': 31.320661, 
                'lon': 120.639862, 
                'info': '保存完好的宋代街区，体现苏州古城风貌', 
                'type': 'day1',
                'nearby_places': {
                    '美食': [
                        {'name': '松鹤楼', 'desc': '百年老字号，苏州名点', 'lat': 31.321661, 'lon': 120.638862},
                        {'name': '东山沙锅面', 'desc': '传统苏州面食', 'lat': 31.320861, 'lon': 120.639962},
                        {'name': '平江路小吃', 'desc': '各类地道苏州小吃', 'lat': 31.320461, 'lon': 120.639762}
                    ],
                    '游玩': [
                        {'name': '平江路工艺品店', 'desc': '传统手工艺品', 'lat': 31.320561, 'lon': 120.639662},
                        {'name': '评弹博物馆', 'desc': '了解苏州评弹文化', 'lat': 31.320761, 'lon': 120.639562}
                    ]
                }
            }
        ],
        'color': 'blue',
        'description': '第一天主要游览苏州经典园林和历史文化街区，体验苏州的传统文化底蕴。'
    },
    'day2': {
        'name': '第二天行程',
        'points': [
            {'name': '维也纳国际酒店', 'lat': 31.339867, 'lon': 120.617061, 'info': '酒店位置优越，交通便利', 'type': 'hotel'},
            {'name': '留园', 'lat': 31.321718, 'lon': 120.598973, 'info': '以山水园林艺术著称，建筑精美绝伦', 'type': 'day2'},
            {'name': '寒山寺', 'lat': 31.316962, 'lon': 120.576878, 'info': '闻名于世的佛教古刹，枫桥夜泊胜地', 'type': 'day2'},
            {
                'name': '山塘街', 
                'lat': 31.323273, 
                'lon': 120.609658, 
                'info': '千年历史文化街区，古建筑保存完好', 
                'type': 'day2',
                'nearby_places': {
                    '美食': [
                        {'name': '山塘人家', 'desc': '传统苏帮菜', 'lat': 31.323373, 'lon': 120.609758},
                        {'name': '五芳斋', 'desc': '百年老字号，特色粽子', 'lat': 31.323173, 'lon': 120.609558},
                        {'name': '同得兴', 'desc': '传统面点', 'lat': 31.323073, 'lon': 120.609458}
                    ],
                    '游玩': [
                        {'name': '山塘古戏台', 'desc': '传统昆曲表演', 'lat': 31.323473, 'lon': 120.609858},
                        {'name': '江南丝绸博物馆', 'desc': '了解苏州丝绸文化', 'lat': 31.323573, 'lon': 120.609958}
                    ]
                }
            }
        ],
        'color': 'red',
        'description': '第二天游览苏州另一处著名园林和古街，感受不同风格的园林艺术和市井文化。'
    }
}

# 定义地点类型对应的颜色
POINT_COLORS = {
    'hotel': 'purple',
    'day1': 'blue',
    'day2': 'red'
}

def calculate_distance(lat1, lon1, lat2, lon2):
    """计算两点之间的距离（单位：米）"""
    R = 6371000  # 地球半径（米）
    
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi/2) * math.sin(delta_phi/2) + \
        math.cos(phi1) * math.cos(phi2) * \
        math.sin(delta_lambda/2) * math.sin(delta_lambda/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

    return R * c

def get_amap_url(start_point, end_point, waypoints=None):
    """生成高德地图导航链接"""
    base_url = "https://maps.amap.com/dir"
    
    # 起点和终点坐标需要调整格式
    start_coord = f"{start_point['lon']},{start_point['lat']}"
    end_coord = f"{end_point['lon']},{end_point['lat']}"
    
    # 使用正确的参数格式
    params = {
        'from[name]': start_point.get('name', '起点'),
        'from[lnglat]': start_coord,
        'to[name]': end_point.get('name', '终点'),
        'to[lnglat]': end_coord,
        'type': 'walk',  # 步行导航
        'policy': '0'    # 最优路线
    }
    
    # 使用urlencode编码参数
    query_string = urlencode(params, safe=',[]')
    return f"{base_url}?{query_string}"

def mcp_amap_maps_maps_direction_walking(origin, destination):
    """高德地图步行路线规划API"""
    try:
        base_url = "https://restapi.amap.com/v3/direction/walking"
        params = {
            'key': api_key,
            'origin': origin,
            'destination': destination,
            'output': 'json'
        }
        
        response = requests.get(base_url, params=params)
        result = response.json()
        
        if result.get('status') == '1':
            return result
        else:
            # 如果API调用失败，使用直线连接作为备选方案
            origin_lng, origin_lat = map(float, origin.split(','))
            dest_lng, dest_lat = map(float, destination.split(','))
            
            route_data = {
                'route': {
                    'paths': [{
                        'steps': [{
                            'polyline': f"{origin_lng},{origin_lat};{dest_lng},{dest_lat}"
                        }]
                    }]
                }
            }
            return route_data
    except Exception as e:
        st.warning(f"路线规划API调用失败: {str(e)}")
        return None

def draw_route_with_waypoints(m, start_point, end_point, waypoints, color):
    """绘制包含途经点的路线"""
    # 构建完整的路径点列表
    all_points = [[start_point['lat'], start_point['lon']]]
    all_points.extend(waypoints or [])
    all_points.append([end_point['lat'], end_point['lon']])
    
    # 用于跟踪是否已显示警告
    warning_shown = False
    
    # 绘制路线段
    for i in range(len(all_points) - 1):
        try:
            # 获取当前段的起点和终点
            curr_start = all_points[i]
            curr_end = all_points[i + 1]
            
            # 调用高德地图API获取路线规划
            result = mcp_amap_maps_maps_direction_walking(
                origin=f"{curr_start[1]},{curr_start[0]}",
                destination=f"{curr_end[1]},{curr_end[0]}"
            )
            
            if result and 'route' in result:
                route_data = result['route']
                if 'paths' in route_data and len(route_data['paths']) > 0:
                    path = route_data['paths'][0]
                    if 'steps' in path:
                        points_list = []
                        for step in path['steps']:
                            if 'polyline' in step:
                                coords = step['polyline'].split(';')
                                for coord in coords:
                                    lng, lat = map(float, coord.split(','))
                                    points_list.append([lat, lng])
                        
                        if points_list:
                            folium.PolyLine(
                                points_list,
                                weight=3,
                                color=color,
                                opacity=0.8
                            ).add_to(m)
        except Exception as e:
            # 只在第一次出现错误时显示警告
            if not warning_shown:
                st.warning("部分路线规划使用直线连接显示")
                warning_shown = True
            
            # 使用直线连接
            folium.PolyLine(
                [curr_start, curr_end],
                weight=2,
                color=color,
                opacity=0.5,
                dash_array='5,10'
            ).add_to(m)
    
    # 添加途经点标记
    for i, point in enumerate(waypoints or []):
        folium.CircleMarker(
            point,
            radius=6,
            color=color,
            fill=True,
            popup=f'途经点 {i+1}',
            tooltip='点击删除此途经点',
            className='waypoint-marker'
        ).add_to(m)
    
    # 添加高德地图链接
    amap_url = get_amap_url(start_point, end_point, waypoints)
    folium.Element(f"""
        <div style="position: absolute; bottom: 10px; left: 10px; z-index: 1000; background-color: white; padding: 10px; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.2);">
            <a href="{amap_url}" target="_blank" style="text-decoration: none; color: #333;">
                <img src="https://a.amap.com/jsapi_demos/static/demo-center/icons/amap-logo.png" style="height: 20px; vertical-align: middle; margin-right: 5px;">
                在高德地图中查看详细路线
            </a>
        </div>
    """).add_to(m)

def main():
    st.title("苏州两日游路线规划")
    
    # 初始化session state
    if 'manual_routes' not in st.session_state:
        st.session_state.manual_routes = {}
    if 'current_route' not in st.session_state:
        st.session_state.current_route = None
    if 'waypoints' not in st.session_state:
        st.session_state.waypoints = {}
    if 'planning_mode' not in st.session_state:
        st.session_state.planning_mode = False
    
    # 创建地图对象
    m = folium.Map(
        location=[31.330214, 120.617061],  # 苏州中心位置
        zoom_start=12,
        tiles="http://webrd02.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=7&x={x}&y={y}&z={z}",
        attr='高德地图'
    )
    
    # 添加手动路线规划控件
    col1, col2 = st.columns(2)
    with col1:
        if st.button("重新规划所有路线"):
            st.session_state.manual_routes = {}
            st.session_state.current_route = None
            st.session_state.waypoints = {}
            st.session_state.planning_mode = False
            st.rerun()
    
    with col2:
        enable_manual = st.checkbox("启用手动路线规划", key="enable_manual")
    
    if enable_manual:
        st.info("使用说明：\n1. 点击'开始规划'按钮选择要规划的路段\n2. 在地图上点击添加途经点\n3. 点击已添加的途经点可以删除它\n4. 点击'完成规划'保存路线")
    
    # 添加景点标记和路线
    for day_key, day_data in ROUTES.items():
        points = day_data['points']
        color = day_data['color']
        
        # 添加每天的路线
        for i in range(len(points) - 1):
            start_point = points[i]
            end_point = points[i + 1]
            route_key = f"{start_point['name']}-{end_point['name']}"
            
            # 如果启用手动规划
            if enable_manual:
                st.write(f"### {route_key}")
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    if st.button(f"开始规划", key=f"plan_{route_key}"):
                        st.session_state.current_route = route_key
                        st.session_state.planning_mode = True
                        if route_key not in st.session_state.waypoints:
                            st.session_state.waypoints[route_key] = []
                        st.rerun()
                
                with col2:
                    if st.button(f"完成规划", key=f"save_{route_key}"):
                        if route_key in st.session_state.waypoints:
                            st.session_state.manual_routes[route_key] = st.session_state.waypoints[route_key]
                            st.session_state.current_route = None
                            st.session_state.planning_mode = False
                            st.success("路线已保存")
                            st.rerun()
            
            # 显示路线
            try:
                if route_key in st.session_state.manual_routes:
                    # 显示手动规划的路线
                    draw_route_with_waypoints(
                        m, 
                        start_point, 
                        end_point, 
                        st.session_state.manual_routes[route_key],
                        color
                    )
                elif st.session_state.current_route == route_key and route_key in st.session_state.waypoints:
                    # 显示正在规划的路线
                    draw_route_with_waypoints(
                        m, 
                        start_point, 
                        end_point, 
                        st.session_state.waypoints[route_key],
                        color
                    )
                else:
                    # 使用默认路线
                    result = mcp_amap_maps_maps_direction_walking(
                        origin=f"{start_point['lon']},{start_point['lat']}",
                        destination=f"{end_point['lon']},{end_point['lat']}"
                    )
                    
                    if result and 'route' in result:
                        route_data = result['route']
                        if 'paths' in route_data and len(route_data['paths']) > 0:
                            path = route_data['paths'][0]
                            if 'steps' in path:
                                points_list = []
                                for step in path['steps']:
                                    if 'polyline' in step:
                                        coords = step['polyline'].split(';')
                                        for coord in coords:
                                            lng, lat = map(float, coord.split(','))
                                            points_list.append([lat, lng])
                                
                                if points_list:
                                    folium.PolyLine(
                                        points_list,
                                        weight=3,
                                        color=color,
                                        opacity=0.8
                                    ).add_to(m)
            except Exception as e:
                st.warning(f"路线规划失败: {str(e)}")
                # 使用直线连接作为备选
                folium.PolyLine(
                    [[start_point['lat'], start_point['lon']], 
                     [end_point['lat'], end_point['lon']]],
                    weight=2,
                    color=color,
                    opacity=0.5,
                    dash_array='5,10'
                ).add_to(m)
            
            # 添加景点标记
            marker_color = POINT_COLORS.get(start_point['type'], 'green')
            folium.Marker(
                [start_point['lat'], start_point['lon']],
                popup=folium.Popup(
                    f"<b>{start_point['name']}</b><br>{start_point['info']}",
                    max_width=300
                ),
                icon=folium.Icon(color=marker_color)
            ).add_to(m)
            
            if i == len(points) - 2:
                marker_color = POINT_COLORS.get(end_point['type'], 'green')
                folium.Marker(
                    [end_point['lat'], end_point['lon']],
                    popup=folium.Popup(
                        f"<b>{end_point['name']}</b><br>{end_point['info']}",
                        max_width=300
                    ),
                    icon=folium.Icon(color=marker_color)
                ).add_to(m)
    
    # 显示地图并获取点击事件
    map_data = st_folium(
        m,
        width=1200,
        height=600,
        key="map"
    )
    
    # 处理地图点击事件
    if map_data and map_data.get('last_clicked') and st.session_state.current_route:
        clicked_lat = map_data['last_clicked'].get('lat')
        clicked_lng = map_data['last_clicked'].get('lng')
        
        if clicked_lat is not None and clicked_lng is not None:
            # 检查是否点击了已有的途经点
            current_waypoints = st.session_state.waypoints.get(st.session_state.current_route, [])
            clicked_point = [clicked_lat, clicked_lng]
            
            # 检查是否点击了已有的途经点（允许一定的误差范围）
            tolerance = 0.0001  # 约10米的误差范围
            clicked_existing = False
            for i, point in enumerate(current_waypoints):
                if (abs(point[0] - clicked_lat) < tolerance and 
                    abs(point[1] - clicked_lng) < tolerance):
                    # 删除被点击的途经点
                    current_waypoints.pop(i)
                    clicked_existing = True
                    st.rerun()
                    break
            
            # 如果不是点击已有途经点，则添加新的途经点
            if not clicked_existing:
                current_waypoints.append(clicked_point)
                st.rerun()
    
    # 显示行程信息
    st.write("## 行程安排")
    for day_key, day_data in ROUTES.items():
        st.write(f"### {day_data['name']}")
        st.write(day_data['description'])
        points = day_data['points']
        
        for i in range(len(points) - 1):
            start_point = points[i]
            end_point = points[i + 1]
            route_key = f"{start_point['name']}-{end_point['name']}"
            
            # 获取该段路线的途经点
            waypoints = None
            if route_key in st.session_state.manual_routes:
                waypoints = st.session_state.manual_routes[route_key]
            
            # 生成高德地图链接
            amap_url = get_amap_url(start_point, end_point, waypoints)
            
            st.write(f"- **{start_point['name']} → {end_point['name']}**")
            st.write(f"  - {end_point['info']}")
            st.write(f"  - [在高德地图中查看详细路线]({amap_url})")
            
            # 如果是终点且有nearby_places信息，显示附近推荐
            if i == len(points) - 2 and 'nearby_places' in end_point:
                st.write(f"  - **{end_point['name']}附近推荐：**")
                for category, places in end_point['nearby_places'].items():
                    st.write(f"    - {category}：")
                    for place in places:
                        distance = calculate_distance(
                            end_point['lat'], end_point['lon'],
                            place['lat'], place['lon']
                        )
                        # 生成到推荐地点的导航链接
                        place_url = get_amap_url(
                            end_point,
                            {'name': place['name'], 'lat': place['lat'], 'lon': place['lon']}
                        )
                        st.write(f"      - [{place['name']}]({place_url}) ({place['desc']}) - 距离{end_point['name']}约{int(distance)}米")

if __name__ == "__main__":
    main() 