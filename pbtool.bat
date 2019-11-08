@echo off
@rem Carrega de l'entorn de treball
set MYDIR=%cd%
for %%f in (%MYDIR%) do set directory=%%~nxf

rem Root OSGEO4W home dir to the same directory this script exists in
set QGIS_PATH="C:\OSGeo4W64"
CALL %QGIS_PATH%\bin\o4w_env.bat
CALL %QGIS_PATH%\bin\qt5_env.bat
CALL %QGIS_PATH%\bin\py3_env.bat

@echo on
@rem Compilacio plugin
cmd /c "pyrcc5 -o resources.py resources.qrc"
cmd /c "pb_tool clean"
cmd /c "pb_tool compile"
cmd /c "rmdir /S /Q D:\Eclipse\QGISV3\ZZ_DEPLOY\%directory%"
cmd /c "mkdir D:\Eclipse\QGISV3\ZZ_DEPLOY\%directory%"
cmd /c "xcopy %MYDIR%\__init__.py D:\Eclipse\QGISV3\ZZ_DEPLOY\%directory% /E /Q /I"
cmd /c "xcopy %MYDIR%\icon.png D:\Eclipse\QGISV3\ZZ_DEPLOY\%directory% /E /Q /I"
cmd /c "xcopy %MYDIR%\metadata.txt D:\Eclipse\QGISV3\ZZ_DEPLOY\%directory% /E /Q /I"
cmd /c "xcopy %MYDIR%\resources.py D:\Eclipse\QGISV3\ZZ_DEPLOY\%directory% /E /Q /I"
cmd /c "xcopy %MYDIR%\%directory%.py D:\Eclipse\QGISV3\ZZ_DEPLOY\%directory% /E /Q /I"
cmd /c "xcopy %MYDIR%\%directory%_dialog.py D:\Eclipse\QGISV3\ZZ_DEPLOY\%directory% /E /Q /I"
cmd /c "xcopy %MYDIR%\%directory%_dialog_base.ui D:\Eclipse\QGISV3\ZZ_DEPLOY\%directory% /E /Q /I"
pause
cd ..
cd ZZ_DEPLOY
erase %directory%.ZIP
pause
@rem Creacio del ZIP file
%WINDIR%\System32\WindowsPowerShell\v1.0\powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "Compress-Archive -path %directory% -DestinationPath .\%directory%"

@rem Copia del ZIP resultant al servidor
pushd "\\192.168.107.9\c$\xampp\htdocs\downloads\QGIS3"
erase %directory%.ZIP
copy D:\Eclipse\QGISV3\ZZ_DEPLOY\%directory%.ZIP .\
popd
cmd /c "pause"
