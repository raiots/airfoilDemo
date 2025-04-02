import os
from pathlib import Path
import subprocess
from foamlib import FoamCase
import glob
import csv
import time  # 添加时间模块

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

def extract_coefficient(base_name):
    """提取系数文件最后一行的第二个数据
    
    Args:
        base_name (str): 处理的文件基本名称
        
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
                if len(values) >= 2:
                    # 提取第二个数值
                    coefficient = float(values[4])
                    print(f"提取到系数值: {coefficient}")
                    return coefficient
                else:
                    print(f"警告：系数行格式不正确: {last_line}")
            else:
                print(f"警告：系数文件无数据")
    except Exception as e:
        print(f"提取系数时出错: {e}")
    
    return None

def main():
    # 获取grids目录下所有的p3d文件
    p3d_files = [f for f in os.listdir('../../grids/grid_exp') if f.endswith('.p3d')]
    
    if not p3d_files:
        print("错误：在grids目录下没有找到.p3d文件！")
        return
    
    print(f"找到以下p3d文件：{p3d_files}")
    
    # 创建CSV文件存储结果
    csv_file = 'grid_exp_coefficients.csv'
    with open(csv_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['文件名', '系数值', '运行时间(秒)'])  # 修改表头，添加运行时间列
    
    # 处理每个p3d文件
    for p3d_file in p3d_files:
        # 获取不带扩展名的文件名
        base_name = os.path.splitext(p3d_file)[0]
        
        print(f"\n正在处理网格文件: {p3d_file}")
        
        # 1. 运行网格处理命令
        print("正在处理网格...")
        run_mesh_commands(p3d_file)
        
        # 2. 运行算例并记录时间
        print("正在运行算例...")
        start_time = time.time()  # 记录开始时间
        case = FoamCase(Path("../../sims"))
        case.clean()
        case.run()
        run_time = time.time() - start_time  # 计算运行时间
        print(f"算例运行时间: {run_time:.2f}秒")
        
        # 3. 提取系数数据
        print("正在提取系数数据...")
        coefficient = extract_coefficient(base_name)
        
        # 4. 将结果写入CSV
        with open(csv_file, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([base_name, coefficient, f"{run_time:.2f}"])  # 添加运行时间到CSV
        
        print(f"已完成 {p3d_file} 的处理！系数和运行时间已记录到 '{csv_file}'")
    
    print(f"\n所有网格文件处理完成！系数数据和运行时间已保存到 '{csv_file}'")

if __name__ == "__main__":
    main()