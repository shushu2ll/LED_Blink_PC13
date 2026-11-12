/**
 ******************************************************************************
 * @file    main.c
 * @brief   作业：点亮 STM32F103C8T6 最小系统板上的 LED（PC13），并让它闪烁
 *
 * 现象：上电后 PC13 上的 LED 以 1Hz（亮 500ms、灭 500ms）闪烁。
 *
 * 代码分四步，和实验报告里的“实验步骤”一一对应：
 *   1. SystemInit()  —— 配置时钟：HSE 8MHz 经 PLL ×9 倍频到 72MHz
 *   2. GPIO_Init()   —— 打开 GPIOC 时钟，把 PC13 配置成推挽输出
 *   3. delay_init()  —— 用 SysTick 做 1ms 基准的延时
 *   4. main()        —— 循环：亮 500ms、灭 500ms
 *
 * 注意：本工程不依赖 HAL 库和 CubeMX 生成的代码，直接操作寄存器，
 *       用 STM32CubeIDE 自带的 arm-none-eabi-gcc 就能编译。
 ******************************************************************************
 */

#include "stm32f103_regs.h"
#include "board.h"

/* 系统当前主频，启动文件和延时函数都会用到 */
uint32_t SystemCoreClock = 8000000UL;

/* 私有函数声明 */
void SystemInit(void);          /* 启动文件会调用它，不能是 static */
static void GPIO_Init(void);
static void delay_init(void);
static void delay_ms(uint32_t ms);

/**
 * @brief  系统时钟初始化，由启动文件在进入 main() 之前调用
 * @note   HSE 起振失败时自动退回内部 HSI（8MHz），保证 LED 仍能闪，
 *         这样即使板子上的 8MHz 晶振没焊/坏了也不会“全黑”。
 */
void SystemInit(void)
{
    uint32_t i;

    /* 1. 打开外部高速晶振 HSE（8MHz），最多等约 13 万个循环 */
    RCC->CR |= RCC_CR_HSEON;
    for (i = 0U; i < 0x20000U; i++) {
        if (RCC->CR & RCC_CR_HSERDY) {
            break;
        }
    }

    if ((RCC->CR & RCC_CR_HSERDY) == 0U) {
        /* HSE 没起来：保持 HSI 8MHz 直接运行，不配 PLL */
        SystemCoreClock = 8000000UL;
        return;
    }

    /* 2. 72MHz 需要 2 个 Flash 等待周期，并打开预取缓冲 */
    FLASH->ACR = (FLASH->ACR & ~FLASH_ACR_LATENCY) | FLASH_ACR_PRFTBE | 0x2UL;

    /* 3. 总线分频：AHB = 72MHz，APB1 = 36MHz，APB2 = 72MHz */
    RCC->CFGR &= ~(RCC_CFGR_HPRE | RCC_CFGR_PPRE1 | RCC_CFGR_PPRE2);
    RCC->CFGR |= (RCC_CFGR_HPRE_DIV1 | RCC_CFGR_PPRE1_DIV2 | RCC_CFGR_PPRE2_DIV1);

    /* 4. PLL 输入选 HSE（不分频），倍频系数 ×9 → 8MHz × 9 = 72MHz */
    RCC->CFGR &= ~(RCC_CFGR_PLLSRC | RCC_CFGR_PLLXTPRE | RCC_CFGR_PLLMULL);
    RCC->CFGR |= (RCC_CFGR_PLLSRC | RCC_CFGR_PLLMULL9);

    /* 5. 使能 PLL 并等待锁定 */
    RCC->CR |= RCC_CR_PLLON;
    while ((RCC->CR & RCC_CR_PLLRDY) == 0U) {
        /* 等待 PLL 稳定 */
    }

    /* 6. 把系统时钟切换为 PLL 输出，并等待切换完成 */
    RCC->CFGR = (RCC->CFGR & ~RCC_CFGR_SW) | RCC_CFGR_SW_PLL;
    while ((RCC->CFGR & RCC_CFGR_SWS) != RCC_CFGR_SWS_PLL) {
        /* 等待 SWS 反映 PLL 已成为系统时钟 */
    }

    SystemCoreClock = 72000000UL;
}

/**
 * @brief  把 PC13 配置成 2MHz 推挽输出
 *
 * GPIO 的每个引脚由 CRL（Pin0~7）/ CRH（Pin8~15）中的 4 位控制：
 *   bit[1:0] MODE：00 输入 / 01 输出 10MHz / 10 输出 2MHz / 11 输出 50MHz
 *   bit[3:2] CNF ：通用推挽输出时为 00
 * PC13 在 CRH 里，起始位 = (13 - 8) × 4 = 20，所以写 0x2 << 20。
 */
static void GPIO_Init(void)
{
    /* 外设时钟默认关闭，用哪个端口就要先开它的时钟（APB2 上的 GPIOC） */
    LED_CLK_ENABLE();

    /* 先清空 PC13 对应的 4 位，再写入“输出 2MHz + 推挽” */
    LED_PORT->CRH &= ~(0xFUL << ((LED_PIN - 8U) * 4U));
    LED_PORT->CRH |= (0x2UL << ((LED_PIN - 8U) * 4U));

    /* 上电默认先灭灯，避免一上电就常亮看不出程序在跑 */
    LED_OFF();
}

/**
 * @brief  SysTick 配置成 1ms 中断一次（这里只用它的计数标志，不开中断）
 */
static void delay_init(void)
{
    SysTick->LOAD = (SystemCoreClock / 1000UL) - 1UL;  /* 计数到 0 正好 1ms */
    SysTick->VAL  = 0UL;                              /* 清当前计数值 */
    SysTick->CTRL = SysTick_CTRL_CLKSOURCE | SysTick_CTRL_ENABLE; /* 时钟源 HCLK，启动 */
}

/**
 * @brief  毫秒级延时（阻塞式）
 * @param  ms 要延时的毫秒数
 */
static void delay_ms(uint32_t ms)
{
    while (ms-- > 0U) {
        /* COUNTFLAG 在计数器减到 0 时置 1，读 CTRL 会自动清零 */
        while ((SysTick->CTRL & SysTick_CTRL_COUNTFLAG) == 0U) {
            /* 忙等 1ms */
        }
    }
}

/**
 * @brief  主函数
 */
int main(void)
{
    GPIO_Init();
    delay_init();

    while (1) {
        LED_ON();
        delay_ms(2000U);
        LED_OFF();
        delay_ms(500U);
    }
}
