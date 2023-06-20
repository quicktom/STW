1. Install requirements with:

pip install -r requirements.txt

2. Change default com port observer.py :

parser.add_argument("--comport",     help="Set serial comport device string.", nargs='?', default="COM6", type=str)

4. Connect remote to PC bluetooth

3. Change path to remote in STWusercontrol.py (use FindRemoteString.py to get the path):

self.path = b'\\\\?\\HID#{00001124-0000-1000-8000-00805f9b34fb}_VID&000205ac_PID&3232&Col04#8&16f637c6&2&0003#{4d1e55b2-f16f-11cf-88cb-001111000030}'


Ubuntu:
sudo apt-get install python3-tk
sudo apt install libhidapi-dev
sudo chmod a+rw /dev/hidraw5
 