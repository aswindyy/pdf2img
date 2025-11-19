import fitz  # PyMuPDF
from PIL import Image
import io
import os
import sys
from pathlib import Path

def pdf_to_images(pdf_path, output_folder="output_images", image_format="png", dpi=300):
    """
    将PDF文件转换为一系列图片。

    :param pdf_path: 输入PDF文件的路径。
    :param output_folder: 输出图片的存放文件夹。
    :param image_format: 输出图片的格式，如 'png', 'jpg'。
    :param dpi: 输出图片的分辨率，DPI值越高，图片越清晰。
    """
    # 检查输入文件是否存在
    if not os.path.exists(pdf_path):
        print(f"错误：文件 '{pdf_path}' 不存在。")
        return

    # 检查输出文件夹，如果不存在则创建
    Path(output_folder).mkdir(parents=True, exist_ok=True)
    print(f"图片将保存到: {os.path.abspath(output_folder)}")

    # 打开PDF文件
    pdf_document = fitz.open(pdf_path)
    total_pages = pdf_document.page_count
    print(f"成功打开PDF，共 {total_pages} 页。开始转换...")

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

        # 构建输出文件名，例如: output_images/page_001.png
        output_filename = f"page_{page_num + 1:03d}.{image_format.lower()}"
        output_path = os.path.join(output_folder, output_filename)
        
        # 保存图片
        img.save(output_path)
        
        # 关闭Pillow Image对象以释放内存
        img.close()

        print(f"已完成: {page_num + 1}/{total_pages}")

    # 关闭PDF文档
    pdf_document.close()
    print("\n转换完成！所有图片已成功保存。")

if __name__ == "__main__":
    # 从命令行接收参数
    if len(sys.argv) < 2:
        print("用法:")
        print("  1. 直接运行脚本并拖入PDF文件:")
        print("     python pdf2img.py <你的PDF文件路径>")
        print("  2. 带参数运行 (例如，转换为JPG，300 DPI):")
        print("     python pdf2img.py <你的PDF文件路径> -format jpg -dpi 300")
        sys.exit(1)

    pdf_path = sys.argv[1]
    output_folder = "output_images"
    image_format = "png"
    dpi = 300

    # 解析可选参数
    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == "-format" and i + 1 < len(sys.argv):
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

    # 调用转换函数
    pdf_to_images(pdf_path, output_folder, image_format, dpi)
    
    # 防止CMD窗口一闪而过（仅在双击运行时有效）
    # 已移除重复的sys导入，使用顶部已导入的sys模块
    if not getattr(sys, 'frozen', False):
        input("\n请按Enter键退出...")