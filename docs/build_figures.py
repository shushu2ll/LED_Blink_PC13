# -*- coding: utf-8 -*-
"""生成作业报告用的两张插图：硬件连接图、程序流程图。"""
import os
from PIL import Image, ImageDraw, ImageFont

OUT_DIR = r"F:\STM32CubeIDE_2.2.0\LED_Blink_PC13\docs"
os.makedirs(OUT_DIR, exist_ok=True)

FONT_CANDIDATES = [
    r"C:\Windows\Fonts\msyh.ttc",
    r"C:\Windows\Fonts\msyhbd.ttc",
    r"C:\Windows\Fonts\simhei.ttf",
    r"C:\Windows\Fonts\simsun.ttc",
]


def load_font(size):
    for path in FONT_CANDIDATES:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    return ImageFont.load_default()


def text_w(draw, text, font):
    box = draw.textbbox((0, 0), text, font=font)
    return box[2] - box[0]


def center_text(draw, cx, cy, text, font, fill=(0, 0, 0)):
    w = text_w(draw, text, font)
    h = draw.textbbox((0, 0), text, font=font)[3]
    draw.text((cx - w / 2, cy - h / 2 - 2), text, font=font, fill=fill)


def rounded_box(draw, x0, y0, x1, y1, radius=14, fill="#FFFFFF", outline="#1F4E79", width=3):
    draw.rounded_rectangle([x0, y0, x1, y1], radius=radius, fill=fill, outline=outline, width=width)


def arrow_head(draw, x, y, direction, color="#1F4E79", size=12):
    if direction == "down":
        draw.polygon([(x, y), (x - size, y - size * 1.4), (x + size, y - size * 1.4)], fill=color)
    elif direction == "up":
        draw.polygon([(x, y), (x - size, y + size * 1.4), (x + size, y + size * 1.4)], fill=color)
    elif direction == "right":
        draw.polygon([(x, y), (x - size * 1.4, y - size), (x - size * 1.4, y + size)], fill=color)
    else:
        draw.polygon([(x, y), (x + size * 1.4, y - size), (x + size * 1.4, y + size)], fill=color)


# ---------------------------------------------------------------- 流程图
def make_flowchart():
    W, H = 900, 1250
    img = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(img)
    f = load_font(24)
    f_small = load_font(20)

    steps = [
        ("上电 / 按下复位键", "start"),
        ("从 0x08000000 取中断向量表\n栈顶 = 0x20005000，复位入口 = Reset_Handler", "proc"),
        ("复位处理：把 .data 段初值从 Flash 搬到 RAM\n把 .bss 段清零", "proc"),
        ("SystemInit()：HSE 8MHz 经 PLL 9 倍频\n系统时钟 = 72MHz（失败则退回 HSI 8MHz）", "proc"),
        ("main() → GPIO_Init()：开 GPIOC 时钟\nPC13 配置为推挽输出 2MHz", "proc"),
        ("delay_init()：SysTick 每 1ms 计满一次", "proc"),
        ("LED_ON()：PC13 输出 0 → 灯亮", "out"),
        ("delay_ms(500)：延时 500ms", "proc"),
        ("LED_OFF()：PC13 输出 1 → 灯灭", "out"),
        ("delay_ms(500)：延时 500ms", "proc"),
    ]
    box_w = 620
    box_h = 86
    gap = 34
    cx = W // 2
    y = 30
    coords = []
    for text, kind in steps:
        x0, y0, x1, y1 = cx - box_w // 2, y, cx + box_w // 2, y + box_h
        if kind == "start":
            rounded_box(d, x0, y0, x1, y1, radius=43, fill="#DEEAF6")
        elif kind == "out":
            rounded_box(d, x0, y0, x1, y1, fill="#FBE5D6")
        else:
            rounded_box(d, x0, y0, x1, y1)
        lines = text.split("\n")
        total = len(lines) * 30
        for i, line in enumerate(lines):
            center_text(d, cx, y0 + box_h / 2 - total / 2 + 15 + i * 30, line, f if i == 0 else f_small)
        coords.append((x0, y0, x1, y1))
        y += box_h + gap

    # 竖向箭头
    for i in range(len(coords) - 1):
        y_from = coords[i][3]
        y_to = coords[i + 1][1]
        d.line([(cx, y_from), (cx, y_to - 2)], fill="#1F4E79", width=3)
        arrow_head(d, cx, y_to, "down")

    # 循环箭头：最后一个盒子 → 第 7 个盒子（LED_ON）
    last = coords[-1]
    target = coords[6]
    y_bottom = last[3] + 46
    x_left = 60
    d.line([(cx, last[3]), (cx, y_bottom)], fill="#C00000", width=3)
    d.line([(cx, y_bottom), (x_left, y_bottom)], fill="#C00000", width=3)
    d.line([(x_left, y_bottom), (x_left, (target[1] + target[3]) // 2)], fill="#C00000", width=3)
    d.line([(x_left, (target[1] + target[3]) // 2), (target[0] - 2, (target[1] + target[3]) // 2)], fill="#C00000", width=3)
    arrow_head(d, target[0], (target[1] + target[3]) // 2, "right", color="#C00000")
    center_text(d, (cx + x_left) / 2, y_bottom - 26, "循环执行，周期 1s", load_font(22), fill="#C00000")

    path = os.path.join(OUT_DIR, "fig_flow.png")
    img.save(path)
    return path


# ---------------------------------------------------------------- 接线图
def make_wiring():
    W, H = 1400, 820
    img = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(img)
    f = load_font(26)
    f_small = load_font(20)
    f_title = load_font(28)

    center_text(d, W / 2, 46, "LED 点亮电路（蓝飞 STM32F103C8T6 最小系统板）", f_title, fill="#1F4E79")

    # 第一行：3.3V → 470Ω → LED → PC13
    y = 190
    bh = 78
    blocks = [
        ("3.3V", 90, 250, "#DEEAF6"),
        ("470Ω 限流电阻", 350, 610, "#FFF2CC"),
        ("LED", 710, 900, "#FBE5D6"),
        ("PC13", 1000, 1200, "#DEEAF6"),
    ]
    boxes = []
    for label, x0, x1, color in blocks:
        rounded_box(d, x0, y, x1, y + bh, fill=color)
        center_text(d, (x0 + x1) / 2, y + bh / 2, label, f)
        boxes.append((x0, x1))

    # 连线 + 箭头
    for i in range(len(boxes) - 1):
        x_from = boxes[i][1]
        x_to = boxes[i + 1][0]
        d.line([(x_from, y + bh / 2), (x_to - 4, y + bh / 2)], fill="#1F4E79", width=4)
        arrow_head(d, x_to, y + bh / 2, "right")

    center_text(d, W / 2, y + bh + 52, "PC13 输出低电平（0）→ 电流从 3.3V 经电阻、LED 流入 PC13 → 灯亮",
                f_small, fill="#C00000")
    center_text(d, W / 2, y + bh + 88, "PC13 输出高电平（1）→ 两端等电位，没有电流 → 灯灭",
                f_small, fill="#404040")

    # 第二行：ST-Link 与目标板
    y2 = 470
    d.line([(90, 420), (1310, 420)], fill="#BFBFBF", width=2)
    center_text(d, W / 2, 440, "下载 / 调试连接（ST-Link V2 与目标板）", f_title, fill="#1F4E79")

    rounded_box(d, 150, y2, 420, y2 + 250, fill="#E2EFDA")
    center_text(d, 285, y2 + 40, "ST-Link V2", f)
    for i, name in enumerate(["SWDIO", "SWCLK", "GND", "3.3V"]):
        center_text(d, 285, y2 + 100 + i * 36, name, f_small)

    rounded_box(d, 950, y2, 1260, y2 + 250, fill="#DEEAF6")
    center_text(d, 1105, y2 + 40, "STM32F103C8T6", f)
    for i, name in enumerate(["PA13", "PA14", "GND", "3.3V"]):
        center_text(d, 1105, y2 + 100 + i * 36, name, f_small)

    for i in range(4):
        yy = y2 + 100 + i * 36
        d.line([(430, yy), (940, yy)], fill="#548235", width=3)
        arrow_head(d, 940, yy, "right", color="#548235")

    center_text(d, W / 2, y2 + 275, "烧录前确认 BOOT0 = 0（从 Flash 启动），下载完成后按一下 NRST 复位",
                f_small, fill="#404040")

    path = os.path.join(OUT_DIR, "fig_wiring.png")
    img.save(path)
    return path


if __name__ == "__main__":
    print(make_flowchart())
    print(make_wiring())
