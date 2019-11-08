
@echo off
@rem Carrega de l'entorn de treball
set MYDIR=%cd%
for %%f in (%MYDIR%) do set directory=%%~nxf

rem Root OSGEO4W home dir to the same directory this script exists in
set QGIS_PATH="C:\OSGeo4W64"
CALL %QGIS_PATH%\bin\o4w_env.bat
CALL %QGIS_PATH%\bin\qt5_env.bat
CALL %QGIS_PATH%\bin\py3_env.bat

set directory_source="\\192.168.107.9\c$\xampp\htdocs\downloads\QGIS3\%directory%.zip"
set directory_old="\\192.168.107.9\c$\xampp\htdocs\downloads\OLD\%directory%"

%WINDIR%\System32\WindowsPowerShell\v1.0\powershell.exe %MYDIR%\Extract_metadata.ps1 %directory_source% %directory_old% %directory%
for /f "delims=" %%a in ('%WINDIR%\System32\WindowsPowerShell\v1.0\powershell.exe %MYDIR%\ScriptPS.ps1 %directory_old%') do Set "$Value=%%a"


@echo on
@rem Compilacio plugin
cmd /c "pyrcc5 -o resources.py resources.qrc"
cmd /c "pb_tool deploy"
@echo off
cd ..
cd ZZ_DEPLOY
erase %directory%.ZIP
erase %directory_old%\metadata.txt

@rem Creacio del ZIP file
%WINDIR%\System32\WindowsPowerShell\v1.0\powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "Compress-Archive -path %directory% -DestinationPath .\%directory%"

@rem Copia del ZIP resultant al servidor
pushd "\\192.168.107.9\c$\xampp\htdocs\downloads\QGIS3"
erase ..\OLD\%directory%\%directory%_%$Value%.ZIP
@echo Movent plugin '%directory%' V.%$Value% ...
copy .\%directory%.ZIP ..\OLD\%directory%\%directory%_%$Value%.ZIP
@echo. 
erase %directory%.ZIP
@echo Actualitzant plugin '%directory%' en servidor ...
copy D:\Eclipse\QGISV3\ZZ_DEPLOY\%directory%.ZIP .\
popd
@echo. 
@echo. 
@echo [104;93m Plugin '%directory%' pujat al servidor.[0m
@echo. 
@echo [104;93m Plugin '%directory%' ver. %$Value% mogut a Repositori OLD del servidor.[0m
@echo. 
@echo. 
cmd /c "pause"
