import fitz  # PyMuPDF
from PIL import Image
import io
import os
import sys
from pathlib import Path

def pdf_to_images(pdf_path, output_folder="output_images", image_format="png", dpi=300):
    """
    将单个PDF文件转换为一系列图片。

    :param pdf_path: 输入PDF文件的路径。
    :param output_folder: 输出图片的存放文件夹。
    :param image_format: 输出图片的格式，如 'png', 'jpg'。
    :param dpi: 输出图片的分辨率，DPI值越高，图片越清晰。
    """
    # 获取原PDF文件名（不含扩展名）
    pdf_basename = os.path.splitext(os.path.basename(pdf_path))[0]
    
    # 为每个PDF创建独立的输出子文件夹，防止文件名冲突
    pdf_output_folder = os.path.join(output_folder, pdf_basename)
    Path(pdf_output_folder).mkdir(parents=True, exist_ok=True)

    try:
        # 打开PDF文件
        pdf_document = fitz.open(pdf_path)
        total_pages = pdf_document.page_count
        print(f"\n--- 开始处理: '{os.path.basename(pdf_path)}'，共 {total_pages} 页 ---")

        # 将DPI转换为PyMuPDF使用的缩放因子 (72是PDF的默认DPI)
        zoom = dpi / 72
        mat = fitz.Matrix(zoom, zoom)

        for page_num in range(total_pages):
            # 获取当前页
            page = pdf_document[page_num]
            
            # 将页面转换为像素图 (pixmap)
            pix = page.get_pixmap(matrix=mat)
            
            # 将pixmap转换为Pillow Image对象
            img = Image.open(io.BytesIO(pix.tobytes("png")))

            # 如果是JPG格式，需要先将RGBA转换为RGB
            if image_format.lower() == "jpg" or image_format.lower() == "jpeg":
                img = img.convert("RGB")

            # 构建输出文件名，格式为：原文件名_页码.格式（例如：example_1.png）
            output_filename = f"{pdf_basename}_{page_num + 1}.{image_format.lower()}"
            output_path = os.path.join(pdf_output_folder, output_filename)
            
            # 保存图片
            img.save(output_path)
            
            # 关闭Pillow Image对象以释放内存
            img.close()

        # 关闭PDF文档
        pdf_document.close()
        print(f"--- 处理完成: '{os.path.basename(pdf_path)}' ---")

    except Exception as e:
        print(f"!!! 处理 '{os.path.basename(pdf_path)}' 时发生错误: {e}")

if __name__ == "__main__":
    # 默认参数
    input_folder = "input"
    output_folder = "output_images"
    image_format = "png"
    dpi = 300

    # 解析命令行参数（用于修改默认设置）
    i = 1
    while i < len(sys.argv):
        if sys.argv[i] == "-in" and i + 1 < len(sys.argv):
            input_folder = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == "-out" and i + 1 < len(sys.argv):
            output_folder = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == "-format" and i + 1 < len(sys.argv):
            image_format = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == "-dpi" and i + 1 < len(sys.argv):
            try:
                dpi = int(sys.argv[i + 1])
            except ValueError:
                print("警告: DPI必须是整数，将使用默认值300。")
            i += 2
        else:
            print(f"警告: 未知参数 '{sys.argv[i]}'，将被忽略。")
            i += 1

    # 检查输入文件夹是否存在
    if not os.path.exists(input_folder):
        print(f"错误：输入文件夹 '{input_folder}' 不存在。请在脚本同目录下创建它，并放入PDF文件。")
        sys.exit(1)

    # 获取文件夹中所有的PDF文件
    pdf_files = [f for f in os.listdir(input_folder) if f.lower().endswith('.pdf')]

    if not pdf_files:
        print(f"在 '{input_folder}' 文件夹中未找到任何PDF文件。")
        sys.exit(0)

    print(f"找到 {len(pdf_files)} 个PDF文件，将开始批量转换...")
    print(f"输出目录: {os.path.abspath(output_folder)}")
    print(f"图片格式: {image_format.upper()}")
    print(f"分辨率: {dpi} DPI")

    # 遍历并转换每个PDF文件
    for pdf_file in pdf_files:
        pdf_path = os.path.join(input_folder, pdf_file)
        pdf_to_images(pdf_path, output_folder, image_format, dpi)

    print("\n所有PDF文件处理完毕！")
    
    # 防止CMD窗口一闪而过（仅在双击运行时有效）
    if not getattr(sys, 'frozen', False):
        input("\n请按Enter键退出...")