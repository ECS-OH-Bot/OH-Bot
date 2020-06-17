#!/bin/bash

DEPS=("python3")
INTERPRETER=$(command -v python3)
ENV_FILE=".env"

echoerr() { echo "$@" 1>&2; }

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

    if [ -f venv/bin/activate ]; then
        echo 'Virtual Environment Found'
    else 
        mkdir venv
        python3 -m venv ./venv          
    fi
    . ./venv/bin/activate  
    INTERPRETER=$(command -v python3)

    if [[ $INTERPRETER != *"/OH-Bot/venv"* ]]; then
        echoerr "Failed to activate virtual environment"
        echoerr "Checks erroes aboce or try to start with a fresh venv"
        exit 129
    else
        echo "Virtual Enironment Activated"
    fi

    echo 'Installing Dependices'
    # Install the deps after we have verified that the venv is loaded
    if python3 -m pip install -r requirements.txt; then
        echo 'Deps installed successfully'
        return
    else 
        echoerr 'Failed to install Dependices, check errors above or try to start with a fresh venv'
        exit 132
    fi
}

verifyDep(){
    #######################
    # Arguments:
    #   $1: Dependicy to be checked
    #######################
    if ! command -V "$1"; then
        echoerr "Dependency $1 not met" 
        exit 128
    fi
    return 0
}

generateEnvFile(){
    touch .env
    echo "Please enter your discord bot token:"
    read -r BOT_TOKEN
    if ! python3 generateEnv.py "$BOT_TOKEN"; then
        echoerr "Failure Generating .env file"
        echoerr "Refer to Docs on generating .env file by hand"
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