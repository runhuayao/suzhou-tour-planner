# -*- coding: utf-8 -*-
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

# 设置中文字体（Windows下一般可用 SimHei 或 Microsoft YaHei）
matplotlib.rcParams['font.sans-serif'] = ['SimHei']
# 防止负号显示成方块
matplotlib.rcParams['axes.unicode_minus'] = False

# 设置随机种子保证可重复性
np.random.seed(42)

# 参数配置
DO_initial = 8.0    # 初始溶解氧浓度 (mg/L)
DO_steady = 2.0     # 稳态溶解氧浓度 (mg/L)
K = 20.0            # 半饱和常数
num_points = 100    # 数据点数量
t_max = 100         # 最大时间（单位可根据实际情况调整）

# 生成时间序列
t = np.linspace(0, t_max, num_points)

# 生成Monod趋势曲线
DO_sim_trend = (DO_initial - DO_steady) * (t / (K + t)) + DO_steady

# 生成模拟数据（带小波动）
sim_noise = np.random.normal(0, 0.05, num_points)  # 模拟数据噪声
DO_sim = DO_sim_trend + sim_noise

# 生成测量数据（带较大噪声）
meas_noise_rel = np.random.normal(0, 0.08, num_points)  # 8%相对噪声
DO_meas = DO_sim_trend * (1 + meas_noise_rel)

# 计算残差
residuals = DO_meas - DO_sim

# 计算符合10%阈值的比例
threshold = 0.1  # 10%临界值
within_threshold = np.abs(residuals) <= threshold * np.abs(DO_sim)
percentage_within = np.mean(within_threshold) * 100

# 可视化结果
plt.figure(figsize=(14, 10))

# 主趋势对比图
plt.subplot(2, 2, 1)
plt.plot(t, DO_sim, label='模拟数据', color='blue', alpha=0.7)
plt.scatter(t, DO_meas, label='测量数据', color='red', s=15, alpha=0.7)
plt.xlabel('时间 (单位自定)')
plt.ylabel('溶解氧浓度 (mg/L)')
plt.title('模拟数据与测量数据对比')
plt.legend()
plt.grid(True)

# 残差时间序列
plt.subplot(2, 2, 2)
plt.scatter(t, residuals, s=15, color='green', alpha=0.7)
plt.axhline(0, color='black', linestyle='--')
plt.xlabel('时间 (单位自定)')
plt.ylabel('残差 (mg/L)')
plt.title('残差时间分布')
plt.grid(True)

# 残差分布直方图
plt.subplot(2, 2, 3)
plt.hist(residuals, bins=20, color='purple', alpha=0.7)
plt.xlabel('残差 (mg/L)')
plt.ylabel('频数')
plt.title('残差分布直方图')
plt.grid(True)

# 统计信息展示
plt.subplot(2, 2, 4)
plt.axis('off')
plt.text(0.1, 0.8, f'残差分析结果：\n\n'
                  f'• {percentage_within:.1f}% 残差在±10%范围内\n'
                  f'• 最大正残差：{residuals.max():.2f} mg/L\n'
                  f'• 最大负残差：{residuals.min():.2f} mg/L\n'
                  f'• 平均绝对误差：{np.mean(np.abs(residuals)):.2f} mg/L',
         fontsize=12, va='top')

plt.tight_layout()
plt.show()
