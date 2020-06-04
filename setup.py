import subprocess
import os

def main():
    requirements = [
        'python3',
        'pip',
        ]
    
    for req in requirements:
        if not checkProgramExists(req):
            raise OSError(f"Cannot find {req} in PATH")

    setupVenv()


def checkProgramExists(prgmName: str) -> bool:
    FNULL = open(os.devnull, 'w')
    process = subprocess.run(["whereis", prgmName], stdout=FNULL, stderr=subprocess.STDOUT)

    return process.returncode == 0


def setupVenv():

    command = "mkdir venv"
    process = subprocess.run(command.split())

    command = "python3 -m venv ./venv"
    proccess = subprocess.run(command.split())



    command = "python3 -m pip install -r requirements.txt"
    # process = subprocess.run(command.split())



if __name__ == "__main__":
    main()