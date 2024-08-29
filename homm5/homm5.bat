@echo off
echo Starting GSNAT...
start "Heroes of Might and Magic V - GSNAT" python gsnat.py
echo.
echo Starting IRC...
start "Heroes of Might and Magic V - IRC" python irc.py
echo.
echo Starting Router...
start "Heroes of Might and Magic V - Router" python router.py
echo.
echo Starting CD Key...
start "Heroes of Might and Magic V - CD Key" python cdkey.py
echo.
echo Starting Router Wait Module...
start "Heroes of Might and Magic V - Router (Wait Module)" python router_wm.py
echo.
echo Starting Proxy...
start "Heroes of Might and Magic V - Proxy" python proxy.py
echo.
exit
