#!/bin/bash

DEPS=("python3")
INTERPRETER=$(command -v python3)

main(){
    for dep in "${DEPS[@]}"
    do
        verifyDep "$dep"
    done

    setupVenv
    generateEnvFile
    generateRunConfig
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
    if ! command -V "$1"; then
        echo "Dependency $1 not met" 
        exit 128
    fi
    return 0
}

generateEnvFile(){
    touch .env
    echo "Please enter your discord bot token:"
    read -r BOT_TOKEN
    if ! python3 generateEnv.py "$BOT_TOKEN"; then
        echo "Failure Generating .env file"
        echo "Refer to Docs on generating .env file by hand"
    fi
    echo "# See docs on how to setup email logging with these variables" >> .env
    echo "#SMTP_HOST"  >> .env
    echo "#TO" >> .env
    echo "#EMAIL" >> .env
    echo "#PASSWORD" >> .env
    echo "#CLASS"   >> .env

    echo -e '.env File generate successfully\n'
    echo -e "Try starting the bot with './run.sh'\n"
}

generateRunConfig(){
    {
        echo "#!/bin/bash"
        echo "source .env"
        echo "$INTERPRETER main.py config.yaml"
    } >> run.sh
    chmod +x run.sh
}

main