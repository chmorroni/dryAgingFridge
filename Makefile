#-----------------------------------------------------------
# Usage: make [TARGET]
#
# Build Targets:
#     install - Installs the dry aging fridge service
#     uninstall - Uninstalls the dry aging fridge service
#
#-----------------------------------------------------------

.PHONY: install
install:
	sudo mkdir -p /usr/local/bin/dryAgingFridge
	sudo cp -r * /usr/local/bin/dryAgingFridge/
	sudo chmod +x /usr/local/bin/dryAgingFridge/app.py
	sudo cp dryAgingFridge.service /etc/systemd/system
	sudo systemctl daemon-reload
	sudo systemctl enable dryAgingFridge

.PHONY: uninstall
uninstall:
	sudo systemctl stop dryAgingFridge
	sudo systemctl disable dryAgingFridge
	sudo rm -f /etc/systemd/dryAgingFridge.service
	sudo rm -rf /usr/local/bin/dryAgingFridge
	sudo systemctl daemon-reload
