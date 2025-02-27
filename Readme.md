# Nushscope


Nushscope is a do-it-yourself project that helps locating objects in the sky with your dobsonian telescope.

It's a web application hosted on a Raspberry Pi Zero 2 W that can be accessed on a smartphone. The application senses your telescope's orientation via incremental encoders, and will provide visual guidance to point your telescope towards the desired object. The application does not require Internet connectivity.

Nushscope's main purpose is to have fun with software, electronics and drilling. The same HW/SW platform could be extended to support motorized GoTo capability or cooling fan control.
There are many alternatives if you are looking for turn-key solutions, some of which don't require any hardware besides a smartphone. See for example [Astrohopper](https://github.com/artyom-beilis/skyhopper/blob/main/README.md).


## How it works (user)

Place your telescope as usual. It does not need to be on a horizontal surface or point in any particular direction. The application will figure out this data during the alignment procedure.
Turn on Nushscope and wait until it boots. Then, using the web UI, perform the initial alignment by pointing your scope towards three known stars.
The application will compare the angles from the encoders to the positions of those stars, and derive its own orientation.
You can then use the UI to search for a celestial object and Nushscope will show you where to point your scope to find it.

## Some caveats if you want to play with it

- You will need to find a way to install incremental encoders on your telescope. This might involve drilling, sawing, etc.
- You will need to buy electronics components, solder, do wiring.
- The application retrieves its GPS position from a phone. This will require installing a self-signed x509 certificate on your phone to enable `https`.
- The software installation process requires familiarity with a variety of tools, including docker, linux command line, raspberry pi imaging tools.

## How it works (developer)

- The main application is hosted in a Docker container running on the Raspberry Pi Zero 2 W.
- A Raspberry Pico microcontroller receives pulses from the altitude/azimuth encoders and converts them into angles.
- The main application reads the telescope angles via a serial connection between Pi Zero and Pico.
- The main application is implemented in Python and runs on a Tornado web server. Its UI is implemented in React. The React app communicates with its backend over wifi (provided by PiZero) using a mix of http verbs (e.g. to download star catalogs) and websockets (e.g. to update the telescope's position).
- When a phone connects to the application, the React app will send the phone's GPS position to the backend.
- During the [alignment procedure](./backend/app/alignment/alignment_delegate.py), the application records the measured telescope angles corresponding to each star.
- It then determines the change-of-basis matrices that represent the telescope orientation wrt. the [Alt-Az coordinates](https://en.wikipedia.org/wiki/Horizontal_coordinate_system) using gradient descent ([method here](./documentation/Alignment.md)).
- Once these matrices are known, the app can determine how the telescope should be oriented to point at any object in the sky.
- The main application will periodically send coordinate updates to the UI to track changes in the telescope / celestial object positions.


```shell
sudo docker run --publish 192.168.99.1:443:8000 -it --entrypoint bash nushscope_arm64
```

# Software installation

## 1. Raspberry Pi OS installation

Download the [Raspberry Pi Imager](https://www.raspberrypi.com/software/) for your OS.
Flash the Raspberry Pi OS Lite 64-bit on your Pi Zero's SD card.
- set hostname: 'raspberrypi.local'
- set a username and password. You'll use it later to ssh into the Pi.
- configure wireless settings with your home wifi, so that you'll be able to install additional packages later
- make sure to set the correct country code or wifi might not work
- configure access via ssh and password

## 2. Raspberry Pi Configuration

This script will install docker, configure ssh via usb, configure wifi in access point mode, disable unneeded services, etc.
```shell
ssh raspberrypi.local 'sudo bash -s' < ./pi_zero/prepare_for_app.sh
```

## 3. Build and deploy the Docker image
```shell
image_name=nushscope_arm64

docker buildx build --platform linux/arm64 --tag $image_name .

docker save $image_name | gzip -c | ssh raspberrypi.local "gunzip | sudo docker load"
```

## 4. Shutdown PiZero

```shell
halt; exit
```

The configuration script set up PiZero to automatically start a WiFi network in access point mode and run the Docker container when there is no USB connectivity. This corresponds to a "prod" mode when the device expects to be running stand-alone.