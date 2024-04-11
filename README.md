# GOES-SATELLITE-IMAGES-RASPBERRYPI
# Hardware Required to Receive GOES Satellites
1.7 GHz Parabolic Antenna

RTL-SDR (Can be one that comes with the kit or another) but needs to support bias t (The one with the kit does) 
SAWbird + GOES LNA

USB Extenders (Optional) - Depends on your set-up (Kit includes one)

sma rf cable (Kit comes with this...depending how far you are from your antenna, you may or may not need this extension)

THIS Antenna KIT CAN BE FOUND HERE: https://amzn.to/4cWtPLJ
![Alt Text](https://github.com/darkiron71/GOES-SATELLITE-IMAGES-RASPBERRYPI/blob/main/Sat%20Dish.jpg)

Tripod - https://amzn.to/3Q0be7o

LCD Screen (Optional) - If you want to view the live Antenna Data. https://amzn.to/43WNnv3

Raspberry pi - Mine is running on a 3B but should work with anything newer:

  Raspberry pi 4 starter kit: https://amzn.to/4cMun6R
  Raspberry pi 3b starter kit: https://amzn.to/3PXJwZ6

# Mounting Options & Weather Proofing
I used a outdoor enclosure met for a sprinkler timer, but any outdoor weatherproof enclosure should work. Make sure there is enough room for the raspberrypi, and power cables. 

You can use something like this: https://amzn.to/3xwXNWl -- keep in mind some of these you may need to drill a hole in the bottom to run the power cable through. 
![Alt Text](https://github.com/darkiron71/GOES-SATELLITE-IMAGES-RASPBERRYPI/blob/main/Outdoor%20enclosure.jpg)
![Alt Text](https://github.com/darkiron71/GOES-SATELLITE-IMAGES-RASPBERRYPI/blob/main/Outdoor%20enclosure%20screen.jpg)

Make sure rf and USB connection points are weather proofed as well. I used these ones: https://amzn.to/3VYGEPp

![Alt Text](https://github.com/darkiron71/GOES-SATELLITE-IMAGES-RASPBERRYPI/blob/main/Weather%20connector.jpg)

The SAW Bird has an external USB port so be sure to cover that with tape if not being used. 

# Software Requirements 

Update raspberry pi - make sure you can access raspberry pi via ssh as you will want to run it headless. Recommend runnning raspberry pi OS lite.

	sudo apt update 
	sudo apt upgrade
 
Install screen

    sudo apt install screen 
 
Install python3
	
    sudo apt install python3
 
Install git

    sudo apt install git
    
If you want to have an LCD display: (This Repository Comes from https://github.com/the-raspberry-pi-guy/lcd)
Follow this guide to install the necessary drivers and connect GPIO pins correctly: 

    https://youtu.be/fR5XhHYzUK0?si=B9Mbdw-HuttwqH2W
   
 Be sure to download the screen_print.py python script to display antenna data to LCD from the repository.

    Link here: https://github.com/darkiron71/GOES-SATELLITE-IMAGES-RASPBERRYPI/blob/main/screen_print.py
 Be sure to make it executable 
	sudo chmod +x "screen_print".py
			
Install Geostools and Goesproc on the raspbery pi: (THIS INFO COMES FROM: https://usradioguy.com/programming-a-pi-for-goestools/) The info below is just copied from their page!


You can follow their guide directly on their website here, but I will have the same commands listed below:

Install dependencies

    sudo apt-get install git build-essential cmake libusb-1.0-0-dev libopencv-dev libproj-dev

Download, compile, and install librtlsdr: (Can be found here if you have trouble installing: https://github.com/steve-m/librtlsdr.git)
  
    git clone https://github.com/steve-m/librtlsdr.git
    cd librtlsdr
    mkdir build
    cd build
    cmake -DCMAKE_INSTALL_PREFIX:PATH=/usr -DINSTALL_UDEV_RULES=ON ..
    sudo make -j2 install

Load udev rules and blacklist the DVB driver shipped with the OS

    sudo cp ../rtl-sdr.rules /etc/udev/rules.d/
    sudo ldconfig
    echo 'blacklist dvb_usb_rtl28xxu' | sudo tee --append /etc/modprobe.d/blacklist-dvb_usb_rtl28xxu.conf

Reboot the device

    sudo reboot

Test to make sure your rtl-sdr donge is working (It should show "Found 1 device(s):")
Hit Ctrl+C to exit

    rtl_test

Install goestools

    git clone https://github.com/pietern/goestools.git
    cd goestools
    git submodule init
    git submodule update --recursive
    mkdir build
    cd build
    cmake -DCMAKE_INSTALL_PREFIX:PATH=/usr ..

Make: This will take a while on a raspberry pi

    sudo make -j2 install

Create goesrecv.conf config file

    cd
    sudo nano goesrecv.conf

Paste the script below into the goesrecv.conf file make the edits noted and then CTRL X and “Yes” to save the file.

Change the sample_rate to 2000000. Higher sample rates MAY cause goesrecv to require multiple restarts in order to get a lock on the frequency.  You can adjust the sample rate later as needed. Check your dongle for the type of BiasTee (if any) it has. Bias tees are the components, that are used to supply DC voltages to bias RF circuits.

If you’re using an RTL-SDR V3 or another SDR with BiasTee function enable the bias tee with set bias_tee = true and increase the gain to 30:

Bias Tee is not needed for the Nooelec SmarTee XTR which supplies constant bias tee power to the LNA or if you’re powering your SAWBird through the micro USB port, set bias_tee = false under [rtlsdr]. And try, when using the Nooelec SmarTee XTR setting the gain to 5.

    [demodulator]
    mode = "hrit"
    source = "rtlsdr"
    
    [rtlsdr]
    frequency = 1694100000
    sample_rate = 2200000
    gain = 5
    
    bias_tee = false
    
    [costas]
    max_deviation = 200e3
    
    [decoder.packet_publisher]
    bind = "tcp://0.0.0.0:5004"
    send_buffer = 1048576
    
    [monitor]
    statsd_address = "udp4://localhost:8125"
    
    [clock_recovery.sample_publisher]
    bind = "tcp://0.0.0.0:5002"
    send_buffer = 2097152
    
    [demodulator.stats_publisher]
    bind = "tcp://0.0.0.0:6001"
    
    [decoder.stats_publisher]
    bind = "tcp://0.0.0.0:6002"
    
    # Change rtlsdr to airspy if you're using an AirSpy, etc.
    # Publishes IQ samples coming straight from the SDR over
    # nanomsg
    [rtlsdr.sample_publisher]
    bind = "tcp://0.0.0.0:5000"
    send_buffer = 2097152

Paste the script above into the goesrecv.conf file and then CTRL X and Yes. Then:

    sudo reboot

Modify or replace the Goesproc-goesr.conf file located in the /usr/share/goestools directory to support GOES 18 and GOES19:

    # GOES 16_17_18_19 GOESTOOLS  goesproc configuration file to process GOES-R series products.
    # USRADIOGUY.COM Version 04/01/2024
    #
    
    # Store all original GOES-16 products.
    [[handler]]
    type = "image"
    origin = "goes16"
    directory = "./goes16/{region:short|lower}/{channel:short|lower}/{time:%Y-%m-%d}"
    filename = "GOES16_{region:short}_{channel:short}_{time:%Y%m%dT%H%M%SZ}"
    format = "jpg"
    json = false
    
      [[handler.map]]
      path = "/usr/share/goestools/ne/ne_50m_admin_0_countries_lakes.json"
    
      [[handler.map]]
      path = "/usr/share/goestools/ne/ne_50m_admin_1_states_provinces_lakes.json"
    
    # Store all original GOES-18 products.
    [[handler]]
    type = "image"
    origin = "goes18"
    directory = "./goes18/{region:short|lower}/{channel:short|lower}/{time:%Y-%m-%d}"
    filename = "GOES18_{region:short}_{channel:short}_{time:%Y%m%dT%H%M%SZ}"
    format = "jpg"
    json = false
    
      [[handler.map]]
      path = "/usr/share/goestools/ne/ne_50m_admin_0_countries_lakes.json"
    
      [[handler.map]]
      path = "/usr/share/goestools/ne/ne_50m_admin_1_states_provinces_lakes.json"
    
    
    # GOES-16 ABI false color.
    [[handler]]
    type = "image"
    origin = "goes16"
    regions = [ "fd", "m1", "m2" ]
    channels = [ "ch02", "ch13" ]
    directory = "./goes16/{region:short|lower}/fc/{time:%Y-%m-%d}"
    filename = "GOES16_{region:short}_FC_{time:%Y%m%dT%H%M%SZ}"
    format = "jpg"
    json = false
    
      [handler.remap.ch02]
      path = "/usr/share/goestools/wxstar/wxstar_goes16_ch02_curve.png"
    
      [handler.lut]
      path = "/usr/share/goestools/wxstar/wxstar_goes16_lut.png"
    
      [[handler.map]]
      path = "/usr/share/goestools/ne/ne_50m_admin_0_countries_lakes.json"
    
      [[handler.map]]
      path = "/usr/share/goestools/ne/ne_50m_admin_1_states_provinces_lakes.json"
    
    # GOES-16 ABI RGB-enhanced
    [[handler]]
    type = "image"
    origin = "goes16"
    regions = [ "fd", "m1", "m2" ]
    channels = [ "ch07", "ch08", "ch09", "ch13", "ch14", "ch15" ]
    directory = "./goes16/{region:short|lower}/{channel:short|lower}_enhanced/{time:%Y-%m-%d}"
    filename = "GOES16_{region:short}_{channel:short}_enhanced_{time:%Y%m%dT%H%M%SZ}"
    format = "jpg"
    json = false
    
      ## The following gradients are rough approximations of the 
      ## McIDAS RGB enhancements used by NOAA/NESDIS/STAR on their site..
      ##
      ## For more info:
      ##
      ##   https://www.star.nesdis.noaa.gov/GOES/GOES16_FullDisk.php 
      ##   http://cimss.ssec.wisc.edu/goes/visit/water_vapor_enhancement.html
      ##   http://cimss.ssec.wisc.edu/goes/visit/enhanced_v_enhancements.html
    
      ## Shortwave IR (Channel 7)
      [handler.gradient.ch07]
      points = [
        { units = 400, color = "#000000" },
        { units = 250, color = "#b9b9b9" },
        { units = 249.999, color = "#00ffff" },
        { units = 240, color = "#000080" },
        { units = 230, color = "#00ff00" },
        { units = 220, color = "#ffff00" },
        { units = 210, color = "#ff0000" },
        { units = 200, color = "#000000" },
        { units = 190, color = "#ffffff" }
      ]
    
      ## Water Vapor (Channels 8 and 9)
      [handler.gradient.ch08]
      points = [
        { units = 276, color = "#000000" },
        { units = 275.9, color = "#ff0000" },
        { units = 258, color = "#ffff00" },
        { units = 250, color = "#000070" },
        { units = 233, color = "#ffffff" },
        { units = 195, color = "#408020" },
        { units = 178, color = "#00ffff" }
      ]
      [handler.gradient.ch09]
      points = [
        { units = 276, color = "#000000" },
        { units = 275.9, color = "#ff0000" },
        { units = 258, color = "#ffff00" },
        { units = 250, color = "#000070" },
        { units = 233, color = "#ffffff" },
        { units = 195, color = "#408020" },
        { units = 178, color = "#00ffff" }
      ]
    
      ## Longwave IR (Channels 13, 14, and 15)
      [handler.gradient.ch13]
      points = [
        { units = 333, color = "#000000" },
        { units = 238, color = "#b9b9b9" },
        { units = 237.999, color = "#00ffff" },
        { units = 228, color = "#000080" },
        { units = 218, color = "#00ff00" },
        { units = 208, color = "#ffff00" },
        { units = 198, color = "#ff0000" },
        { units = 188, color = "#000000" },
        { units = 178, color = "#ffffff" }
      ]
      [handler.gradient.ch14]
      points = [
        { units = 333, color = "#000000" },
        { units = 238, color = "#b9b9b9" },
        { units = 237.999, color = "#00ffff" },
        { units = 228, color = "#000080" },
        { units = 218, color = "#00ff00" },
        { units = 208, color = "#ffff00" },
        { units = 198, color = "#ff0000" },
        { units = 188, color = "#000000" },
        { units = 178, color = "#ffffff" }
      ]
      [handler.gradient.ch15]
      points = [
        { units = 333, color = "#000000" },
        { units = 238, color = "#b9b9b9" },
        { units = 237.999, color = "#00ffff" },
        { units = 228, color = "#000080" },
        { units = 218, color = "#00ff00" },
        { units = 208, color = "#ffff00" },
        { units = 198, color = "#ff0000" },
        { units = 188, color = "#000000" },
        { units = 178, color = "#ffffff" }
      ]
    
      [[handler.map]]
      path = "/usr/share/goestools/ne/ne_50m_admin_0_countries_lakes.json"
    
      [[handler.map]]
      path = "/usr/share/goestools/ne/ne_50m_admin_1_states_provinces_lakes.json"
    
    
    
    
    # Images relayed from Himawari-9 After Dec 13th 2022. 
    [[handler]] 
    type = "image" 
    origin = "himawari8" 
    directory = "./himawari9/{region:short|lower}/{time:%Y-%m-%d}" 
    filename = "Himawari9_{region:short}_{channel:short}_{time:%Y%m%dT%H%M%SZ}" 
    format = "jpg" 
    json = false 
    
    [[handler.map]] 
    path = "/usr/share/goestools/ne/ne_50m_admin_0_countries_lakes.json" 
    
    [[handler.map]] 
    path = "/usr/share/goestools/ne/ne_50m_admin_1_states_provinces_lakes.json"
    
    
    # NWS text (weather reports).
    [[handler]]
    type = "text"
    origin = "nws"
    directory = "./nws/{time:%Y-%m-%d}"
    filename = "{time:%Y%m%dT%H%M%SZ}_{awips:nnn}{awips:xxx}"
    json = false
    
    # NWS images.
    [[handler]]
    type = "image"
    origin = "nws"
    directory = "./nws/{time:%Y-%m-%d}"
    filename = "{time:%Y%m%dT%H%M%SZ}_{filename}"
    format = "png"
    json = false
    
    # Miscellaneous text.
    [[handler]]
    type = "text"
    origin = "other"
    directory = "./text/{time:%Y-%m-%d}"
    filename = "{time:%Y%m%dT%H%M%SZ}_{filename}"
    json = false
    
    
    ################
    ##  GOES-18 ####
    ################
    # Store all original GOES-18 products.
    [[handler]]
    type = "image"
    origin = "goes18"
    directory = "./goes18/{region:short|lower}/{channel:short|lower}/{time:%Y-%m-%d}"
    filename = "GOES18_{region:short}_{channel:short}_{time:%Y%m%dT%H%M%SZ}"
    format = "jpg"
    json = false
    
      [[handler.map]]
      path = "/usr/share/goestools/ne/ne_50m_admin_0_countries_lakes.json"
    
      [[handler.map]]
      path = "/usr/share/goestools/ne/ne_50m_admin_1_states_provinces_lakes.json"
      
    # GOES-18 ABI false color.
    [[handler]]
    type = "image"
    origin = "goes18"
    regions = [ "fd", "m1", "m2" ]
    channels = [ "ch02", "ch13" ]
    directory = "./goes18/{region:short|lower}/fc/{time:%Y-%m-%d}"
    filename = "GOES18_{region:short}_FC_{time:%Y%m%dT%H%M%SZ}"
    format = "jpg"
    json = false
    
      # This reuses the GOES-16 contrast curve assuming it is identical
      [handler.remap.ch02]
      path = "/usr/share/goestools/wxstar/wxstar_goes16_ch02_curve.png"
    
      # This reuses the GOES-16 LUT assuming it is identical
      [handler.lut]
      path = "/usr/share/goestools/wxstar/wxstar_goes16_lut.png"
    
      [[handler.map]]
      path = "/usr/share/goestools/ne/ne_50m_admin_0_countries_lakes.json"
    
      [[handler.map]]
      path = "/usr/share/goestools/ne/ne_50m_admin_1_states_provinces_lakes.json"
    
    # GOES-18 ABI RGB-enhanced
    [[handler]]
    type = "image"
    origin = "goes18"
    regions = [ "fd", "m1", "m2" ]
    channels = [ "ch07", "ch08", "ch09", "ch13", "ch14", "ch15" ]
    directory = "./goes18/{region:short|lower}/{channel:short|lower}_enhanced/{time:%Y-%m-%d}"
    filename = "GOES18_{region:short}_{channel:short}_enhanced_{time:%Y%m%dT%H%M%SZ}"
    format = "jpg"
    json = false
    
      ## The following gradients are rough approximations of the 
      ## McIDAS RGB enhancements used by NOAA/NESDIS/STAR on their site..
      ##
      ## For more info:
      ##
      ##   https://www.star.nesdis.noaa.gov/GOES/GOES16_FullDisk.php 
      ##   http://cimss.ssec.wisc.edu/goes/visit/water_vapor_enhancement.html
      ##   http://cimss.ssec.wisc.edu/goes/visit/enhanced_v_enhancements.html
    
      ## Shortwave IR (Channel 7)
      [handler.gradient.ch07]
      points = [
        { units = 400, color = "#000000" },
        { units = 250, color = "#b9b9b9" },
        { units = 249.999, color = "#00ffff" },
        { units = 240, color = "#000080" },
        { units = 230, color = "#00ff00" },
        { units = 220, color = "#ffff00" },
        { units = 210, color = "#ff0000" },
        { units = 200, color = "#000000" },
        { units = 190, color = "#ffffff" }
      ]
    
      ## Water Vapor (Channels 8 and 9)
      [handler.gradient.ch08]
      points = [
        { units = 276, color = "#000000" },
        { units = 275.9, color = "#ff0000" },
        { units = 258, color = "#ffff00" },
        { units = 250, color = "#000070" },
        { units = 233, color = "#ffffff" },
        { units = 195, color = "#408020" },
        { units = 178, color = "#00ffff" }
      ]
      [handler.gradient.ch09]
      points = [
        { units = 276, color = "#000000" },
        { units = 275.9, color = "#ff0000" },
        { units = 258, color = "#ffff00" },
        { units = 250, color = "#000070" },
        { units = 233, color = "#ffffff" },
        { units = 195, color = "#408020" },
        { units = 178, color = "#00ffff" }
      ]
    
      ## Longwave IR (Channels 13, 14, and 15)
      [handler.gradient.ch13]
      points = [
        { units = 333, color = "#000000" },
        { units = 238, color = "#b9b9b9" },
        { units = 237.999, color = "#00ffff" },
        { units = 228, color = "#000080" },
        { units = 218, color = "#00ff00" },
        { units = 208, color = "#ffff00" },
        { units = 198, color = "#ff0000" },
        { units = 188, color = "#000000" },
        { units = 178, color = "#ffffff" }
      ]
      [handler.gradient.ch14]
      points = [
        { units = 333, color = "#000000" },
        { units = 238, color = "#b9b9b9" },
        { units = 237.999, color = "#00ffff" },
        { units = 228, color = "#000080" },
        { units = 218, color = "#00ff00" },
        { units = 208, color = "#ffff00" },
        { units = 198, color = "#ff0000" },
        { units = 188, color = "#000000" },
        { units = 178, color = "#ffffff" }
      ]
      [handler.gradient.ch15]
      points = [
        { units = 333, color = "#000000" },
        { units = 238, color = "#b9b9b9" },
        { units = 237.999, color = "#00ffff" },
        { units = 228, color = "#000080" },
        { units = 218, color = "#00ff00" },
        { units = 208, color = "#ffff00" },
        { units = 198, color = "#ff0000" },
        { units = 188, color = "#000000" },
        { units = 178, color = "#ffffff" }
      ]
    
      [[handler.map]]
      path = "/usr/share/goestools/ne/ne_50m_admin_0_countries_lakes.json"
    
      [[handler.map]]
      path = "/usr/share/goestools/ne/ne_50m_admin_1_states_provinces_lakes.json"
    
    
    ################
    ##  GOES-19 ####
    ################
    # Store all original GOES-19 products.
    [[handler]]
    type = "image"
    origin = "goes19"
    directory = "./goes19/{region:short|lower}/{channel:short|lower}/{time:%Y-%m-%d}"
    filename = "GOES19_{region:short}_{channel:short}_{time:%Y%m%dT%H%M%SZ}"
    format = "jpg"
    json = false
    
      [[handler.map]]
      path = "/usr/share/goestools/ne/ne_50m_admin_0_countries_lakes.json"
    
      [[handler.map]]
      path = "/usr/share/goestools/ne/ne_50m_admin_1_states_provinces_lakes.json"
      
    # GOES-19 ABI false color.
    [[handler]]
    type = "image"
    origin = "goes19"
    regions = [ "fd", "m1", "m2" ]
    channels = [ "ch02", "ch13" ]
    directory = "./goes19/{region:short|lower}/fc/{time:%Y-%m-%d}"
    filename = "GOES19_{region:short}_FC_{time:%Y%m%dT%H%M%SZ}"
    format = "jpg"
    json = false
    
      # This reuses the GOES-16 contrast curve assuming it is identical
      [handler.remap.ch02]
      path = "/usr/share/goestools/wxstar/wxstar_goes16_ch02_curve.png"
    
      # This reuses the GOES-16 LUT assuming it is identical
      [handler.lut]
      path = "/usr/share/goestools/wxstar/wxstar_goes16_lut.png"
    
      [[handler.map]]
      path = "/usr/share/goestools/ne/ne_50m_admin_0_countries_lakes.json"
    
      [[handler.map]]
      path = "/usr/share/goestools/ne/ne_50m_admin_1_states_provinces_lakes.json"
    
    # GOES-19 ABI RGB-enhanced
    [[handler]]
    type = "image"
    origin = "goes19"
    regions = [ "fd", "m1", "m2" ]
    channels = [ "ch07", "ch08", "ch09", "ch13", "ch14", "ch15" ]
    directory = "./goes19/{region:short|lower}/{channel:short|lower}_enhanced/{time:%Y-%m-%d}"
    filename = "GOES19_{region:short}_{channel:short}_enhanced_{time:%Y%m%dT%H%M%SZ}"
    format = "jpg"
    json = false
    
      ## The following gradients are rough approximations of the 
      ## McIDAS RGB enhancements used by NOAA/NESDIS/STAR on their site..
      ##
      ## For more info:
      ##
      ##   https://www.star.nesdis.noaa.gov/GOES/GOES16_FullDisk.php 
      ##   http://cimss.ssec.wisc.edu/goes/visit/water_vapor_enhancement.html
      ##   http://cimss.ssec.wisc.edu/goes/visit/enhanced_v_enhancements.html
    
      ## Shortwave IR (Channel 7)
      [handler.gradient.ch07]
      points = [
        { units = 400, color = "#000000" },
        { units = 250, color = "#b9b9b9" },
        { units = 249.999, color = "#00ffff" },
        { units = 240, color = "#000080" },
        { units = 230, color = "#00ff00" },
        { units = 220, color = "#ffff00" },
        { units = 210, color = "#ff0000" },
        { units = 200, color = "#000000" },
        { units = 190, color = "#ffffff" }
      ]
    
      ## Water Vapor (Channels 8 and 9)
      [handler.gradient.ch08]
      points = [
        { units = 276, color = "#000000" },
        { units = 275.9, color = "#ff0000" },
        { units = 258, color = "#ffff00" },
        { units = 250, color = "#000070" },
        { units = 233, color = "#ffffff" },
        { units = 195, color = "#408020" },
        { units = 178, color = "#00ffff" }
      ]
      [handler.gradient.ch09]
      points = [
        { units = 276, color = "#000000" },
        { units = 275.9, color = "#ff0000" },
        { units = 258, color = "#ffff00" },
        { units = 250, color = "#000070" },
        { units = 233, color = "#ffffff" },
        { units = 195, color = "#408020" },
        { units = 178, color = "#00ffff" }
      ]
    
      ## Longwave IR (Channels 13, 14, and 15)
      [handler.gradient.ch13]
      points = [
        { units = 333, color = "#000000" },
        { units = 238, color = "#b9b9b9" },
        { units = 237.999, color = "#00ffff" },
        { units = 228, color = "#000080" },
        { units = 218, color = "#00ff00" },
        { units = 208, color = "#ffff00" },
        { units = 198, color = "#ff0000" },
        { units = 188, color = "#000000" },
        { units = 178, color = "#ffffff" }
      ]
      [handler.gradient.ch14]
      points = [
        { units = 333, color = "#000000" },
        { units = 238, color = "#b9b9b9" },
        { units = 237.999, color = "#00ffff" },
        { units = 228, color = "#000080" },
        { units = 218, color = "#00ff00" },
        { units = 208, color = "#ffff00" },
        { units = 198, color = "#ff0000" },
        { units = 188, color = "#000000" },
        { units = 178, color = "#ffffff" }
      ]
      [handler.gradient.ch15]
      points = [
        { units = 333, color = "#000000" },
        { units = 238, color = "#b9b9b9" },
        { units = 237.999, color = "#00ffff" },
        { units = 228, color = "#000080" },
        { units = 218, color = "#00ff00" },
        { units = 208, color = "#ffff00" },
        { units = 198, color = "#ff0000" },
        { units = 188, color = "#000000" },
        { units = 178, color = "#ffffff" }
      ]
    
      [[handler.map]]
      path = "/usr/share/goestools/ne/ne_50m_admin_0_countries_lakes.json"
    
      [[handler.map]]
      path = "/usr/share/goestools/ne/ne_50m_admin_1_states_provinces_lakes.json"

# Getting a Satellite Connection
Now that you have updated your config file lets get a your satellite dish locked in. First thing you want to do if find where the satellite you want to connect to is located. Good tool to use is https://www.dishpointer.com
This will help you find the right direction and tilt is required for your antenna placement. The satellite I connected to was GOES-16. 
Once you have your antenna in the direction as specified by dishpointer, you will need to start up goesrecv. We will run this is a screen session. 

    screen -S goesrecv

You should now be in a new termianl screen session. Next run the goesrecv program. 

    goesrecv -v -i 1 -c ~/goesrecv.conf

![alt text](https://usradioguy.com/wp-content/uploads/2020/05/ViterbiAverage-1.jpg)


Anything below 300 for vit avg should be fine. The adjustments have to be very percise but once locked in it will work great. Try moving your antenna 1-2 inches at a time while monitoring the vit(avg). Once you have your antenna placement set, make sure to lock your antenna into place. 

# Monitor goesrecv on LCD Screen (Optional)
With goesrecv running in a screen, we can now start up your LCD screen session to monitor this connection. Detach the previous screen by doing the following: 

    Ctrl+a+d

You should now be back at the main terminal. Change directories to where you save the print_screen.py. Open a new screen. This is where we will run our LCD session. 

    screen -S screen_print

Now in the new screen start the program:

    python3 screen_print.py

As long as everything worked, you should now see the goesrecv screen termianl output scrolling on your LCD dispaly. The Python code can be modified to any screen session name you want if you want it to show something different. Now detach from that screen.

    Ctrl+a+d

# Mount a NAS Drive (Optional)
Install dependencies
    
    apt-get install  samba-common smbclient samba-common-bin smbclient  cifs-utils

Then, create a local directory and mount the remote share:
  
    mkdir /mnt/abc
    sudo mount -t cifs //server/share /mnt/abc
    
If you have it password protected, you may need to pass it with additional arguments

    sudo mount -t cifs //server/share /mnt/abc -o user=user,pass=password,dom=domain
    

# Capture Packets and Convert To Images
With the goesrecv screen running you now open another screen session for goesproc 

    screen -S goesproc

Now change it's important that you change directories to wherever you want the images to be stored. For me I mounted a NAS to store my images.

    cd /your/storage/location
    sudo goesproc -c /usr/share/goestools/goesproc-goesr.conf -m packet --subscribe tcp://127.0.0.1:5004

You should now see your terminal begin to populate with packets being received. Keep in mind it can take up to 10-30 minutes before you receive any full images. But once you do, it should look like this in the terminal: 

Writing: /home/pi/goes/./goes16/fd/staticimage/GOES16_FD_FC_NOMAP20200527T140016Z.jpg (took 1.838s)

Writing: /home/pi/goes/./goes16/fd/NOMAP/2020-05-27/GOES16_FD_FC_NOMAP20200527T140016Z.jpg (took 1.804s)

Writing: /home/pi/goes/./goes16/fd/ch02/2020-05-27/GOES16_FD_CH02_20200527T140016Z.jpg (took 1.474s)

Writing: /home/pi/goes/./goes16/fd/fc/2020-05-27/GOES16_FD_FC_20200527T140016Z.jpg (took 1.981s)


You should now be able to find these new directories located in the folder you are running the program.
![Alt Text](https://github.com/darkiron71/GOES-SATELLITE-IMAGES-RASPBERRYPI/blob/main/Directories.jpg)

Be sure to detach from this screen first if you are viewing these from the pi itself. You can detach with Ctrl+a+d
If for whatever reason you need to reattach to a screen session you can re-attach by:

    #Find the screen name
    screen -ls 
    #Reattach the screen 
    screen -r "screenname"

# Captured Data & Images
Below are some examples of the images and NOAA weather data you will receive after some time of letting this run. 

Example Images here: 
![Alt Text](https://github.com/darkiron71/GOES-SATELLITE-IMAGES-RASPBERRYPI/blob/main/Earth%20Image.jpg)
![Alt Text](https://github.com/darkiron71/GOES-SATELLITE-IMAGES-RASPBERRYPI/blob/main/NWS%20Images.gif)
![Alt Text](https://github.com/darkiron71/GOES-SATELLITE-IMAGES-RASPBERRYPI/blob/main/Weather.jpg)


