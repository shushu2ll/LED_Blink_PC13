@echo off
setlocal
rem ===========================================================================
rem  Build LED_Blink_PC13 with the toolchain bundled in STM32CubeIDE 2.2.0
rem  Just double-click this file. Output goes to the build\ folder.
rem ===========================================================================
set "GCC=F:\STM32CubeIDE_2.2.0\STM32CubeIDE\plugins\com.st.stm32cube.ide.mcu.externaltools.gnu-tools-for-stm32.14.3.rel1.win32_1.0.100.202602081740\tools\bin"
set "MAKE=F:\STM32CubeIDE_2.2.0\STM32CubeIDE\plugins\com.st.stm32cube.ide.mcu.externaltools.make.win32_2.2.200.202604021615\tools\bin"
set "PATH=%GCC%;%MAKE%;%PATH%"
cd /d "%~dp0"

echo ============================================
echo  Building LED_Blink_PC13 ...
echo ============================================
make
if errorlevel 1 (
    echo.
    echo [FAILED] Build error, see the messages above.
    pause
    exit /b 1
)
echo.
echo [OK] Generated:
echo     build\LED_Blink_PC13.hex   -- flash this file
echo     build\LED_Blink_PC13.bin
echo     build\LED_Blink_PC13.elf   -- for debugging
echo.
pause
