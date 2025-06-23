@echo off
echo Cleaning up unnecessary files...

REM Backup the original dashboard_server.py if it's not already backed up
if exist dashboard_server.py (
    if not exist dashboard_server_backup.py (
        echo Creating backup of dashboard_server.py as dashboard_server_backup.py
        copy dashboard_server.py dashboard_server_backup.py
    )
)

REM Copy the properly indented server to be the main server
if exist dashboard_server_properly_indented.py (
    echo Setting properly indented dashboard server as the main server
    copy dashboard_server_properly_indented.py dashboard_server.py
)

REM List of files to be deleted
echo.
echo The following files will be deleted:
echo.

set /p confirm=Are you sure you want to delete these files? (Y/N): 

if /i "%confirm%"=="Y" (
    echo.
    echo Deleting files...
    
    REM Delete unnecessary files
    if exist dashboard_server_fixed.py (
        echo Deleting dashboard_server_fixed.py
        del dashboard_server_fixed.py
    )
    
    if exist dashboard_server_original.py (
        echo Deleting dashboard_server_original.py
        del dashboard_server_original.py
    )
    
    if exist run_dashboard.py (
        echo Deleting run_dashboard.py
        del run_dashboard.py
    )
    
    if exist watch_and_update.py (
        echo Deleting watch_and_update.py
        del watch_and_update.py
    )
    
    if exist api.html (
        echo Deleting api.html
        del api.html
    )
    
    echo.
    echo Cleanup complete!
) else (
    echo.
    echo Cleanup cancelled.
)

pause
