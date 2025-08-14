from utils import run_command
import multiprocessing
import sys
import signal

def cleanup(signum, frame):
    print("Shutting down cleanly...")
    # Do cleanup here (close sockets, save logs, etc.)
    sys.exit(0)

signal.signal(signal.SIGTERM, cleanup)
signal.signal(signal.SIGINT, cleanup)

commands = [
    "sudo python3 received_data_node_api.py",
    "sudo python3 send_file_api.py"
]

for cmd in commands:
    p = multiprocessing.Process(target=run_command, args=(cmd,))
    p.start()

#--------------------------------------------------------------------------------