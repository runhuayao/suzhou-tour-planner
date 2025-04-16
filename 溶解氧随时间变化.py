import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']  # 微软雅黑
# 或 ['SimSun'] 宋体 / ['KaiTi'] 楷体
# ================== 可调节参数 ==================
base_file = "D:\\HuaweiMoveData\\Users\\11346\\Desktop\\溶解氧随随时间发生的变化.csv"  # 替换为实际文件路径
noise_level = 0.2    # 噪音幅度 (±5%)
scaling_factors = {   # 各区比例系数
    '过氧区': 1.5,    # DO8 (8/5=1.6)
    '低氧区': 0.4     # DO2 (2/5=0.4)
}
# ================================================

# 读取真实过渡区数据
df = pd.read_csv(base_file)

# 生成模拟数据
np.random.seed(42)  # 固定随机种子保证可重复性
for zone, factor in scaling_factors.items():
    base_values = df['过渡区'].values
    noise = np.random.uniform(-noise_level, noise_level, size=len(base_values))
    df[zone] = base_values * factor * (1 + noise)

# 可视化配置
plt.figure(figsize=(10,6))
colors = {'过氧区':'#FF4500', '过渡区':'#32CD32', '低氧区':'#1E90FF'}
linestyles = {'过氧区':'-', '过渡区':'--', '低氧区':'-'}

# 绘制三条曲线
for column in df.columns[1:]:
    plt.plot(df['时间'], df[column],
             label=f"{column} " if column != '过渡区' else '过渡区',
             color=colors[column],
             linestyle=linestyles[column],
             linewidth=2)

# 图表美化
plt.title('溶解氧动态变化趋势', pad=20, fontsize=14)
plt.xlabel('时间 (分钟)', fontsize=12)
plt.ylabel('溶解氧浓度 (mg/L)', fontsize=12)
plt.legend(frameon=False, loc='upper right')
plt.grid(True, alpha=0.3, linestyle=':')
plt.xticks(rotation=45)
plt.tight_layout()

# 保存数据文件
df.to_csv("生成数据_带噪音.csv", index=False)
plt.show()