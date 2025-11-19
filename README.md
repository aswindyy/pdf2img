Windows可用的PDF转图片小程序。

这个程序将使用Python编写，因为它有非常强大的PDF处理库，并且易于打包成一个独立的Windows可执行文件（`.exe`），这样你就不需要安装任何额外的软件或配置复杂的环境。

我们将使用两个核心库：
1.  **PyMuPDF (fitz)**: 这是一个处理PDF文件的利器，转换速度快，而且能够完美地保持PDF的矢量内容（如文字、线条）在图片中依然清晰，这是实现“无损”转换的关键。
2.  **Pillow (PIL Fork)**: 一个强大的图像处理库，我们用它来将PyMuPDF生成的图像数据最终保存为常见的图片格式，如PNG或JPG。

---

### 第一步：准备工作 (如果你想自己运行源代码)

如果你想直接运行Python脚本，而不是生成`.exe`文件，你需要先安装Python和必要的库。

1.  **安装Python**:
    如果你还没有安装Python，请从[python.org](https://www.python.org/downloads/windows/)下载并安装。**在安装时，请务必勾选“Add Python to PATH”选项**。

2.  **安装依赖库**:
    打开Windows的命令提示符（`CMD`）或 PowerShell，然后运行以下命令来安装我们需要的库：
    ```bash
    pip install PyMuPDF Pillow
    ```

---

### 第二步：编写Python脚本

下面是完整的Python代码。你可以将它保存为一个名为 `pdf2img.py` 的文件。

```python
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
    input("\n请按Enter键退出...")
```

#### 代码说明：
*   **`pdf_to_images` 函数**: 这是核心功能函数，接收PDF路径、输出文件夹、图片格式和DPI等参数，然后执行转换。
*   **`fitz.open(pdf_path)`**: 使用PyMuPDF打开指定的PDF文件。
*   **`page.get_pixmap(matrix=mat)`**: 将PDF的一页渲染成一个像素图（Pixmap）。`matrix=mat` 是实现高DPI的关键，通过缩放矩阵来提高输出分辨率。
*   **`Image.open(...)` 和 `img.save(...)`**: 利用Pillow库将PyMuPDF的Pixmap对象转换成标准的图片文件并保存。
*   **命令行参数**: 脚本支持从命令行接收输入文件路径，并可以通过 `-format` 和 `-dpi` 参数自定义输出格式和分辨率。
*   **`if __name__ == "__main__":`**: 这是Python脚本的入口点。它会检查命令行参数，如果没有提供，则显示帮助信息。

---

### 第三步：如何使用

你有两种使用方式：

#### 方式A：直接运行Python脚本 (适合有Python环境的用户)

1.  将上面的代码保存为 `pdf2img.py`。
2.  打开命令提示符（`CMD`）或 PowerShell。
3.  使用 `cd` 命令切换到你保存 `pdf2img.py` 文件和PDF文件所在的目录。
4.  运行命令：
    ```bash
    # 基本用法 (默认转换为PNG，300 DPI)
    python pdf2img.py "你的文件.pdf"

    # 示例：将 "report.pdf" 转换为JPG格式，分辨率为600 DPI
    # 图片会保存在名为 "output_images" 的文件夹中
    python pdf2img.py "report.pdf" -format jpg -dpi 600
    ```
    **提示**：在CMD中，你可以直接将PDF文件拖入窗口，它会自动填充文件路径，非常方便。

#### 方式B：创建一个无需安装的Windows可执行文件 (.exe) (推荐给所有人)

为了让没有安装Python的朋友也能使用，我们可以将这个脚本打包成一个独立的`.exe`文件。

1.  **安装打包工具**:
    在CMD中运行以下命令安装 `pyinstaller`：
    ```bash
    pip install pyinstaller
    ```

2.  **打包脚本**:
    在CMD中，进入 `pdf2img.py` 所在的目录，然后运行以下命令：
    ```bash
    pyinstaller --onefile --windowed pdf2img.py
    ```
    *   `--onefile`: 将所有代码和依赖库打包成一个单一的`.exe`文件。
    *   `--windowed`: (可选) 打包成一个窗口程序，运行时不会弹出黑色的CMD控制台窗口。如果需要看转换进度，可以去掉这个参数。

3.  **找到生成的`.exe`文件**:
    打包完成后，会在当前目录下生成一个 `build` 文件夹和一个 `dist` 文件夹。你的 `pdf2img.exe` 文件就在 `dist` 文件夹里。

4.  **使用`.exe`文件**:
    *   **方法一 (推荐)**: 直接将你的PDF文件拖放到 `pdf2img.exe` 文件图标上。程序会自动运行，并在`pdf2img.exe`所在的目录下创建一个 `output_images` 文件夹，转换好的图片就存放在里面。
    *   **方法二**: 也可以通过命令行运行 `.exe` 文件，用法和运行Python脚本类似：
        ```bash
        pdf2img.exe "C:\path\to\your\file.pdf" -format jpg -dpi 400
        ```

### 总结与建议

*   **无损转换**: 使用PyMuPDF并设置较高的DPI（如300或600）可以获得非常清晰的图片，对于文字和简单图形，效果几乎等同于“无损”。
*   **图片格式**:
    *   **PNG**: 支持透明背景，图片质量高，但文件体积相对较大。适合需要编辑或高质量展示的场景。
    *   **JPG**: 文件体积小，但采用有损压缩，反复保存会失真。适合快速预览或在对画质要求不高的地方使用。
*   **分辨率 (DPI)**:
    *   **300 DPI**: 是印刷和高质量显示的标准，效果很好。
    *   **600 DPI**: 超高清，文件体积会更大，转换时间也更长，适用于对细节要求极高的场合。
    *   **默认 (72或96 DPI)**: 适合快速预览，画质一般。
