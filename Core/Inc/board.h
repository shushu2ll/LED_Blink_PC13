/**
 * @file    board.h
 * @brief   板级定义：LED 接在哪个引脚、高低电平哪个是亮
 *
 * 蓝飞（STM32F103C8T6 最小系统板）：
 *   PC13 --- LED --- R(470Ω) --- 3.3V
 *   即 LED 的阳极接 3.3V，阴极经限流电阻接 PC13，所以：
 *        PC13 输出低电平 → LED 亮
 *        PC13 输出高电平 → LED 灭
 *
 * 如果你手上是别的板子，只改下面 3 行即可。
 */

#ifndef BOARD_H
#define BOARD_H

#include "stm32f103_regs.h"

#define LED_PORT        GPIOC
#define LED_PIN         13U
#define LED_ACTIVE_LOW  1       /* 1 = 低电平点亮；0 = 高电平点亮 */

#if LED_ACTIVE_LOW
  #define LED_ON()      (LED_PORT->BSRR = (1UL << (LED_PIN + 16U)))  /* 置位 BSRR 高 16 位 = 输出低 */
  #define LED_OFF()     (LED_PORT->BSRR = (1UL << LED_PIN))          /* 置位 BSRR 低 16 位 = 输出高 */
#else
  #define LED_ON()      (LED_PORT->BSRR = (1UL << LED_PIN))
  #define LED_OFF()     (LED_PORT->BSRR = (1UL << (LED_PIN + 16U)))
#endif

/* 打开 LED 所在端口（GPIOC）的时钟 */
#define LED_CLK_ENABLE()  (RCC->APB2ENR |= RCC_APB2ENR_IOPCEN)

#endif /* BOARD_H */
