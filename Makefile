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
	sudo cp * /usr/local/bin/dryAgingFridge/
	sudo cp dryAgingFridge.service /etc/systemd/system
	sudo systemctl daemon-reload
	sudo systemctl enable module3

.PHONY: uninstall
uninstall:
	sudo systemctl stop dryAgingFridge
	sudo systemctl disable dryAgingFridge
	sudo rm -f /etc/systemd/dryAgingFridge.service
	sudo rm -rf /usr/local/bin/dryAgingFridge
	sudo systemctl daemon-reload
