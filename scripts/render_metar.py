"""拉取 ZBAA METAR（aviationweather.gov 免密钥公开 API），渲染明暗两张 SVG 卡。

用法：python3 scripts/render_metar.py [输出目录，默认 dist]
失败语义：任何一步失败即以非零码退出且不写文件，workflow 据此保留旧卡
（卡内 OBS 时间戳即数据年龄，时效外显）。
"""

import json
import os
import sys
import time
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from svgkit import el, svg, text
from tokens import TOKENS, theme

STATION = "ZBAA"
STATION_NAME = "BEIJING CAPITAL INTL"
API = f"https://aviationweather.gov/api/data/metar?ids={STATION}&format=json"
UA = "qiaoqiaobby-profile-readme (https://github.com/qiaoqiaobby/qiaoqiaobby)"
W, H = 830, 200
CATEGORY_ORDER = ["VFR", "MVFR", "IFR", "LIFR"]


def fetch():
    last_err = None
    for attempt in range(3):
        try:
            req = urllib.request.Request(API, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            if not data:
                raise ValueError("empty METAR response")
            return data[0]
        except Exception as err:  # 统一重试语义
            last_err = err
            if attempt < 2:
                time.sleep(5 * (attempt + 1))
    raise last_err


def parse_visibility(value):
    """visib 形如 6、"6+"、"10+"（法定英里）；无法解析返回 None。"""
    if value is None:
        return None
    try:
        return float(str(value).rstrip("+"))
    except ValueError:
        return None


def flight_category(report):
    """FAA 标准阈值：LIFR ceiling<500ft 或 vis<1SM；IFR <1000/<3；MVFR ≤3000/≤5。"""
    ceiling = None
    for layer in report.get("clouds") or []:
        if layer.get("cover") in ("BKN", "OVC", "OVX") and layer.get("base") is not None:
            ceiling = layer["base"] if ceiling is None else min(ceiling, layer["base"])
    vis = parse_visibility(report.get("visib"))

    def worse(a, b):
        return a if CATEGORY_ORDER.index(a) >= CATEGORY_ORDER.index(b) else b

    cat = "VFR"
    if ceiling is not None:
        if ceiling < 500:
            cat = worse(cat, "LIFR")
        elif ceiling < 1000:
            cat = worse(cat, "IFR")
        elif ceiling <= 3000:
            cat = worse(cat, "MVFR")
    if vis is not None:
        if vis < 1:
            cat = worse(cat, "LIFR")
        elif vis < 3:
            cat = worse(cat, "IFR")
        elif vis <= 5:
            cat = worse(cat, "MVFR")
    return cat


def fmt_wind(report):
    """返回 (风的去向角度或 None, 显示文本)。"""
    wdir, wspd = report.get("wdir"), report.get("wspd")
    if wspd in (None, ""):
        return None, "—"
    if int(wspd) == 0:
        return None, "CALM"
    variable = wdir is None or str(wdir).upper() == "VRB"
    direction = "VRB" if variable else f"{int(wdir):03d}°"
    label = f"{direction}/{int(wspd)}kt"
    if report.get("wgst"):
        label += f" G{int(report['wgst'])}"
    return (None if variable else (int(wdir) + 180) % 360), label


def fmt_visibility(report):
    value = report.get("visib")
    return f"{value} SM" if value not in (None, "") else "—"


def fmt_temp(report):
    temp, dewp = report.get("temp"), report.get("dewp")
    if temp is None:
        return "—"
    dew = f"{dewp:.0f}" if dewp is not None else "—"
    return f"{temp:.0f}/{dew} °C"


def fmt_qnh(report):
    altim = report.get("altim")
    return f"{round(altim)} hPa" if altim is not None else "—"


def fmt_clouds(report):
    layers = report.get("clouds") or []
    parts = []
    for layer in layers:
        cover = layer.get("cover") or ""
        base = layer.get("base")
        parts.append(f"{cover}{int(base) // 100:03d}" if base is not None else cover)
    return " ".join(parts) if parts else "—"


def fmt_obs_time(report):
    epoch = report.get("obsTime")
    if epoch:
        return time.strftime("%Y-%m-%d %H:%MZ", time.gmtime(epoch))
    report_time = report.get("reportTime")
    return f"{str(report_time)[:16]}Z" if report_time else "—"


def wind_arrow(x, y, angle_to, color):
    """小箭头指向风的去向（气流方向）；angle_to 为顺时针角度，0=北。"""
    body = (
        el("line", x1=0, y1=7, x2=0, y2=-7, stroke=color,
           stroke_width=TOKENS["stroke"]) +
        el("path", d="M0,-7 L-3.5,-1.5 M0,-7 L3.5,-1.5", stroke=color,
           stroke_width=TOKENS["stroke"], fill="none")
    )
    return el("g", body, transform=f"translate({x},{y}) rotate({angle_to})")


def build(mode, report):
    t = theme(mode)
    mono = TOKENS["font_mono"]
    cat = flight_category(report)
    cat_color = t[cat.lower()]
    parts = [
        el("rect", x=0.5, y=0.5, width=W - 1, height=H - 1,
           rx=TOKENS["radius"], fill=t["bg"], stroke=t["grid"]),
        text(24, 38, f"{STATION} · {STATION_NAME}", fill=t["ink"],
             font_family=mono, font_size=TOKENS["fs_md"],
             font_weight="bold", letter_spacing=1),
    ]

    # 飞行类别 chip（语义色绑定 FAA 阈值，见 flight_category）
    chip_w = 64
    parts.append(el("rect", x=W - 24 - chip_w, y=20, width=chip_w, height=24,
                    rx=TOKENS["radius"], fill="none", stroke=cat_color,
                    stroke_width=TOKENS["stroke"]))
    parts.append(text(W - 24 - chip_w / 2, 37, cat, fill=cat_color,
                      font_family=mono, font_size=TOKENS["fs_sm"],
                      font_weight="bold", text_anchor="middle"))

    # 原始报文不隐藏（面向专家用户），超长折两行
    raw = report.get("rawOb") or ""
    lines = [raw[:104], raw[104:208]] if len(raw) > 104 else [raw]
    for i, line in enumerate(l for l in lines if l):
        parts.append(text(24, 68 + i * 18, line, fill=t["muted"],
                          font_family=mono, font_size=TOKENS["fs_sm"]))

    # 解码组：缺失字段渲染「—」，不隐藏该栏（空态设计，见 DESIGN.md §5）
    angle_to, wind_label = fmt_wind(report)
    groups = [
        ("WIND", wind_label), ("VIS", fmt_visibility(report)),
        ("T/TD", fmt_temp(report)), ("QNH", fmt_qnh(report)),
        ("WX", report.get("wxString") or "—"), ("CLOUD", fmt_clouds(report)),
    ]
    xs = [24, 194, 314, 424, 544, 664]
    y_label, y_value = 124, 148
    for (label, value), gx in zip(groups, xs):
        parts.append(text(gx, y_label, label, fill=t["muted"], font_family=mono,
                          font_size=TOKENS["fs_sm"], letter_spacing=1))
        vx = gx
        if label == "WIND" and angle_to is not None:
            parts.append(wind_arrow(gx + 6, y_value - 5, angle_to, t["accent"]))
            vx = gx + 18
        parts.append(text(vx, y_value, value, fill=t["ink"], font_family=mono,
                          font_size=TOKENS["fs_md"]))

    # footer：观测时间 UTC + 来源（时效诚实外显）
    parts.append(el("line", x1=24, y1=166, x2=W - 24, y2=166,
                    stroke=t["grid"], stroke_width=1))
    parts.append(text(24, 186,
                      f"OBS {fmt_obs_time(report)} · aviationweather.gov · "
                      "refreshed hourly by GitHub Actions",
                      fill=t["muted"], font_family=mono, font_size=TOKENS["fs_sm"]))
    return svg(W, H, "".join(parts))


def main():
    out_dir = sys.argv[1] if len(sys.argv) > 1 else "dist"
    report = fetch()
    rendered = {mode: build(mode, report) for mode in ("dark", "light")}
    os.makedirs(out_dir, exist_ok=True)
    for mode, content in rendered.items():
        path = os.path.join(out_dir, f"metar-{STATION.lower()}-{mode}.svg")
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"wrote {path}")


if __name__ == "__main__":
    try:
        main()
    except Exception as err:  # 失败不产文件，保留旧卡
        print(f"render_metar failed: {err}", file=sys.stderr)
        sys.exit(1)
