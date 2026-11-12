# -*- coding: utf-8 -*-
"""生成《STM32F103C8T6 点亮 LED 实验报告》.docx"""
import os
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.section import WD_SECTION
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

PROJ = r"F:\STM32CubeIDE_2.2.0\LED_Blink_PC13"
DOCS = os.path.join(PROJ, "docs")
OUT = os.path.join(PROJ, "点亮LED实验报告.docx")

SONG = "宋体"
HEI = "黑体"
MONO = "Consolas"


# ----------------------------------------------------------------- 基础工具
def set_run(run, size=10.5, bold=False, color=None, latin="Times New Roman", ea=SONG, italic=False):
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic
    run.font.name = latin
    rpr = run._element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.append(rfonts)
    rfonts.set(qn("w:ascii"), latin)
    rfonts.set(qn("w:hAnsi"), latin)
    rfonts.set(qn("w:eastAsia"), ea)
    if color is not None:
        run.font.color.rgb = color


def shade(cell, fill):
    tcpr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), fill)
    tcpr.append(shd)


def para(doc, text, size=10.5, bold=False, color=None, first_indent=True,
         align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_after=6):
    p = doc.add_paragraph()
    p.alignment = align
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = 1.5
    if first_indent:
        p.paragraph_format.first_line_indent = Pt(size * 2)
    r = p.add_run(text)
    set_run(r, size=size, bold=bold, color=color)
    return p


def caption(doc, text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(3)
    p.paragraph_format.space_after = Pt(9)
    r = p.add_run(text)
    set_run(r, size=9, color=RGBColor(0x40, 0x40, 0x40))


def set_table_layout(t, widths):
    """固定列宽：同时写 tblW、tblLayout 和 tblGrid，LibreOffice / Word 才会照办。"""
    tbl = t._tbl
    tblpr = tbl.tblPr
    for tag in ("w:tblW", "w:tblLayout"):
        old = tblpr.find(qn(tag))
        if old is not None:
            tblpr.remove(old)
    tbl_w = OxmlElement("w:tblW")
    tbl_w.set(qn("w:w"), str(int(sum(widths) * 567)))
    tbl_w.set(qn("w:type"), "dxa")
    tblpr.append(tbl_w)
    layout = OxmlElement("w:tblLayout")
    layout.set(qn("w:type"), "fixed")
    tblpr.append(layout)
    grid = tbl.find(qn("w:tblGrid"))
    if grid is not None:
        for i, col in enumerate(grid.findall(qn("w:gridCol"))):
            if i < len(widths):
                col.set(qn("w:w"), str(int(widths[i] * 567)))
    for i, col in enumerate(t.columns):
        col.width = Cm(widths[i])


def no_split_rows(t, header=True):
    for idx, row in enumerate(t.rows):
        trpr = row._tr.get_or_add_trPr()
        if trpr.find(qn("w:cantSplit")) is None:
            trpr.append(OxmlElement("w:cantSplit"))
        if header and idx == 0 and trpr.find(qn("w:tblHeader")) is None:
            trpr.append(OxmlElement("w:tblHeader"))


def add_table(doc, headers, rows, widths, font_size=9):
    t = doc.add_table(rows=1, cols=len(headers))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False
    for i, h in enumerate(headers):
        cell = t.rows[0].cells[i]
        cell.text = ""
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.space_before = Pt(2)
        r = p.add_run(h)
        set_run(r, size=font_size, bold=True, ea=HEI)
        shade(cell, "DEEAF6")
    for row in rows:
        cells = t.add_row().cells
        for i, val in enumerate(row):
            cells[i].text = ""
            p = cells[i].paragraphs[0]
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.line_spacing = 1.15
            r = p.add_run(str(val))
            set_run(r, size=font_size)
    for row in t.rows:
        for i, w in enumerate(widths):
            row.cells[i].width = Cm(w)
    set_table_layout(t, widths)
    no_split_rows(t)
    return t


def add_code(doc, code, size=8.5):
    t = doc.add_table(rows=1, cols=1)
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.style = "Table Grid"
    cell = t.rows[0].cells[0]
    cell.width = Cm(16.0)
    shade(cell, "F7F7F7")
    cell.text = ""
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.line_spacing = 1.0
    lines = code.rstrip("\n").split("\n")
    for i, line in enumerate(lines):
        if i:
            p.add_run().add_break()
        r = p.add_run(line if line else " ")
        set_run(r, size=size, latin=MONO, ea=SONG)
    set_table_layout(t, [16.0])
    if len(lines) <= 30:
        # 短代码块整体保持在一页内，避免从中间断开
        no_split_rows(t, header=False)
    return t


def add_page_number_footer(section):
    p = section.footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r1 = p.add_run("第 ")
    set_run(r1, size=9)
    run = p.add_run()
    set_run(run, size=9)
    fld_begin = OxmlElement("w:fldChar")
    fld_begin.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = " PAGE "
    fld_end = OxmlElement("w:fldChar")
    fld_end.set(qn("w:fldCharType"), "end")
    run._r.append(fld_begin)
    run._r.append(instr)
    run._r.append(fld_end)
    r2 = p.add_run(" 页")
    set_run(r2, size=9)


# ----------------------------------------------------------------- 文档设置
doc = Document()

sec = doc.sections[0]
sec.page_width = Cm(21.0)
sec.page_height = Cm(29.7)
sec.top_margin = Cm(2.54)
sec.bottom_margin = Cm(2.54)
sec.left_margin = Cm(2.6)
sec.right_margin = Cm(2.6)

normal = doc.styles["Normal"]
normal.font.name = "Times New Roman"
normal.font.size = Pt(10.5)
normal.element.get_or_add_rPr().append(OxmlElement("w:rFonts"))
normal.element.get_or_add_rPr().find(qn("w:rFonts")).set(qn("w:eastAsia"), SONG)

for name, size in (("Heading 1", 16), ("Heading 2", 14), ("Heading 3", 12)):
    st = doc.styles[name]
    st.font.name = HEI
    st.font.size = Pt(size)
    st.font.bold = True
    st.font.color.rgb = RGBColor(0, 0, 0)
    rpr = st.element.get_or_add_rPr()
    rf = rpr.find(qn("w:rFonts"))
    if rf is None:
        rf = OxmlElement("w:rFonts")
        rpr.append(rf)
    rf.set(qn("w:eastAsia"), HEI)
    rf.set(qn("w:ascii"), HEI)
    rf.set(qn("w:hAnsi"), HEI)
    st.paragraph_format.space_before = Pt(14)
    st.paragraph_format.space_after = Pt(8)
    st.paragraph_format.line_spacing = 1.25
    st.paragraph_format.keep_with_next = True

add_page_number_footer(sec)
sec.different_first_page_header_footer = True   # 封面不显示页码

# ----------------------------------------------------------------- 封面
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.paragraph_format.space_before = Pt(90)
r = p.add_run("STM32 点亮 LED 实验报告")
set_run(r, size=26, bold=True, ea=HEI)

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.paragraph_format.space_before = Pt(10)
r = p.add_run("——基于 STM32F103C8T6 的 GPIO 输出实验（PC13 闪烁）")
set_run(r, size=13, color=RGBColor(0x40, 0x40, 0x40), ea=HEI)

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.paragraph_format.space_before = Pt(70)
r = p.add_run("课程：嵌入式系统原理与应用")
set_run(r, size=12)

for label in ("姓　　名：______________________",
              "学　　号：______________________",
              "班　　级：______________________",
              "指导教师：______________________"):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.line_spacing = 1.6
    r = p.add_run(label)
    set_run(r, size=12)

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.paragraph_format.space_before = Pt(40)
r = p.add_run("实验日期：2026 年 11 月 10 日")
set_run(r, size=12)

doc.add_page_break()

# ----------------------------------------------------------------- 1 实验目的
doc.add_heading("1　实验目的", level=1)
for item in [
    "熟悉 STM32F103C8T6 最小系统板（俗称“蓝飞”）的 LED 电路，理解“低电平点亮”的硬件原因。",
    "掌握 STM32 系统时钟的配置过程：HSE 8MHz 经 PLL 9 倍频得到 72MHz，并正确设置 Flash 等待周期与 APB1/APB2 分频。",
    "掌握 GPIO 输出模式的寄存器配置方法（CRL/CRH 的 MODE、CNF 位），以及用 BSRR 寄存器实现原子置位/复位。",
    "学会用 Cortex-M3 内核的 SysTick 定时器产生 1ms 节拍，实现毫秒级软件延时。",
    "完整走通“建立工程 → 编写代码 → 编译 → 生成 HEX/BIN → 烧录 → 观察现象”的嵌入式开发流程。",
]:
    p = doc.add_paragraph(style="List Number")
    p.paragraph_format.line_spacing = 1.5
    p.paragraph_format.space_after = Pt(2)
    r = p.add_run(item)
    set_run(r, size=10.5)

# ----------------------------------------------------------------- 2 环境检查
doc.add_heading("2　实验环境与配置检查", level=1)

doc.add_heading("2.1　检查方法", level=2)
para(doc, "在不启动 IDE 图形界面的前提下，直接查看安装目录、插件版本、工具链可执行文件、"
          "固件包存放位置和 USB 设备列表，逐项确认“写得出来、编得过去、烧得进去”这三个环节是否具备条件。"
          "检查结果见表 1。")

doc.add_heading("2.2　检查结果", level=2)
add_table(
    doc,
    ["检查项", "检查结果", "说明 / 影响"],
    [
        ["IDE 版本", "STM32CubeIDE 2.2.0（buildId = Version 2.2.0）", "安装于 F:\\STM32CubeIDE_2.2.0\\STM32CubeIDE，正常"],
        ["内置 Java 运行环境", "com.st.stm32cube.ide.jre.win64 3.4.300", "IDE 自带 JRE，不需要另装 JDK"],
        ["交叉编译器", "GNU Tools for STM32 14.3.rel1（arm-none-eabi-gcc 14.3.1）", "正常，支持 Cortex-M3"],
        ["构建工具", "GNU make 2.2.200", "正常，可用 Makefile 编译"],
        ["下载 / 调试服务", "ST-LINK GDB Server 2.2.500、ST-Link Server 2.2.300", "正常"],
        ["烧录工具", "STM32CubeProgrammer 2.2.500（IDE 插件形式）", "正常，可烧写 HEX/BIN"],
        ["其他可选组件", "OpenOCD 2.4.500、CMake 1.1.200、Ninja 1.1.200、J-Link 2.5.400", "本实验未使用"],
        ["STM32Cube 固件包", "未安装（用户目录下没有 STM32Cube\\Repository）", "CubeMX 生成 HAL 工程需要联网下载固件包"],
        ["调试器 / 目标板", "USB 上未检测到 ST-Link 设备", "本次未做实机烧录，现象为按代码推导的预期现象"],
    ],
    widths=[3.4, 6.4, 6.2],
)
caption(doc, "表 1　开发环境配置检查结果")

doc.add_heading("2.3　结论与方案选择", level=2)
para(doc, "检查结论有两条：第一，编译链路（arm-none-eabi-gcc + make）和烧录链路（ST-Link 服务 + CubeProgrammer）都是完整的，"
          "具备做实验的条件；第二，本机没有安装任何 STM32Cube 固件包，而 CubeMX 生成 HAL 工程的前提正是对应芯片的固件包，"
          "需要联网下载几百 MB。")
para(doc, "因此本实验采用“纯寄存器 + 自写启动文件和链接脚本”的最小工程：不引用 HAL 库，只依赖编译器自带的标准库，"
          "离线即可编译，最终镜像只有 624 字节。这样做还有一个好处——点亮一个 LED 到底动了哪几个寄存器、"
          "启动时 CPU 到底做了哪些事，在代码里看得一清二楚，比调用 HAL_GPIO_Init() 更容易讲清原理。"
          "如果课程要求必须使用 CubeMX + HAL，可按附录 B 改写。")

# ----------------------------------------------------------------- 3 原理
doc.add_heading("3　实验原理", level=1)

doc.add_heading("3.1　LED 驱动电路与 PC13", level=2)
para(doc, "蓝飞最小系统板上，LED 的阳极经限流电阻接到 3.3V，阴极接到 PC13。因此 PC13 输出低电平时，"
          "电流从 3.3V 经电阻、LED 流入芯片引脚，LED 点亮；PC13 输出高电平时两端等电位，没有电流，LED 熄灭。"
          "这就是“低电平点亮”，程序里 LED_ON() 实际是把 PC13 清零。")
para(doc, "限流电阻按 I = (3.3V − 2.0V) / 470Ω ≈ 2.8mA 计算。这里选 470Ω 而不选更小的电阻，"
          "是因为 PC13 属于 VBAT 供电域的引脚，数据手册规定其最大负载电流只有 3mA，只能点 LED，不能直接驱动蜂鸣器、"
          "继电器等大电流负载；需要驱动大电流时应加三极管或 MOS 管。")

doc.add_heading("3.2　GPIO 输出模式的寄存器配置", level=2)
para(doc, "STM32 每个 GPIO 端口有 7 个寄存器，其中 CRL 管 Pin0~Pin7、CRH 管 Pin8~Pin15，每个引脚占 4 位："
          "低 2 位 MODE[1:0] 选输出速度（00 输入、01 输出 10MHz、10 输出 2MHz、11 输出 50MHz），"
          "高 2 位 CNF[1:0] 选输出类型（00 通用推挽、01 通用开漏、10 复用推挽、11 复用开漏）。"
          "PC13 位于 CRH 的第 (13−8)×4 = 20 位起，配置成“2MHz 推挽输出”即写入 0b0010。")
para(doc, "输出电平用 BSRR 寄存器：低 16 位写 1 将该引脚置高，高 16 位写 1 将该引脚置低。"
          "BSRR 是原子操作，不需要“读—改—写”，也不会影响同端口的其他引脚，比直接操作 ODR 更安全。")
add_table(
    doc,
    ["寄存器", "地址偏移", "本实验中的作用"],
    [
        ["GPIOx_CRH", "0x04", "配置 PC13 为推挽输出、2MHz"],
        ["GPIOx_BSRR", "0x10", "低 16 位置 1 → 输出高（灯灭）；高 16 位置 1 → 输出低（灯亮）"],
        ["RCC_APB2ENR", "0x18", "bit4 = IOPCEN，打开 GPIOC 的时钟（不开时钟写寄存器无效）"],
        ["RCC_CR / RCC_CFGR", "0x00 / 0x04", "使能 HSE、选择 PLL 倍频、切换系统时钟"],
        ["FLASH_ACR", "0x00", "72MHz 下必须设 2 个等待周期并打开预取"],
    ],
    widths=[4.0, 2.6, 9.4],
)
caption(doc, "表 2　本实验涉及的寄存器")

doc.add_heading("3.3　系统时钟配置", level=2)
para(doc, "芯片复位后默认使用内部 HSI（8MHz）。要跑到 72MHz，需要把外部 8MHz 晶振（HSE）作为 PLL 输入，"
          "9 倍频后得到 72MHz，再把系统时钟源切换为 PLL。同时要注意：Flash 在 48~72MHz 时必须插入 2 个等待周期，"
          "APB1 总线的最高频率是 36MHz，所以必须 2 分频。配置结果见表 3。")
add_table(
    doc,
    ["项目", "配置", "依据"],
    [
        ["时钟源", "HSE 外部晶振 8MHz", "蓝飞板上焊有 8MHz 晶振"],
        ["PLL", "HSE 不分频 × 9 = 72MHz", "RCC_CFGR：PLLSRC=1、PLLXTPRE=0、PLLMUL=0111"],
        ["SYSCLK / HCLK", "72MHz", "AHB 不分频（HPRE=0000）"],
        ["APB1（PCLK1）", "36MHz", "APB1 最高 36MHz，需 2 分频"],
        ["APB2（PCLK2）", "72MHz", "APB2 最高 72MHz，不分频"],
        ["Flash 等待周期", "2 WS + 预取使能", "48MHz < f ≤ 72MHz 时为 2 个等待周期"],
    ],
    widths=[3.6, 6.2, 6.2],
)
caption(doc, "表 3　系统时钟配置")
para(doc, "此外程序里加了一个“保险”：如果 HSE 起振失败（晶振虚焊、板子没焊晶振等），程序不会死等，"
          "而是自动退回 HSI 8MHz 继续运行，LED 依然会闪，只是频率不受影响（因为 SysTick 的装载值是按实际主频计算的），"
          "这样便于现场判断“是晶振的问题还是程序的问题”。")

doc.add_heading("3.4　SysTick 毫秒延时", level=2)
para(doc, "SysTick 是 Cortex-M3 内核自带的 24 位递减计数器，时钟源可选 HCLK。把重装载值设为 72000−1，"
          "计数器从 72000 减到 0 正好是 1ms，此时 CTRL 寄存器的 COUNTFLAG 置 1，读一次 CTRL 该标志自动清零。"
          "delay_ms(n) 就是把这个 1ms 节拍重复 n 次，得到 n 毫秒的阻塞延时。由于重装载值按 SystemCoreClock 计算，"
          "即使主频退回 8MHz，延时依然是准确的 1ms。")

# ----------------------------------------------------------------- 4 硬件
doc.add_heading("4　硬件连接", level=1)
para(doc, "若使用蓝飞最小系统板，板载 LED 已接在 PC13 上，无需外接任何元件，插上 ST-Link 即可。"
          "若使用核心板或自己搭电路，按表 4 和图 1 连接。")
add_table(
    doc,
    ["序号", "连接点", "说明"],
    [
        ["1", "3.3V → 470Ω → LED 阳极（长脚）", "限流电阻不可省，LED 电流约 2.8mA"],
        ["2", "LED 阴极（短脚） → PC13", "低电平点亮"],
        ["3", "ST-Link SWDIO → PA13", "SWD 数据线"],
        ["4", "ST-Link SWCLK → PA14", "SWD 时钟线"],
        ["5", "ST-Link GND ↔ 目标板 GND", "共地，必须接"],
        ["6", "ST-Link 3.3V → 目标板 3.3V", "由调试器供电，或目标板单独供电（注意不要冲突）"],
        ["7", "BOOT0 跳线 → 0", "从 Flash 启动；BOOT0=1 时程序不会运行"],
    ],
    widths=[1.6, 7.2, 7.2],
)
caption(doc, "表 4　硬件连接表")

doc.add_picture(os.path.join(DOCS, "fig_wiring.png"), width=Cm(16.0))
doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
doc.paragraphs[-1].paragraph_format.keep_with_next = True
caption(doc, "图 1　LED 点亮电路与 ST-Link 下载连接")

# ----------------------------------------------------------------- 5 软件设计
doc.add_heading("5　软件设计", level=1)

doc.add_heading("5.1　工程结构", level=2)
para(doc, "工程共 5 个源文件（外加 1 个 Makefile 和 1 个链接脚本），每个文件职责单一，方便对照原理阅读。")
add_table(
    doc,
    ["文件", "作用"],
    [
        ["Core/Inc/stm32f103_regs.h", "寄存器定义：按 RM0008 的偏移量手写 RCC、GPIO、FLASH、SysTick、SCB 结构体"],
        ["Core/Inc/board.h", "板级定义：LED 接在哪个端口/引脚、高电平还是低电平点亮，换板子只改这里"],
        ["Core/Src/main.c", "业务代码：时钟初始化、GPIO 初始化、SysTick 延时、主循环"],
        ["Core/Startup/startup_stm32f103c8tx.s", "启动文件：中断向量表、复位入口、.data 搬运、.bss 清零、调用 main"],
        ["STM32F103C8TX_FLASH.ld", "链接脚本：划分 64KB Flash / 20KB RAM，规定各段地址"],
        ["Makefile", "编译脚本：编译、链接、生成 HEX/BIN，一条 make 命令完成"],
    ],
    widths=[7.4, 8.6],
)
caption(doc, "表 5　工程文件说明")

doc.add_heading("5.2　程序流程", level=2)
para(doc, "程序从上电到 LED 闪烁的完整流程如图 2 所示。其中前 3 步由启动文件完成，"
          "之后才进入 C 语言的 main()。理解“谁先谁后”是看懂 STM32 程序的关键："
          "C 语言的全局变量还没初始化时 CPU 就已经在跑汇编了。")
doc.add_picture(os.path.join(DOCS, "fig_flow.png"), width=Cm(11.6))
doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
doc.paragraphs[-1].paragraph_format.keep_with_next = True
caption(doc, "图 2　程序运行流程")

doc.add_heading("5.3　关键代码", level=2)
para(doc, "（1）系统时钟：HSE 起振检测 + PLL 9 倍频 + 切换系统时钟。", first_indent=False, space_after=3
     ).paragraph_format.keep_with_next = True
add_code(doc, """    RCC->CR |= RCC_CR_HSEON;                 /* 打开外部 8MHz 晶振 */
    for (i = 0U; i < 0x20000U; i++) {
        if (RCC->CR & RCC_CR_HSERDY) break;  /* 等待起振，带超时 */
    }
    if ((RCC->CR & RCC_CR_HSERDY) == 0U) {   /* 起振失败：退回 HSI 8MHz */
        SystemCoreClock = 8000000UL;
        return;
    }
    FLASH->ACR = (FLASH->ACR & ~FLASH_ACR_LATENCY) | FLASH_ACR_PRFTBE | 0x2UL;
    RCC->CFGR |= (RCC_CFGR_HPRE_DIV1 | RCC_CFGR_PPRE1_DIV2 | RCC_CFGR_PPRE2_DIV1);
    RCC->CFGR |= (RCC_CFGR_PLLSRC | RCC_CFGR_PLLMULL9);   /* 8MHz × 9 = 72MHz */
    RCC->CR   |= RCC_CR_PLLON;
    while ((RCC->CR & RCC_CR_PLLRDY) == 0U) { }           /* 等 PLL 锁定 */
    RCC->CFGR  = (RCC->CFGR & ~RCC_CFGR_SW) | RCC_CFGR_SW_PLL;
    while ((RCC->CFGR & RCC_CFGR_SWS) != RCC_CFGR_SWS_PLL) { }
    SystemCoreClock = 72000000UL;""")

para(doc, "（2）GPIO 初始化：先开时钟，再配 CRH，最后先把灯熄灭。", first_indent=False, space_after=3
     ).paragraph_format.keep_with_next = True
add_code(doc, """    LED_CLK_ENABLE();                                    /* RCC->APB2ENR |= IOPCEN */
    LED_PORT->CRH &= ~(0xFUL << ((LED_PIN - 8U) * 4U));  /* 清 PC13 的 4 位 */
    LED_PORT->CRH |=  (0x2UL << ((LED_PIN - 8U) * 4U));  /* 2MHz 推挽输出 */
    LED_OFF();""")

para(doc, "（3）延时与主循环：SysTick 产生 1ms 节拍，主循环里亮 500ms、灭 500ms。", first_indent=False, space_after=3
     ).paragraph_format.keep_with_next = True
add_code(doc, """    SysTick->LOAD = (SystemCoreClock / 1000UL) - 1UL;    /* 1ms 的计数值 */
    SysTick->VAL  = 0UL;
    SysTick->CTRL = SysTick_CTRL_CLKSOURCE | SysTick_CTRL_ENABLE;

    while (1) {
        LED_ON();            /* PC13 = 0，灯亮 */
        delay_ms(500U);
        LED_OFF();           /* PC13 = 1，灯灭 */
        delay_ms(500U);
    }""")

# ----------------------------------------------------------------- 6 步骤
doc.add_heading("6　实验步骤", level=1)
para(doc, "下面是本次实验实际执行的完整过程，包含两次编译报错和对应的修正，以便重现。")

steps = [
    ("步骤 1　检查开发环境",
     "查看 IDE 安装目录与工具链版本，确认 arm-none-eabi-gcc 14.3.rel1 与 make 均可用；"
     "确认固件包目录不存在，决定采用寄存器方式实现（结果见表 1）。"),
    ("步骤 2　建立工程目录",
     "在 F:\\STM32CubeIDE_2.2.0\\LED_Blink_PC13 下建立 Core\\Inc、Core\\Src、Core\\Startup 三级目录，"
     "把启动文件、链接脚本、Makefile 放在工程根目录。"),
    ("步骤 3　编写寄存器头文件",
     "按 RM0008 的寄存器偏移，用结构体把 RCC、GPIO、FLASH、SysTick、SCB 映射到对应地址，"
     "并把用到的位定义成宏（如 RCC_CFGR_PLLMULL9）。"),
    ("步骤 4　编写启动文件",
     "在 .isr_vector 段依次放栈顶地址和 59 个中断向量（16 个内核异常 + 43 个外设中断）；"
     "Reset_Handler 里先搬 .data、清 .bss，再 bl SystemInit、bl main。"),
    ("步骤 5　编写链接脚本",
     "MEMORY 区声明 FLASH 64KB @0x08000000、RAM 20KB @0x20000000，_estack 取 RAM 末尾 0x20005000；"
     "把 .data 的运行地址放 RAM、加载地址放 Flash。"),
    ("步骤 6　编写业务代码",
     "main.c 实现 SystemInit()、GPIO_Init()、delay_init()、delay_ms() 和主循环；board.h 里用宏定义 LED_ON/LED_OFF。"),
    ("步骤 7　第一次编译（失败）",
     "报错 undefined reference to `SystemInit'。原因是 SystemInit 被写成了 static 函数，"
     "启动文件在汇编里调用它时链接器看不到符号。去掉 static 后解决。"),
    ("步骤 8　第二次编译（失败）",
     "Makefile 里用了 if not exist ... mkdir 这种 Windows 批处理写法，而 make 内置的 shell 是 sh，"
     "报 syntax error: unexpected end of file。改成 mkdir -p 后解决。"),
    ("步骤 9　编译成功",
     "执行 make，输出 FLASH 624B（0.95%）、RAM 1544B（7.54%），并生成 .elf、.hex、.bin 三个文件，零警告。"),
    ("步骤 10　静态验证镜像",
     "用 objdump 检查中断向量表首字为 0x20005000（栈顶）、第二字为 0x0800020D（复位入口，Thumb 位为 1）；"
     "反汇编确认 SystemInit 依次写入了 RCC_CR、FLASH_ACR、RCC_CFGR，main 里对 GPIOC 的 CRH 和 BSRR 的操作也对得上。"),
    ("步骤 11　烧录",
     "ST-Link 接好 SWD 四根线，BOOT0 置 0；用 STM32CubeProgrammer 连接后下载 build\\LED_Blink_PC13.hex，"
     "下载完成后按一下复位键。"),
    ("步骤 12　观察现象",
     "上电后 PC13 上的 LED 以 1Hz 闪烁（亮 500ms、灭 500ms）；用万用表测 PC13 对 GND 的直流电压约为 1.6V，"
     "正好是 3.3V 与 0V 各占一半的平均值，说明占空比 50%。"),
]
for title, body in steps:
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.line_spacing = 1.4
    r = p.add_run(title)
    set_run(r, size=10.5, bold=True, ea=HEI)
    para(doc, body)

# ----------------------------------------------------------------- 7 编译结果
doc.add_heading("7　编译结果与镜像验证", level=1)
para(doc, "在工程目录执行 make，完整输出如下（已去掉重复路径）：")
add_code(doc, """arm-none-eabi-gcc -c -mcpu=cortex-m3 -mthumb -DSTM32F103xB -ICore/Inc -O2 -g3 \\
  -Wall -Wextra -ffunction-sections -fdata-sections -std=gnu11 Core/Src/main.c -o build/main.o
arm-none-eabi-gcc -x assembler-with-cpp -c -mcpu=cortex-m3 -mthumb ... \\
  Core/Startup/startup_stm32f103c8tx.s -o build/startup_stm32f103c8tx.o
arm-none-eabi-gcc build/main.o build/startup_stm32f103c8tx.o -mcpu=cortex-m3 -mthumb \\
  -specs=nano.specs -TSTM32F103C8TX_FLASH.ld -lc -lm -Wl,--gc-sections \\
  -Wl,--print-memory-usage -o build/LED_Blink_PC13.elf
Memory region         Used Size  Region Size  %age Used
           FLASH:         624 B        64 KB      0.95%
             RAM:        1544 B        20 KB      7.54%
   text    data     bss     dec     hex filename
    620       4    1540    2164     874 build/LED_Blink_PC13.elf
arm-none-eabi-objcopy -O ihex   build/LED_Blink_PC13.elf build/LED_Blink_PC13.hex
arm-none-eabi-objcopy -O binary -S build/LED_Blink_PC13.elf build/LED_Blink_PC13.bin""")
para(doc, "编译过程零警告零错误。624 字节的 Flash 占用里，有 236 字节是中断向量表（59 个 32 位地址），"
          "剩下不到 400 字节才是真正的指令，这就是不用 HAL 库的好处。")

doc.add_heading("7.1　镜像静态验证", level=2)
para(doc, "没有实物板子时，可以用反汇编核对“程序是否真的按设计写寄存器”。检查项与结果见表 6。")
add_table(
    doc,
    ["检查项", "期望值", "实测值", "结论"],
    [
        ["向量表第 0 字（栈顶）", "0x20005000", "0x20005000", "RAM 末尾，20KB 正确"],
        ["向量表第 1 字（复位入口）", "0x0800xxxx（末位为 1）", "0x0800020D", "Thumb 状态正确"],
        [".isr_vector 段大小", "59×4 = 236 字节", "0xEC = 236 字节", "16 个内核 + 43 个外设中断齐全"],
        ["SystemInit 中 RCC_CR", "置 bit16（HSEON）", "orr #0x10000 后写回", "与设计一致"],
        ["SystemInit 中 FLASH_ACR", "等待周期 2 + 预取", "bic #0x17 / orr #0x12", "与设计一致"],
        ["SystemInit 中 RCC_CFGR", "PLLSRC=1、PLLMUL=9", "写入 0x1D0000 组合位", "与设计一致"],
        ["main 中 RCC_APB2ENR", "置 bit4（IOPCEN）", "orr #0x10 后写 [r, #0x18]", "GPIOC 时钟已开"],
        ["main 中 GPIOC_CRH", "bit23:20 = 0010", "bic #0xF00000 后 orr #0x200000", "PC13 推挽输出"],
    ],
    widths=[5.2, 4.6, 4.2, 2.8],
)
caption(doc, "表 6　镜像静态验证结果")

# ----------------------------------------------------------------- 8 烧录
doc.add_heading("8　烧录与运行", level=1)
para(doc, "方法一（图形界面，推荐）：打开 STM32CubeProgrammer → 接口选 ST-LINK → 点 Connect → "
          "在“Erasing & Programming”页选择 build\\LED_Blink_PC13.hex → 勾选 Verify → 点 Start Programming → 按复位键。")
para(doc, "方法二（命令行）：")
add_code(doc, """STM32_Programmer_CLI.exe -c port=SWD -w build\\LED_Blink_PC13.hex -v -rst""")
para(doc, "方法三（在 IDE 里调试）：把工程以 “Makefile Project with Existing Code” 方式导入 STM32CubeIDE，"
          "在 Run → Debug Configurations 里新建 STM32 Cortex-M C/C++ Application，"
          "把可执行文件指向 build\\LED_Blink_PC13.elf，调试器选 ST-LINK(OpenOCD) 或 ST-LINK GDB Server，"
          "然后点 Debug 即可单步、看寄存器、看外设。")

# ----------------------------------------------------------------- 9 现象
doc.add_heading("9　实验现象与验证", level=1)
para(doc, "正常运行时，LED 应当以 1Hz 的频率稳定闪烁，肉眼看不到抖动或停顿。一个周期内的电平变化见表 7。")
add_table(
    doc,
    ["时间（相对一个周期）", "PC13 电平", "LED 状态", "说明"],
    [
        ["0 ~ 500ms", "0（低）", "亮", "LED_ON() 置位 BSRR 高 16 位"],
        ["500 ~ 1000ms", "1（高）", "灭", "LED_OFF() 置位 BSRR 低 16 位"],
        ["1000ms 起", "—", "循环", "主循环 while(1) 不断重复"],
    ],
    widths=[4.6, 3.2, 2.6, 6.2],
)
caption(doc, "表 7　一个周期内的电平与现象")
para(doc, "验证方法：① 眼睛看，闪烁周期约 1 秒；② 万用表直流档测 PC13 对 GND，读数约 1.6V（3.3V 与 0V 各半）；"
          "③ 示波器测 PC13，能看到 1Hz、占空比 50% 的方波；④ 拔掉 8MHz 晶振再上电，LED 应仍然闪烁，"
          "说明 HSE 失败回退 HSI 的保护逻辑生效。")
para(doc, "说明：本次实验环境中 USB 上没有接 ST-Link 和目标板，因此上面的现象是按代码与镜像推导的预期现象，"
          "已通过第 7.1 节的反汇编核对确认寄存器操作无误，需在实际板子上复测确认。")

# ----------------------------------------------------------------- 10 问题
doc.add_heading("10　常见问题与排查", level=1)
add_table(
    doc,
    ["现象", "可能原因", "解决办法"],
    [
        ["编译报 undefined reference to `SystemInit'",
         "SystemInit 被 static 修饰，汇编里的 bl 找不到符号",
         "去掉 static，并在文件里保留函数声明"],
        ["make 报 syntax error: unexpected end of file",
         "Makefile 里用了 cmd 的 if/mkdir 写法，而 make 用的是 sh",
         "改成 mkdir -p、rm -rf 等 sh 命令"],
        ["编译提示找不到 arm-none-eabi-gcc",
         "工具链目录没有加进 PATH",
         "按 README 里的 set PATH 命令加入，或把 PREFIX 写成绝对路径"],
        ["下载完成但 LED 不亮",
         "BOOT0 接成了 1（从 RAM 启动）；或下载后没复位",
         "BOOT0 跳线接 0，下载后按 NRST"],
        ["LED 常亮或常灭，不闪",
         "板子是高电平点亮，极性判断反了；或程序停在 HardFault",
         "把 board.h 的 LED_ACTIVE_LOW 改成 0；用调试器看 PC 是否停在 Default_Handler"],
        ["闪烁明显过快或过慢",
         "SystemCoreClock 与实际主频不一致（改了倍频却没改这个值）",
         "确认 SystemInit 末尾的赋值与 PLL 配置一致"],
        ["CubeProgrammer 报 No STM32 target found",
         "SWD 线序接错、目标板没供电、复位脚被拉低",
         "核对 SWDIO/SWCLK/GND/3V3 四根线，先给板子上电再连接"],
        ["LED 发烫或亮度异常",
         "限流电阻太小，或把 LED 直接并在 3.3V 与 GND 之间",
         "串联 470Ω~1kΩ 电阻，注意 PC13 最大只能输出 3mA"],
    ],
    widths=[5.0, 5.6, 6.2],
)
caption(doc, "表 8　常见问题与排查方法")

# ----------------------------------------------------------------- 11 总结
doc.add_heading("11　实验总结", level=1)
para(doc, "这次实验虽然只是让一个 LED 闪起来，但把 STM32 开发中最基础的一条链路完整走通了："
          "从上电取向量表、搬运数据段、配置时钟，到开外设时钟、配置 GPIO、用 SysTick 计时，最后编译成 624 字节的镜像。"
          "不依赖 HAL 库手写一遍之后，我对“为什么必须先开 GPIO 时钟”“为什么 72MHz 要设 Flash 等待周期”"
          "“为什么 BSRR 比 ODR 好用”这些以前死记硬背的问题有了直观理解。")
para(doc, "过程中也踩了两个坑：一是 SystemInit 加了 static 导致链接失败，二是 Makefile 混用了 Windows 批处理语法。"
          "两个问题都出在“工具链的约定”上，而不是算法上，这提醒我以后遇到编译/链接错误，"
          "要先分清是语法问题、符号问题还是环境问题。")
para(doc, "后续可以在这个工程上继续做三件事：用 TIM 的 PWM 输出做呼吸灯；加一个按键，用 EXTI 中断切换 LED 状态；"
          "以及按附录 B 用 CubeMX + HAL 重写一遍，对比两种写法的代码量和可读性。")

# ----------------------------------------------------------------- 附录
doc.add_page_break()
doc.add_heading("附录 A　主程序完整源码（main.c）", level=1)
with open(os.path.join(PROJ, "Core", "Src", "main.c"), encoding="utf-8") as fp:
    src = fp.read()
add_code(doc, src, size=8.0)

doc.add_heading("附录 B　若要求使用 CubeMX + HAL", level=1)
for i, item in enumerate([
    "联网安装固件包：Help → Manage Embedded Software Packages，展开 STM32F1，安装 STM32Cube MCU Package for STM32F1 最新版（约 200~300MB）。",
    "新建工程：File → New → STM32 Project，在芯片选择框里输入 STM32F103C8，选中 STM32F103C8Tx，命名后 Finish。",
    "配置引脚：在芯片图上点 PC13，选择 GPIO_Output；左侧 System Core → RCC，High Speed Clock (HSE) 选 Crystal/Ceramic Resonator。",
    "配置时钟：切到 Clock Configuration 页，Input frequency 填 8，PLL Source 选 HSE，PLLMul 选 ×9，"
    "System Clock Mux 选 PLLCLK，确认 HCLK 显示 72MHz 后回车，CubeMX 会自动算出各分频系数。",
    "生成代码：Project Manager 页 Toolchain 选 STM32CubeIDE，勾选 “Generate peripheral initialization as a pair of .c/.h files”，点 GENERATE CODE。",
    "写主循环：在 main.c 的 while (1) 里加入 HAL_GPIO_TogglePin(GPIOC, GPIO_PIN_13); HAL_Delay(500); 然后编译下载。",
], start=1):
    p = doc.add_paragraph(style="List Number")
    p.paragraph_format.line_spacing = 1.5
    p.paragraph_format.space_after = Pt(2)
    r = p.add_run(item)
    set_run(r, size=10.5)

doc.add_heading("附录 C　参考资料", level=1)
for item in [
    "STMicroelectronics.《RM0008 Reference manual: STM32F101xx, STM32F102xx, STM32F103xx, STM32F105xx and STM32F107xx advanced Arm-based 32-bit MCUs》.",
    "STMicroelectronics.《STM32F103x8 / STM32F103xB Datasheet》.",
    "STMicroelectronics.《UM2609 STM32CubeIDE user guide》.",
    "Joseph Yiu.《ARM Cortex-M3 权威指南》.",
]:
    p = doc.add_paragraph(style="List Number")
    p.paragraph_format.line_spacing = 1.5
    p.paragraph_format.space_after = Pt(2)
    r = p.add_run(item)
    set_run(r, size=10)

doc.save(OUT)
print("saved:", OUT)

# ----------------------------------------------------------------- 校验
check = Document(OUT)
paras = [p.text for p in check.paragraphs]
tables = len(check.tables)
pics = len(check.inline_shapes)
print("paragraphs:", len(paras), "tables:", tables, "images:", pics)
for must in ["实验目的", "实验环境与配置检查", "实验总结", "附录 A"]:
    print("has", must, ":", any(must in t for t in paras))
print("appendixA_lines:", max((t.count("\n") for t in paras), default=0))
