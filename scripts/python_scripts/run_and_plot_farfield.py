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
        f"plot3dToFoam ../grids/farfield_exp/{p3d_file} -2D 1 -singleBlock -noBlank",
        "autoPatch 45 -overwrite",
        "createPatch -overwrite",
        "transformPoints -rotate-angle '((0 0 1) -10)'"
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
    p3d_files = [f for f in os.listdir('../../grids/farfield_exp') if f.endswith('.p3d')]
    
    if not p3d_files:
        print("错误：在grids目录下没有找到.p3d文件！")
        return
    
    print(f"找到以下p3d文件：{p3d_files}")
    
    # 存储所有残差数据和力数据
    all_residuals = []
    all_forces = []
    case_names = []
    
    # 处理每个p3d文件
    for p3d_file in p3d_files:
        # 获取不带扩展名的文件名
        base_name = os.path.splitext(p3d_file)[0]
        case_names.append(base_name)
        
        print(f"\n正在处理网格文件: {p3d_file}")
        
        # 1. 运行网格处理命令
        print("正在处理网格...")
        run_mesh_commands(p3d_file)
        
        # 2. 运行算例
        print("正在运行算例...")
        case = FoamCase(Path("../../sims"))
        case.clean()
        case.run()
        
        # 3. 收集残差数据
        print("正在收集残差数据...")
        from plotdev import parse_residuals, plot_residuals, parse_forces, plot_forces
        df_residuals = parse_residuals('../../sims/log.simpleFoam')
        all_residuals.append(df_residuals)
        
        # 4. 收集力数据
        print("正在收集力数据...")
        force_file = '../../sims/postProcessing/forces/0/force_0.dat'
        if os.path.exists(force_file):
            df_forces = parse_forces(force_file)
            all_forces.append(df_forces)
            
            # 为每个网格文件单独保存力图
            plot_forces(df_forces, output_filename=f'force_x_{base_name}.png', force_type='force_x')
            plot_forces(df_forces, output_filename=f'force_y_{base_name}.png', force_type='force_y')
        else:
            print(f"警告：无法找到力数据文件 {force_file}")
        
        # 为每个网格文件单独保存Ux残差图
        plot_residuals(df_residuals, output_filename=f'Ux_residual_{base_name}.png', residual_type='Ux_residual')
    
    # 绘制所有残差曲线到不同图中
    print("正在生成组合残差图...")
    # 绘制p残差图
    plot_residuals(all_residuals, output_filename='combined_p_residuals.png', 
                   labels=case_names, residual_type='p_residual')
    
    # 绘制Ux残差图 
    plot_residuals(all_residuals, output_filename='combined_Ux_residuals.png', 
                   labels=case_names, residual_type='Ux_residual')
    
    # 绘制Uy残差图
    plot_residuals(all_residuals, output_filename='combined_Uy_residuals.png', 
                   labels=case_names, residual_type='Uy_residual')
    
    # 绘制所有力曲线到不同图中
    if all_forces:
        print("正在生成组合力图...")
        # 绘制X力图
        plot_forces(all_forces, output_filename='combined_force_x.png', 
                    labels=case_names, force_type='force_x')
        
        # 绘制Y力图
        plot_forces(all_forces, output_filename='combined_force_y.png', 
                    labels=case_names, force_type='force_y')
    
    print("\n所有网格文件处理完成！")
    print("残差图已保存为:")
    print("- 'combined_p_residuals.png'")
    print("- 'combined_Ux_residuals.png'")
    print("- 'combined_Uy_residuals.png'")
    
    if all_forces:
        print("力图已保存为:")
        print("- 'combined_force_x.png'")
        print("- 'combined_force_y.png'")

if __name__ == "__main__":
    main() 