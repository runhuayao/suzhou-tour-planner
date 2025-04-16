import numpy as np
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']  # 微软雅黑
# 或 ['SimSun'] 宋体 / ['KaiTi'] 楷体
# ----------------------------
# 模型参数设置
# ----------------------------
threshold_speed = -0.5  # 触发阈值
total_time = 50  # 总模拟时间 (小时)
dt = 0.1  # 时间步长
noise_level = 0.02  # 噪声水平

# 初始条件与动力学参数（示例值，可根据需要调整）
X0 = 0.1  # 初始微生物浓度 (g/L)
S0 = 1.0  # 初始底物浓度 (g/L)
mu_max = 0.4  # 最大生长速率 (1/h)
K_s = 0.5  # 底物半饱和常数 (g/L)
Y = 0.5  # 转化率
k_decay = 0.1  # 衰减速率 (1/h)

# ----------------------------
# 时间离散化
# ----------------------------
time_points = np.arange(0, total_time, dt)
n_steps = len(time_points)

# ----------------------------
# 正确初始化数组（关键修正点）
# ----------------------------
X = np.zeros(n_steps)  # 微生物浓度数组
S = np.zeros(n_steps)  # 底物浓度数组
X[0] = X0  # 设置初始微生物浓度
S[0] = S0  # 设置初始底物浓度

trigger_points = []  # 存储触发补充底物的时间点和浓度

# ----------------------------
# 模拟主循环
# ----------------------------
for i in range(1, n_steps):
    prev_X = X[i - 1]
    prev_S = S[i - 1]

    # 判断是否处于生长阶段
    if prev_S > 1e-3:  # 添加微小阈值避免浮点误差
        mu = mu_max * prev_S / (K_s + prev_S)
        dXdt = mu * prev_X
        dSdt = -dXdt / Y
    else:
        dXdt = -k_decay * prev_X
        dSdt = 0.0

    # 检查是否满足触发条件
    if dXdt <= threshold_speed:
        # 补充底物：更新上一时刻的底物浓度，并重新计算生长速率
        S[i - 1] = S0
        prev_S = S0
        mu = mu_max * prev_S / (K_s + prev_S)
        dXdt = mu * prev_X
        dSdt = -dXdt / Y
        trigger_points.append((time_points[i], prev_X))

    # 更新微生物和底物浓度
    X[i] = prev_X + dXdt * dt
    S[i] = max(prev_S + dSdt * dt, 0)  # 保证底物浓度不为负

# ----------------------------
# 添加噪声，模拟观测数据
# ----------------------------
X_noisy = X + np.random.normal(0, noise_level, n_steps)

# ----------------------------
# 结果可视化
# ----------------------------
plt.figure(figsize=(10, 6))
plt.plot(time_points, X_noisy, label='观测浓度', alpha=0.8)
plt.plot(time_points, X, 'k--', label='理论浓度', alpha=0.5)

# 标记触发点
if trigger_points:
    t_trigger, X_trigger = zip(*trigger_points)
    plt.scatter(t_trigger, X_trigger, c='red', s=80, edgecolor='white',
                label=f'触发点 (阈值={threshold_speed})')

plt.title('微生物浓度动态模拟')
plt.xlabel('时间 (h)')
plt.ylabel('浓度 (g/L)')
plt.legend()
plt.grid(alpha=0.3)
plt.show()
