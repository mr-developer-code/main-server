import pexpect
import sys

## execute command that needs input
def run_command(command):
   
    with open("/home/coder/Desktop/securegenai/sur_files/progress.txt", "r")as f:
        count = float(f.read().strip())

    print(f"[Running] \"{command}\"")

    full_command = f"bash -lc \"{command}\""
    print(full_command)
    child = pexpect.spawn(full_command, encoding="utf-8")
    child.logfile = sys.stdout  # Shows in terminal

    try:
        while True:
            i = child.expect([                     
                'Press.*Enter.*',                   # Press Enter
                '[Yy]/[Nn]',                        # y/n confirmation
                pexpect.EOF,
                pexpect.TIMEOUT                     # Timeout
            ], timeout=10)

            if i == 0:
                print("Pressing Enter")
                child.sendline('')
            elif i == 1:
                print("Sending 'y'")
                child.sendline('y')
            elif i == 2:
                print("Command finished.")
                break

        count = round(count + 1.16,1)
        
        with open("/home/coder/Desktop/securegenai/sur_files/progress.txt", "w") as f:
            f.write(str(count))
    except Exception as e:
        print(f"Unexpected error: {e}")

    child.close()

#--------------------------------------------------------------------------------