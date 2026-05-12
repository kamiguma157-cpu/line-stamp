from PIL import Image
import os

OUTPUT_DIR = "/mnt/user-data/outputs"

# メイン画像: stamp_01〜04を2×2に並べて240×240px
def make_main_image():
    size = 240
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    positions = [(0, 0), (120, 0), (0, 120), (120, 120)]
    for i, (x, y) in enumerate(positions):
        img = Image.open(os.path.join(OUTPUT_DIR, f"stamp_{i+1:02d}.png")).convert("RGBA")
        img = img.resize((120, 120), Image.LANCZOS)
        canvas.paste(img, (x, y), img)
    out = os.path.join(OUTPUT_DIR, "main_image.png")
    canvas.save(out, "PNG")
    print(f"メイン画像保存: {out}")

# タブ画像: stamp_01を96×74pxにリサイズ
def make_tab_image():
    w, h = 96, 74
    img = Image.open(os.path.join(OUTPUT_DIR, "stamp_01.png")).convert("RGBA")
    img.thumbnail((w, h), Image.LANCZOS)
    canvas = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    x = (w - img.width) // 2
    y = (h - img.height) // 2
    canvas.paste(img, (x, y), img)
    out = os.path.join(OUTPUT_DIR, "tab_image.png")
    canvas.save(out, "PNG")
    print(f"タブ画像保存: {out}")

make_main_image()
make_tab_image()
print("完了")
