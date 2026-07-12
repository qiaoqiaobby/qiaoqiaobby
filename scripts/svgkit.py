"""极薄 SVG 拼装助手：属性拼接与文档包裹，Python 标准库 only。"""

from xml.sax.saxutils import escape


def esc(value):
    return escape(str(value), {'"': "&quot;"})


def _attrs(attrs):
    parts = []
    for key, value in attrs.items():
        if value is None:
            continue
        if key == "cls":
            key = "class"
        parts.append(f'{key.replace("_", "-")}="{esc(value)}"')
    return " ".join(parts)


def el(name, content=None, **attrs):
    a = _attrs(attrs)
    if content is None:
        return f"<{name} {a}/>"
    return f"<{name} {a}>{content}</{name}>"


def text(x, y, s, **attrs):
    return el("text", esc(s), x=x, y=y, **attrs)


def svg(width, height, body, style=""):
    style_block = f"<style>{style}</style>" if style else ""
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img">{style_block}{body}</svg>\n'
    )
