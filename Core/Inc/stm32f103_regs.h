/**
 * @file    stm32f103_regs.h
 * @brief   STM32F103C8T6 最简寄存器定义（只包含点亮 LED 用得到的部分）
 *
 * 说明：
 *   - 全部按《STM32F10x 参考手册》RM0008 的寄存器偏移手工定义，
 *     不依赖 ST 官方的 CMSIS / HAL 固件包，因此可以完全离线编译。
 *   - 结构体成员的顺序 == 寄存器偏移顺序，这是这种写法的关键。
 */

#ifndef STM32F103_REGS_H
#define STM32F103_REGS_H

#include <stdint.h>

#define __IO   volatile            /* 读/写寄存器 */
#define __I    volatile const      /* 只读寄存器   */
#define __O    volatile            /* 只写寄存器   */

/* ---------------- 外设基地址 ---------------- */
#define PERIPH_BASE       0x40000000UL
#define APB2PERIPH_BASE   (PERIPH_BASE + 0x00010000UL)
#define AHBPERIPH_BASE    (PERIPH_BASE + 0x00020000UL)

#define RCC_BASE          (AHBPERIPH_BASE + 0x00001000UL)   /* 0x40021000 */
#define FLASH_R_BASE      (AHBPERIPH_BASE + 0x00002000UL)   /* 0x40022000 */

#define GPIOA_BASE        (APB2PERIPH_BASE + 0x00000800UL)  /* 0x40010800 */
#define GPIOB_BASE        (APB2PERIPH_BASE + 0x00000C00UL)  /* 0x40010C00 */
#define GPIOC_BASE        (APB2PERIPH_BASE + 0x00001000UL)  /* 0x40011000 */
#define GPIOD_BASE        (APB2PERIPH_BASE + 0x00001400UL)  /* 0x40011400 */

/* ---------------- 寄存器结构体 ---------------- */

/* GPIO：CRL 0x00, CRH 0x04, IDR 0x08, ODR 0x0C, BSRR 0x10, BRR 0x14, LCKR 0x18 */
typedef struct {
    __IO uint32_t CRL;
    __IO uint32_t CRH;
    __IO uint32_t IDR;
    __IO uint32_t ODR;
    __IO uint32_t BSRR;
    __IO uint32_t BRR;
    __IO uint32_t LCKR;
} GPIO_TypeDef;

/* RCC：CR 0x00, CFGR 0x04, CIR 0x08, APB2RSTR 0x0C, APB1RSTR 0x10,
        AHBENR 0x14, APB2ENR 0x18, APB1ENR 0x1C, BDCR 0x20, CSR 0x24 */
typedef struct {
    __IO uint32_t CR;
    __IO uint32_t CFGR;
    __IO uint32_t CIR;
    __IO uint32_t APB2RSTR;
    __IO uint32_t APB1RSTR;
    __IO uint32_t AHBENR;
    __IO uint32_t APB2ENR;
    __IO uint32_t APB1ENR;
    __IO uint32_t BDCR;
    __IO uint32_t CSR;
} RCC_TypeDef;

/* FLASH 接口：ACR 0x00, KEYR 0x04, OPTKEYR 0x08, SR 0x0C, CR 0x10, AR 0x14 ... */
typedef struct {
    __IO uint32_t ACR;
    __IO uint32_t KEYR;
    __IO uint32_t OPTKEYR;
    __IO uint32_t SR;
    __IO uint32_t CR;
    __IO uint32_t AR;
} FLASH_TypeDef;

/* Cortex-M3 内核外设 */
typedef struct {
    __IO uint32_t CTRL;      /* 0xE000E010 */
    __IO uint32_t LOAD;      /* 0xE000E014 */
    __IO uint32_t VAL;       /* 0xE000E018 */
    __I  uint32_t CALIB;     /* 0xE000E01C */
} SysTick_TypeDef;

typedef struct {
    __I  uint32_t CPUID;     /* 0xE000ED00 */
    __IO uint32_t ICSR;      /* 0xE000ED04 */
    __IO uint32_t VTOR;      /* 0xE000ED08 */
    __IO uint32_t AIRCR;     /* 0xE000ED0C */
    __IO uint32_t SCR;       /* 0xE000ED10 */
    __IO uint32_t CCR;       /* 0xE000ED14 */
} SCB_TypeDef;

/* ---------------- 外设实例指针 ---------------- */
#define GPIOA   ((GPIO_TypeDef *) GPIOA_BASE)
#define GPIOB   ((GPIO_TypeDef *) GPIOB_BASE)
#define GPIOC   ((GPIO_TypeDef *) GPIOC_BASE)
#define GPIOD   ((GPIO_TypeDef *) GPIOD_BASE)

#define RCC     ((RCC_TypeDef *)  RCC_BASE)
#define FLASH   ((FLASH_TypeDef *) FLASH_R_BASE)

#define SysTick ((SysTick_TypeDef *) 0xE000E010UL)
#define SCB     ((SCB_TypeDef *)     0xE000ED00UL)

/* ---------------- RCC_CR 位定义 ---------------- */
#define RCC_CR_HSION        (1UL << 0)
#define RCC_CR_HSIRDY       (1UL << 1)
#define RCC_CR_HSEON        (1UL << 16)
#define RCC_CR_HSERDY       (1UL << 17)
#define RCC_CR_PLLON        (1UL << 24)
#define RCC_CR_PLLRDY       (1UL << 25)

/* ---------------- RCC_CFGR 位定义 ---------------- */
#define RCC_CFGR_SW                     (3UL << 0)
#define RCC_CFGR_SW_HSI                 (0UL << 0)
#define RCC_CFGR_SW_HSE                 (1UL << 0)
#define RCC_CFGR_SW_PLL                 (2UL << 0)

#define RCC_CFGR_SWS                    (3UL << 2)
#define RCC_CFGR_SWS_HSI                (0UL << 2)
#define RCC_CFGR_SWS_HSE                (1UL << 2)
#define RCC_CFGR_SWS_PLL                (2UL << 2)

#define RCC_CFGR_HPRE                   (0xFUL << 4)        /* AHB  分频 */
#define RCC_CFGR_HPRE_DIV1              (0x0UL << 4)

#define RCC_CFGR_PPRE1                  (0x7UL << 8)        /* APB1 分频，最大 36MHz */
#define RCC_CFGR_PPRE1_DIV2             (0x4UL << 8)

#define RCC_CFGR_PPRE2                  (0x7UL << 11)       /* APB2 分频，最大 72MHz */
#define RCC_CFGR_PPRE2_DIV1             (0x0UL << 11)

#define RCC_CFGR_PLLSRC                 (1UL << 16)         /* 1 = HSE 作为 PLL 输入 */
#define RCC_CFGR_PLLXTPRE               (1UL << 17)         /* 0 = HSE 不分频 */
#define RCC_CFGR_PLLMULL                (0xFUL << 18)
#define RCC_CFGR_PLLMULL9               (0x7UL << 18)       /* ×9 → 8MHz × 9 = 72MHz */

/* ---------------- RCC_APB2ENR 位定义 ---------------- */
#define RCC_APB2ENR_AFIOEN              (1UL << 0)
#define RCC_APB2ENR_IOPAEN              (1UL << 2)
#define RCC_APB2ENR_IOPBEN              (1UL << 3)
#define RCC_APB2ENR_IOPCEN              (1UL << 4)
#define RCC_APB2ENR_IOPDEN              (1UL << 5)

/* ---------------- FLASH_ACR 位定义 ---------------- */
#define FLASH_ACR_LATENCY               (0x7UL << 0)        /* 等待周期：48MHz 以上要 2 */
#define FLASH_ACR_PRFTBE                (1UL << 4)          /* 预取缓冲使能 */

/* ---------------- SysTick_CTRL 位定义 ---------------- */
#define SysTick_CTRL_ENABLE             (1UL << 0)
#define SysTick_CTRL_TICKINT            (1UL << 1)
#define SysTick_CTRL_CLKSOURCE          (1UL << 2)          /* 1 = HCLK */
#define SysTick_CTRL_COUNTFLAG          (1UL << 16)

#endif /* STM32F103_REGS_H */
