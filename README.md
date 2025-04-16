# 苏州两日游行程规划

基于 Streamlit 和高德地图 API 开发的旅游规划工具。

## 功能特点
                                                                                          
- 苏州景点地图展示
- ![image](https://github.com/user-attachments/assets/1f8138c7-840d-460c-ae09-4047cf2a2164)
- 智能路线规划
- ![image](https://github.com/user-attachments/assets/0bb9a0c0-9e1b-4ba5-b141-77106bf57d5f)

- 实时路况查看（需要企业级开发权限，个人开发权限目前只能文字描述形势）
- 多种地图视图切换(不稳定删了)
- 手动路线调整（当实时规划路径给不了的时候[权限不够]会直接给个直线路径，跟上图一样，但是提供了个可以自改改路线的权限）
- 
- 路线刷新功能

## 如何使用

1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 运行应用：
```bash
streamlit run suzhou_tour_map.py
```

3. 使用功能：
- 选择地图类型（2D地图、路线规划图、实时路况图）
- 使用"刷新路线规划"按钮更新路线
- 通过"手动调整路线"自定义行程
- 查看实时路况信息

## 技术栈

- Python
- Streamlit
- 高德地图 API
- Folium
## 问题
-出现问题都是你的问题，俺不会承认的（傲娇），可以邮箱讨论
