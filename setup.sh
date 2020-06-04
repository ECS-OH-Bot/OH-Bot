#!/bin/bash

DEPS=("python3")

main(){
    for dep in "${DEPS[@]}"
    do
        verifyDep "$dep"
    done

    setupVenv
}

setupVenv(){
    mkdir venv
    python3 -m venv ./venv
    . ./venv/bin/activate
   
    INTERPRETER=$(command -v python3)

    if [[ $INTERPRETER != *"/OH-Bot/venv"* ]]; then
        echo "Failed to activate virtual environment"
        exit 129
    else
        echo "Virtual Enironment Activated"
    fi

    # Install the deps after we have verified that the venv is loaded
    python3 -m pip install -r requirements.txt
}

verifyDep(){

    if ! command -V "$1" > '\dev\null' 2>&1; then
        echo "Dependency $1 not met" 
        exit 128
    fi
    return 0
}

generateEnv(){
    
}


main