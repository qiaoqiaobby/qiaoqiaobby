"""拉取北京未来 24 小时 ECMWF IFS 预报（Open-Meteo，CC-BY 4.0），渲染风温 SVG 图。

用法：python3 scripts/render_wind.py [输出目录，默认 dist]
失败语义：任何一步失败即以非零码退出且不写文件，workflow 据此保留旧图。
"""

import json
import math
import os
import sys
import time
import urllib.request
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from svgkit import el, svg, text
from tokens import TOKENS, theme

API = (
    "https://api.open-meteo.com/v1/forecast"
    "?latitude=39.9042&longitude=116.4074"
    "&hourly=temperature_2m,wind_speed_10m,wind_direction_10m"
    "&wind_speed_unit=kn&timezone=Asia%2FShanghai&forecast_days=2"
    "&models=ecmwf_ifs025"
)
UA = "qiaoqiaobby-profile-readme (https://github.com/qiaoqiaobby/qiaoqiaobby)"
W, H = 830, 260
PLOT_L, PLOT_R = 56, 806
TEMP_TOP, TEMP_BOT = 52, 120
WIND_TOP, WIND_BOT = 158, 224
BARB_Y = 139
HOURS = 24


def fetch():
    last_err = None
    for attempt in range(3):
        try:
            req = urllib.request.Request(API, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=15) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as err:
            last_err = err
            if attempt < 2:
                time.sleep(5 * (attempt + 1))
    raise last_err


def slice_next_24h(payload):
    hourly = payload["hourly"]
    times = hourly["time"]
    now_bjt = datetime.now(timezone(timedelta(hours=8))).strftime("%Y-%m-%dT%H:00")
    start = times.index(now_bjt) if now_bjt in times else 0
    end = start + HOURS
    series = {
        "time": times[start:end],
        "temp": hourly["temperature_2m"][start:end],
        "wspd": hourly["wind_speed_10m"][start:end],
        "wdir": hourly["wind_direction_10m"][start:end],
    }
    if len(series["time"]) < HOURS or any(
        v is None for v in series["temp"] + series["wspd"] + series["wdir"]
    ):
        raise ValueError("incomplete hourly series")
    return series


def nice_ticks(vmin, vmax, target=4):
    span = max(vmax - vmin, 1e-6)
    raw_step = span / target
    magnitude = 10 ** math.floor(math.log10(raw_step))
    step = next(m * magnitude for m in (1, 2, 5, 10) if m * magnitude >= raw_step)
    low = math.floor(vmin / step) * step
    ticks = []
    value = low
    while value <= vmax + step * 0.5:
        ticks.append(round(value, 6))
        value += step
    return ticks


def x_at(index):
    return PLOT_L + index * (PLOT_R - PLOT_L) / (HOURS - 1)


def panel(values, top, bottom, color, t):
    ticks = nice_ticks(min(values), max(values))
    lo, hi = ticks[0], ticks[-1]
    parts = []
    for tick in ticks:
        y = bottom - (tick - lo) * (bottom - top) / (hi - lo)
        parts.append(el("line", x1=PLOT_L, y1=round(y, 1), x2=PLOT_R,
                        y2=round(y, 1), stroke=t["grid"], stroke_width=1))
        label = f"{tick:g}"
        parts.append(text(PLOT_L - 8, round(y + 4, 1), label, fill=t["muted"],
                          font_family=TOKENS["font_mono"],
                          font_size=TOKENS["fs_sm"], text_anchor="end"))
    points = " ".join(
        f"{round(x_at(i), 1)},{round(bottom - (v - lo) * (bottom - top) / (hi - lo), 1)}"
        for i, v in enumerate(values)
    )
    parts.append(el("polyline", points=points, fill="none", stroke=color,
                    stroke_width=TOKENS["stroke"], stroke_linejoin="round"))
    return "".join(parts)


def wind_barb(cx, cy, wdir, spd_kt, color):
    """标准风羽：杆指向风的来向；长羽 10 kt、短羽 5 kt、三角旗 50 kt。"""
    speed = int(round(spd_kt / 5.0)) * 5
    if speed < 5:
        return el("circle", cx=cx, cy=cy, r=2.5, fill="none", stroke=color,
                  stroke_width=1)
    rad = math.radians(wdir)
    ux, uy = math.sin(rad), -math.cos(rad)           # 指向来向的单位向量
    brad = math.radians(wdir + 65)
    bx, by = math.sin(brad), -math.cos(brad)         # 羽支方向
    staff = 13.0
    tip_x, tip_y = cx + staff * ux, cy + staff * uy
    parts = [el("line", x1=cx, y1=cy, x2=round(tip_x, 1), y2=round(tip_y, 1),
                stroke=color, stroke_width=1)]
    pennants, rest = divmod(speed, 50)
    fulls, rest = divmod(rest, 10)
    halves = rest // 5
    pos = staff
    for _ in range(pennants):
        p1 = (cx + pos * ux, cy + pos * uy)
        p2 = (cx + (pos - 3.5) * ux, cy + (pos - 3.5) * uy)
        p3 = (p1[0] + 6 * bx, p1[1] + 6 * by)
        d = (f"M{p1[0]:.1f},{p1[1]:.1f} L{p3[0]:.1f},{p3[1]:.1f} "
             f"L{p2[0]:.1f},{p2[1]:.1f} Z")
        parts.append(el("path", d=d, fill=color))
        pos -= 4.5
    for _ in range(fulls):
        sx, sy = cx + pos * ux, cy + pos * uy
        parts.append(el("line", x1=round(sx, 1), y1=round(sy, 1),
                        x2=round(sx + 6.5 * bx, 1), y2=round(sy + 6.5 * by, 1),
                        stroke=color, stroke_width=1))
        pos -= 3.0
    for _ in range(halves):
        sx, sy = cx + pos * ux, cy + pos * uy
        parts.append(el("line", x1=round(sx, 1), y1=round(sy, 1),
                        x2=round(sx + 3.5 * bx, 1), y2=round(sy + 3.5 * by, 1),
                        stroke=color, stroke_width=1))
        pos -= 3.0
    return el("g", "".join(parts))


def build(mode, series):
    t = theme(mode)
    mono = TOKENS["font_mono"]
    parts = [
        el("rect", x=0.5, y=0.5, width=W - 1, height=H - 1,
           rx=TOKENS["radius"], fill=t["bg"], stroke=t["grid"]),
        text(24, 32, "BEIJING · 24 H FORECAST · BJT (UTC+8)", fill=t["ink"],
             font_family=mono, font_size=TOKENS["fs_md"], font_weight="bold",
             letter_spacing=1),
    ]
    # 图例（两条序列各自的色相标识）
    parts.append(el("line", x1=560, y1=27, x2=580, y2=27,
                    stroke=t["series_temp"], stroke_width=TOKENS["stroke"]))
    parts.append(text(586, 31, "2 m temp °C", fill=t["muted"], font_family=mono,
                      font_size=TOKENS["fs_sm"]))
    parts.append(el("line", x1=692, y1=27, x2=712, y2=27,
                    stroke=t["series_wind"], stroke_width=TOKENS["stroke"]))
    parts.append(text(718, 31, "10 m wind kt", fill=t["muted"], font_family=mono,
                      font_size=TOKENS["fs_sm"]))

    parts.append(panel(series["temp"], TEMP_TOP, TEMP_BOT, t["series_temp"], t))
    parts.append(panel(series["wspd"], WIND_TOP, WIND_BOT, t["series_wind"], t))

    # 每 3 小时一支风羽 + x 轴时标
    for i in range(0, HOURS, 3):
        cx = x_at(i)
        parts.append(wind_barb(round(cx, 1), BARB_Y, series["wdir"][i],
                               series["wspd"][i], t["series_wind"]))
        parts.append(text(round(cx, 1), 240, series["time"][i][11:13],
                          fill=t["muted"], font_family=mono,
                          font_size=TOKENS["fs_sm"], text_anchor="middle"))
    generated = time.strftime("%Y-%m-%d %H:%MZ", time.gmtime())
    parts.append(text(24, 254,
                      f"ECMWF IFS via Open-Meteo (CC-BY 4.0) · generated {generated}"
                      " · refreshed daily by GitHub Actions",
                      fill=t["muted"], font_family=mono, font_size=TOKENS["fs_sm"]))
    return svg(W, H, "".join(parts))


def main():
    out_dir = sys.argv[1] if len(sys.argv) > 1 else "dist"
    series = slice_next_24h(fetch())
    rendered = {mode: build(mode, series) for mode in ("dark", "light")}
    os.makedirs(out_dir, exist_ok=True)
    for mode, content in rendered.items():
        path = os.path.join(out_dir, f"wind-beijing-{mode}.svg")
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"wrote {path}")


if __name__ == "__main__":
    try:
        main()
    except Exception as err:  # 失败不产文件，保留旧图
        print(f"render_wind failed: {err}", file=sys.stderr)
        sys.exit(1)
