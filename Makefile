##############################################################################
# 点亮 LED（STM32F103C8T6 / PC13）Makefile
#
# 用法（在 cmd / PowerShell 里，先让 make 和 arm-none-eabi-gcc 在 PATH 中）：
#     make          # 编译，生成 build/LED_Blink_PC13.elf / .hex / .bin
#     make clean    # 删除 build 目录
#
# 也可以用 STM32CubeIDE 自带的工具链，见 README.md 里“命令行编译”一节。
##############################################################################

TARGET      = LED_Blink_PC13
BUILD_DIR   = build
LDSCRIPT    = STM32F103C8TX_FLASH.ld

# 源文件
C_SOURCES   = $(wildcard Core/Src/*.c)
ASM_SOURCES = $(wildcard Core/Startup/*.s)

# 工具链
PREFIX = arm-none-eabi-
CC     = $(PREFIX)gcc
AS     = $(PREFIX)gcc -x assembler-with-cpp
CP     = $(PREFIX)objcopy
SZ     = $(PREFIX)size

# 目标芯片参数
MCU      = -mcpu=cortex-m3 -mthumb
C_DEFS   = -DSTM32F103xB
C_INCLUDES = -ICore/Inc
OPT      = -O2 -g3
CFLAGS   = $(MCU) $(C_DEFS) $(C_INCLUDES) $(OPT) -Wall -Wextra \
           -ffunction-sections -fdata-sections -std=gnu11
ASFLAGS  = $(MCU) $(OPT)

LIBS     = -lc -lm
LDFLAGS  = $(MCU) -specs=nano.specs -T$(LDSCRIPT) $(LIBS) \
           -Wl,-Map=$(BUILD_DIR)/$(TARGET).map,--cref \
           -Wl,--gc-sections -Wl,--print-memory-usage

# 把 .c / .s 映射成 build 下的 .o
OBJECTS  = $(addprefix $(BUILD_DIR)/,$(notdir $(C_SOURCES:.c=.o)))
OBJECTS += $(addprefix $(BUILD_DIR)/,$(notdir $(ASM_SOURCES:.s=.o)))
vpath %.c $(sort $(dir $(C_SOURCES)))
vpath %.s $(sort $(dir $(ASM_SOURCES)))

.PHONY: all clean

all: $(BUILD_DIR)/$(TARGET).elf $(BUILD_DIR)/$(TARGET).hex $(BUILD_DIR)/$(TARGET).bin

# ---- 编译 ----
$(BUILD_DIR)/%.o: %.c Makefile | $(BUILD_DIR)
	$(CC) -c $(CFLAGS) -Wa,-a,-ad,-alms=$(BUILD_DIR)/$(notdir $(<:.c=.lst)) $< -o $@

$(BUILD_DIR)/%.o: %.s Makefile | $(BUILD_DIR)
	$(AS) -c $(CFLAGS) $< -o $@

# ---- 链接 ----
$(BUILD_DIR)/$(TARGET).elf: $(OBJECTS) Makefile
	$(CC) $(OBJECTS) $(LDFLAGS) -o $@
	$(SZ) $@

$(BUILD_DIR)/%.hex: $(BUILD_DIR)/%.elf
	$(CP) -O ihex $< $@

$(BUILD_DIR)/%.bin: $(BUILD_DIR)/%.elf
	$(CP) -O binary -S $< $@

$(BUILD_DIR):
	mkdir -p $(BUILD_DIR)

clean:
	rm -rf $(BUILD_DIR)
