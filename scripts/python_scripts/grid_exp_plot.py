import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import re
import seaborn as sns
from matplotlib.lines import Line2D

# 设置 seaborn 样式
sns.set_theme(style="whitegrid")

# 读取CSV文件
df = pd.read_csv('scripts/python_scripts/grid_exp_coefficients.csv')
print(f"读取到的数据：\n{df}")

# 提取文件名中p后面的数值
def extract_p_value(filename):
    match = re.search(r'p(\d+)', filename)
    if match:
        return int(match.group(1))
    return None

# 计算误差（与0.01201的差值），以百分比表示
reference_value = 1.0707
df['误差百分比'] = abs(df['系数值'] - reference_value) / reference_value * 100

# 提取p值并添加到DataFrame
df['p值'] = df['文件名'].apply(extract_p_value)

# 按p值排序
df = df.sort_values('p值')

# 计算核时间 (Runtime x 4)
df['核时间'] = df['运行时间(秒)'] * 4

# 创建图表
fig, ax1 = plt.subplots(figsize=(10, 6))

# 设置第一个Y轴（误差百分比）
color = 'tab:blue'
ax1.set_xlabel('Number of Grid Points')
ax1.set_ylabel('Error of Cl (%)', color=color)
sns.lineplot(x='p值', y='误差百分比', data=df, marker='o', color=color, ax=ax1, label='Error of Cl')
ax1.tick_params(axis='y', labelcolor=color)

# 创建第二个Y轴（核时间）
ax2 = ax1.twinx()
color = 'tab:red'
ax2.set_ylabel('Core Hours (seconds)', color=color)
sns.lineplot(x='p值', y='核时间', data=df, marker='s', color=color, ax=ax2, label='Core Hours')
ax2.tick_params(axis='y', labelcolor=color)

# 添加标题和图例
plt.title('Relationship between Grid Points, Error of Cl(%) and Core Hours')

# 修复图例问题
# 清除自动生成的图例
ax1.get_legend().remove() if ax1.get_legend() else None
ax2.get_legend().remove() if ax2.get_legend() else None

# 手动创建图例元素
legend_elements = [
    Line2D([0], [0], color='tab:blue', marker='o', linestyle='-', label='Error of Cl'),
    Line2D([0], [0], color='tab:red', marker='s', linestyle='-', label='Core Hours')
]

# 添加手动创建的图例
ax1.legend(handles=legend_elements, loc='upper left')

# 设置网格样式 (seaborn已经添加了网格线，但可以自定义)
ax1.grid(True, linestyle='--', alpha=0.7)

# 显示图表
plt.tight_layout()
plt.savefig('Error_and_RunTime_Comparison.png', dpi=300)
plt.show()

print("图表已保存为'Error_and_RunTime_Comparison.png'")