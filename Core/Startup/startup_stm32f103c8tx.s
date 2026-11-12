/**
 ******************************************************************************
 * @file    startup_stm32f103c8tx.s
 * @brief   STM32F103C8T6 启动文件（GNU as 语法）
 *
 * 启动文件干三件事：
 *   1. 在 Flash 起始处放“中断向量表”，第一个字是栈顶地址，第二个字是复位入口
 *   2. 复位后先把 .data 段从 Flash 搬到 RAM、把 .bss 段清零
 *   3. 调用 SystemInit() 配时钟，再跳进 main()
 ******************************************************************************
 */

  .syntax unified
  .cpu cortex-m3
  .thumb

/* ---------------- 中断向量表 ---------------- */
  .section  .isr_vector, "a", %progbits
  .global   g_pfnVectors
  .type     g_pfnVectors, %object

g_pfnVectors:
  .word  _estack                 /* 0: 栈顶地址（RAM 末尾）        */
  .word  Reset_Handler           /* 1: 复位                        */
  .word  NMI_Handler             /* 2: 不可屏蔽中断                */
  .word  HardFault_Handler       /* 3: 硬件错误                    */
  .word  MemManage_Handler       /* 4: 存储器管理错误              */
  .word  BusFault_Handler        /* 5: 总线错误                    */
  .word  UsageFault_Handler      /* 6: 用法错误                    */
  .word  0                       /* 7~10: 保留                     */
  .word  0
  .word  0
  .word  0
  .word  SVC_Handler             /* 11: 系统服务调用               */
  .word  DebugMon_Handler        /* 12: 调试监控                   */
  .word  0                       /* 13: 保留                       */
  .word  PendSV_Handler          /* 14: 可挂起服务                 */
  .word  SysTick_Handler         /* 15: 系统滴答定时器             */

/* 16~58: STM32F103 中容量产品的 43 个外设中断 */
  .word  WWDG_IRQHandler
  .word  PVD_IRQHandler
  .word  TAMPER_IRQHandler
  .word  RTC_IRQHandler
  .word  FLASH_IRQHandler
  .word  RCC_IRQHandler
  .word  EXTI0_IRQHandler
  .word  EXTI1_IRQHandler
  .word  EXTI2_IRQHandler
  .word  EXTI3_IRQHandler
  .word  EXTI4_IRQHandler
  .word  DMA1_Channel1_IRQHandler
  .word  DMA1_Channel2_IRQHandler
  .word  DMA1_Channel3_IRQHandler
  .word  DMA1_Channel4_IRQHandler
  .word  DMA1_Channel5_IRQHandler
  .word  DMA1_Channel6_IRQHandler
  .word  DMA1_Channel7_IRQHandler
  .word  ADC1_2_IRQHandler
  .word  USB_HP_CAN1_TX_IRQHandler
  .word  USB_LP_CAN1_RX0_IRQHandler
  .word  CAN1_RX1_IRQHandler
  .word  CAN1_SCE_IRQHandler
  .word  EXTI9_5_IRQHandler
  .word  TIM1_BRK_IRQHandler
  .word  TIM1_UP_IRQHandler
  .word  TIM1_TRG_COM_IRQHandler
  .word  TIM1_CC_IRQHandler
  .word  TIM2_IRQHandler
  .word  TIM3_IRQHandler
  .word  TIM4_IRQHandler
  .word  I2C1_EV_IRQHandler
  .word  I2C1_ER_IRQHandler
  .word  I2C2_EV_IRQHandler
  .word  I2C2_ER_IRQHandler
  .word  SPI1_IRQHandler
  .word  SPI2_IRQHandler
  .word  USART1_IRQHandler
  .word  USART2_IRQHandler
  .word  USART3_IRQHandler
  .word  EXTI15_10_IRQHandler
  .word  RTCAlarm_IRQHandler
  .word  USBWakeUp_IRQHandler

  .size  g_pfnVectors, . - g_pfnVectors

/* ---------------- 复位处理 ---------------- */
  .section  .text.Reset_Handler, "ax", %progbits
  .weak     Reset_Handler
  .type     Reset_Handler, %function

Reset_Handler:
  /* 1. 把 .data 段的初值从 Flash（_sidata）搬到 RAM（_sdata ~ _edata） */
  ldr   r0, =_sdata
  ldr   r1, =_edata
  ldr   r2, =_sidata
  b     copy_check

copy_loop:
  ldr   r3, [r2], #4
  str   r3, [r0], #4

copy_check:
  cmp   r0, r1
  bcc   copy_loop

  /* 2. 把 .bss 段（未初始化全局变量）清零 */
  ldr   r0, =_sbss
  ldr   r1, =_ebss
  movs  r3, #0
  b     zero_check

zero_loop:
  str   r3, [r0], #4

zero_check:
  cmp   r0, r1
  bcc   zero_loop

  /* 3. 配置时钟，然后进入 main() */
  bl    SystemInit
  bl    main

  /* 4. main() 正常不会返回；万一返回就停在这里 */
hang:
  b     hang

  .size  Reset_Handler, . - Reset_Handler

/* ---------------- 默认中断处理函数 ---------------- */
  .section  .text.Default_Handler, "ax", %progbits
  .type     Default_Handler, %function
Default_Handler:
  b  Default_Handler
  .size  Default_Handler, . - Default_Handler

/* 所有中断都先弱链接到 Default_Handler，用户自己实现同名函数即可覆盖 */
  .macro  IRQ_HANDLER  name
  .weak   \name
  .thumb_set \name, Default_Handler
  .endm

  IRQ_HANDLER  NMI_Handler
  IRQ_HANDLER  HardFault_Handler
  IRQ_HANDLER  MemManage_Handler
  IRQ_HANDLER  BusFault_Handler
  IRQ_HANDLER  UsageFault_Handler
  IRQ_HANDLER  SVC_Handler
  IRQ_HANDLER  DebugMon_Handler
  IRQ_HANDLER  PendSV_Handler
  IRQ_HANDLER  SysTick_Handler

  IRQ_HANDLER  WWDG_IRQHandler
  IRQ_HANDLER  PVD_IRQHandler
  IRQ_HANDLER  TAMPER_IRQHandler
  IRQ_HANDLER  RTC_IRQHandler
  IRQ_HANDLER  FLASH_IRQHandler
  IRQ_HANDLER  RCC_IRQHandler
  IRQ_HANDLER  EXTI0_IRQHandler
  IRQ_HANDLER  EXTI1_IRQHandler
  IRQ_HANDLER  EXTI2_IRQHandler
  IRQ_HANDLER  EXTI3_IRQHandler
  IRQ_HANDLER  EXTI4_IRQHandler
  IRQ_HANDLER  DMA1_Channel1_IRQHandler
  IRQ_HANDLER  DMA1_Channel2_IRQHandler
  IRQ_HANDLER  DMA1_Channel3_IRQHandler
  IRQ_HANDLER  DMA1_Channel4_IRQHandler
  IRQ_HANDLER  DMA1_Channel5_IRQHandler
  IRQ_HANDLER  DMA1_Channel6_IRQHandler
  IRQ_HANDLER  DMA1_Channel7_IRQHandler
  IRQ_HANDLER  ADC1_2_IRQHandler
  IRQ_HANDLER  USB_HP_CAN1_TX_IRQHandler
  IRQ_HANDLER  USB_LP_CAN1_RX0_IRQHandler
  IRQ_HANDLER  CAN1_RX1_IRQHandler
  IRQ_HANDLER  CAN1_SCE_IRQHandler
  IRQ_HANDLER  EXTI9_5_IRQHandler
  IRQ_HANDLER  TIM1_BRK_IRQHandler
  IRQ_HANDLER  TIM1_UP_IRQHandler
  IRQ_HANDLER  TIM1_TRG_COM_IRQHandler
  IRQ_HANDLER  TIM1_CC_IRQHandler
  IRQ_HANDLER  TIM2_IRQHandler
  IRQ_HANDLER  TIM3_IRQHandler
  IRQ_HANDLER  TIM4_IRQHandler
  IRQ_HANDLER  I2C1_EV_IRQHandler
  IRQ_HANDLER  I2C1_ER_IRQHandler
  IRQ_HANDLER  I2C2_EV_IRQHandler
  IRQ_HANDLER  I2C2_ER_IRQHandler
  IRQ_HANDLER  SPI1_IRQHandler
  IRQ_HANDLER  SPI2_IRQHandler
  IRQ_HANDLER  USART1_IRQHandler
  IRQ_HANDLER  USART2_IRQHandler
  IRQ_HANDLER  USART3_IRQHandler
  IRQ_HANDLER  EXTI15_10_IRQHandler
  IRQ_HANDLER  RTCAlarm_IRQHandler
  IRQ_HANDLER  USBWakeUp_IRQHandler
