#!/bin/bash

# This should be run from the root of the repository
main(){
    for hook in hooks/*; do
        ln "$hook" .git/hooks/
    done
}

main