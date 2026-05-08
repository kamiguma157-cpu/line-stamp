"""
LINE stamp generator v2 – "ゆるロボ" series
Redrawn in the style of the ChatGPT reference image:
  • Rounded square head/body
  • Big round eyes + pink cheeks + smile
  • Jointed arms & legs, U-shaped hands
  • Warm beige palette with dark brown outline
"""

from PIL import Image, ImageDraw, ImageFont
import math
import os

STAMP_W, STAMP_H = 370, 320
TAB_W,   TAB_H   = 96,  74
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "output")
FONT_PATH  = "/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf"

# ── Palette ──────────────────────────────────────────────────────────────────
SKIN   = (210, 170, 110)
SKIN_D = (180, 140,  85)
SKIN_L = (235, 200, 155)
LINE   = ( 80,  50,  20)
CHEEK  = (255, 180, 165, 200)
EYE    = ( 45,  30,  15)
WHITE  = (255, 255, 255)
PANEL  = (190, 150,  90)
DOT1   = (130, 210, 200)
DOT2   = (240, 170, 170)

def font(size):
    try:
        return ImageFont.truetype(FONT_PATH, size)
    except Exception:
        return ImageFont.load_default()

def outline_text(draw, pos, text, fnt, fill, outline=(60, 30, 10), thickness=3):
    x, y = pos
    for dx in range(-thickness, thickness + 1):
        for dy in range(-thickness, thickness + 1):
            if dx != 0 or dy != 0:
                draw.text((x + dx, y + dy), text, font=fnt, fill=outline)
    draw.text(pos, text, font=fnt, fill=fill)

def centered_text(draw, cx, y, text, fnt, fill=(255, 255, 255), outline=(60, 30, 10)):
    bb = draw.textbbox((0, 0), text, font=fnt)
    w  = bb[2] - bb[0]
    outline_text(draw, (cx - w // 2, y), text, fnt, fill, outline, thickness=3)

# ── Primitive helpers ─────────────────────────────────────────────────────────
def rrect(draw, x0, y0, x1, y1, r, fill, outline=LINE, lw=2):
    """Rounded rectangle (polygon approximation)."""
    pts = []
    for cx2, cy2, a0, a1 in [
        (x0+r, y0+r, 180, 270), (x1-r, y0+r, 270, 360),
        (x1-r, y1-r,   0,  90), (x0+r, y1-r,  90, 180),
    ]:
        for a in range(a0, a1+1, 5):
            rad = math.radians(a)
            pts.append((cx2 + r*math.cos(rad), cy2 + r*math.sin(rad)))
    draw.polygon(pts, fill=fill)
    draw.polygon(pts, outline=outline, width=lw)

def circle(draw, cx, cy, r, fill, outline=LINE, lw=2):
    draw.ellipse([(cx-r, cy-r), (cx+r, cy+r)], fill=fill, outline=outline, width=lw)

def rect(draw, x0, y0, x1, y1, fill, outline=LINE, lw=2):
    draw.rectangle([(x0,y0),(x1,y1)], fill=fill, outline=outline, width=lw)

# ── Robot parts ───────────────────────────────────────────────────────────────
def draw_head(draw, cx, cy, expression="smile", tilt=0):
    """Head centred at (cx, cy).  Returns eye positions."""
    s = 1.0

    def rot(dx, dy):
        c, s2 = math.cos(tilt), math.sin(tilt)
        return (cx + dx*c - dy*s2, cy + dx*s2 + dy*c)

    # antenna
    ax, ay = rot(0, -54)
    rect(draw, ax-5, ay-12, ax+5, ay, SKIN, LINE, 2)

    # ear studs
    for side in [-1, 1]:
        ex, ey = rot(side*44, -10)
        circle(draw, ex, ey, 9, SKIN_D, LINE, 2)

    # head box
    hw, hh = 76, 60
    # approximate rotated rounded rect with polygon
    corners_local = [(-hw//2, -hh//2), (hw//2, -hh//2),
                     (hw//2,  hh//2),  (-hw//2, hh//2)]
    r = 8
    pts = []
    for i, (lx, ly) in enumerate(corners_local):
        nx, ny = corners_local[(i+1) % 4]
        ex2 = nx - lx; ey2 = ny - ly
        ln = math.hypot(ex2, ey2)
        ex2 /= ln; ey2 /= ln
        px, py = -ey2, ex2
        pts.append(rot(lx + ex2*r, ly + ey2*r))
        pts.append(rot(lx + px*0  , ly + py*0  ))   # keep sharp-ish
    draw.polygon(pts, fill=SKIN)
    draw.polygon(pts, outline=LINE, width=2)

    # eyes
    for side in [-1, 1]:
        ex, ey = rot(side*18, -8)
        circle(draw, ex, ey, 9, EYE)

        if expression == "smile" or expression == "happy":
            # shine dot
            sx, sy = rot(side*18 - 3*side, -13)
            circle(draw, sx, sy, 3, WHITE, WHITE, 0)
        elif expression == "wink" and side == 1:
            # wink: draw arc instead of circle
            draw.ellipse([(ex-9, ey-9), (ex+9, ey+9)], fill=SKIN)
            draw.arc([(ex-9, ey-3), (ex+9, ey+9)], 0, 180, fill=EYE, width=3)
        elif expression == "surprised":
            circle(draw, ex, ey, 11, EYE)
            circle(draw, ex-3*side, ey-3, 4, WHITE, WHITE, 0)
        elif expression == "sad":
            # droopy: small dot lower
            draw.ellipse([(ex-6, ey-3), (ex+6, ey+9)], fill=EYE)
        elif expression == "angry":
            circle(draw, ex, ey, 8, EYE)
            # brow
            bx0, by0 = rot(side*10, -22)
            bx1, by1 = rot(side*26, -18)
            if side == -1:
                draw.line([(bx0, by0), (bx1, by1)], fill=EYE, width=3)
            else:
                draw.line([(bx1, by1), (bx0, by0)], fill=EYE, width=3)
        elif expression == "sleep":
            # closed line
            draw.arc([(ex-9, ey-5), (ex+9, ey+5)], 200, 340, fill=EYE, width=3)
        elif expression == "dead":
            # x eyes
            draw.line([(ex-7, ey-7), (ex+7, ey+7)], fill=EYE, width=3)
            draw.line([(ex+7, ey-7), (ex-7, ey+7)], fill=EYE, width=3)

    # cheeks
    for side in [-1, 1]:
        chx, chy = rot(side*28, 4)
        chimg = Image.new("RGBA", (20, 12), (0,0,0,0))
        chd   = ImageDraw.Draw(chimg)
        chd.ellipse([(0,0),(19,11)], fill=CHEEK)
        draw._image.paste(chimg, (int(chx-10), int(chy-6)), chimg)

    # mouth
    mx, my = rot(0, 14)
    if expression in ("smile", "happy", "wink", "surprised"):
        draw.arc([(mx-12, my-8), (mx+12, my+8)], 10, 170, fill=EYE, width=3)
        if expression == "surprised":
            # open mouth
            draw.ellipse([(mx-8, my-4), (mx+8, my+8)], fill=EYE)
    elif expression == "sad":
        draw.arc([(mx-10, my-4), (mx+10, my+12)], 190, 350, fill=EYE, width=3)
    elif expression == "angry":
        draw.arc([(mx-10, my-4), (mx+10, my+12)], 190, 350, fill=EYE, width=3)
    elif expression == "sleep":
        draw.arc([(mx-10, my-6), (mx+10, my+6)], 10, 170, fill=EYE, width=2)
    else:
        draw.arc([(mx-10, my-6), (mx+10, my+6)], 10, 170, fill=EYE, width=3)

    return tilt  # for callers that need it


def draw_body(draw, cx, cy, tilt=0):
    def rot(dx, dy):
        c, s2 = math.cos(tilt), math.sin(tilt)
        return (cx + dx*c - dy*s2, cy + dx*s2 + dy*c)

    bw, bh = 72, 60
    corners = [(-bw//2,-bh//2),(bw//2,-bh//2),(bw//2,bh//2),(-bw//2,bh//2)]
    pts = [rot(lx, ly) for lx, ly in corners]
    draw.polygon(pts, fill=SKIN)
    draw.polygon(pts, outline=LINE, width=2)

    # panel
    px, py = rot(-16, -5)
    draw.rectangle([(px-10, py-8), (px+10, py+8)], fill=PANEL, outline=LINE, width=1)
    draw.rectangle([(px-7, py-5), (px+7, py+5)], fill=SKIN_D, outline=LINE, width=1)
    for i in range(3):
        draw.rectangle([(px-5+i*4, py-2), (px-3+i*4, py+2)], fill=LINE)

    # dots
    d1x, d1y = rot(10, -2)
    d2x, d2y = rot(22, -2)
    circle(draw, d1x, d1y, 6, DOT1, LINE, 1)
    circle(draw, d2x, d2y, 6, DOT2, LINE, 1)


def draw_neck(draw, cx, cy, tilt=0):
    def rot(dx, dy):
        c, s2 = math.cos(tilt), math.sin(tilt)
        return (cx + dx*c - dy*s2, cy + dx*s2 + dy*c)
    pts = [rot(-6,-10), rot(6,-10), rot(6,10), rot(-6,10)]
    draw.polygon(pts, fill=SKIN_D, outline=LINE, width=2)


def draw_arm(draw, cx, cy, side, pose="rest", tilt=0):
    """side: -1=left, +1=right"""
    def rot(dx, dy):
        c, s2 = math.cos(tilt), math.sin(tilt)
        return (cx + dx*c - dy*s2, cy + dx*s2 + dy*c)

    sx = side * 44   # shoulder x offset
    sy = -16          # shoulder y

    if pose == "rest":
        # upper arm down, forearm down
        segs = [(sx, sy, sx, sy+30), (sx, sy+30, sx+side*4, sy+58)]
        hand_cx, hand_cy = sx+side*4, sy+62
    elif pose == "wave":
        # arm raised, hand at top
        segs = [(sx, sy, sx+side*14, sy-30), (sx+side*14, sy-30, sx+side*22, sy-56)]
        hand_cx, hand_cy = sx+side*22, sy-62
    elif pose == "raise":
        segs = [(sx, sy, sx+side*8, sy-28), (sx+side*8, sy-28, sx+side*12, sy-54)]
        hand_cx, hand_cy = sx+side*12, sy-60
    elif pose == "cheer":
        segs = [(sx, sy, sx+side*10, sy-32), (sx+side*10, sy-32, sx+side*14, sy-60)]
        hand_cx, hand_cy = sx+side*14, sy-66
    elif pose == "hip":
        segs = [(sx, sy, sx+side*28, sy+14), (sx+side*28, sy+14, sx+side*30, sy+36)]
        hand_cx, hand_cy = sx+side*30, sy+40
    elif pose == "scratch":
        segs = [(sx, sy, sx+side*10, sy-14), (sx+side*10, sy-14, sx+side*6, sy+10)]
        hand_cx, hand_cy = sx+side*6, sy+14
    elif pose == "think":
        segs = [(sx, sy, sx+side*18, sy+10), (sx+side*18, sy+10, sx+side*14, sy-12)]
        hand_cx, hand_cy = sx+side*14, sy-18
    elif pose == "down":
        segs = [(sx, sy, sx+side*4, sy+34), (sx+side*4, sy+34, sx+side*2, sy+58)]
        hand_cx, hand_cy = sx+side*2, sy+64
    elif pose == "hug":
        segs = [(sx, sy, sx+side*20, sy+18), (sx+side*20, sy+18, sx+side*10, sy+30)]
        hand_cx, hand_cy = sx+side*10, sy+36
    elif pose == "thumbup":
        segs = [(sx, sy, sx+side*26, sy+10), (sx+side*26, sy+10, sx+side*30, sy+34)]
        hand_cx, hand_cy = sx+side*30, sy+28
        # draw thumb
        tx, ty = rot(sx+side*36, sy+20)
        circle(draw, tx, ty, 7, SKIN, LINE, 2)
    else:
        segs = [(sx, sy, sx, sy+30), (sx, sy+30, sx+side*4, sy+58)]
        hand_cx, hand_cy = sx+side*4, sy+62

    # draw segments as thick rounded lines
    for (x0,y0,x1,y1) in segs:
        p0 = rot(x0, y0)
        p1 = rot(x1, y1)
        draw.line([p0, p1], fill=SKIN, width=14)
        draw.line([p0, p1], fill=LINE, width=2)
        circle(draw, p0[0], p0[1], 7, SKIN_D, LINE, 1)
        circle(draw, p1[0], p1[1], 7, SKIN_D, LINE, 1)

    # U-shaped hand (claw)
    hcx, hcy = rot(hand_cx, hand_cy)
    angle = math.atan2(hand_cy - segs[-1][3], hand_cx - segs[-1][2])
    for finger in [-1, 0, 1]:
        fx = hcx + finger * 8 * math.cos(angle + math.pi/2)
        fy = hcy + finger * 8 * math.sin(angle + math.pi/2)
        draw.ellipse([(fx-5, fy-5), (fx+5, fy+5)], fill=SKIN, outline=LINE, width=1)
    circle(draw, hcx, hcy, 9, SKIN, LINE, 2)


def draw_leg(draw, cx, cy, side, pose="stand", tilt=0):
    def rot(dx, dy):
        c, s2 = math.cos(tilt), math.sin(tilt)
        return (cx + dx*c - dy*s2, cy + dx*s2 + dy*c)

    lx = side * 20
    ly = 30  # hip

    if pose == "stand":
        segs = [(lx, ly, lx, ly+30), (lx, ly+30, lx, ly+58)]
        foot_cx, foot_cy = lx, ly+64
    elif pose == "walk":
        lean = side * 0.2
        segs = [(lx, ly, lx+side*8, ly+28), (lx+side*8, ly+28, lx+side*18, ly+52)]
        foot_cx, foot_cy = lx+side*18, ly+60
    elif pose == "run":
        segs = [(lx, ly, lx+side*14, ly+24), (lx+side*14, ly+24, lx+side*4, ly+50)]
        foot_cx, foot_cy = lx+side*4, ly+58
    elif pose == "jump":
        segs = [(lx, ly, lx+side*10, ly+22), (lx+side*10, ly+22, lx+side*18, ly+40)]
        foot_cx, foot_cy = lx+side*18, ly+48
    elif pose == "sit":
        segs = [(lx, ly, lx+side*26, ly+8), (lx+side*26, ly+8, lx+side*40, ly+26)]
        foot_cx, foot_cy = lx+side*42, ly+30
    elif pose == "sleep":
        segs = [(lx, ly, lx+side*28, ly+6), (lx+side*28, ly+6, lx+side*48, ly+14)]
        foot_cx, foot_cy = lx+side*52, ly+16
    else:
        segs = [(lx, ly, lx, ly+30), (lx, ly+30, lx, ly+58)]
        foot_cx, foot_cy = lx, ly+64

    for (x0,y0,x1,y1) in segs:
        p0 = rot(x0, y0)
        p1 = rot(x1, y1)
        draw.line([p0, p1], fill=SKIN, width=16)
        draw.line([p0, p1], fill=LINE, width=2)
        circle(draw, p0[0], p0[1], 8, SKIN_D, LINE, 1)
        circle(draw, p1[0], p1[1], 8, SKIN_D, LINE, 1)

    # foot (blocky rectangle)
    fx, fy = rot(foot_cx, foot_cy)
    fa = math.atan2(segs[-1][3]-segs[-1][1], segs[-1][2]-segs[-1][0]) + tilt
    fw, fh = 22, 12
    fc = [
        (fx + (-fw//2)*math.cos(fa) - (-fh//2)*math.sin(fa),
         fy + (-fw//2)*math.sin(fa) + (-fh//2)*math.cos(fa)),
        (fx + ( fw//2)*math.cos(fa) - (-fh//2)*math.sin(fa),
         fy + ( fw//2)*math.sin(fa) + (-fh//2)*math.cos(fa)),
        (fx + ( fw//2)*math.cos(fa) - ( fh//2)*math.sin(fa),
         fy + ( fw//2)*math.sin(fa) + ( fh//2)*math.cos(fa)),
        (fx + (-fw//2)*math.cos(fa) - ( fh//2)*math.sin(fa),
         fy + (-fw//2)*math.sin(fa) + ( fh//2)*math.cos(fa)),
    ]
    draw.polygon(fc, fill=SKIN_D, outline=LINE, width=2)


def draw_robot(draw, cx, cy, expression="smile",
               arm_l="rest", arm_r="rest",
               leg_l="stand", leg_r="stand",
               tilt=0, scale=1.0):
    """Draw complete robot centred at (cx, cy)."""
    # scale transform: shift (cx,cy) then scale local coords
    # We bake scale into helper positions by adjusting cx/cy offsets.
    # Simpler: draw at cx,cy with parts offset, then PIL doesn't support
    # per-object scale easily – so just call with scaled offsets.
    # For simplicity, build on fixed scale and rely on reasonable stamp layout.

    # legs (drawn first / behind)
    draw_leg(draw, cx, cy, -1, leg_l, tilt)
    draw_leg(draw, cx, cy,  1, leg_r, tilt)

    # arms (behind body for 'rest', in front for 'raise'/'cheer')
    behind_arms = arm_l in ("rest","down","hip","hug") and arm_r in ("rest","down","hip","hug")
    if behind_arms:
        draw_arm(draw, cx, cy, -1, arm_l, tilt)
        draw_arm(draw, cx, cy,  1, arm_r, tilt)

    # body
    draw_neck(draw, cx, cy - 52, tilt)
    draw_body(draw, cx, cy, tilt)

    # arms in front
    if not behind_arms:
        draw_arm(draw, cx, cy, -1, arm_l, tilt)
        draw_arm(draw, cx, cy,  1, arm_r, tilt)

    # head
    draw_head(draw, cx, cy - 88, expression, tilt)


# ── Decoration helpers ────────────────────────────────────────────────────────
def sparkles(draw, positions, color=(255, 210, 50), size=10):
    for sx, sy in positions:
        for a in range(0, 360, 45):
            rad = math.radians(a)
            ex = sx + size * math.cos(rad)
            ey = sy + size * math.sin(rad)
            draw.line([(sx, sy), (ex, ey)], fill=color, width=2)

def heart(draw, cx, cy, size=20, fill=(255, 100, 140)):
    unit = size / 3
    pts = []
    for dx, dy in [
        (-3,-2),(-2,-3),(-1,-3),(0,-2),(1,-3),(2,-3),(3,-2),
        (3,-1),(3,0),(2,1),(1,2),(0,3),(-1,2),(-2,1),(-3,0),(-3,-1),
    ]:
        pts.append((cx + dx*unit, cy + dy*unit))
    draw.polygon(pts, fill=fill)
    draw.polygon(pts, outline=(180, 60, 90), width=max(1, size//12))

def sweat(draw, cx, cy, size=14):
    pts = [(cx + size*0.5*math.cos(math.radians(a)),
            cy + size*math.sin(math.radians(a)) - size*0.3)
           for a in range(0, 360, 12)]
    pts[0] = (cx, cy - size)
    draw.polygon(pts, fill=(120, 180, 255, 200))
    draw.polygon(pts, outline=(60, 120, 200), width=1)

def tears(draw, cx, cy):
    for tx, ty in [(cx-20, cy+10), (cx+20, cy+10)]:
        draw.ellipse([(tx-4, ty-4),(tx+4, ty+12)], fill=(100, 170, 255))


def make_stamp(idx, draw_fn):
    img = Image.new("RGBA", (STAMP_W, STAMP_H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw_fn(img, draw)
    path = os.path.join(OUTPUT_DIR, f"stamp_{idx:02d}.png")
    img.save(path)
    print(f"  Saved {path}")


# ── 16 Stamps ─────────────────────────────────────────────────────────────────
def s01(img, draw):   # いってきます！
    cx, cy = 180, 172
    draw_robot(draw, cx, cy, "smile", arm_l="rest", arm_r="wave", leg_l="walk", leg_r="walk", tilt=math.radians(-5))
    for i in range(3):
        draw.line([(cx-95-i*14, cy-30+i*20),(cx-65-i*14, cy-30+i*20)], fill=(180,140,80,160), width=2)
    centered_text(draw, cx+30, 18, "いってきます！", font(28), (255, 230, 50))

def s02(img, draw):   # ただいま！
    cx, cy = 185, 170
    draw_robot(draw, cx, cy, "happy", arm_l="cheer", arm_r="cheer")
    sparkles(draw, [(cx-70,cy-130),(cx+78,cy-125),(cx-55,cy-90),(cx+62,cy-85)], size=11)
    centered_text(draw, cx, 18, "ただいま！", font(32), (255, 230, 50))

def s03(img, draw):   # おはよう～
    cx, cy = 185, 172
    draw_robot(draw, cx, cy, "sleep", arm_l="rest", arm_r="scratch", tilt=math.radians(6))
    for i, (zx, zy, zs) in enumerate([(cx+60,cy-118,20),(cx+74,cy-136,16),(cx+86,cy-150,13)]):
        outline_text(draw, (zx, zy), "z", font(zs), (160, 210, 255), (80, 100, 160))
    centered_text(draw, cx-15, 18, "おはよう～", font(30), (160, 215, 255))

def s04(img, draw):   # おやすみ…
    cx, cy = 190, 195
    draw_robot(draw, cx, cy, "sleep", arm_l="sleep", arm_r="sleep",
               leg_l="sleep", leg_r="sleep", tilt=math.radians(20))
    for i, (zx, zy, zs) in enumerate([(cx+52,cy-80,22),(cx+68,cy-98,18),(cx+82,cy-114,14)]):
        outline_text(draw, (zx, zy), "Z", font(zs), (160, 210, 255), (80, 100, 160))
    centered_text(draw, cx-35, 16, "おやすみ…", font(30), (160, 215, 255))

def s05(img, draw):   # がんばれ！！
    cx, cy = 185, 168
    draw_robot(draw, cx, cy, "happy", arm_l="cheer", arm_r="cheer", leg_l="jump", leg_r="jump")
    sparkles(draw, [(cx-82,cy-138),(cx+90,cy-132),(cx-68,cy-96),(cx+76,cy-90)],
             color=(255, 80, 80), size=13)
    centered_text(draw, cx, 16, "がんばれ！！", font(34), (255, 80, 80))

def s06(img, draw):   # ありがとう！
    cx, cy = 185, 178
    draw_robot(draw, cx, cy, "smile", arm_l="down", arm_r="down", tilt=math.radians(28))
    heart(draw, cx-55, cy-115, 20)
    heart(draw, cx+62, cy-108, 16)
    centered_text(draw, cx+18, 18, "ありがとう！", font(28), (255, 180, 200))

def s07(img, draw):   # だいすき！
    cx, cy = 185, 170
    draw_robot(draw, cx, cy, "happy", arm_l="cheer", arm_r="cheer")
    heart(draw, cx-74, cy-128, 26)
    heart(draw, cx+78, cy-122, 22)
    heart(draw, cx, cy-148, 18)
    centered_text(draw, cx, 18, "だいすき！", font(32), (255, 130, 170))

def s08(img, draw):   # やったー！！
    cx, cy = 185, 165
    draw_robot(draw, cx, cy, "happy", arm_l="cheer", arm_r="cheer",
               leg_l="jump", leg_r="jump", tilt=math.radians(-7))
    sparkles(draw, [(cx-82,cy-135),(cx+88,cy-128),(cx-65,cy-95),(cx+72,cy-88),(cx,cy-155)],
             color=(255, 210, 50), size=14)
    centered_text(draw, cx, 16, "やったー！！", font(36), (255, 210, 50))

def s09(img, draw):   # どうしよう…
    cx, cy = 185, 172
    draw_robot(draw, cx, cy, "sad", arm_l="scratch", arm_r="think", tilt=math.radians(7))
    sweat(draw, cx+68, cy-90, 13)
    outline_text(draw, (cx-88, cy-118), "？", font(34), (255, 200, 80), (80, 50, 20))
    centered_text(draw, cx-8, 18, "どうしよう…", font(28), (200, 200, 255))

def s10(img, draw):   # はーい！
    cx, cy = 185, 172
    draw_robot(draw, cx, cy, "smile", arm_l="rest", arm_r="wave")
    sparkles(draw, [(cx+72, cy-132), (cx+86, cy-112)], size=9)
    centered_text(draw, cx+12, 18, "はーい！", font(36), (255, 235, 80))

def s11(img, draw):   # 休憩中～
    cx, cy = 185, 175
    draw_robot(draw, cx, cy, "smile", arm_l="rest", arm_r="rest",
               leg_l="sit", leg_r="sit")
    # coffee cup
    cpx, cpy = cx+62, cy+22
    pts = [(cpx,cpy),(cpx+28,cpy),(cpx+24,cpy+32),(cpx+4,cpy+32)]
    draw.polygon(pts, fill=(210, 120, 60), outline=LINE, width=2)
    rect(draw, cpx+2, cpy, cpx+26, cpy+6, (230, 200, 160), LINE, 1)
    for i, sx2 in enumerate([cpx+7, cpx+14, cpx+21]):
        draw.arc([(sx2-4, cpy-18+i*2),(sx2+4, cpy-10+i*2)], 180, 0, fill=(200,200,200), width=2)
    centered_text(draw, cx-22, 18, "休憩中～", font(30), (200, 160, 100))

def s12(img, draw):   # よろしく！
    cx, cy = 185, 170
    draw_robot(draw, cx, cy, "smile", arm_l="raise", arm_r="wave")
    sparkles(draw, [(cx-72, cy-120), (cx+80, cy-115)], size=10)
    centered_text(draw, cx, 18, "よろしく！", font(32), (100, 220, 170))

def s13(img, draw):   # ごめんね…
    cx, cy = 185, 178
    draw_robot(draw, cx, cy, "sad", arm_l="down", arm_r="down", tilt=math.radians(22))
    tears(draw, cx + 20, cy - 90)
    sweat(draw, cx+68, cy-82, 10)
    centered_text(draw, cx+14, 18, "ごめんね…", font(30), (160, 210, 255))

def s14(img, draw):   # OK！
    cx, cy = 185, 172
    draw_robot(draw, cx, cy, "wink", arm_l="rest", arm_r="thumbup")
    sparkles(draw, [(cx+78, cy-55)], color=(255, 210, 50), size=13)
    centered_text(draw, cx-8, 18, "OK！", font(44), (100, 220, 120))

def s15(img, draw):   # なるほど！
    cx, cy = 185, 172
    draw_robot(draw, cx, cy, "smile", arm_l="rest", arm_r="think", tilt=math.radians(4))
    # lightbulb
    bx2, by2 = cx+58, cy-128
    circle(draw, bx2, by2, 14, (255, 240, 80), (160, 130, 0), 2)
    rect(draw, bx2-6, by2+10, bx2+6, by2+20, (180,180,180), LINE, 1)
    sparkles(draw, [(bx2, by2)], color=(255, 220, 50), size=18)
    centered_text(draw, cx-5, 18, "なるほど！", font(30), (255, 215, 80))

def s16(img, draw):   # おつかれ！
    cx, cy = 182, 170
    draw_robot(draw, cx, cy, "smile", arm_l="rest", arm_r="wave",
               leg_l="run", leg_r="run", tilt=math.radians(-4))
    for i in range(3):
        draw.line([(cx-95-i*12, cy-22+i*18),(cx-62-i*12, cy-22+i*18)],
                  fill=(180,140,80,160), width=2)
    sparkles(draw, [(cx+74, cy-98)], color=(255, 200, 50), size=10)
    centered_text(draw, cx+22, 18, "おつかれ！", font(30), (255, 195, 100))


STAMPS = [
    (1, s01),(2, s02),(3, s03),(4, s04),
    (5, s05),(6, s06),(7, s07),(8, s08),
    (9, s09),(10,s10),(11,s11),(12,s12),
    (13,s13),(14,s14),(15,s15),(16,s16),
]

def make_tab():
    img  = Image.new("RGBA", (TAB_W, TAB_H), (0,0,0,0))
    draw = ImageDraw.Draw(img)
    cx, cy = TAB_W//2, TAB_H//2 + 8
    draw_head(draw, cx, cy-24, "smile")
    draw_neck(draw, cx, cy-14)
    # tiny body
    rrect(draw, cx-18, cy-12, cx+18, cy+18, 4, SKIN, LINE, 1)
    path = os.path.join(OUTPUT_DIR, "tab.png")
    img.save(path)
    print(f"  Saved {path}")

if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print("Generating stamps v2…")
    for idx, fn in STAMPS:
        make_stamp(idx, fn)
    print("Generating tab…")
    make_tab()
    print(f"Done! → {OUTPUT_DIR}/")
