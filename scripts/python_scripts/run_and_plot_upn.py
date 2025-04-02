import os
from pathlib import Path
import subprocess
import time
import matplotlib.pyplot as plt
import numpy as np
from foamlib import FoamCase
import csv

def run_mesh_commands(p3d_file):
    """运行网格处理相关命令
    
    Args:
        p3d_file (str): p3d文件的名称
    """
    commands = [
        "cd ../../sims",
        f"plot3dToFoam ../grids/grid_exp/{p3d_file} -2D 1 -singleBlock -noBlank",
        "autoPatch 45 -overwrite",
        "createPatch -overwrite",
        "transformPoints -rotate-angle '((0 0 1) -10)'"
    ]
    
    combined_command = " && ".join(commands)
    subprocess.run(combined_command, shell=True, check=True)

def extract_coefficient():
    """提取系数文件最后一行的值
    
    Returns:
        float: 提取的系数值，如果提取失败则返回None
    """
    coeff_file = '../../sims/postProcessing/forceCoeffs/0/coefficient_0.dat'
    if not os.path.exists(coeff_file):
        print(f"警告：无法找到系数文件 {coeff_file}")
        return None
    
    try:
        with open(coeff_file, 'r') as f:
            lines = f.readlines()
            # 过滤掉注释行和空行
            data_lines = [line for line in lines if line.strip() and not line.startswith('#')]
            if data_lines:
                # 获取最后一行数据并分割
                last_line = data_lines[-1]
                values = last_line.split()
                if len(values) >= 5:  # 确保有足够的列
                    coefficient = float(values[4])  # 提取Cd值
                    return coefficient
                else:
                    print(f"警告：系数行格式不正确: {last_line}")
            else:
                print(f"警告：系数文件无数据")
    except Exception as e:
        print(f"提取系数时出错: {e}")
    
    return None

def extract_residuals():
    """提取求解器的残差数据用于稳定性分析
    
    Returns:
        dict: 包含各个变量残差数据的字典，如果提取失败则返回None
    """
    residual_file = '../../sims/log.simpleFoam'
    residuals = {'时间步': [], 'U_x': [], 'U_y': [], 'p': [], 'nuTilda': []}
    
    if not os.path.exists(residual_file):
        print(f"警告：无法找到残差文件 {residual_file}")
        return residuals  # 返回空的残差数据结构而非None
    
    try:
        # 尝试导入并使用plotdev模块
        try:
            from plotdev import parse_residuals
            df = parse_residuals(residual_file)
            
            # 转换为我们的格式
            if not df.empty:
                residuals['时间步'] = df.index.tolist()
                
                if 'Ux_residual' in df.columns:
                    residuals['U_x'] = df['Ux_residual'].tolist()
                
                if 'Uy_residual' in df.columns:
                    residuals['U_y'] = df['Uy_residual'].tolist()
                
                if 'p_residual' in df.columns:
                    residuals['p'] = df['p_residual'].tolist()
                
                if 'nuTilda_residual' in df.columns:
                    residuals['nuTilda'] = df['nuTilda_residual'].tolist()
                
                return residuals
            
        except (ImportError, Exception) as e:
            print(f"使用plotdev模块提取残差失败: {e}")
            print("将使用备用方法提取残差...")
        
        # 备用方法：直接从日志文件解析
        with open(residual_file, 'r') as f:
            lines = f.readlines()
            time_step = 0
            
            # 初始化变量来追踪已找到的各种残差
            found_ux = False
            found_uy = False
            found_p = False
            found_nut = False
            
            for line in lines:
                # 添加更详细的调试信息
                # if "residual" in line:
                #    print(f"DEBUG - 分析行: {line.strip()}")
                
                if "Solving for Ux" in line and "Initial residual" in line:
                    time_step += 1
                    residuals['时间步'].append(time_step)
                    
                    try:
                        ux_res = float(line.split("Initial residual = ")[1].split(',')[0])
                        residuals['U_x'].append(ux_res)
                        found_ux = True
                    except Exception as e:
                        print(f"解析Ux残差行时出错: {e} - 行: {line}")
                        # 如果解析失败，填充一个前一个值或0
                        residuals['U_x'].append(residuals['U_x'][-1] if residuals['U_x'] else 0.0)
                
                if "Solving for Uy" in line and "Initial residual" in line:
                    try:
                        uy_res = float(line.split("Initial residual = ")[1].split(',')[0])
                        # 确保列表长度一致
                        while len(residuals['U_y']) < len(residuals['时间步']) - 1:
                            residuals['U_y'].append(0.0)  # 填充缺失的值
                        residuals['U_y'].append(uy_res)
                        found_uy = True
                    except Exception as e:
                        print(f"解析Uy残差行时出错: {e} - 行: {line}")
                        # 如果解析失败，填充一个前一个值或0
                        residuals['U_y'].append(residuals['U_y'][-1] if residuals['U_y'] else 0.0)
                
                if "Solving for p" in line and "Initial residual" in line:
                    try:
                        p_res = float(line.split("Initial residual = ")[1].split(',')[0])
                        # 确保列表长度一致
                        while len(residuals['p']) < len(residuals['时间步']) - 1:
                            residuals['p'].append(0.0)  # 填充缺失的值
                        residuals['p'].append(p_res)
                        found_p = True
                    except Exception as e:
                        print(f"解析p残差行时出错: {e} - 行: {line}")
                        # 如果解析失败，填充一个前一个值或0
                        residuals['p'].append(residuals['p'][-1] if residuals['p'] else 0.0)
                
                if "Solving for nuTilda" in line and "Initial residual" in line:
                    try:
                        nut_res = float(line.split("Initial residual = ")[1].split(',')[0])
                        # 确保列表长度一致
                        while len(residuals['nuTilda']) < len(residuals['时间步']) - 1:
                            residuals['nuTilda'].append(0.0)  # 填充缺失的值
                        residuals['nuTilda'].append(nut_res)
                        found_nut = True
                    except Exception as e:
                        print(f"解析nuTilda残差行时出错: {e} - 行: {line}")
                        # 如果解析失败，填充一个前一个值或0
                        residuals['nuTilda'].append(residuals['nuTilda'][-1] if residuals['nuTilda'] else 0.0)
            
            # 确保所有列表长度一致
            max_len = len(residuals['时间步'])
            
            # 打印残差查找状态
            print(f"残差提取状态: Ux={found_ux}, Uy={found_uy}, p={found_p}, nuTilda={found_nut}")
            print(f"提取的数据长度: 时间步={len(residuals['时间步'])}, U_x={len(residuals['U_x'])}, " +
                  f"U_y={len(residuals['U_y'])}, p={len(residuals['p'])}, nuTilda={len(residuals['nuTilda'])}")
            
            # 确保所有列表长度一致
            for key in ['U_x', 'U_y', 'p', 'nuTilda']:
                # 如果没有找到某种残差，创建一个相同长度的零列表
                if len(residuals[key]) == 0 and max_len > 0:
                    print(f"警告: 没有找到{key}残差数据，用零填充")
                    residuals[key] = [0.0] * max_len
                
                # 填充可能缺失的值
                while len(residuals[key]) < max_len:
                    residuals[key].append(residuals[key][-1] if residuals[key] else 0.0)
                
                # 截断多余的值
                residuals[key] = residuals[key][:max_len]
            
        return residuals
    
    except Exception as e:
        print(f"提取残差时出错: {e}")
        # 返回空的残差数据结构而非None
        return residuals

def run_case_with_relaxation_factors(p3d_file, case_name, u_factor, p_factor, nut_factor):
    """运行一个带有特定松弛因子的算例
    
    Args:
        p3d_file (str): 网格文件名
        case_name (str): 算例名称
        u_factor (float): U方程的松弛因子
        p_factor (float): p方程的松弛因子
        nut_factor (float): nuTilda方程的松弛因子
    
    Returns:
        tuple: (运行时间, 系数值, 残差数据)
    """
    print(f"\n正在运行算例: {case_name}")
    print(f"松弛因子设置: U={u_factor}, p={p_factor}, nuTilda={nut_factor}")
    
    # 1. 运行网格处理命令
    print("正在处理网格...")
    run_mesh_commands(p3d_file)
    
    # 2. 设置松弛因子并运行算例
    case = FoamCase(Path("../../sims"))
    
    # 设置松弛因子
    case.fv_solution['relaxationFactors']['equations']['U'] = u_factor
    case.fv_solution['relaxationFactors']['equations']['p'] = p_factor
    case.fv_solution['relaxationFactors']['equations']['nuTilda'] = nut_factor
    
    # 保存设置更改
    # case.fv_solution.save()
    
    # 清理并运行算例
    case.clean()
    
    print("正在运行算例...")
    start_time = time.time()
    case.run()
    run_time = time.time() - start_time
    
    # 运行时间乘以4，按照要求
    adjusted_run_time = run_time * 4
    print(f"算例运行时间: {run_time:.2f}秒 (调整后: {adjusted_run_time:.2f}秒)")
    
    # 3. 提取系数数据和残差数据
    coefficient = extract_coefficient()
    residuals = extract_residuals()
    
    return adjusted_run_time, coefficient, residuals

def plot_results(results):
    """绘制结果图表并分别保存
    
    Args:
        results (list): 包含各算例结果的列表
    """
    # 1. 绘制计算时间柱状图
    fig1, ax1 = plt.subplots(figsize=(10, 6))
    
    # 提取数据
    case_names = [result['算例名称'] for result in results]
    case_names_eng = ["Default", "All 0.9", "All 0.3"]  # 英文名称
    run_times = [result['运行时间'] for result in results]
    
    # 绘制运行时间柱状图
    bar_width = 0.35
    x = np.arange(len(case_names))
    
    time_bars = ax1.bar(x, run_times, bar_width, label='Computation Time')
    ax1.set_xlabel('Relaxation Factor Settings')
    ax1.set_ylabel('Computation Time (s)')
    ax1.set_title('Comparison of Computation Time for Different Relaxation Factors')
    ax1.set_xticks(x)
    ax1.set_xticklabels(case_names_eng)
    
    # 在柱状图上添加数值标签
    for bar in time_bars:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                f'{height:.2f}', ha='center', va='bottom')
    
    plt.tight_layout()
    plt.savefig('computation_time_comparison.png', dpi=300)
    print("计算时间对比图已保存为 'computation_time_comparison.png'")
    plt.close(fig1)
    
    # 2. 绘制p残差收敛图
    fig2, ax2 = plt.subplots(figsize=(10, 6))
    
    valid_p_data = False
    for i, result in enumerate(results):
        if result['残差数据'] and 'p' in result['残差数据'] and len(result['残差数据']['p']) > 0:
            # 确保时间步和残差数据有相同的长度
            time_steps = result['残差数据']['时间步']
            p_residuals = result['残差数据']['p']
            
            # 确保两者长度相同
            min_len = min(len(time_steps), len(p_residuals))
            if min_len > 0:
                ax2.semilogy(time_steps[:min_len], p_residuals[:min_len], 
                            label=f"{case_names_eng[i]}")
                valid_p_data = True
    
    if valid_p_data:
        ax2.set_xlabel('Time Step')
        ax2.set_ylabel('Initial Residual (log scale)')
        ax2.set_title('Convergence of p Equation Residuals for Different Relaxation Factors')
        ax2.legend()
        ax2.grid(True, which="both", ls="-")
    else:
        ax2.text(0.5, 0.5, 'No valid p residual data available', 
                 ha='center', va='center', transform=ax2.transAxes)
    
    plt.tight_layout()
    plt.savefig('p_residual_comparison.png', dpi=300)
    print("p残差对比图已保存为 'p_residual_comparison.png'")
    plt.close(fig2)
    
    # 3. 分别绘制各个残差变量的图表
    variables = ['U_x', 'U_y', 'p', 'nuTilda']
    titles = ['U_x Equation Residual', 'U_y Equation Residual', 
              'p Equation Residual', 'nuTilda Equation Residual']
    filenames = ['Ux_residual_comparison.png', 'Uy_residual_comparison.png', 
                'p_residual_comparison.png', 'nuTilda_residual_comparison.png']
    
    for var, title, filename in zip(variables, titles, filenames):
        fig, ax = plt.subplots(figsize=(10, 6))
        valid_data = False
        
        for i, result in enumerate(results):
            if (result['残差数据'] and var in result['残差数据'] and 
                len(result['残差数据'][var]) > 0 and len(result['残差数据']['时间步']) > 0):
                
                # 确保两者长度相同
                time_steps = result['残差数据']['时间步']
                var_residuals = result['残差数据'][var]
                
                min_len = min(len(time_steps), len(var_residuals))
                if min_len > 0:
                    ax.semilogy(time_steps[:min_len], var_residuals[:min_len], 
                                label=f"{case_names_eng[i]}")
                    valid_data = True
        
        ax.set_xlabel('Time Step')
        ax.set_ylabel('Initial Residual (log scale)')
        ax.set_title(title)
        
        if valid_data:
            ax.legend()
            ax.grid(True, which="both", ls="-")
        else:
            ax.text(0.5, 0.5, f'No valid {var} residual data available', 
                    ha='center', va='center', transform=ax.transAxes)
        
        plt.tight_layout()
        plt.savefig(filename, dpi=300)
        print(f"{var}残差对比图已保存为 '{filename}'")
        plt.close(fig)

def save_results_to_csv(results):
    """将结果保存到CSV文件，包括最后一次迭代的残差
    
    Args:
        results (list): 包含各算例结果的列表
    """
    csv_file = 'relaxation_factors_comparison.csv'
    with open(csv_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            'Case Name', 'U Factor', 'p Factor', 'nuTilda Factor', 
            'Computation Time (s)', 'Coefficient Value',
            'Final U_x Residual', 'Final U_y Residual', 'Final p Residual', 'Final nuTilda Residual'
        ])
        
        for result in results:
            # 获取最后一次迭代的残差值
            final_ux_res = 'N/A'
            final_uy_res = 'N/A'
            final_p_res = 'N/A'
            final_nut_res = 'N/A'
            
            if result['残差数据']:
                if 'U_x' in result['残差数据'] and len(result['残差数据']['U_x']) > 0:
                    final_ux_res = result['残差数据']['U_x'][-1]
                
                if 'U_y' in result['残差数据'] and len(result['残差数据']['U_y']) > 0:
                    final_uy_res = result['残差数据']['U_y'][-1]
                
                if 'p' in result['残差数据'] and len(result['残差数据']['p']) > 0:
                    final_p_res = result['残差数据']['p'][-1]
                
                if 'nuTilda' in result['残差数据'] and len(result['残差数据']['nuTilda']) > 0:
                    final_nut_res = result['残差数据']['nuTilda'][-1]
            
            writer.writerow([
                result['算例名称'],
                result['松弛因子']['U'],
                result['松弛因子']['p'],
                result['松弛因子']['nuTilda'],
                f"{result['运行时间']:.2f}",
                result['系数值'] if result['系数值'] is not None else 'N/A',
                f"{final_ux_res:.8e}" if isinstance(final_ux_res, float) else final_ux_res,
                f"{final_uy_res:.8e}" if isinstance(final_uy_res, float) else final_uy_res,
                f"{final_p_res:.8e}" if isinstance(final_p_res, float) else final_p_res,
                f"{final_nut_res:.8e}" if isinstance(final_nut_res, float) else final_nut_res
            ])
    
    print(f"结果数据已保存到 '{csv_file}'")

def main():
    p3d_file = "naca0012_c10_p34551.p3d"
    
    # 定义三种松弛因子配置
    relaxation_configs = [
        {
            "name": "默认设置",
            "U": 0.7,
            "p": 0.3,
            "nuTilda": 0.9
        },
        {
            "name": "全部0.9",
            "U": 0.9,
            "p": 0.9,
            "nuTilda": 0.9
        },
        {
            "name": "全部0.3",
            "U": 0.3,
            "p": 0.3,
            "nuTilda": 0.3
        }
    ]
    
    # 运行所有配置并收集结果
    results = []
    
    for config in relaxation_configs:
        run_time, coefficient, residuals = run_case_with_relaxation_factors(
            p3d_file,
            config["name"],
            config["U"],
            config["p"],
            config["nuTilda"]
        )
        
        results.append({
            "算例名称": config["name"],
            "松弛因子": {
                "U": config["U"],
                "p": config["p"],
                "nuTilda": config["nuTilda"]
            },
            "运行时间": run_time,
            "系数值": coefficient,
            "残差数据": residuals
        })
    
    # 保存结果到CSV
    save_results_to_csv(results)
    
    # 绘制结果图表
    plot_results(results)
    
    print("\n所有算例运行完成！结果已保存为CSV文件和图表。")

if __name__ == "__main__":
    main()