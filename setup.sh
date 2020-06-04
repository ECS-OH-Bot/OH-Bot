#!/bin/bash

main(){
    setupVenv
}

setupVenv(){
    mkdir venv
    python3 -m venv ./venv
    . ./venv/bin/activate
   
    if [[ which python3 == "foo" ]]; then
        echo "Failed to activate virtual environment"
    else
        echo "foo"
    fi
}

main