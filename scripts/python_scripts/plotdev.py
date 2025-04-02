import re
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

def parse_residuals(log_file):
    # 存储时间步和多种残差值
    data = {
        'step': [],
        'Ux_residual': [],
        'Uy_residual': [],
        'p_residual': [],
    }
    
    current_step = 0
    
    with open(log_file, 'r') as f:
        for line in f:
            # 检查是否是新的时间步
            if line.startswith('Time = '):
                current_step = float(line.split('=')[1].strip())
                
            # 提取Ux残差
            if 'Solving for Ux' in line:
                match = re.search(r'Initial residual = ([0-9.e-]+)', line)
                if match:
                    data['step'].append(current_step)
                    data['Ux_residual'].append(float(match.group(1)))
            
            # 提取Uy残差
            elif 'Solving for Uy' in line:
                match = re.search(r'Initial residual = ([0-9.e-]+)', line)
                if match:
                    # 确保已经有相同数量的step记录
                    if len(data['step']) > len(data['Uy_residual']):
                        data['Uy_residual'].append(float(match.group(1)))
            
            # 提取p残差
            elif 'Solving for p' in line:
                match = re.search(r'Initial residual = ([0-9.e-]+)', line)
                if match:
                    # 确保已经有相同数量的step记录
                    if len(data['step']) > len(data['p_residual']):
                        data['p_residual'].append(float(match.group(1)))

    # 确保所有列表长度一致（补充缺失值）
    max_len = len(data['step'])
    for key in data:
        if len(data[key]) < max_len:
            data[key].extend([None] * (max_len - len(data[key])))

    return pd.DataFrame(data)

def plot_residuals(dfs, output_filename='Ux_residual.png', labels=None, residual_type='Ux_residual'):
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
        if residual_type in df.columns:
            sns.lineplot(data=df, x='step', y=residual_type, label=label)
    
    # 设置y轴为对数刻度
    plt.yscale('log')
    
    # 设置标题和标签
    title_map = {
        'Ux_residual': 'Ux Residual vs Time Step',
        'Uy_residual': 'Uy Residual vs Time Step',
        'p_residual': 'p Residual vs Time Step'
    }
    
    plt.title(title_map.get(residual_type, f'{residual_type} vs Time Step'))
    plt.xlabel('Time Step')
    plt.ylabel('Residual')
    
    # 添加图例
    plt.legend()
    
    # 保存图片
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    plt.close()

def parse_forces(force_file):
    """解析力数据文件
    
    Args:
        force_file (str): 力数据文件的路径
        
    Returns:
        pd.DataFrame: 包含时间步、总力x、总力y数据的DataFrame
    """
    data = {
        'time': [],
        'force_x': [],
        'force_y': []
    }
    
    with open(force_file, 'r') as f:
        for line in f:
            # 跳过注释行
            if line.startswith('#'):
                continue
            
            # 解析数据行
            values = line.strip().split()
            if len(values) >= 4:  # 确保有足够的列
                time = float(values[0])
                force_x = float(values[1])
                force_y = float(values[2])
                
                data['time'].append(time)
                data['force_x'].append(force_x)
                data['force_y'].append(force_y)
    
    return pd.DataFrame(data)

def plot_forces(dfs, output_filename='forces.png', labels=None, force_type='force_x'):
    """绘制力数据
    
    Args:
        dfs: 单个DataFrame或DataFrame列表，包含力数据
        output_filename (str): 输出图片文件名
        labels (list): 每个数据集的标签
        force_type (str): 要绘制的力类型 ('force_x' 或 'force_y')
    """
    # 设置绘图风格
    sns.set_style("whitegrid")
    plt.figure(figsize=(10, 6))
    
    # 如果传入的是单个DataFrame，转换为列表
    if isinstance(dfs, pd.DataFrame):
        dfs = [dfs]
    if labels is None:
        labels = [f'Case {i+1}' for i in range(len(dfs))]
    
    # 绘制每个算例的力曲线
    for df, label in zip(dfs, labels):
        if force_type in df.columns:
            sns.lineplot(data=df, x='time', y=force_type, label=label)
    
    # 设置标题和标签
    title_map = {
        'force_x': '力的X分量随时间变化',
        'force_y': '力的Y分量随时间变化'
    }
    
    plt.title(title_map.get(force_type, f'{force_type} vs Time'))
    plt.xlabel('时间 (s)')
    plt.ylabel('力 (N)')
    
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