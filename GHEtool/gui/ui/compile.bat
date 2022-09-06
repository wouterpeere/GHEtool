@echo off
call py -m "C:\OSGeo4W64\bin\o4w_env.bat"
call py -m "C:\OSGeo4W64\bin\qt5_env.bat"
call py -m "C:\OSGeo4W64\bin\py3_env.bat"

@echo on
py -m pyrcc5 -o .\icons_rc.py .\ui\icons.qrc