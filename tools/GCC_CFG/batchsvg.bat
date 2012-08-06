@echo off
set PATH="C:\Program Files\Graphviz2.26.3\bin";%PATH%
for /F %%i in ('dir *.dot /b') do (
	echo %%i
	dot.exe -Tsvg %%i -o %%i.svg
)
pause