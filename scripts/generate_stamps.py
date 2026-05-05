"""
LINE stamp generator for "ゆるロボ" (Yuru-Robo) series.
Generates 16 main stamps (370x320px) + 1 tab image (96x74px).
"""

from PIL import Image, ImageDraw, ImageFont
import math
import os

STAMP_W, STAMP_H = 370, 320
TAB_W, TAB_H = 96, 74
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "output")
FONT_PATH = "/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf"

# Robot color palette (cardboard box robot)
BODY_COLOR    = (210, 170, 110)
BODY_SHADOW   = (170, 130,  80)
BODY_LIGHT    = (240, 210, 160)
EDGE_COLOR    = (120,  80,  40)
EYE_COLOR     = (255, 255, 255)
PUPIL_COLOR   = ( 40,  40,  40)
SCREEN_COLOR  = ( 80, 180, 220)
LED_GREEN     = ( 80, 220, 120)
LED_RED       = (240,  80,  80)
JOINT_COLOR   = (140, 100,  60)
METAL_COLOR   = (180, 180, 190)


def font(size):
    try:
        return ImageFont.truetype(FONT_PATH, size)
    except Exception:
        return ImageFont.load_default()


def outline_text(draw, pos, text, fnt, fill, outline, thickness=3):
    x, y = pos
    for dx in range(-thickness, thickness + 1):
        for dy in range(-thickness, thickness + 1):
            if dx != 0 or dy != 0:
                draw.text((x + dx, y + dy), text, font=fnt, fill=outline)
    draw.text(pos, text, font=fnt, fill=fill)


def centered_text(draw, cx, y, text, fnt, fill=(255, 255, 255), outline=(60, 30, 10)):
    bb = draw.textbbox((0, 0), text, font=fnt)
    w = bb[2] - bb[0]
    outline_text(draw, (cx - w // 2, y), text, fnt, fill, outline, thickness=3)


def draw_robot_base(draw, cx, cy, scale=1.0, tilt=0):
    """Draw the core robot body at center (cx, cy)."""
    s = scale

    def pt(dx, dy):
        # tilt = rotate around center
        rx = dx * math.cos(tilt) - dy * math.sin(tilt)
        ry = dx * math.sin(tilt) + dy * math.cos(tilt)
        return (cx + rx, cy + ry)

    def box(x0, y0, x1, y1, fill, outline=EDGE_COLOR, width=2):
        """Draw a tilted rectangle by rotating each corner."""
        corners = [pt(x0, y0), pt(x1, y0), pt(x1, y1), pt(x0, y1)]
        draw.polygon(corners, fill=fill)
        draw.polygon(corners, outline=outline, width=width)

    # --- body ---
    bx, by = -38 * s, -10 * s
    bw, bh = 76 * s, 60 * s
    box(bx, by, bx + bw, by + bh, BODY_COLOR)
    # crease lines
    box(bx + 8 * s, by + 4 * s, bx + bw - 8 * s, by + 8 * s, BODY_SHADOW, BODY_SHADOW, 1)

    # --- neck ---
    box(-10 * s, -28 * s, 10 * s, -10 * s, JOINT_COLOR)

    # --- head ---
    hx, hy = -40 * s, -80 * s
    hw, hh = 80 * s, 55 * s
    box(hx, hy, hx + hw, hy + hh, BODY_COLOR)
    # top flap
    box(hx + 6 * s, hy - 6 * s, hx + hw - 6 * s, hy, BODY_LIGHT)
    # ear bolts
    for ex in [hx - 6 * s, hx + hw + 2 * s]:
        corners = [pt(ex, hy + 12 * s), pt(ex + 8 * s, hy + 12 * s),
                   pt(ex + 8 * s, hy + 28 * s), pt(ex, hy + 28 * s)]
        draw.polygon(corners, fill=METAL_COLOR)
        draw.polygon(corners, outline=EDGE_COLOR, width=2)

    # --- eyes (screen area) ---
    screen_corners = [
        pt(hx + 10 * s, hy + 10 * s), pt(hx + hw - 10 * s, hy + 10 * s),
        pt(hx + hw - 10 * s, hy + hh - 10 * s), pt(hx + 10 * s, hy + hh - 10 * s)
    ]
    draw.polygon(screen_corners, fill=SCREEN_COLOR)
    draw.polygon(screen_corners, outline=EDGE_COLOR, width=2)

    return hx, hy, hw, hh, bx, by, bw, bh


def draw_eyes_normal(draw, cx, cy, hx, hy, hw, hh, s=1.0, tilt=0):
    def pt(dx, dy):
        rx = dx * math.cos(tilt) - dy * math.sin(tilt)
        ry = dx * math.sin(tilt) + dy * math.cos(tilt)
        return (cx + rx, cy + ry)

    for ex_off in [-16 * s, 10 * s]:
        ex = hx + hw // 2 + ex_off
        ey = hy + hh // 2 - 2 * s
        # white
        corners = [pt(ex - 10 * s, ey - 10 * s), pt(ex + 10 * s, ey - 10 * s),
                   pt(ex + 10 * s, ey + 10 * s), pt(ex - 10 * s, ey + 10 * s)]
        draw.polygon(corners, fill=EYE_COLOR)
        # pupil
        corners2 = [pt(ex - 5 * s, ey - 5 * s), pt(ex + 5 * s, ey - 5 * s),
                    pt(ex + 5 * s, ey + 5 * s), pt(ex - 5 * s, ey + 5 * s)]
        draw.polygon(corners2, fill=PUPIL_COLOR)


def draw_eyes_happy(draw, cx, cy, hx, hy, hw, hh, s=1.0, tilt=0):
    """^^ eyes"""
    def pt(dx, dy):
        rx = dx * math.cos(tilt) - dy * math.sin(tilt)
        ry = dx * math.sin(tilt) + dy * math.cos(tilt)
        return (cx + rx, cy + ry)

    for ex_off in [-16 * s, 10 * s]:
        ex = hx + hw // 2 + ex_off
        ey = hy + hh // 2 - 2 * s
        # arc-shaped eyes
        for i in range(8):
            a1 = math.radians(200 + i * 17)
            a2 = math.radians(200 + (i + 1) * 17)
            x1 = ex + 9 * s * math.cos(a1)
            y1 = ey + 7 * s * math.sin(a1)
            x2 = ex + 9 * s * math.cos(a2)
            y2 = ey + 7 * s * math.sin(a2)
            p1 = pt(x1 - cx, y1 - cy)
            p2 = pt(x2 - cx, y2 - cy)
            draw.line([p1, p2], fill=PUPIL_COLOR, width=max(3, int(4 * s)))


def draw_eyes_surprised(draw, cx, cy, hx, hy, hw, hh, s=1.0, tilt=0):
    """O O eyes"""
    def pt(dx, dy):
        rx = dx * math.cos(tilt) - dy * math.sin(tilt)
        ry = dx * math.sin(tilt) + dy * math.cos(tilt)
        return (cx + rx, cy + ry)

    for ex_off in [-16 * s, 10 * s]:
        ex = hx + hw // 2 + ex_off
        ey = hy + hh // 2 - 2 * s
        corners = [pt(ex - 12 * s, ey - 12 * s), pt(ex + 12 * s, ey - 12 * s),
                   pt(ex + 12 * s, ey + 12 * s), pt(ex - 12 * s, ey + 12 * s)]
        draw.polygon(corners, fill=EYE_COLOR)
        corners2 = [pt(ex - 7 * s, ey - 7 * s), pt(ex + 7 * s, ey - 7 * s),
                    pt(ex + 7 * s, ey + 7 * s), pt(ex - 7 * s, ey + 7 * s)]
        draw.polygon(corners2, fill=PUPIL_COLOR)


def draw_eyes_sad(draw, cx, cy, hx, hy, hw, hh, s=1.0, tilt=0):
    """-- eyes (droopy)"""
    def pt(dx, dy):
        rx = dx * math.cos(tilt) - dy * math.sin(tilt)
        ry = dx * math.sin(tilt) + dy * math.cos(tilt)
        return (cx + rx, cy + ry)

    for ex_off in [-16 * s, 10 * s]:
        ex = hx + hw // 2 + ex_off
        ey = hy + hh // 2 - 2 * s
        draw.line([pt(ex - 8 * s, ey), pt(ex + 8 * s, ey)],
                  fill=PUPIL_COLOR, width=max(3, int(4 * s)))


def draw_arm(draw, cx, cy, bx, by, bw, bh, s, side, pose, tilt=0):
    """side='left'/'right', pose='wave'/'normal'/'hug'/'cheer'"""
    def pt(dx, dy):
        rx = dx * math.cos(tilt) - dy * math.sin(tilt)
        ry = dx * math.sin(tilt) + dy * math.cos(tilt)
        return (cx + rx, cy + ry)

    if side == "left":
        sx = bx + 8 * s
    else:
        sx = bx + bw - 8 * s

    sy = by + 14 * s

    if pose == "wave" and side == "right":
        # arm up and waving
        corners = [pt(sx, sy), pt(sx + 18 * s, sy),
                   pt(sx + 20 * s, sy - 40 * s), pt(sx + 2 * s, sy - 40 * s)]
        draw.polygon(corners, fill=BODY_COLOR, outline=EDGE_COLOR, width=2)
        # hand
        hand = [pt(sx + 1 * s, sy - 45 * s), pt(sx + 21 * s, sy - 45 * s),
                pt(sx + 21 * s, sy - 35 * s), pt(sx + 1 * s, sy - 35 * s)]
        draw.polygon(hand, fill=BODY_LIGHT, outline=EDGE_COLOR, width=2)
    elif pose == "think" and side == "right":
        corners = [pt(sx, sy), pt(sx + 18 * s, sy),
                   pt(sx + 14 * s, sy - 30 * s), pt(sx - 4 * s, sy - 30 * s)]
        draw.polygon(corners, fill=BODY_COLOR, outline=EDGE_COLOR, width=2)
        hand = [pt(sx - 10 * s, sy - 36 * s), pt(sx + 10 * s, sy - 36 * s),
                pt(sx + 10 * s, sy - 26 * s), pt(sx - 10 * s, sy - 26 * s)]
        draw.polygon(hand, fill=BODY_LIGHT, outline=EDGE_COLOR, width=2)
    elif pose == "cheer":
        if side == "right":
            corners = [pt(sx, sy), pt(sx + 16 * s, sy),
                       pt(sx + 26 * s, sy - 50 * s), pt(sx + 10 * s, sy - 50 * s)]
            draw.polygon(corners, fill=BODY_COLOR, outline=EDGE_COLOR, width=2)
            hand = [pt(sx + 8 * s, sy - 58 * s), pt(sx + 28 * s, sy - 58 * s),
                    pt(sx + 28 * s, sy - 46 * s), pt(sx + 8 * s, sy - 46 * s)]
            draw.polygon(hand, fill=BODY_LIGHT, outline=EDGE_COLOR, width=2)
        else:
            corners = [pt(sx - 16 * s, sy), pt(sx, sy),
                       pt(sx - 10 * s, sy - 50 * s), pt(sx - 26 * s, sy - 50 * s)]
            draw.polygon(corners, fill=BODY_COLOR, outline=EDGE_COLOR, width=2)
            hand = [pt(sx - 28 * s, sy - 58 * s), pt(sx - 8 * s, sy - 58 * s),
                    pt(sx - 8 * s, sy - 46 * s), pt(sx - 28 * s, sy - 46 * s)]
            draw.polygon(hand, fill=BODY_LIGHT, outline=EDGE_COLOR, width=2)
    elif pose == "hug_r" and side == "right":
        corners = [pt(sx, sy), pt(sx + 16 * s, sy),
                   pt(sx + 10 * s, sy + 20 * s), pt(sx - 6 * s, sy + 20 * s)]
        draw.polygon(corners, fill=BODY_COLOR, outline=EDGE_COLOR, width=2)
        hand = [pt(sx - 12 * s, sy + 26 * s), pt(sx + 8 * s, sy + 26 * s),
                pt(sx + 8 * s, sy + 18 * s), pt(sx - 12 * s, sy + 18 * s)]
        draw.polygon(hand, fill=BODY_LIGHT, outline=EDGE_COLOR, width=2)
    elif pose == "hug_l" and side == "left":
        corners = [pt(sx - 16 * s, sy), pt(sx, sy),
                   pt(sx + 6 * s, sy + 20 * s), pt(sx - 10 * s, sy + 20 * s)]
        draw.polygon(corners, fill=BODY_COLOR, outline=EDGE_COLOR, width=2)
        hand = [pt(sx - 8 * s, sy + 26 * s), pt(sx + 12 * s, sy + 26 * s),
                pt(sx + 12 * s, sy + 18 * s), pt(sx - 8 * s, sy + 18 * s)]
        draw.polygon(hand, fill=BODY_LIGHT, outline=EDGE_COLOR, width=2)
    elif pose == "down_r" and side == "right":
        corners = [pt(sx, sy), pt(sx + 16 * s, sy),
                   pt(sx + 20 * s, sy + 35 * s), pt(sx + 4 * s, sy + 35 * s)]
        draw.polygon(corners, fill=BODY_COLOR, outline=EDGE_COLOR, width=2)
        hand = [pt(sx + 2 * s, sy + 40 * s), pt(sx + 22 * s, sy + 40 * s),
                pt(sx + 22 * s, sy + 32 * s), pt(sx + 2 * s, sy + 32 * s)]
        draw.polygon(hand, fill=BODY_LIGHT, outline=EDGE_COLOR, width=2)
    elif pose == "down_l" and side == "left":
        corners = [pt(sx - 16 * s, sy), pt(sx, sy),
                   pt(sx - 4 * s, sy + 35 * s), pt(sx - 20 * s, sy + 35 * s)]
        draw.polygon(corners, fill=BODY_COLOR, outline=EDGE_COLOR, width=2)
        hand = [pt(sx - 22 * s, sy + 40 * s), pt(sx - 2 * s, sy + 40 * s),
                pt(sx - 2 * s, sy + 32 * s), pt(sx - 22 * s, sy + 32 * s)]
        draw.polygon(hand, fill=BODY_LIGHT, outline=EDGE_COLOR, width=2)
    else:
        # default: arm at side
        if side == "right":
            corners = [pt(sx, sy), pt(sx + 16 * s, sy),
                       pt(sx + 16 * s, sy + 36 * s), pt(sx, sy + 36 * s)]
        else:
            corners = [pt(sx - 16 * s, sy), pt(sx, sy),
                       pt(sx, sy + 36 * s), pt(sx - 16 * s, sy + 36 * s)]
        draw.polygon(corners, fill=BODY_COLOR, outline=EDGE_COLOR, width=2)


def draw_legs(draw, cx, cy, bx, by, bw, bh, s, pose="normal", tilt=0):
    def pt(dx, dy):
        rx = dx * math.cos(tilt) - dy * math.sin(tilt)
        ry = dx * math.sin(tilt) + dy * math.cos(tilt)
        return (cx + rx, cy + ry)

    foot_y = by + bh

    if pose == "run":
        # left leg forward, right leg back
        for i, (lx, angle) in enumerate([(-18 * s, -0.3), (4 * s, 0.25)]):
            x0 = bx + lx
            lc = [pt(x0, foot_y), pt(x0 + 18 * s, foot_y),
                  pt(x0 + 18 * s + angle * 30 * s, foot_y + 36 * s),
                  pt(x0 + angle * 30 * s, foot_y + 36 * s)]
            draw.polygon(lc, fill=BODY_COLOR, outline=EDGE_COLOR, width=2)
            foot = [pt(x0 + angle * 30 * s - 4 * s, foot_y + 42 * s),
                    pt(x0 + angle * 30 * s + 22 * s, foot_y + 42 * s),
                    pt(x0 + angle * 30 * s + 22 * s, foot_y + 34 * s),
                    pt(x0 + angle * 30 * s - 4 * s, foot_y + 34 * s)]
            draw.polygon(foot, fill=JOINT_COLOR, outline=EDGE_COLOR, width=2)
    elif pose == "jump":
        for i, lx in enumerate([-18 * s, 4 * s]):
            angle = 0.3 if i == 0 else -0.3
            x0 = bx + lx
            lc = [pt(x0, foot_y), pt(x0 + 18 * s, foot_y),
                  pt(x0 + 18 * s + angle * 20 * s, foot_y + 28 * s),
                  pt(x0 + angle * 20 * s, foot_y + 28 * s)]
            draw.polygon(lc, fill=BODY_COLOR, outline=EDGE_COLOR, width=2)
            foot = [pt(x0 + angle * 20 * s - 4 * s, foot_y + 34 * s),
                    pt(x0 + angle * 20 * s + 22 * s, foot_y + 34 * s),
                    pt(x0 + angle * 20 * s + 22 * s, foot_y + 26 * s),
                    pt(x0 + angle * 20 * s - 4 * s, foot_y + 26 * s)]
            draw.polygon(foot, fill=JOINT_COLOR, outline=EDGE_COLOR, width=2)
    else:
        for lx in [-18 * s, 4 * s]:
            x0 = bx + lx
            lc = [pt(x0, foot_y), pt(x0 + 18 * s, foot_y),
                  pt(x0 + 18 * s, foot_y + 36 * s), pt(x0, foot_y + 36 * s)]
            draw.polygon(lc, fill=BODY_COLOR, outline=EDGE_COLOR, width=2)
            foot = [pt(x0 - 4 * s, foot_y + 42 * s), pt(x0 + 22 * s, foot_y + 42 * s),
                    pt(x0 + 22 * s, foot_y + 34 * s), pt(x0 - 4 * s, foot_y + 34 * s)]
            draw.polygon(foot, fill=JOINT_COLOR, outline=EDGE_COLOR, width=2)


def draw_sparkles(draw, positions, color=(255, 220, 50), size=8):
    for (sx, sy) in positions:
        for angle in range(0, 360, 45):
            rad = math.radians(angle)
            ex = sx + size * math.cos(rad)
            ey = sy + size * math.sin(rad)
            draw.line([(sx, sy), (ex, ey)], fill=color, width=2)


def draw_sweat(draw, x, y, size=14):
    """Draw a sweat drop."""
    pts = []
    for i in range(20):
        a = math.radians(i * 18)
        if a < math.pi:
            r = size * 0.7
        else:
            r = size
        pts.append((x + r * math.cos(a), y + r * math.sin(a) + size * 0.3))
    draw.polygon(pts, fill=(100, 180, 255, 200))
    draw.polygon(pts, outline=(60, 120, 200), width=1)


def make_stamp(idx, draw_fn):
    img = Image.new("RGBA", (STAMP_W, STAMP_H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw_fn(img, draw)
    path = os.path.join(OUTPUT_DIR, f"stamp_{idx:02d}.png")
    img.save(path)
    print(f"  Saved {path}")
    return img


# ─────────────────────────── Stamp definitions ────────────────────────────────

def stamp_01_ittekimasu(img, draw):
    """いってきます！ – walking out, waving"""
    cx, cy = 185, 155
    s = 1.0
    tilt = math.radians(-6)
    draw_legs(draw, cx, cy, -38, -10, 76, 60, s, "run", tilt)
    draw_arm(draw, cx, cy, -38, -10, 76, 60, s, "left", "normal", tilt)
    draw_arm(draw, cx, cy, -38, -10, 76, 60, s, "right", "wave", tilt)
    hx, hy, hw, hh, bx, by, bw, bh = draw_robot_base(draw, cx, cy, s, tilt)
    draw_eyes_happy(draw, cx, cy, hx, hy, hw, hh, s, tilt)
    # motion lines
    for i in range(3):
        x0 = cx - 85 - i * 14
        draw.line([(x0, cy - 20 + i * 18), (x0 + 30, cy - 20 + i * 18)],
                  fill=(180, 140, 80, 160), width=2)
    centered_text(draw, cx + 30, 22, "いってきます！", font(30), (255, 240, 50))


def stamp_02_tadaima(img, draw):
    """ただいま！ – arriving home"""
    cx, cy = 185, 160
    s = 1.0
    draw_legs(draw, cx, cy, -38, -10, 76, 60, s)
    draw_arm(draw, cx, cy, -38, -10, 76, 60, s, "left", "cheer", 0)
    draw_arm(draw, cx, cy, -38, -10, 76, 60, s, "right", "cheer", 0)
    hx, hy, hw, hh, bx, by, bw, bh = draw_robot_base(draw, cx, cy)
    draw_eyes_happy(draw, cx, cy, hx, hy, hw, hh)
    draw_sparkles(draw, [(cx - 60, cy - 80), (cx + 70, cy - 70), (cx - 50, cy - 40)], size=10)
    centered_text(draw, cx, 24, "ただいま！", font(34), (255, 240, 50))


def stamp_03_ohayou(img, draw):
    """おはよう – yawning, sleepy"""
    cx, cy = 185, 165
    s = 1.0
    draw_legs(draw, cx, cy, -38, -10, 76, 60, s)
    draw_arm(draw, cx, cy, -38, -10, 76, 60, s, "left", "normal")
    draw_arm(draw, cx, cy, -38, -10, 76, 60, s, "right", "think")
    hx, hy, hw, hh, bx, by, bw, bh = draw_robot_base(draw, cx, cy)
    # half-open eyes
    draw.line([(cx - 22, cy - 52), (cx - 8, cy - 52)], fill=PUPIL_COLOR, width=4)
    draw.line([(cx + 8, cy - 52), (cx + 22, cy - 52)], fill=PUPIL_COLOR, width=4)
    # sleepy z's
    for i, (zx, zy, zs) in enumerate([(cx + 52, cy - 80, 18), (cx + 64, cy - 96, 14)]):
        f = font(zs)
        bb = draw.textbbox((0, 0), "z", font=f)
        draw.text((zx - (bb[2] - bb[0]) // 2, zy), "z", font=f, fill=(150, 200, 255))
    centered_text(draw, cx, 24, "おはよう～", font(32), (180, 230, 255))


def stamp_04_oyasumi(img, draw):
    """おやすみ – sleeping"""
    cx, cy = 185, 165
    s = 1.0
    # tilted (sleeping)
    tilt = math.radians(18)
    draw_legs(draw, cx, cy, -38, -10, 76, 60, s, "normal", tilt)
    draw_arm(draw, cx, cy, -38, -10, 76, 60, s, "left", "down_l", tilt)
    draw_arm(draw, cx, cy, -38, -10, 76, 60, s, "right", "down_r", tilt)
    hx, hy, hw, hh, bx, by, bw, bh = draw_robot_base(draw, cx, cy, s, tilt)

    def pt(dx, dy):
        rx = dx * math.cos(tilt) - dy * math.sin(tilt)
        ry = dx * math.sin(tilt) + dy * math.cos(tilt)
        return (cx + rx, cy + ry)

    for ex_off in [-16 * s, 10 * s]:
        ex = hx + hw / 2 + ex_off
        ey = hy + hh / 2 - 2 * s
        draw.line([pt(ex - 10 * s, ey), pt(ex + 10 * s, ey)], fill=PUPIL_COLOR, width=4)
    # Z Z Z
    for i, (zx, zy, zs) in enumerate([(cx + 55, cy - 90, 22), (cx + 70, cy - 112, 18), (cx + 82, cy - 130, 14)]):
        f = font(zs)
        bb = draw.textbbox((0, 0), "Z", font=f)
        outline_text(draw, (zx - (bb[2] - bb[0]) // 2, zy), "Z", f, (150, 200, 255), (80, 80, 160))
    centered_text(draw, cx - 30, 20, "おやすみ…", font(30), (150, 200, 255))


def stamp_05_ganbare(img, draw):
    """がんばれ！ – cheering"""
    cx, cy = 185, 158
    s = 1.05
    draw_legs(draw, cx, cy, -38, -10, 76, 60, s, "jump")
    draw_arm(draw, cx, cy, -38, -10, 76, 60, s, "left", "cheer")
    draw_arm(draw, cx, cy, -38, -10, 76, 60, s, "right", "cheer")
    hx, hy, hw, hh, bx, by, bw, bh = draw_robot_base(draw, cx, cy, s)
    draw_eyes_happy(draw, cx, cy, hx, hy, hw, hh, s)
    draw_sparkles(draw, [(cx - 75, cy - 90), (cx + 82, cy - 85),
                          (cx - 65, cy - 50), (cx + 72, cy - 45)], size=12)
    centered_text(draw, cx, 20, "がんばれ！！", font(34), (255, 100, 100))


def stamp_06_arigatou(img, draw):
    """ありがとう – bowing"""
    cx, cy = 185, 175
    s = 1.0
    tilt = math.radians(28)
    draw_legs(draw, cx, cy, -38, -10, 76, 60, s, "normal", tilt)
    draw_arm(draw, cx, cy, -38, -10, 76, 60, s, "left", "normal", tilt)
    draw_arm(draw, cx, cy, -38, -10, 76, 60, s, "right", "normal", tilt)
    hx, hy, hw, hh, bx, by, bw, bh = draw_robot_base(draw, cx, cy, s, tilt)
    draw_eyes_normal(draw, cx, cy, hx, hy, hw, hh, s, tilt)
    draw_heart(draw, cx - 55, cy - 92, 18)
    draw_heart(draw, cx + 60, cy - 78, 14)
    centered_text(draw, cx + 20, 20, "ありがとう！", font(30), (255, 180, 200))


def draw_heart(draw, cx, cy, size, fill=(255, 100, 140), outline=(180, 50, 90)):
    """Draw a pixel heart shape."""
    s = size / 20
    pts = []
    for i, (dx, dy) in enumerate([
        (-3, -2), (-2, -3), (-1, -3), (0, -2), (1, -3), (2, -3), (3, -2),
        (3, -1), (3, 0), (2, 1), (1, 2), (0, 3), (-1, 2), (-2, 1),
        (-3, 0), (-3, -1),
    ]):
        pts.append((cx + dx * size // 3, cy + dy * size // 3))
    draw.polygon(pts, fill=fill)
    draw.polygon(pts, outline=outline, width=max(1, size // 14))


def stamp_07_daisuki(img, draw):
    """だいすき！ – holding a heart"""
    cx, cy = 185, 160
    s = 1.0
    draw_legs(draw, cx, cy, -38, -10, 76, 60, s)
    draw_arm(draw, cx, cy, -38, -10, 76, 60, s, "left", "cheer")
    draw_arm(draw, cx, cy, -38, -10, 76, 60, s, "right", "cheer")
    hx, hy, hw, hh, bx, by, bw, bh = draw_robot_base(draw, cx, cy)
    draw_eyes_happy(draw, cx, cy, hx, hy, hw, hh)
    # hearts floating around
    draw_heart(draw, cx - 68, cy - 100, 28)
    draw_heart(draw, cx + 72, cy - 95, 22)
    draw_heart(draw, cx, cy - 118, 18)
    centered_text(draw, cx, 22, "だいすき！", font(32), (255, 140, 180))


def stamp_08_yatta(img, draw):
    """やったー！！ – celebrating"""
    cx, cy = 185, 162
    s = 1.05
    tilt = math.radians(-8)
    draw_legs(draw, cx, cy, -38, -10, 76, 60, s, "jump", tilt)
    draw_arm(draw, cx, cy, -38, -10, 76, 60, s, "left", "cheer", tilt)
    draw_arm(draw, cx, cy, -38, -10, 76, 60, s, "right", "cheer", tilt)
    hx, hy, hw, hh, bx, by, bw, bh = draw_robot_base(draw, cx, cy, s, tilt)
    draw_eyes_happy(draw, cx, cy, hx, hy, hw, hh, s, tilt)
    draw_sparkles(draw, [(cx - 80, cy - 100), (cx + 88, cy - 92),
                          (cx - 70, cy - 60), (cx + 78, cy - 55),
                          (cx, cy - 115)],
                  color=(255, 200, 50), size=14)
    centered_text(draw, cx, 18, "やったー！！", font(36), (255, 220, 50))


def stamp_09_doushiyou(img, draw):
    """どうしよう… – worried"""
    cx, cy = 185, 162
    s = 1.0
    tilt = math.radians(8)
    draw_legs(draw, cx, cy, -38, -10, 76, 60, s, "normal", tilt)
    draw_arm(draw, cx, cy, -38, -10, 76, 60, s, "left", "normal", tilt)
    draw_arm(draw, cx, cy, -38, -10, 76, 60, s, "right", "think", tilt)
    hx, hy, hw, hh, bx, by, bw, bh = draw_robot_base(draw, cx, cy, s, tilt)
    draw_eyes_sad(draw, cx, cy, hx, hy, hw, hh, s, tilt)
    # sweat drop
    draw_sweat(draw, cx + 62, cy - 75, 12)
    # question mark
    f = font(32)
    outline_text(draw, (cx - 80, cy - 100), "？", f, (255, 200, 80), (80, 50, 20))
    centered_text(draw, cx - 10, 22, "どうしよう…", font(30), (200, 200, 255))


def stamp_10_haaai(img, draw):
    """はーい！ – raising hand"""
    cx, cy = 185, 158
    s = 1.0
    draw_legs(draw, cx, cy, -38, -10, 76, 60, s)
    draw_arm(draw, cx, cy, -38, -10, 76, 60, s, "left", "normal")
    draw_arm(draw, cx, cy, -38, -10, 76, 60, s, "right", "wave")
    hx, hy, hw, hh, bx, by, bw, bh = draw_robot_base(draw, cx, cy)
    draw_eyes_happy(draw, cx, cy, hx, hy, hw, hh)
    draw_sparkles(draw, [(cx + 62, cy - 110), (cx + 78, cy - 90)], size=8)
    centered_text(draw, cx + 10, 22, "はーい！", font(36), (255, 240, 100))


def stamp_11_kyuukei(img, draw):
    """休憩中 – sitting with coffee"""
    cx, cy = 185, 168
    s = 1.0
    # sitting legs
    draw.polygon([(cx - 40, cy + 50), (cx - 16, cy + 50),
                  (cx - 16, cy + 72), (cx - 40, cy + 72)],
                 fill=BODY_COLOR, outline=EDGE_COLOR, width=2)
    draw.polygon([(cx + 16, cy + 50), (cx + 40, cy + 50),
                  (cx + 40, cy + 72), (cx + 16, cy + 72)],
                 fill=BODY_COLOR, outline=EDGE_COLOR, width=2)
    draw_arm(draw, cx, cy, -38, -10, 76, 60, s, "left", "normal")
    draw_arm(draw, cx, cy, -38, -10, 76, 60, s, "right", "normal")
    hx, hy, hw, hh, bx, by, bw, bh = draw_robot_base(draw, cx, cy)
    draw_eyes_happy(draw, cx, cy, hx, hy, hw, hh)
    # coffee cup
    cup_x, cup_y = cx + 50, cy + 20
    draw.polygon([(cup_x, cup_y), (cup_x + 26, cup_y),
                  (cup_x + 22, cup_y + 30), (cup_x + 4, cup_y + 30)],
                 fill=(220, 120, 60), outline=EDGE_COLOR, width=2)
    # steam
    for i, sx in enumerate([cup_x + 6, cup_x + 13, cup_x + 20]):
        for j in range(3):
            draw.arc([(sx - 4, cup_y - 20 + j * 8 - i * 2),
                      (sx + 4, cup_y - 12 + j * 8 - i * 2)], 180, 0,
                     fill=(200, 200, 200), width=2)
    centered_text(draw, cx - 20, 22, "休憩中～", font(30), (200, 160, 100))


def stamp_12_yoroshiku(img, draw):
    """よろしく！ – friendly greeting"""
    cx, cy = 185, 158
    s = 1.0
    draw_legs(draw, cx, cy, -38, -10, 76, 60, s)
    draw_arm(draw, cx, cy, -38, -10, 76, 60, s, "left", "cheer")
    draw_arm(draw, cx, cy, -38, -10, 76, 60, s, "right", "wave")
    hx, hy, hw, hh, bx, by, bw, bh = draw_robot_base(draw, cx, cy)
    draw_eyes_happy(draw, cx, cy, hx, hy, hw, hh)
    draw_sparkles(draw, [(cx - 72, cy - 85), (cx + 78, cy - 80)], size=10)
    centered_text(draw, cx, 22, "よろしく！", font(32), (100, 230, 180))


def stamp_13_gomen(img, draw):
    """ごめんね – apologizing"""
    cx, cy = 185, 175
    s = 1.0
    tilt = math.radians(22)
    draw_legs(draw, cx, cy, -38, -10, 76, 60, s, "normal", tilt)
    draw_arm(draw, cx, cy, -38, -10, 76, 60, s, "left", "normal", tilt)
    draw_arm(draw, cx, cy, -38, -10, 76, 60, s, "right", "normal", tilt)
    hx, hy, hw, hh, bx, by, bw, bh = draw_robot_base(draw, cx, cy, s, tilt)
    draw_eyes_sad(draw, cx, cy, hx, hy, hw, hh, s, tilt)
    # tears
    draw.ellipse([(cx - 28, cy - 42), (cx - 22, cy - 36)], fill=(120, 180, 255))
    draw.ellipse([(cx + 16, cy - 40), (cx + 22, cy - 34)], fill=(120, 180, 255))
    # sweat
    draw_sweat(draw, cx + 65, cy - 70, 10)
    centered_text(draw, cx + 15, 20, "ごめんね…", font(30), (180, 220, 255))


def stamp_14_ok(img, draw):
    """OK！ – thumbs up pose"""
    cx, cy = 185, 158
    s = 1.0
    draw_legs(draw, cx, cy, -38, -10, 76, 60, s)
    draw_arm(draw, cx, cy, -38, -10, 76, 60, s, "left", "normal")
    # right arm with thumb up
    draw.polygon([(cx + 30, cy + 14), (cx + 50, cy + 14),
                  (cx + 50, cy - 20), (cx + 30, cy - 20)],
                 fill=BODY_COLOR, outline=EDGE_COLOR, width=2)
    draw.polygon([(cx + 26, cy - 24), (cx + 54, cy - 24),
                  (cx + 58, cy - 8), (cx + 22, cy - 8)],
                 fill=BODY_LIGHT, outline=EDGE_COLOR, width=2)
    hx, hy, hw, hh, bx, by, bw, bh = draw_robot_base(draw, cx, cy)
    draw_eyes_happy(draw, cx, cy, hx, hy, hw, hh)
    draw_sparkles(draw, [(cx + 72, cy - 38)], color=(255, 220, 50), size=12)
    centered_text(draw, cx - 10, 22, "OK！", font(42), (100, 220, 120))


def stamp_15_naruhodo(img, draw):
    """なるほど – thinking / nodding"""
    cx, cy = 185, 162
    s = 1.0
    tilt = math.radians(5)
    draw_legs(draw, cx, cy, -38, -10, 76, 60, s, "normal", tilt)
    draw_arm(draw, cx, cy, -38, -10, 76, 60, s, "left", "normal", tilt)
    draw_arm(draw, cx, cy, -38, -10, 76, 60, s, "right", "think", tilt)
    hx, hy, hw, hh, bx, by, bw, bh = draw_robot_base(draw, cx, cy, s, tilt)
    draw_eyes_normal(draw, cx, cy, hx, hy, hw, hh, s, tilt)
    # light-bulb (hand-drawn)
    bx2, by2 = cx + 52, cy - 120
    draw.ellipse([(bx2 - 14, by2 - 14), (bx2 + 14, by2 + 14)], fill=(255, 240, 80), outline=(180, 140, 0), width=2)
    draw.rectangle([(bx2 - 6, by2 + 10), (bx2 + 6, by2 + 20)], fill=(180, 180, 180), outline=(80, 80, 80), width=1)
    draw_sparkles(draw, [(bx2, by2)], color=(255, 220, 50), size=18)
    centered_text(draw, cx - 5, 20, "なるほど！", font(30), (255, 220, 100))


def stamp_16_otsukaresama(img, draw):
    """おつかれ！ – end of day, wave"""
    cx, cy = 185, 158
    s = 1.0
    tilt = math.radians(-4)
    draw_legs(draw, cx, cy, -38, -10, 76, 60, s, "run", tilt)
    draw_arm(draw, cx, cy, -38, -10, 76, 60, s, "left", "normal", tilt)
    draw_arm(draw, cx, cy, -38, -10, 76, 60, s, "right", "wave", tilt)
    hx, hy, hw, hh, bx, by, bw, bh = draw_robot_base(draw, cx, cy, s, tilt)
    draw_eyes_happy(draw, cx, cy, hx, hy, hw, hh, s, tilt)
    draw_sparkles(draw, [(cx + 68, cy - 80)], color=(255, 200, 50), size=10)
    centered_text(draw, cx + 20, 20, "おつかれ！", font(32), (255, 200, 120))


# ─────────────────────────── Tab image ────────────────────────────────────────

def make_tab():
    img = Image.new("RGBA", (TAB_W, TAB_H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    cx, cy = TAB_W // 2, TAB_H // 2 + 4
    s = 0.42
    hx, hy, hw, hh, bx, by, bw, bh = draw_robot_base(draw, cx, cy, s)
    draw_eyes_happy(draw, cx, cy, hx, hy, hw, hh, s)
    path = os.path.join(OUTPUT_DIR, "tab.png")
    img.save(path)
    print(f"  Saved {path}")


# ──────────────────────────────── Main ────────────────────────────────────────

STAMPS = [
    (1,  stamp_01_ittekimasu),
    (2,  stamp_02_tadaima),
    (3,  stamp_03_ohayou),
    (4,  stamp_04_oyasumi),
    (5,  stamp_05_ganbare),
    (6,  stamp_06_arigatou),
    (7,  stamp_07_daisuki),
    (8,  stamp_08_yatta),
    (9,  stamp_09_doushiyou),
    (10, stamp_10_haaai),
    (11, stamp_11_kyuukei),
    (12, stamp_12_yoroshiku),
    (13, stamp_13_gomen),
    (14, stamp_14_ok),
    (15, stamp_15_naruhodo),
    (16, stamp_16_otsukaresama),
]

if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print("Generating stamps…")
    for idx, fn in STAMPS:
        make_stamp(idx, fn)
    print("Generating tab image…")
    make_tab()
    print(f"Done! {len(STAMPS)} stamps + 1 tab → {OUTPUT_DIR}/")
