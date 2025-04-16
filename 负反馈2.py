import numpy as np
import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif'] = ['SimSun']  # 使用宋体显示中文

# ======================
# 核心参数配置（调试后可触发回调）
# ======================
params = {
    'X0': 0.1,  # 初始微生物浓度 (g/L)
    'S0': 30.0,  # 初始底物浓度 (g/L)
    'mu_max': 1.2,  # 最大生长速率 (1/h) ↑提高生长速度
    'K_s': 2.0,  # 半饱和常数 ↓降低底物需求
    'Y': 0.6,  # 转化率 ↑提高底物利用率
    'k_decay': 0.8,  # 衰减速率 (1/h) ↑加速衰减
    'threshold_speed': -0.3,  # 触发阈值 ↓更容易触发
    'total_time': 50,  # 总模拟时间
    'dt': 0.1,
    'noise_level': 0.02
}

# ======================
# 模拟初始化
# ======================
time_points = np.arange(0, params['total_time'], params['dt'])
n_steps = len(time_points)

X = np.zeros(n_steps)  # 微生物浓度
S = np.zeros(n_steps)  # 底物浓度
X[0] = params['X0']
S[0] = params['S0']

trigger_events = []  # 存储触发事件数据

# ======================
# 带回调机制的模拟循环
# ======================
for i in range(1, n_steps):
    prev_X = X[i - 1]
    prev_S = S[i - 1]

    # 阶段判断
    if prev_S > 1e-3:  # 生长阶段
        mu = params['mu_max'] * prev_S / (params['K_s'] + prev_S)
        dXdt = mu * prev_X
        dSdt = -dXdt / params['Y']
    else:  # 衰亡阶段
        dXdt = -params['k_decay'] * prev_X
        dSdt = 0.0

    # 触发回调检测（关键逻辑）
    if dXdt <= params['threshold_speed']:
        # 执行回调：补充底物并重置生长状态
        S[i - 1] = params['S0']  # 立即补充底物
        prev_S = params['S0']  # 更新当前步底物值

        # 重新计算生长速率
        mu = params['mu_max'] * prev_S / (params['K_s'] + prev_S)
        dXdt = mu * prev_X
        dSdt = -dXdt / params['Y']

        # 记录触发事件（时间，触发时浓度）
        trigger_events.append((time_points[i], prev_X))
        print(f"触发回调于 {time_points[i]:.1f} 小时，当前浓度：{prev_X:.3f}")

    # 更新状态
    X[i] = prev_X + dXdt * params['dt']
    S[i] = max(prev_S + dSdt * params['dt'], 0)

# ======================
# 可视化与输出
# ======================
# 添加噪声
X_obs = X + np.random.normal(0, params['noise_level'], n_steps)

plt.figure(figsize=(12, 6))
plt.plot(time_points, X_obs, 'b-', label='观测浓度', alpha=0.8)
plt.plot(time_points, X, 'k--', label='真实浓度', lw=1, alpha=0.6)

# 标注触发事件
if trigger_events:
    trigger_times, trigger_X = zip(*trigger_events)
    plt.scatter(trigger_times, trigger_X, c='r', s=100,
                edgecolor='white', label=f'触发事件 (阈值={params["threshold_speed"]})')

# 绘制底物浓度（次坐标轴）
ax2 = plt.gca().twinx()
ax2.plot(time_points, S, 'g--', alpha=0.4, label='底物浓度')
ax2.set_ylabel('底物浓度 (g/L)', color='g')
ax2.tick_params(axis='y', colors='g')

plt.title('微生物浓度动态变化\n带速度阈值触发的底物补充机制')
plt.xlabel('时间 (h)')
plt.ylabel('微生物浓度 (g/L)')
plt.legend(loc='upper left')
plt.grid(alpha=0.2)
plt.tight_layout()
plt.show()

# 输出触发统计
print(f"\n模拟结果统计：")
print(f"总触发次数：{len(trigger_events)}")
if trigger_events:
    print(f"首次触发时间：{trigger_events:.1f} h")
    print(f"最终浓度：{X[-1]:.3f} g/L")