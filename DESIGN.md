# DESIGN.md — qiaoqiaobby profile 视觉宪法

## 1. 身份与气质

- 宣读定稿：读作个人主页仪表板（profile README + 自绘 SVG header 与数据卡），面向路过的工程师与同行，航空仪表语言——克制、等宽、数据优先；参照 ATC 雷达屏与 METAR 报文版式 + GitHub 原生 UI 色系。
- 签名元素：header 的雷达扫描动画。这是全仓唯一的动画，不得在其他资产复用动效。
- 暗底磷光绿命中全局登记簿「暗底荧光」方向级条目，主题依据：ATC 雷达屏本身即暗底磷光绿，由题材直接推导，属选择而非默认。
- 明确排除：无来由渐变、发光、玻璃拟态；紫蓝配色套路；装饰性粒子与呼吸光圈；伪造数据（包括装饰用途的假 METAR 文本）。

## 2. 三刻度盘

V=2 / M=3 / D=6。理由：布局对称克制（V2）；动效仅 header 雷达扫描一处循环（M3）；仪表卡信息密度偏高但不逾字号与留白下限（D6）。

## 3. Design tokens

数值唯一权威源：`scripts/tokens.py` 的 `TOKENS`，本文件只写语义。色彩取 GitHub 明暗主题原生色系以与页面融合；唯一强调色为雷达磷光绿；VFR / MVFR / IFR / LIFR 为绑定 FAA 标准阈值的语义色（阈值实现在 `scripts/render_metar.py` 的 `flight_category`），禁止装饰性使用；图表琥珀/蓝双序列色仅用于区分数据线。改 token 后必须重跑 `python3 scripts/render_header.py`。

## 4. 字阶

等宽栈（tokens 的 `font_mono`，系统字体；SVG 作 `<img>` 加载不得引外部字体）。12px 辅助与标注 / 14px 数据值 / 20px 预留 / 36px header 展示名。12px 为硬下限。本仓库 SVG 文本全部为拉丁字符与数字，无 CJK 混排；README 正文的 CJK 排版由 GitHub 默认行为负责，不做干预。

## 5. 组件状态

SVG 卡片无交互态，需定义的是数据态：正常态（最新数据 + UTC 时间戳 + 来源署名）；降级态（API 失败不重渲染、保留旧卡，staleness 由读者从时间戳判读——这是「失败不提交」架构的固有属性，已如实声明，不伪装成实时）；空态（缺失字段渲染「—」，不隐藏该栏）。

## 6. 动效性格

仅允许一种：header 雷达扫描线匀速旋转 + 回波点同步闪现。功能论证：ATC 身份的签名表达。实现只用 CSS `@keyframes`（写入 SVG `<style>`），必须带 `prefers-reduced-motion: reduce` 静态降级。数据卡一律静态。

## 7. 本项目追加禁令

- 不出现假数据、假徽章、假背书；演示性内容必须标注。
- 不使用会被 GitHub camo 缓存拖垮的第三方「实时」图直链。
- 不回退到公共共享实例的统计卡（github-readme-stats / trophy 已因 503/402 裂图移除）。

闭包条款：本宪法未覆盖的视觉决策，停下提案，不得即兴。

## 预检清单

- diff 无 tokens 之外的新色值。
- SVG 内无小于 12px 的文字。
- 明暗双版本齐备，`<picture>` 的 source/img 指向正确。
- 动画仅存在于 header 且带 reduced-motion 降级。
- 数据卡带 UTC 时间戳与来源署名（Open-Meteo 必须保留 CC-BY 4.0）。
- 无追加禁令与全局 Tells 清单中的元素。
