@REM Use this BAT-file to run this stand-alone-python environment.
@REM
@REM Example: python.bat IOClient.py
@REM

@SET thispath=%~dp0


@set PATH=%thispath%WPy64-3810\python-3.8.1.amd64;%thispath%WPy64-3810\python-3.8.1.amd64\Lib\;%PATH%
@set PYTHONPATH=%thispath%WPy64-3810\python-3.8.1.amd64;%thispath%WPy64-3810\python-3.8.1.amd64\lib;%thispath%WPy64-3810\python-3.8.1.amd64\libs;%thispath%WPy64-3810\python-3.8.1.amd64\DLLs
cd %thispath%MFD39\
@python mfdleft_opengl.py
pause
