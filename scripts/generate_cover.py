"""Generate cover image (240x240px) for LINE Creators Market."""

from PIL import Image, ImageDraw, ImageFont
import math, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from generate_stamps_v2 import (
    draw_head, draw_neck, draw_body, draw_arm, draw_leg,
    sparkles, heart, font, centered_text, outline_text,
    SKIN, SKIN_D, SKIN_L, LINE, CHEEK, EYE, WHITE, PANEL, DOT1, DOT2
)

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "output")

def make_cover():
    W, H = 240, 240
    img  = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # pastel gradient background circle
    for r in range(108, 0, -1):
        ratio = r / 108
        rc = int(255 * (0.98 - ratio * 0.06))
        gc = int(255 * (0.94 - ratio * 0.08))
        bc = int(255 * (0.88 - ratio * 0.10))
        draw.ellipse([(W//2 - r, H//2 - r), (W//2 + r, H//2 + r)],
                     fill=(rc, gc, bc, 255))

    # sparkles
    sparkles(draw, [(38, 42), (200, 38), (30, 185), (208, 192)],
             color=(255, 210, 100), size=8)

    # hearts
    heart(draw, 52,  58, 14)
    heart(draw, 188, 52, 11)

    # robot centred, slightly larger
    cx, cy = W // 2, H // 2 + 22

    draw_leg(draw, cx, cy, -1, "stand")
    draw_leg(draw, cx, cy,  1, "stand")
    draw_arm(draw, cx, cy, -1, "raise")
    draw_arm(draw, cx, cy,  1, "wave")
    draw_neck(draw, cx, cy - 52)
    draw_body(draw, cx, cy)
    draw_head(draw, cx, cy - 88, "happy")

    # title text
    f = font(20)
    centered_text(draw, W // 2, 8, "ゆるロボ", f,
                  fill=(120, 80, 40), outline=(255, 245, 230))

    path = os.path.join(OUTPUT_DIR, "cover.png")
    img.save(path)
    print(f"Saved {path}")

if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    make_cover()
