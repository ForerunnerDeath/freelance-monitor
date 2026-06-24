#!/usr/bin/env bash
set -e

export DISPLAY=:99

Xvfb :99 -screen 0 1400x900x24 -ac +extension GLX +render -noreset >/tmp/xvfb.log 2>&1 &
sleep 1

fluxbox >/tmp/fluxbox.log 2>&1 &
x11vnc -display :99 -forever -shared -rfbport 5900 -nopw >/tmp/x11vnc.log 2>&1 &
websockify --web=/usr/share/novnc/ 0.0.0.0:6080 localhost:5900 >/tmp/novnc.log 2>&1 &

echo "noVNC: http://127.0.0.1:6080/vnc.html?autoconnect=true"

python -m scripts.profi_login_vnc
