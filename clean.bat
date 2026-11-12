@echo off
setlocal
rem ===========================================================================
rem  Clean build output (delete the whole build\ folder).
rem  Use it when a build behaves strangely, then run build.bat again.
rem ===========================================================================
set "GCC=F:\STM32CubeIDE_2.2.0\STM32CubeIDE\plugins\com.st.stm32cube.ide.mcu.externaltools.gnu-tools-for-stm32.14.3.rel1.win32_1.0.100.202602081740\tools\bin"
set "MAKE=F:\STM32CubeIDE_2.2.0\STM32CubeIDE\plugins\com.st.stm32cube.ide.mcu.externaltools.make.win32_2.2.200.202604021615\tools\bin"
set "PATH=%GCC%;%MAKE%;%PATH%"
cd /d "%~dp0"

make clean
echo.
echo [DONE] build\ removed. Run build.bat for a full rebuild.
echo.
pause
