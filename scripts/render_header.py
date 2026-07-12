"""生成 assets/header-{dark,light}.svg：雷达扫描 header。

这是本仓库唯一的动画签名元素（设计定稿见 DESIGN.md §1/§6）。
设计期手动运行，产物提交进 main：
    python3 scripts/render_header.py
"""

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from svgkit import el, svg, text
from tokens import TOKENS, theme

W, H = 830, 170
CX, CY, R = 110, 85, 62
PERIOD = TOKENS["sweep_period_s"]
# 雷达回波点：(顺时针角度, 半径)，扫描线扫过对应角度时闪现
BLIPS = [(70, 38), (160, 52), (290, 30)]


def polar(deg, radius):
    rad = math.radians(deg)
    return CX + radius * math.sin(rad), CY - radius * math.cos(rad)


def build(mode):
    t = theme(mode)
    mono = TOKENS["font_mono"]
    parts = [
        el("rect", x=0.5, y=0.5, width=W - 1, height=H - 1,
           rx=TOKENS["radius"], fill=t["bg"], stroke=t["grid"]),
    ]

    # 雷达刻度环与十字线
    for radius in (20, 41, R):
        parts.append(el("circle", cx=CX, cy=CY, r=radius, fill="none",
                        stroke=t["grid"], stroke_width=1))
    parts.append(el("line", x1=CX - R, y1=CY, x2=CX + R, y2=CY,
                    stroke=t["grid"], stroke_width=1))
    parts.append(el("line", x1=CX, y1=CY - R, x2=CX, y2=CY + R,
                    stroke=t["grid"], stroke_width=1))

    # 扫描线 + 余辉（递减透明度的实线模拟，不用渐变），整组旋转
    sweep = [el("line", x1=CX, y1=CY, x2=CX, y2=CY - R,
                stroke=t["accent"], stroke_width=TOKENS["stroke"])]
    for i, off in enumerate((-7, -14, -21), start=1):
        x2, y2 = polar(off, R)
        sweep.append(el("line", x1=CX, y1=CY, x2=round(x2, 1), y2=round(y2, 1),
                        stroke=t["accent"], stroke_width=1,
                        opacity=round(0.38 - i * 0.11, 2)))
    parts.append(el("g", "".join(sweep), cls="sweep"))

    # 回波点：animation-delay 与扫描角度同步
    for deg, radius in BLIPS:
        x, y = polar(deg, radius)
        delay = round(deg / 360 * PERIOD, 2)
        parts.append(el("circle", cx=round(x, 1), cy=round(y, 1), r=3,
                        fill=t["accent"], cls="blip",
                        style=f"animation-delay:{delay}s"))

    # 文字区
    parts.append(text(210, 76, "QIAO", fill=t["ink"], font_family=mono,
                      font_size=TOKENS["fs_xl"], font_weight="bold",
                      letter_spacing=6))
    parts.append(text(212, 104, "AIR TRAFFIC CONTROL × AVIATION WEATHER × GIS",
                      fill=t["accent"], font_family=mono,
                      font_size=TOKENS["fs_md"], letter_spacing=3))
    parts.append(text(212, 128,
                      "Product manager who ships. Connecting the sky to the screen.",
                      fill=t["muted"], font_family=mono, font_size=TOKENS["fs_sm"]))

    style = (
        f".sweep{{transform-origin:{CX}px {CY}px;"
        f"animation:sweep {PERIOD}s linear infinite}}"
        "@keyframes sweep{from{transform:rotate(0deg)}to{transform:rotate(360deg)}}"
        f".blip{{opacity:0;animation:blip {PERIOD}s linear infinite}}"
        "@keyframes blip{0%{opacity:.9}18%{opacity:0}100%{opacity:0}}"
        "@media (prefers-reduced-motion:reduce){"
        ".sweep,.blip{animation:none}.blip{opacity:.55}}"
    )
    return svg(W, H, "".join(parts), style=style)


def main():
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")
    os.makedirs(out_dir, exist_ok=True)
    for mode in ("dark", "light"):
        path = os.path.normpath(os.path.join(out_dir, f"header-{mode}.svg"))
        with open(path, "w", encoding="utf-8") as f:
            f.write(build(mode))
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
