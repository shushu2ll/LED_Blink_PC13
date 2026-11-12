# -*- coding: utf-8 -*-
"""生成《从零做一遍：点亮 LED 作业操作流程》.docx（只新建文档，不改动工程代码）"""
import os
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

PROJ = r"F:\STM32CubeIDE_2.2.0\LED_Blink_PC13"
OUT = os.path.join(PROJ, "从零做一遍-点亮LED作业流程.docx")

SONG, HEI, MONO = "宋体", "黑体", "Consolas"


# ------------------------------------------------------------------ 基础工具
def set_run(run, size=10.5, bold=False, color=None, latin="Times New Roman", ea=SONG):
    run.font.size = Pt(size)
    run.bold = bold
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


def para(doc, text, size=10.5, bold=False, color=None, indent=True,
         align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_after=6, spacing=1.5):
    p = doc.add_paragraph()
    p.alignment = align
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = spacing
    if indent:
        p.paragraph_format.first_line_indent = Pt(size * 2)
    r = p.add_run(text)
    set_run(r, size=size, bold=bold, color=color)
    return p


def bullet(doc, text, size=10.5, style="List Bullet"):
    p = doc.add_paragraph(style=style)
    p.paragraph_format.line_spacing = 1.4
    p.paragraph_format.space_after = Pt(2)
    r = p.add_run(text)
    set_run(r, size=size)
    return p


def caption(doc, text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(3)
    p.paragraph_format.space_after = Pt(9)
    r = p.add_run(text)
    set_run(r, size=9, color=RGBColor(0x40, 0x40, 0x40))


def set_table_layout(t, widths):
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
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(2)
        r = p.add_run(h)
        set_run(r, size=font_size, bold=True, ea=HEI)
        shade(cell, "DEEAF6")
    for row in rows:
        cells = t.add_row().cells
        for i, val in enumerate(row):
            cells[i].text = ""
            p = cells[i].paragraphs[0]
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(2)
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
    cell.width = Cm(15.6)
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
    set_table_layout(t, [15.6])
    if len(lines) <= 30:
        no_split_rows(t, header=False)
    return t


def add_footer(section):
    p = section.footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r1 = p.add_run("第 ")
    set_run(r1, size=9)
    run = p.add_run()
    set_run(run, size=9)
    b = OxmlElement("w:fldChar")
    b.set(qn("w:fldCharType"), "begin")
    it = OxmlElement("w:instrText")
    it.set(qn("xml:space"), "preserve")
    it.text = " PAGE "
    e = OxmlElement("w:fldChar")
    e.set(qn("w:fldCharType"), "end")
    run._r.append(b)
    run._r.append(it)
    run._r.append(e)
    r2 = p.add_run(" 页")
    set_run(r2, size=9)


# ------------------------------------------------------------------ 文档设置
doc = Document()
sec = doc.sections[0]
sec.page_width, sec.page_height = Cm(21.0), Cm(29.7)
sec.top_margin = sec.bottom_margin = Cm(2.54)
sec.left_margin = sec.right_margin = Cm(2.6)

normal = doc.styles["Normal"]
normal.font.name = "Times New Roman"
normal.font.size = Pt(10.5)
normal.element.get_or_add_rPr().append(OxmlElement("w:rFonts"))
normal.element.get_or_add_rPr().find(qn("w:rFonts")).set(qn("w:eastAsia"), SONG)

for name, size in (("Heading 1", 15.5), ("Heading 2", 12.5)):
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
    for attr in ("w:eastAsia", "w:ascii", "w:hAnsi"):
        rf.set(qn(attr), HEI)
    st.paragraph_format.space_before = Pt(14)
    st.paragraph_format.space_after = Pt(7)
    st.paragraph_format.line_spacing = 1.25
    st.paragraph_format.keep_with_next = True

add_footer(sec)
sec.different_first_page_header_footer = True

# ------------------------------------------------------------------ 标题
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.paragraph_format.space_before = Pt(6)
r = p.add_run("从零做一遍：点亮 LED 作业操作流程")
set_run(r, size=20, bold=True, ea=HEI)

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.paragraph_format.space_after = Pt(10)
r = p.add_run("STM32F103C8T6 ｜ PC13 ｜ 寄存器方式（不需要 HAL、不需要联网）")
set_run(r, size=11, color=RGBColor(0x40, 0x40, 0x40), ea=HEI)

t = add_table(
    doc,
    ["这份文档是什么", "这份文档不是什么"],
    [["“操作流程单”：每一步写清楚做什么、怎么做、怎么判断做对了，按顺序做完就能得到一块会闪的板子和一份能交的报告。",
      "不是实验报告本身（报告是《点亮LED实验报告.docx》，讲原理和结果）；这里只讲“动手的先后顺序和验证方法”。"]],
    widths=[7.8, 7.8],
    font_size=9,
)
caption(doc, "表 0　文档定位")

para(doc, "配套的成品工程已经放在 F:\\STM32CubeIDE_2.2.0\\LED_Blink_PC13 里。如果你只想把现成工程跑起来、"
          "不想重写代码，直接看第 4、5、6 章；如果你想自己从零写一遍（交作业、答辩更踏实），按第 1 章到第 7 章"
          "的顺序做，全程约 4 小时。文中的文件路径、命令都是按你机器上的实际位置写的，可以照抄。")

# ------------------------------------------------------------------ 0 全景
doc.add_heading("0　先看全景：六个阶段、四小时", level=1)
para(doc, "整件事可以拆成六段，每段都有明确的“做完的标志”。不要跳着做，尤其不要跳过第 1 段直接写代码——"
          "环境没确认就动手，后面出问题会分不清是代码错还是环境错。")
add_table(
    doc,
    ["阶段", "你要做的事", "做完的产出", "怎么算做完了", "用时"],
    [
        ["1 环境", "确认 IDE、编译器、板子三方就绪", "三条命令能出结果", "gcc 报 14.3.1、make 报版本、设备管理器有 STLink", "15 分钟"],
        ["2 骨架", "建目录，放 6 个空壳文件", "能编译的最小工程", "make 通过，elf 只有几十字节", "10 分钟"],
        ["3 代码", "按顺序填 4 个文件的逻辑", "main.c 写完", "编译零警告", "60~90 分钟"],
        ["4 编译", "make，看内存占用和镜像", "build 下三个产物", "FLASH 624 B、RAM 1544 B", "15 分钟"],
        ["5 烧录", "接线、下载、复位", "芯片里有程序", "下载提示成功、灯开始闪", "15 分钟"],
        ["6 验证", "看现象、做对照实验、留证据", "数据和照片", "能说清“为什么亮、为什么是这个频率”", "20 分钟"],
        ["7 报告", "按骨架填内容", "交上去的 docx", "原理、步骤、数据、结论齐全", "60 分钟"],
    ],
    widths=[1.6, 5.0, 3.4, 4.4, 1.4],
    font_size=8.5,
)
caption(doc, "表 1　六个阶段与验收标准")

# ------------------------------------------------------------------ 1 环境
doc.add_heading("1　阶段一：确认环境（15 分钟）", level=1)
para(doc, "这一步只做三件事：确认 IDE 能开、编译器能用、板子能被电脑认出来。任何一件不满足，先解决它，别往下走。")

doc.add_heading("1.1　IDE 能开", level=2)
para(doc, "双击 F:\\STM32CubeIDE_2.2.0\\STM32CubeIDE\\stm32cubeide.exe。第一次启动会让你选工作区（Workspace），"
          "默认路径是 C:\\Users\\<用户名>\\STM32CubeIDE\\workspace_2.2.0，直接用它或者填 F:\\STM32_workspace 都行。"
          "注意：不要把这个工作区放到 IDE 的安装目录里面，以后备份、重装会很麻烦。")

doc.add_heading("1.2　编译器能用", level=2)
para(doc, "IDE 自带编译器，不用另装。打开 cmd 或 PowerShell，把工具链目录加进 PATH 再查版本：")
add_code(doc, """set PATH=F:\\STM32CubeIDE_2.2.0\\STM32CubeIDE\\plugins\\com.st.stm32cube.ide.mcu.externaltools.gnu-tools-for-stm32.14.3.rel1.win32_1.0.100.202602081740\\tools\\bin;%PATH%
arm-none-eabi-gcc --version""")
para(doc, "第一行应该出现“GNU Tools for STM32 14.3.rel1”和“14.3.1”。make 同理，把 make 插件目录也加进 PATH："
          "…\\com.st.stm32cube.ide.mcu.externaltools.make.win32_2.2.200.202604021615\\tools\\bin，执行 make --version。",
     align=WD_ALIGN_PARAGRAPH.LEFT, indent=False)

doc.add_heading("1.3　板子能被认出来", level=2)
para(doc, "ST-Link 插到电脑 USB 口，打开“设备管理器”，通用串行总线设备里应出现 STLink 字样。"
          "如果什么都没出现，或者出现带黄色感叹号的未知设备，就装一次驱动："
          "运行 F:\\STM32CubeIDE_2.2.0\\STM32CubeIDE\\drivers\\STLinkUSBDriver\\dpinst_amd64.exe，装完拔插一次。")
add_table(
    doc,
    ["检查项", "在哪里看 / 敲什么", "正常表现", "不正常怎么办"],
    [
        ["IDE", "双击 stm32cubeide.exe", "出现选择工作区的窗口", "重装 IDE，或检查安装目录是否完整"],
        ["gcc", "arm-none-eabi-gcc --version", "GNU Tools for STM32 14.3.rel1", "PATH 没加对，检查路径拼写"],
        ["make", "make --version", "GNU Make 4.x", "同上，注意是 make 插件目录"],
        ["下载器", "设备管理器 → USB 设备", "出现 STLink", "装 dpinst_amd64.exe 驱动"],
        ["固件包", "不需要", "本流程用不到", "CubeMX 生成 HAL 才需要，见附录 B"],
    ],
    widths=[2.2, 5.2, 4.4, 4.0],
    font_size=8.5,
)
caption(doc, "表 2　环境检查表")

# ------------------------------------------------------------------ 2 骨架
doc.add_heading("2　阶段二：搭骨架（10 分钟）", level=1)
para(doc, "先建目录、放“空壳”，让一个什么都不做的工程先编译通过，再往里填代码。这是嵌入式开发最省时间的做法："
          "把“环境问题”和“代码问题”分开解决。")

doc.add_heading("2.1　目录结构", level=2)
add_code(doc, """LED_Blink_PC13\\
├── Core\\
│   ├── Inc\\      stm32f103_regs.h（寄存器定义）、board.h（LED 在哪个脚）
│   ├── Src\\      main.c
│   └── Startup\\  startup_stm32f103c8tx.s（启动文件）
├── STM32F103C8TX_FLASH.ld   链接脚本
├── Makefile                 编译脚本
└── build\\                   编译产物（自动生成，不用手工建）""")

doc.add_heading("2.2　六个文件各干什么", level=2)
add_table(
    doc,
    ["文件", "职责", "建议写的顺序", "能不能抄现成的"],
    [
        ["stm32f103_regs.h", "把 RCC、GPIO、FLASH、SysTick 的寄存器映射成 C 结构体", "第 2 个", "可以，纯体力活"],
        ["Core\\Startup\\startup_….s", "中断向量表 + 复位后搬 .data、清 .bss、调 main", "第 4 个", "可以，重点看懂三段"],
        ["STM32F103C8TX_FLASH.ld", "告诉链接器 Flash 64K、RAM 20K 从哪开始", "第 3 个", "可以，只有几行要改"],
        ["Core\\Inc\\board.h", "LED 接在哪个端口/引脚、高电平还是低电平点亮", "第 1 个", "自己写，只有几行"],
        ["Core\\Src\\main.c", "时钟、GPIO、SysTick、主循环", "第 5 个", "要自己写，这是作业主体"],
        ["Makefile", "编译、链接、生成 hex/bin", "先写一个能用的版本", "可以，注意 shell 语法"],
    ],
    widths=[4.0, 5.6, 3.0, 3.0],
    font_size=8.5,
)
caption(doc, "表 3　文件职责与建议顺序")

doc.add_heading("2.3　两个必须想明白的问题", level=2)
para(doc, "为什么要有启动文件？芯片一上电，CPU 只会做一件事：从 Flash 的最前面读两个数，第一个当栈顶地址，第二个当"
          "复位后第一条指令的地址。这个“表”就是中断向量表，而 C 语言写不出这种按地址布局的东西，所以必须有一段汇编垫在"
          "main() 前面。它还要负责把带初值的全局变量从 Flash 搬到 RAM、把没初值的变量清零——这两件事做完，C 语言的"
          "环境才算准备好了。")
para(doc, "为什么要有链接脚本？编译器只知道“有个变量”，不知道这块芯片 Flash 有 64K、RAM 有 20K、分别从哪个地址开始。"
          "链接脚本就是告诉链接器这些信息，顺便定义 _estack（栈顶）和 _sidata（.data 在 Flash 里的存放位置），"
          "启动文件里的搬运代码就是靠这几个符号干活的。")

doc.add_heading("2.4　先让空壳编译通过", level=2)
para(doc, "把链接脚本、Makefile、启动文件先放进去，main.c 里只写一个空的死循环：")
add_code(doc, """int main(void)
{
    while (1) { }
}""")
para(doc, "这时执行 make，应该能生成一个只有几百字节的 elf。能通过就说明目录、链接脚本、Makefile、启动文件四者配合正确，"
          "后面再往 main.c 里加逻辑，出错就一定是逻辑错，不会是环境错。这一步做不做，决定了你后面排错是五分钟还是两小时。")

# ------------------------------------------------------------------ 3 代码
doc.add_heading("3　阶段三：填代码（60~90 分钟）", level=1)
para(doc, "顺序建议：board.h → 寄存器头文件 → 链接脚本 → 启动文件 → main.c → Makefile。每写完一个都编译一次，"
          "不要一口气写完再编。下面是四个关键片段，以及“为什么这么写”。")

doc.add_heading("3.1　board.h：把“灯在哪、怎么样才算亮”定义清楚", level=2)
add_code(doc, """#define LED_PORT        GPIOC
#define LED_PIN         13U
#define LED_ACTIVE_LOW  1        /* 蓝飞板：低电平点亮 */

#if LED_ACTIVE_LOW
  #define LED_ON()   (LED_PORT->BSRR = (1UL << (LED_PIN + 16U)))  /* 写高 16 位 = 输出低 */
  #define LED_OFF()  (LED_PORT->BSRR = (1UL << LED_PIN))          /* 写低 16 位 = 输出高 */
#else
  #define LED_ON()   (LED_PORT->BSRR = (1UL << LED_PIN))
  #define LED_OFF()  (LED_PORT->BSRR = (1UL << (LED_PIN + 16U)))
#endif""")
para(doc, "把极性做成宏的好处是：换一块高电平点亮的板子，只改一个 1，不用满代码找。用 BSRR 而不是直接写 ODR，"
          "是因为 BSRR 是原子操作，写一次只影响一个引脚，同端口其他脚不受干扰。")

doc.add_heading("3.2　寄存器头文件：两天规则", level=2)
para(doc, "第一条：结构体成员的顺序必须和手册里寄存器的偏移顺序一致，因为 C 结构体是连续排布的；"
          "第二条：结构体指针的基地址必须和手册“存储器映射”章节的地址一致（RCC 是 0x40021000，GPIOC 是 0x40011000）。"
          "只要这两条对，编译器生成的访问指令就一定落在正确的寄存器上。这部分可以直接抄工程里的 stm32f103_regs.h，"
          "但建议你对着手册核一遍 RCC 和 GPIO 两个结构体，核完就再也不会怕“为什么我的寄存器写不进去”。")

doc.add_heading("3.3　启动文件：只看三段", level=2)
para(doc, "不用逐行读，抓住三段就够：")
bullet(doc, "向量表：开头两行是 .word _estack 和 .word Reset_Handler，后面依次是各个中断的名字；")
bullet(doc, "复位处理：把 _sidata 开始的初值搬到 _sdata，再把 _sbss 到 _ebss 清零；")
bullet(doc, "最后两行：bl SystemInit（配时钟）、bl main（进 C 世界）。")
para(doc, "写完可以用反汇编验证：向量表第一个字应该是 0x20005000（RAM 末尾），第二个字是复位入口且末位为 1（Thumb 状态）。")

doc.add_heading("3.4　链接脚本：只有三处要按芯片改", level=2)
add_code(doc, """MEMORY
{
  FLASH (rx)  : ORIGIN = 0x08000000, LENGTH = 64K   /* C8T6 是 64K */
  RAM   (xrw) : ORIGIN = 0x20000000, LENGTH = 20K   /* C8T6 是 20K */
}
_estack = ORIGIN(RAM) + LENGTH(RAM);                 /* 栈顶 = 0x20005000 */""")
para(doc, "换成 C8T6 以外的型号（比如 ZET6 是 512K/64K），只改这两个 LENGTH。另外 _sidata = LOADADDR(.data) 这一行别删，"
          "启动文件搬初值要靠它。")

doc.add_heading("3.5　main.c：四段，一段一件事", level=2)
para(doc, "（1）时钟。复位后跑的是内部 HSI 8MHz，要用外部晶振倍频到 72MHz，关键是三件事：等 HSE 起振、"
          "PLL 选 HSE 且 ×9、把系统时钟切到 PLL；72MHz 还要给 Flash 插 2 个等待周期。", indent=False, space_after=3)
add_code(doc, """RCC->CR   |= RCC_CR_HSEON;                       /* 开晶振 */
while ((RCC->CR & RCC_CR_HSERDY) == 0U) { }       /* 等起振（实际加了超时） */
FLASH->ACR = (FLASH->ACR & ~FLASH_ACR_LATENCY) | FLASH_ACR_PRFTBE | 0x2UL;
RCC->CFGR |= (RCC_CFGR_HPRE_DIV1 | RCC_CFGR_PPRE1_DIV2 | RCC_CFGR_PPRE2_DIV1);
RCC->CFGR |= (RCC_CFGR_PLLSRC | RCC_CFGR_PLLMULL9);   /* 8MHz × 9 = 72MHz */
RCC->CR   |= RCC_CR_PLLON;
while ((RCC->CR & RCC_CR_PLLRDY) == 0U) { }
RCC->CFGR  = (RCC->CFGR & ~RCC_CFGR_SW) | RCC_CFGR_SW_PLL;
while ((RCC->CFGR & RCC_CFGR_SWS) != RCC_CFGR_SWS_PLL) { }""")

para(doc, "（2）GPIO。先开 GPIOC 的时钟（不开时钟写 CRH 是白写），再把 PC13 配成 2MHz 推挽输出。PC13 在 CRH 里，"
          "起始位是 (13−8)×4 = 20。", indent=False, space_after=3)
add_code(doc, """RCC->APB2ENR |= RCC_APB2ENR_IOPCEN;                   /* 开 GPIOC 时钟 */
GPIOC->CRH &= ~(0xFUL << 20);                       /* 清 PC13 的 4 位 */
GPIOC->CRH |=  (0x2UL << 20);                       /* 0010 = 输出 2MHz 推挽 */""")

para(doc, "（3）延时。用内核的 SysTick：装载值 = 主频/1000 − 1，减到 0 就是 1ms，读 CTRL 的 COUNTFLAG 判断。"
          "注意装载值要用 SystemCoreClock 算，不能写死 72000，否则晶振失败退回 8MHz 时延时会差 9 倍。", indent=False, space_after=3)
add_code(doc, """SysTick->LOAD = (SystemCoreClock / 1000UL) - 1UL;
SysTick->VAL  = 0UL;
SysTick->CTRL = SysTick_CTRL_CLKSOURCE | SysTick_CTRL_ENABLE;
/* 延时：while (ms--) { while (!(SysTick->CTRL & SysTick_CTRL_COUNTFLAG)) { } } */""")

para(doc, "（4）主循环。亮 500ms、灭 500ms，周期就是 1 秒。", indent=False, space_after=3)
add_code(doc, """while (1) {
    LED_ON();      delay_ms(500U);
    LED_OFF();     delay_ms(500U);
}""")

doc.add_heading("3.6　写完自检三问", level=2)
bullet(doc, "我有没有先打开这个外设的时钟？（GPIO 在 APB2，串口/定时器在 APB1，开错了寄存器根本不响应）")
bullet(doc, "CRH 还是 CRL？位号算对了吗？（Pin0~7 用 CRL，Pin8~15 用 CRH，起始位 =(pin%8)×4）")
bullet(doc, "我的延时基准和真实主频一致吗？（改了倍频没改 SystemCoreClock，灯会快 9 倍或慢 9 倍）")

# ------------------------------------------------------------------ 4 编译
doc.add_heading("4　阶段四：编译（15 分钟）", level=1)
para(doc, "在工程目录下打开 cmd，把工具链加进 PATH 后执行 make（或者直接双击工程里的 build.bat）。成功的标志是这样三行：")
add_code(doc, """Memory region         Used Size  Region Size  %age Used
           FLASH:         624 B        64 KB      0.95%
             RAM:        1544 B        20 KB      7.54%""")
para(doc, "同时 build 目录下会出现 LED_Blink_PC13.elf / .hex / .bin 三个文件。624 字节里有一半是中断向量表（236 字节），"
          "真正干活的指令不到 400 字节——这就是不用 HAL 库的直观好处，也是报告里可以写的一个点。")

doc.add_heading("4.1　常见报错对照", level=2)
add_table(
    doc,
    ["报错关键字", "真正的原因", "怎么改"],
    [
        ["undefined reference to `SystemInit'", "函数写成了 static，汇编里的 bl 找不到符号", "去掉 static"],
        ["syntax error: unexpected end of file", "Makefile 里用了 cmd 的 if/mkdir，而 make 用 sh", "改成 mkdir -p、rm -rf"],
        ["arm-none-eabi-gcc: not found", "PATH 没加对，或从没配过", "按 1.2 补齐 PATH"],
        ["region `FLASH' overflowed", "代码超过 64K（一般是误加了大的数组或库）", "看 map 文件，检查段大小"],
        ["warning: '_close' is not implemented", "链接了 nosys 的系统调用桩，无害", "可忽略，或在链接参数里去掉 nosys"],
    ],
    widths=[5.0, 6.0, 4.6],
    font_size=8.5,
)
caption(doc, "表 4　编译报错对照表")
para(doc, "前两条是这次实际踩过的坑，写进报告里反而是加分项——说明你真的一步步做过，而不是拷了一份代码。")

doc.add_heading("4.2　编译之外的三条自检命令", level=2)
add_code(doc, """arm-none-eabi-objdump -s -j .isr_vector build\\LED_Blink_PC13.elf   rem 看向量表前 4 个字
arm-none-eabi-nm -n build\\LED_Blink_PC13.elf | findstr /i "estack Reset_Handler SystemInit"
arm-none-eabi-objdump -d build\\LED_Blink_PC13.elf | findstr /a:0A /c:"<main>:" /c:"<SystemInit>:\"""")
para(doc, "期望值：向量表第一个字 0x20005000（20K RAM 的末尾）、第二个字形如 0x0800xxxx 且末位是 1；"
          "_estack 在 0x20005000；main 的反汇编里能看到对 0x40011000+0x04（GPIOC_CRH）和 +0x10（BSRR）的写入。"
          "这一步不用板子就能证明“程序写对了”，报告里的“镜像校验”一节就是这么来的。")

# ------------------------------------------------------------------ 5 烧录
doc.add_heading("5　阶段五：烧录（15 分钟）", level=1)
para(doc, "烧录前先确认三件硬件上的事，任何一件不满足都会卡在这里：")
add_table(
    doc,
    ["项目", "怎么接 / 怎么设置", "不接会怎样"],
    [
        ["SWD 四根线", "SWDIO → PA13，SWCLK → PA14，GND ↔ GND，3.3V ↔ 3.3V", "连不上芯片，报 No target"],
        ["供电", "ST-Link 的 3.3V 给板子供电，或板子单独 USB 供电（二选一）", "芯片不工作，同样连不上"],
        ["BOOT0", "跳线接到 0（从 Flash 启动）", "能下载但程序不跑，灯不亮"],
    ],
    widths=[2.4, 7.6, 5.6],
    font_size=8.5,
)
caption(doc, "表 5　烧录前的硬件检查")

para(doc, "三种烧录方式，按你的情况选一种：")
add_table(
    doc,
    ["方式", "怎么做", "适合谁", "失败了看哪里"],
    [
        ["双击脚本", "双击工程里的 flash.bat", "想省事、第一次做", "窗口里的报错提示"],
        ["命令行", "STM32_Programmer_CLI.exe -c port=SWD -w build\\LED_Blink_PC13.hex -v -rst", "想批量、想写进报告", "命令行最后一行"],
        ["IDE 调试", "右键工程 → Debug As → STM32 C/C++ Application", "要单步、看寄存器", "Console 里的 GDB 日志"],
    ],
    widths=[2.2, 7.4, 3.4, 3.0],
    font_size=8.5,
)
caption(doc, "表 6　三种烧录方式")
para(doc, "成功标志：命令行出现 Download verified successfully，然后板子复位、LED 开始 1 秒一闪。"
          "如果看到 No debug probe detected，是没插 ST-Link 或驱动没装；看到 No STM32 target found，是 SWD 线不对或板子没供电；"
          "下载成功了但灯不亮，先查 BOOT0，再查 LED 极性。")

# ------------------------------------------------------------------ 6 验证
doc.add_heading("6　阶段六：验证与记录（20 分钟）", level=1)
para(doc, "“灯亮了”只是及格线，作业里要能说清楚“为什么亮、为什么是这个频率”。下面是判据和三个对照实验。")
add_table(
    doc,
    ["现象", "说明什么", "下一步"],
    [
        ["1Hz 均匀闪烁（亮 500ms、灭 500ms）", "时钟、GPIO、延时全对", "可以记录数据了"],
        ["闪得飞快或极慢", "SystemCoreClock 和实际主频不一致", "检查 PLL 配置与赋值"],
        ["一直亮 / 一直灭", "极性反了，或程序卡在 HardFault", "改 LED_ACTIVE_LOW，或进调试看 PC"],
        ["完全不亮，测 PC13 一直是 3.3V", "程序没跑起来（BOOT0、复位、供电）", "按 5 章的顺序排查"],
        ["完全不亮，测 PC13 一直是 0V", "引脚被短路或配置成输入", "检查焊接和 CRH 的值"],
    ],
    widths=[5.4, 5.6, 4.6],
    font_size=8.5,
)
caption(doc, "表 7　现象判据")

para(doc, "三种测量手段，有什么用什么：眼睛看周期；万用表直流档测 PC13 对 GND，应约 1.6V（3.3V 与 0V 各占一半，"
          "这正好证明占空比 50%）；有示波器就量波形，1Hz 方波、占空比 50%。")

doc.add_heading("6.1　三个“故意做错”的对照实验", level=2)
add_table(
    doc,
    ["实验", "怎么改", "预期现象", "说明什么"],
    [
        ["拔掉晶振再上电", "把 8MHz 晶振一端焊开（或找个没焊晶振的板子）", "LED 仍然 1Hz 闪", "HSE 失败自动退回 HSI 的保护逻辑有效"],
        ["改极性", "board.h 里 LED_ACTIVE_LOW 改成 0，重编译烧录", "变成“亮 500ms、灭 500ms”反相：原本亮的时候灭", "证明你理解了低电平点亮"],
        ["改延时", "delay_ms(500U) 改成 100U", "闪得更快（周期 200ms）", "证明延时的基准是 1ms 节拍"],
    ],
    widths=[3.2, 5.4, 4.2, 4.8],
    font_size=8.5,
)
caption(doc, "表 8　三个对照实验")

doc.add_heading("6.2　要留下的证据", level=2)
bullet(doc, "板子通电、LED 亮的照片 1 张（能看清 PC13 附近的丝印最好）；")
bullet(doc, "闪烁视频 10 秒（手机拍即可，报告里写“见附件视频”）；")
bullet(doc, "编译成功的截图（要有 624 B 那三行）；")
bullet(doc, "万用表读数照片或示波器截图；")
bullet(doc, "调试时停在 main() 的截图（可选，但很能说明问题）。")

# ------------------------------------------------------------------ 7 报告
doc.add_heading("7　阶段七：写报告（60 分钟）", level=1)
para(doc, "报告不用从零编，按下面的骨架填内容就行。这个骨架和《点亮LED实验报告.docx》是一一对应的，"
          "你可以直接拿它当模板，把里面的数据换成你自己测的。")
add_table(
    doc,
    ["章节", "写什么", "放什么图表"],
    [
        ["1 实验目的", "4~5 条，动词开头（熟悉/掌握/学会/走通）", "无"],
        ["2 环境检查", "IDE 版本、编译器版本、有没有固件包、有没有接调试器", "配置检查表"],
        ["3 实验原理", "LED 电路与低电平点亮、GPIO 的 4 位配置、时钟树、SysTick", "寄存器表、时钟配置表"],
        ["4 硬件连接", "接线表 + 电路示意", "接线表 + 接线图"],
        ["5 软件设计", "工程结构、程序流程、关键代码", "文件说明表 + 流程图 + 代码片段"],
        ["6 实验步骤", "按你实际做的顺序写，包含报错和修正", "无（用编号列表）"],
        ["7 编译结果", "贴真实编译输出、size、镜像校验数据", "编译日志 + 校验表"],
        ["8 烧录与运行", "接线、软件、命令、成功标志", "烧录命令"],
        ["9 现象与验证", "现象描述 + 测量数据 + 对照实验", "现象表 + 照片/示波器图"],
        ["10 问题与排查", "你踩过的坑（至少写 2 个）", "排错表"],
        ["11 总结", "收获、不足、改进方向", "无"],
    ],
    widths=[3.0, 8.4, 4.2],
    font_size=8.5,
)
caption(doc, "表 9　报告骨架")

doc.add_heading("7.1　加分点与扣分点", level=2)
para(doc, "加分：① 原理部分能讲清“为什么 PC13 要配成 0010”“为什么 72MHz 要 2 个等待周期”，而不是抄一段话；"
          "② 贴真实的编译输出和报错，包括你改错的过程；③ 有对照实验的数据（表 8），说明你不是“碰巧点亮”。")
para(doc, "扣分：① 只有截图没有原理；② 现象写成“灯亮了，实验成功”，没有周期、没有电压；"
          "③ 报告里的代码和工程里的对不上（改过但忘了同步）。")

# ------------------------------------------------------------------ 附录
doc.add_heading("附录 A　一页速查", level=1)
add_code(doc, """rem 1) 配好 PATH（两个目录）
set PATH=F:\\STM32CubeIDE_2.2.0\\STM32CubeIDE\\plugins\\com.st.stm32cube.ide.mcu.externaltools.gnu-tools-for-stm32.14.3.rel1.win32_1.0.100.202602081740\\tools\\bin;F:\\STM32CubeIDE_2.2.0\\STM32CubeIDE\\plugins\\com.st.stm32cube.ide.mcu.externaltools.make.win32_2.2.200.202604021615\\tools\\bin;%PATH%

rem 2) 编译（或双击 build.bat）
cd /d F:\\STM32CubeIDE_2.2.0\\LED_Blink_PC13
make

rem 3) 烧录（或双击 flash.bat）
set PATH=F:\\STM32CubeIDE_2.2.0\\STM32CubeIDE\\plugins\\com.st.stm32cube.ide.mcu.externaltools.cubeprogrammer.win32_2.2.500.202603051304\\tools\\bin;%PATH%
STM32_Programmer_CLI.exe -c port=SWD -w build\\LED_Blink_PC13.hex -v -rst

rem 4) 清理重编（或双击 clean.bat）
make clean && make""")

doc.add_heading("附录 B　如果老师要求用 CubeMX + HAL", level=1)
para(doc, "流程会变，但“先编译通过再烧录”的顺序不变。主要差别如下：")
add_table(
    doc,
    ["环节", "本流程（寄存器）", "CubeMX + HAL"],
    [
        ["准备", "只要 IDE 自带工具链", "还要联网下载 STM32Cube F1 固件包（几百 MB）"],
        ["建工程", "手工建目录、写启动文件和链接脚本", "File → New → STM32 Project，选芯片，工具自动生成"],
        ["配引脚", "写 CRH 的 4 位", "芯片图上点 PC13 → GPIO_Output"],
        ["配时钟", "写 RCC_CR / RCC_CFGR", "Clock Configuration 页填 8、选 HSE、×9，自动算分频"],
        ["点灯代码", "LED_ON(); delay_ms(500);", "HAL_GPIO_TogglePin(GPIOC, GPIO_PIN_13); HAL_Delay(500);"],
        ["镜像大小", "624 字节", "通常 8~12 KB（含 HAL 库）"],
    ],
    widths=[2.4, 6.6, 6.6],
    font_size=8.5,
)
caption(doc, "表 10　两种写法对照")

doc.add_heading("附录 C　交付物清单", level=1)
for item in [
    "工程目录 LED_Blink_PC13（含 Core、Makefile、链接脚本）",
    "build 目录下的 .hex（老师可能要，能直接烧）",
    "实验报告 docx（按第 7 章骨架）",
    "照片 / 视频 / 万用表读数（第 6.2 节）",
    "如果做了对照实验，附上三组数据的记录",
]:
    bullet(doc, item, style="List Number")

doc.save(OUT)
print("saved:", OUT)

check = Document(OUT)
print("paragraphs:", len(check.paragraphs), "tables:", len(check.tables))
for must in ["阶段一", "阶段七", "附录 A"]:
    print("has", must, ":", any(must in p.text for p in check.paragraphs))
