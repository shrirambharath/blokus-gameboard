#!/usr/bin/env python
"""Launch the Blokus web app on the local network.

	python run_web.py

Then open http://<this-machine-LAN-IP>:8000 from any device on the wifi.
"""

import uvicorn

if __name__ == "__main__":
	uvicorn.run("webapp.server:app", host="0.0.0.0", port=8000, reload=False)
