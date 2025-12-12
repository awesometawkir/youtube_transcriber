@echo off
echo Starting WSL Server...
wsl -d Ubuntu-24.04 -u awesometawkir -- exec bash /mnt/d/project/youtube/run_wsl.sh
pause
