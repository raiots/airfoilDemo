import os
from pathlib import Path
import subprocess
from foamlib import FoamCase
import glob

def run_mesh_commands(p3d_file):
    """运行网格处理相关命令
    
    Args:
        p3d_file (str): p3d文件的名称
    """
    commands = [
        "cd ../../sims",
        f"plot3dToFoam ../grids/{p3d_file} -2D 1 -singleBlock -noBlank",
        "autoPatch 45 -overwrite",
        "createPatch -overwrite"
    ]
    
    combined_command = " && ".join(commands)
    subprocess.run(combined_command, shell=True, check=True)

def process_case(p3d_file):
    """处理单个算例
    
    Args:
        p3d_file (str): p3d文件的名称
    """
    # 获取不带扩展名的文件名，用于图片命名
    base_name = os.path.splitext(p3d_file)[0]
    
    print(f"\n正在处理网格文件: {p3d_file}")
    
    # 1. 运行网格处理命令
    print("正在处理网格...")
    run_mesh_commands(p3d_file)
    
    # 2. 运行算例
    print("正在运行算例...")
    case = FoamCase(Path("../../sims"))
    case.clean()
    case.run(cmd="simpleFoam")
    
    # 3. 绘制残差图
    print("正在生成残差图...")
    from plotdev import parse_residuals, plot_residuals
    df = parse_residuals('../../sims/log.simpleFoam')
    
    # 修改plot_residuals函数调用，添加自定义文件名
    plot_residuals(df, output_filename=f'Ux_residual_{base_name}.png')
    
    print(f"已完成 {p3d_file} 的处理！残差图已保存为 'Ux_residual_{base_name}.png'")

def main():
    # 获取grids目录下所有的p3d文件
    p3d_files = [f for f in os.listdir('../../grids') if f.endswith('.p3d')]
    
    if not p3d_files:
        print("错误：在grids目录下没有找到.p3d文件！")
        return
    
    print(f"找到以下p3d文件：{p3d_files}")
    
    # 处理每个p3d文件
    for p3d_file in p3d_files:
        process_case(p3d_file)
    
    print("\n所有网格文件处理完成！")

if __name__ == "__main__":
    main() 