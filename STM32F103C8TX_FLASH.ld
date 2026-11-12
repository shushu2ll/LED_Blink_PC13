/*
 * STM32F103C8T6 链接脚本
 *   Flash : 64 KB   @ 0x08000000
 *   SRAM  : 20 KB   @ 0x20000000
 *
 * 链接脚本决定每个段放到哪里：
 *   .isr_vector 放在 Flash 最前面（0x08000000，芯片复位后从这里取栈顶和复位入口）
 *   .text/.rodata 也放 Flash
 *   .data 的“运行地址”在 RAM、“存放地址”在 Flash，启动时由启动文件搬过去
 *   .bss  只占 RAM，启动时清零
 */

ENTRY(Reset_Handler)

/* 栈顶地址 = RAM 起始 + RAM 大小（栈向下生长） */
_estack = ORIGIN(RAM) + LENGTH(RAM);

/* 最小堆/栈检查用的保留空间 */
_Min_Heap_Size  = 0x200;   /* 512 B  */
_Min_Stack_Size = 0x400;   /* 1 KB   */

MEMORY
{
  FLASH (rx)  : ORIGIN = 0x08000000, LENGTH = 64K
  RAM   (xrw) : ORIGIN = 0x20000000, LENGTH = 20K
}

SECTIONS
{
  /* 中断向量表 */
  .isr_vector :
  {
    . = ALIGN(4);
    KEEP(*(.isr_vector))
    . = ALIGN(4);
  } >FLASH

  /* 程序代码 */
  .text :
  {
    . = ALIGN(4);
    *(.text)
    *(.text*)
    *(.glue_7)
    *(.glue_7t)
    *(.eh_frame)
    KEEP(*(.init))
    KEEP(*(.fini))
    . = ALIGN(4);
    _etext = .;
  } >FLASH

  /* 只读数据（常量、字符串） */
  .rodata :
  {
    . = ALIGN(4);
    *(.rodata)
    *(.rodata*)
    . = ALIGN(4);
  } >FLASH

  /* ARM 异常展开表（本工程用不到，放这儿防止出现 orphan section） */
  .ARM.extab :
  {
    . = ALIGN(4);
    *(.ARM.extab* .gnu.linkonce.armextab.*)
    . = ALIGN(4);
  } >FLASH

  .ARM.exidx :
  {
    . = ALIGN(4);
    __exidx_start = .;
    *(.ARM.exidx* .gnu.linkonce.armexidx.*)
    __exidx_end = .;
    . = ALIGN(4);
  } >FLASH

  /* 已初始化全局变量：运行在 RAM，初值存在 Flash（_sidata 指向初值） */
  _sidata = LOADADDR(.data);

  .data :
  {
    . = ALIGN(4);
    _sdata = .;
    *(.data)
    *(.data*)
    . = ALIGN(4);
    _edata = .;
  } >RAM AT> FLASH

  /* 未初始化/零初始化全局变量 */
  .bss :
  {
    . = ALIGN(4);
    _sbss = .;
    __bss_start__ = _sbss;
    *(.bss)
    *(.bss*)
    *(COMMON)
    . = ALIGN(4);
    _ebss = .;
    __bss_end__ = _ebss;
  } >RAM

  /* 检查堆栈是否还放得下：放不下会在链接期直接报错 */
  ._user_heap_stack :
  {
    . = ALIGN(8);
    PROVIDE ( end = . );
    PROVIDE ( _end = . );
    . = . + _Min_Heap_Size;
    . = . + _Min_Stack_Size;
    . = ALIGN(8);
  } >RAM

  /DISCARD/ :
  {
    libc.a ( * )
    libm.a ( * )
    libgcc.a ( * )
  }

  .ARM.attributes 0 : { *(.ARM.attributes) }
}
