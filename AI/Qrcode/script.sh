#!/bin/bash/
start=$(date +'%s')
echo "Begin!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
sleep 5
cd
sudo apt-get autoremove -y
sudo apt-get update -y
sudo apt-get upgrade -y
sudo apt-get update


echo "Begin install systems"

echo "___________Install depedency backpage_________"
sudo apt-get install chromium-browser* -y
sleep 5
sudo apt-get install chrome-gnome-shell -y
sleep 5
sudo apt-get install gir1.2-handy-0.0 -y
sleep 5
sudo apt-get install gnome-shell-extension-prefs -y
sleep 5
sudo apt-get install  gnome-tweaks -y
sleep 5
sudo apt-get install  gnome-tweak-tool -y
echo "___________Add display to Applications _________"
cd /home/tit/AI/3
sudo chmod 777 my-app.sh
sudo chmod 777 camera_video.py
cd ~/Display
sudo cp -f cdata.desktop /usr/share/applications
sudo cp -f processingsysy.desktop /usr/share/applications
sudo cp -f display.desktop /usr/share/applications
sudo cp -f TITKULAPP.desktop /usr/share/applications
sudo cp -f uploadcode.desktop /usr/share/applications

cd 
cd ~/Display
bash display.sh
sleep 5
echo "___________ Install vim, visual studio code _______"
sudo apt-get install  -y vim 
sleep 5
sudo snap install code --classic 
sleep 5
sudo apt-get install htop -y
echo "____________Install  dev dependency package___________"
sudo apt-get install build-essential libssl-dev libffi-dev python3-dev -y
echo "____________Install pip3 on python3___________"
sudo apt-get install -y python3-pip
sleep 5
sudo apt-get autoremove -y
sudo -S <<< 2020 apt-get update
sudo apt-get upgrade -y
sudo apt-get update
echo "____________Guivideo__________"
sleep 5
echo "____________Depence backage___________"
sudo apt-get install libxcb-xinerama0 -y
sudo apt-get install cmake -y
sudo apt-get install gcc g++ -y
sudo apt-get install python3-numpy -y 
sudo apt-get install libavcodec-dev libavformat-dev libswscale-dev -y
sudo apt-get install libgstreamer-plugins-base1.0-dev libgstreamer1.0-dev -y
sudo apt-get install libgtk2.0-dev -y
sleep 5
sudo apt-get install libgtk-3-dev -y
sudo apt-get install libpng-dev -y
sudo apt-get install libjpeg-dev -y
sudo apt-get install libopenexr-dev -y
sudo apt-get install libtiff-dev -y
sudo apt-get install libwebp-dev -y
echo "Installed the package on  python"
sleep 10
echo "Install pyqt5"
sudo apt-get install python3-pyqt5* -y
sudo apt-get install  qtcreator pyqt5-dev-tools -y
sudo apt-get install python3-sip -y
sudo pip3 install  PyQtWebEngine --no-cache-dir
sudo apt-get autoremove -y
sudo -S <<< 2020 apt-get update
sudo apt-get upgrade -y
sudo apt-get update -y
echo "Installed pytqt5"
echo "Installing the package" 
sudo apt-get install python3-opencv -y
sudo apt-get install mysql-server -y
sudo apt-get install libmysqlclient-dev -y
sudo pip3 install flask-mysqldb
sudo apt-get install mpg123 -y
sleep 5
sudo pip3 install  scipy
sudo pip3 install  sklearn
sudo pip3 install  Cython
sudo pip3 install  matplotlib
sudo pip3 install Click
sudo pip3 install Pillow
sudo pip3 install  dlib
sudo -S <<< 2020 apt-get update
sudo pip3 install ipython
sudo pip3 install flake8
sudo pip3 install tox
sudo pip3 install coverage
sudo pip3 install Sphinx
sudo pip3 install  requests
sudo pip3 install ipython
sudo pip3 install  launchpadlib
sudo pip3 install  tensorflow
sudo pip3 install pickle5
sudo pip3 install mpg123
sudo pip3 install opencv-python
sleep 5
echo "______Install  and permision  for pyserial____"
sudo pip3 install  pyserial
sudo usermod -a -G dialout $USER
sudo usermod -a -G tty* $USER
sudo apt-get install  gnome-shell-extension-autohidetopbar
sudo apt-get install gnome-screensaver

# cd ~/AI/3_basisTK
# sudo python3 ~/AI/3_basisTK/GUIVIDEO.py --no-sandbox
sleep 5
sudo apt-get autoremove -y
sudo apt-get update -y
sudo apt-get upgrade -y
sudo apt-get update
echo "bat dau thoi gian:$start"
end=$(date +'%s')
echo "ket thuc thoi gian:$end"
sleep 40

promptyn () {
    while true; do
        read -p "$1 " yn
        case $yn in
            [Yy]* ) return 0;;
            [Nn]* ) return 1;;
            * ) echo "Please answer yes or no.";;
        esac
    done
}


if promptyn "Reboot my computer(Yes/No)?"; then
    echo "Reboot starts!"
    sleep 3
    reboot
else
    echo "no"
fi
