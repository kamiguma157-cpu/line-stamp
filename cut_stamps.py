import numpy as np
from PIL import Image
import os

INPUT_PATH = "/mnt/user-data/uploads/414b9082fac01547901211b542cf8316179b13e55e3866d31882a586b66ad694.png"
OUTPUT_DIR = "/mnt/user-data/outputs"
COLS, ROWS = 4, 4
LINE_SIZE = (370, 320)
BG_THRESHOLD = 230
SOFT_RANGE = 20  # フェード幅（ソフトマスク用）

os.makedirs(OUTPUT_DIR, exist_ok=True)

sheet = Image.open(INPUT_PATH).convert("RGBA")
w, h = sheet.size
cell_w = w // COLS
cell_h = h // ROWS

print(f"シートサイズ: {w}x{h}, セルサイズ: {cell_w}x{cell_h}")

for idx in range(ROWS * COLS):
    row = idx // COLS
    col = idx % COLS

    left = col * cell_w
    upper = row * cell_h
    right = left + cell_w
    lower = upper + cell_h

    cell = sheet.crop((left, upper, right, lower)).convert("RGBA")
    arr = np.array(cell, dtype=np.float32)

    r, g, b, a = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2], arr[:, :, 3]

    # 各チャンネルのうち最小値で「どれだけ白いか」を判定
    min_rgb = np.minimum(np.minimum(r, g), b)

    # しきい値以上 → 透過、それ以下 → 不透明、間 → ソフトフェード
    alpha_mask = np.ones_like(min_rgb) * 255.0
    alpha_mask = np.where(min_rgb >= BG_THRESHOLD, 0.0, alpha_mask)
    fade_region = (min_rgb >= BG_THRESHOLD - SOFT_RANGE) & (min_rgb < BG_THRESHOLD)
    alpha_mask = np.where(
        fade_region,
        (BG_THRESHOLD - min_rgb) / SOFT_RANGE * 255.0,
        alpha_mask,
    )

    # 元のアルファと合成
    new_alpha = np.minimum(a, alpha_mask)
    arr[:, :, 3] = np.clip(new_alpha, 0, 255)

    result = Image.fromarray(arr.astype(np.uint8), "RGBA")

    # LINEスタンプ規定サイズにリサイズ（アスペクト比保持、余白は透過）
    result.thumbnail(LINE_SIZE, Image.LANCZOS)
    canvas = Image.new("RGBA", LINE_SIZE, (0, 0, 0, 0))
    paste_x = (LINE_SIZE[0] - result.width) // 2
    paste_y = (LINE_SIZE[1] - result.height) // 2
    canvas.paste(result, (paste_x, paste_y), result)

    out_path = os.path.join(OUTPUT_DIR, f"stamp_{idx + 1:02d}.png")
    canvas.save(out_path, "PNG")
    print(f"保存: {out_path} ({result.width}x{result.height} → canvas {LINE_SIZE[0]}x{LINE_SIZE[1]})")

print("完了: 全16枚を保存しました。")
