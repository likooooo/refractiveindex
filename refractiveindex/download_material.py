import matplotlib.pyplot as plt
import refractiveindex as ri
import numpy as np
import argparse
import os
import sys

db_path = os.path.join(os.path.expanduser("~"), "repos/infrastructure/kernels/virtuallab/pynb/filmstack/material/refractiveindex.info-database")

def plot_nk(material, wl, n=None, k=None):
    """
    绘制材料的 n 和/或 k 随波长变化的曲线。
    如果 n 或 k 为 None，则不绘制对应的曲线。

    :param material: 材料名称 (str)。
    :param wl: 波长数组 (numpy array)。
    :param n: 折射率数组 (numpy array 或 None)。
    :param k: 消光系数数组 (numpy array 或 None)。
    """
    
    if n is None and k is None:
        print(f"Warning: Nothing to plot for material {material}. n and k are both None.")
        return

    plt.figure(figsize=(8, 5))
    
    labels_to_plot = [] 
    
    if n is not None:
        if np.iscomplexobj(n):
            # 虽然 ri 库通常返回实数，但为了健壮性保留对复杂 n 的处理
            plt.plot(wl, np.real(n), label="n (Real)")
        else:
            plt.plot(wl, n, label="n")
        labels_to_plot.append("n")
        
    if k is not None:
        if np.iscomplexobj(k):
            # 同样保留对复杂 k 的处理
            plt.plot(wl, np.real(k), label="k (Real)")
        else:
            plt.plot(wl, k, label="k")
        labels_to_plot.append("k")
        
    plt.xlabel("Wavelength ($\\mu$m)")
    # 使用 `n` 和 `k` 作为 Y 轴标签
    y_label_str = ", ".join(sorted(list(set(labels_to_plot)))) 
    plt.ylabel(y_label_str) 
    plt.title(f"Material Properties for {material}")
    plt.grid(True)
    plt.legend()
    plt.show()

def print_nk_table(wl, n, k):
    """
    打印波长、折射率和消光系数的表格。
    """
    print(f"{'Wavelength (μm)':<20} {'n':<20} {'k':<20}")
    # 确保 n 和 k 具有与 wl 相同的长度
    # 如果 n 或 k 是 None，则用 0.0 的数组代替
    n_data = n if n is not None else np.zeros_like(wl, dtype=float)
    k_data = k if k is not None else np.zeros_like(wl, dtype=float)
    
    for w, val_n, val_k in zip(wl, n_data, k_data):
        # 格式化输出，处理 n 或 k 可能是复数的情况（虽然不常见）
        n_str = f"{np.real(val_n):.6f}" if np.iscomplexobj(val_n) else f"{val_n:.6f}"
        k_str = f"{np.real(val_k):.6f}" if np.iscomplexobj(val_k) else f"{val_k:.6f}"
        print(f"{w:<20.6f} {n_str:<20} {k_str:<20}")

def main(material_name, do_plot):
    try:
        DB = ri.RefractiveIndex(databasePath=db_path)
    except FileNotFoundError:
        print(f"Error: Database path not found at {db_path}", file=sys.stderr)
        return
    if("" == material_name): return
    print(f"Material path is {DB.getMaterialFilename(material_name)}", file=sys.stderr)
    
    try:
        material = DB.getMaterial(book=material_name)
    except Exception as e:
        print(f"Error fetching material {material_name}: {e}", file=sys.stderr)
        return

    wl = material.originalData['wavelength (um)']
    # ri 库的查找函数通常需要 nm
    wl_nm = wl * 1e3
    
    n, k = None, None
    try:
        # 获取折射率 n
        n = material.getRefractiveIndex(wl_nm)
    except Exception:
        # 捕获异常，将 n 保持为 None
        pass 
        
    try:
        # 获取消光系数 k
        k = material.getExtinctionCoefficient(wl_nm)
    except Exception:
        # 捕获异常，将 k 保持为 None
        pass 

    print_nk_table(wl=wl, n=n, k=k)
    if do_plot:
        plot_nk(material=material_name, wl=wl, n=n, k=k)
        
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Fetch refractive index data and either plot it or print a table for a given material."
    )
    
    parser.add_argument(
        "material_name",
        nargs='?', # 表示该参数是可选的 (0或1个)
        default="", 
        help="The name of the material (e.g., 'SiO2', 'Si')."
    )
    
    parser.add_argument(
        "--plot", 
        action="store_true", # 如果在命令行中出现，则设置为 True
        help="Enable plotting of n and k vs. wavelength using matplotlib."
    )
    
    args = parser.parse_args()
    main(args.material_name, args.plot)