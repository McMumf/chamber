# Deployment

How to setup the software on the raspberry pi for deployment.

## 1. Image the Raspberrypi

## 2. Create a System Service

1. Copy `chamber.service` to `/lib/systemd/system/chamber.service`
2. Reload the system daemon: `sudo systemctl daemon-reload`
3. Enable the service: `sudo systemctl enable chamber.service`
4. Start the service: `sudo systemctl start chamber.service`
5. Check the status: `sudo systemctl status chamber.service`
