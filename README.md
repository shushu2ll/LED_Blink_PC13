# LED_Blink_PC13 —— STM32F103C8T6 点亮 LED（PC13）

一个**不依赖 HAL 库、不依赖 CubeMX 生成代码**的最小工程：直接写寄存器，用 STM32CubeIDE
自带的 `arm-none-eabi-gcc` 就能编译出可烧录的 `.hex / .bin`。

- 芯片：STM32F103C8T6（中容量，64KB Flash / 20KB RAM，Cortex-M3）
- LED：PC13，低电平点亮（蓝飞最小系统板的接法）
- 现象：上电后 LED 以 1Hz 闪烁（亮 500ms、灭 500ms）
- 主频：HSE 8MHz × PLL9 = 72MHz；若晶振不起振，自动退回内部 HSI 8MHz

## 一、目录结构

```
LED_Blink_PC13/
├── Core/
│   ├── Inc/
│   │   ├── stm32f103_regs.h           # 寄存器定义（只包含用到的外设）
│   │   └── board.h                    # 板级定义：LED 在哪个引脚、极性
│   ├── Src/
│   │   └── main.c                     # 时钟 / GPIO / SysTick / 主循环
│   └── Startup/
│       └── startup_stm32f103c8tx.s    # 中断向量表 + 复位入口
├── STM32F103C8TX_FLASH.ld             # 链接脚本（64K Flash / 20K RAM）
├── Makefile                           # 编译脚本
├── build/                             # 编译产物（make 自动生成）
│   ├── LED_Blink_PC13.elf
│   ├── LED_Blink_PC13.hex
│   ├── LED_Blink_PC13.bin
│   └── LED_Blink_PC13.map
├── build.bat / flash.bat / clean.bat  # 一键编译 / 烧录 / 清理
├── README.md                          # 本文件
└── 点亮LED实验报告.docx                # 作业报告（过程、原理、步骤、结果）
```

## 二、硬件连接

| 连接 | 说明 |
| --- | --- |
| 3.3V → 470Ω 电阻 → LED 阳极（长脚） | 限流，防止烧 LED 和 IO |
| LED 阴极（短脚） → PC13 | 低电平点亮 |
| ST-Link：SWDIO → PA13，SWCLK → PA14，GND ↔ GND，3.3V ↔ 3.3V | 下载与调试 |

> 蓝飞板上 PC13 的 LED 已经焊好、电阻也有，**直接用就行，不用外接**。
> 若你的板子 LED 是高电平点亮，把 `board.h` 里的 `LED_ACTIVE_LOW` 改成 `0`。

## 三、编译

### 方式 A：双击 `build.bat`（最省事，已实测）

本目录下有 3 个脚本，双击即可，不用配环境变量：

| 脚本 | 作用 |
| --- | --- |
| `build.bat` | 编译，生成 `build\LED_Blink_PC13.hex / .bin / .elf` |
| `flash.bat` | 通过 ST-Link 把 hex 烧进芯片（自动调用 IDE 自带的 STM32CubeProgrammer 命令行） |
| `clean.bat` | 删除 `build` 目录，编译出怪问题时先清理再重编 |

看到 `[OK] Generated:` 就表示成功；脚本里的工具链路径是按本机安装位置写死的，换电脑要改。

### 方式 B：命令行（本工程已验证通过）

```bat
set PATH=F:\STM32CubeIDE_2.2.0\STM32CubeIDE\plugins\com.st.stm32cube.ide.mcu.externaltools.gnu-tools-for-stm32.14.3.rel1.win32_1.0.100.202602081740\tools\bin;F:\STM32CubeIDE_2.2.0\STM32CubeIDE\plugins\com.st.stm32cube.ide.mcu.externaltools.make.win32_2.2.200.202604021615\tools\bin;%PATH%
cd /d F:\STM32CubeIDE_2.2.0\LED_Blink_PC13
make
```

看到下面三行就算成功：

```
Memory region         Used Size  Region Size  %age Used
           FLASH:         624 B        64 KB      0.95%
             RAM:        1544 B        20 KB      7.54%
```

清理：`make clean`。

### 方式 C：在 STM32CubeIDE 里打开

1. `File → New → Makefile Project with Existing Code`
2. `Existing Code Location` 选到 `F:\STM32CubeIDE_2.2.0\LED_Blink_PC13`
3. Toolchain 选 `MCU ARM GCC`，Finish
4. 在 `Project → Properties → C/C++ Build → Environment` 里把工具链路径加到 `PATH`
   （或者直接把 `Makefile` 里的 `PREFIX` 改成绝对路径）
5. 点工具栏小锤子编译

## 四、烧录

**前提**：ST-Link 插 USB（设备管理器里出现 STLink 才算驱动装好）；SWD 的 SWDIO→PA13、
SWCLK→PA14、GND→GND、3.3V→3.3V；目标板供电；**BOOT0 跳线接 0**（从 Flash 启动，否则程序不跑）。
驱动没装的话，运行 `F:\STM32CubeIDE_2.2.0\STM32CubeIDE\drivers\STLinkUSBDriver\dpinst_amd64.exe`。

### 方式 A：双击 `flash.bat`（推荐，已实测命令行可用）

```
[OK] Programmed and reset. The LED on PC13 should blink at 1 Hz.
```

### 方式 B：手动敲命令

本机没有单独安装 STM32CubeProgrammer 图形界面，但 IDE 自带它的命令行版本（v2.23.0）：

```bat
set PATH=F:\STM32CubeIDE_2.2.0\STM32CubeIDE\plugins\com.st.stm32cube.ide.mcu.externaltools.cubeprogrammer.win32_2.2.500.202603051304\tools\bin;%PATH%
cd /d F:\STM32CubeIDE_2.2.0\LED_Blink_PC13
STM32_Programmer_CLI.exe -c port=SWD -w build\LED_Blink_PC13.hex -v -rst
```

### 方式 C：在 IDE 里烧录 / 单步调试

导入工程后：`Run → Debug Configurations → STM32 Cortex-M C/C++ Application` 新建一个，
C/C++ Application 选 `build\LED_Blink_PC13.elf`，Debugger 页选 `ST-LINK (OpenOCD)`、接口 `SWD`，然后点 Debug。

## 五、改引脚 / 改闪烁频率

- 换 LED 引脚：改 `Core/Inc/board.h` 里的 `LED_PORT`、`LED_PIN`，并同步改
  `Core/Src/main.c` 里 `GPIO_Init()` 中 `CRH/CRL` 的写法（Pin0~7 用 `CRL`，Pin8~15 用 `CRH`）。
- 换闪烁频率：改 `main()` 里 `delay_ms(500U)` 的数值，例如呼吸灯可以先改成 100ms。

## 六、这个工程为什么没有 HAL

本机 STM32CubeIDE 2.2.0 里**没有下载任何 STM32Cube 固件包**
（`C:\Users\<用户名>\STM32Cube\Repository` 不存在），CubeMX 生成 HAL 工程需要先联网下载
对应芯片的固件包。为了让你现在就能编译、烧录、交作业，这里改成纯寄存器写法：
不依赖任何第三方库，编译只要 GCC + Make，生成的镜像只有 **624 字节**。

如果你后面想改用 CubeMX + HAL 的写法，步骤见报告附录。
