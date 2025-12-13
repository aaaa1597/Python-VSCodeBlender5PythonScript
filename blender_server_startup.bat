@echo off

 -p 1920 1500 1500 1280
set BLENDER="C:\Program Files\Blender Foundation\Blender 5.0\blender.exe"
set BLEND="blender_server_startup.blend"

start "" %BLENDER% %BLEND% -p 1920 1500 1800 1280
exit
