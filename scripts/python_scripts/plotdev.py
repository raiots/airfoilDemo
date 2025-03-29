import re
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

def parse_residuals(log_file):
    # 只存储时间步和Ux残差值
    data = {
        'step': [],
        'Ux_residual': [],
    }
    
    current_step = 0
    
    with open(log_file, 'r') as f:
        for line in f:
            # 检查是否是新的时间步
            if line.startswith('Time = '):
                current_step = float(line.split('=')[1].strip())
                
            # 只提取Ux残差
            if 'Solving for Ux' in line:
                match = re.search(r'Initial residual = ([0-9.e-]+)', line)
                if match:
                    data['step'].append(current_step)
                    data['Ux_residual'].append(float(match.group(1)))

    return pd.DataFrame(data)

def plot_residuals(dfs, output_filename='Ux_residual.png', labels=None):
    # 设置绘图风格
    sns.set_style("whitegrid")
    plt.figure(figsize=(10, 6))
    
    # 如果传入的是单个DataFrame，转换为列表
    if isinstance(dfs, pd.DataFrame):
        dfs = [dfs]
    if labels is None:
        labels = [f'Case {i+1}' for i in range(len(dfs))]
    
    # 绘制每个算例的残差曲线
    for df, label in zip(dfs, labels):
        sns.lineplot(data=df, x='step', y='Ux_residual', label=label)
    
    # 设置y轴为对数刻度
    plt.yscale('log')
    
    # 设置标题和标签
    plt.title('Ux Residual vs Time Step')
    plt.xlabel('Time Step')
    plt.ylabel('Residual')
    
    # 添加图例
    plt.legend()
    
    # 保存图片
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    plt.close()

if __name__ == '__main__':
    # 读取并解析log文件
    df = parse_residuals('sims/log.simpleFoam')
    # 绘制残差图
    plot_residuals(df)