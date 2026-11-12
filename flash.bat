@echo off
setlocal
rem ===========================================================================
rem  Flash build\LED_Blink_PC13.hex through ST-Link, using the STM32CubeProgrammer
rem  CLI bundled in STM32CubeIDE 2.2.0.
rem  Before running: ST-Link plugged in, SWD wired, board powered, BOOT0 = 0.
rem ===========================================================================
set "CP=F:\STM32CubeIDE_2.2.0\STM32CubeIDE\plugins\com.st.stm32cube.ide.mcu.externaltools.cubeprogrammer.win32_2.2.500.202603051304\tools\bin"
set "PATH=%CP%;%PATH%"
cd /d "%~dp0"

if not exist "build\LED_Blink_PC13.hex" (
    echo [ERROR] No hex file yet. Run build.bat first.
    pause
    exit /b 1
)

echo ============================================
echo  Flashing build\LED_Blink_PC13.hex ...
echo ============================================
STM32_Programmer_CLI.exe -c port=SWD -w "build\LED_Blink_PC13.hex" -v -rst
if errorlevel 1 (
    echo.
    echo [FAILED] Cannot talk to the chip. Check:
    echo    1. ST-Link plugged in and driver installed (Device Manager: STLink)
    echo    2. SWDIO=PA13, SWCLK=PA14, GND=GND, 3.3V=3.3V
    echo    3. BOOT0 jumper = 0
    pause
    exit /b 1
)
echo.
echo [OK] Programmed and reset. The LED on PC13 should blink at 1 Hz.
pause
