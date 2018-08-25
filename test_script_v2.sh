#!/bin/bash

# input: set up a configure on "name of the folders" (multiple directories).
# 1. specify a specific folder.
# 2. the program will perform all sub-folders in that folder.

# declare variables
FOLDER_PATH="$PWD/$1"
LEVEL=$2
COUNT_NUM=$3
GRID_PERCENT=$4
arrays=()

# determine whether or not the folder exists in the working directory
if [ -d "$FOLDER_PATH" ]; then
    # create a directory in order to store all results 
    if [ ! -d "$PWD/result" ]; then
        mkdir result
    fi

    # grab names of all sub-directories
    cd $FOLDER_PATH
    for x in $(ls); do 
        arrays+=(${x})
    done
    
    # go back the parent directory and run the program given all sub-directories
    cd ..
    for i in "${arrays[@]}" ; do
        #echo "$FOLDER_PATH/$i"
        
        if [ ! -d "$PWD/result/$i" ]; then
            mkdir "$PWD/result/$i"
        fi
        
        python3 test_v2.py "$FOLDER_PATH/$i" $LEVEL "$PWD/result/$i" $COUNT_NUM $GRID_PERCENT
    done
else
    echo "The $1 does not exist !!"
fi





