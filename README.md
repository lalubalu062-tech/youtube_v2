command 1 requirement ke liye

pip install -r requirements.txt --break-system-packages

command 2 install ke liye

python3 -m playwright install

command 3

python3 -m playwright install-deps

command 4 fake screen ke liye

sudo apt-get install xvfb -y

command 5 fake screen me chalaye

xvfb-run python3 youtube_v2.py

script ko background me chalane ke liye
command 1
sudo apt install screen -y
command 2
screen -S bot
command 3
xvfb-run python3 youtube_v2.py

iske baad 
CTRL + A
CTRL + D
successfully background me ho jayega 
wapis dekhne ke liye 
command 1
screen -r bot

DIKH jayega 
fir background ke liye 
ctrl + a
ctrl + d
