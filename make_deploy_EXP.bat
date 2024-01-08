
@echo off
@rem VERSIÓ MAKE_DEPLOY 0.6
@rem Carrega de l'entorn de treball
set MYDIR=%cd%
for %%f in (%MYDIR%) do set directory=%%~nxf

rem Root OSGEO4W home dir to the same directory this script exists in
set QGIS_PATH=C:\OSGeo4W
CALL "%QGIS_PATH%\bin\o4w_env.bat"
rem CALL %QGIS_PATH%\bin\qt5_env.bat
rem CALL %QGIS_PATH%\bin\py3_env.bat

@echo on
@rem Compilacio plugin
cmd /c "pyrcc5 -o resources.py resources.qrc"

cmd /c "pb_tool deploy"

@echo off
set directory_source="\\192.168.107.9\c$\xampp\htdocs\downloads\QGIS3\%directory%.zip"
set directory_old="\\192.168.107.9\c$\xampp\htdocs\downloads\OLD\%directory%"
set directory_plugins_xml=\\192.168.107.9\c$\xampp\htdocs

%WINDIR%\System32\WindowsPowerShell\v1.0\powershell.exe "%MYDIR%\Extract_metadata.ps1" %directory_source% %directory_old% %directory%
for /f "delims=" %%a in ('%WINDIR%\System32\WindowsPowerShell\v1.0\powershell.exe %MYDIR%\ScriptPS.ps1 %directory_old%') do Set "$Version_old=%%a"

for /f "delims=" %%a in ('%WINDIR%\System32\WindowsPowerShell\v1.0\powershell.exe %MYDIR%\ScriptPS.ps1 %MYDIR%') do Set "$Version_new=%%a"
@echo Actualitzant %directory% [101;93mV.%$Version_old%[0m a [104;93mV.%$Version_new%.[0m

rem cmd /k
@echo off
cd ..
cmd /c "python compress.py ./%directory% .\ZZ_DEPLOY/%directory%.zip"
cd ZZ_DEPLOY
rem erase %directory%.ZIP
erase %directory_old%\metadata.txt
@rem Creacio del ZIP file
rem %WINDIR%\System32\WindowsPowerShell\v1.0\powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "Compress-Archive -path %directory% -DestinationPath .\%directory%"

@rem Modificació de l'arxiu plugins.xml al servidor
%WINDIR%\System32\WindowsPowerShell\v1.0\powershell.exe %MYDIR%\Update_xml_EXP.ps1 %directory% %directory_plugins_xml% %$Version_old% %$Version_new%

@rem Copia del ZIP resultant al servidor
pushd "\\192.168.107.9\c$\xampp\htdocs\downloads\QGIS3"
erase ..\OLD\%directory%\%directory%_%$Version_old%.ZIP
@echo Movent plugin '%directory%' V.%$Version_old% ...
copy .\%directory%.ZIP ..\OLD\%directory%\%directory%_%$Version_old%.ZIP
@echo. 
erase %directory%.ZIP
@echo Actualitzant plugin '%directory%' en servidor ...
copy D:\CCU\QGIS3\ZZ_DEPLOY\%directory%.ZIP .\
popd
@echo. 
@echo. 
@echo [104;93m Plugin '%directory%' pujat al servidor.[0m
@echo. 
@echo [104;93m Plugin '%directory%' ver. %$Version_old% mogut a Repositori OLD del servidor.[0m
@echo. 
@echo. 
cmd /c "pause"
rem cmd /k