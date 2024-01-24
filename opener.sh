#!/bin/bash

source /opt/ros/noetic/setup.bash

export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"  # This loads nvm
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"  # This load>

source /home/rnd/catkin_ws/devel/setup.bash
source /home/rnd/sonar_ws/devel/setup.bash
. "$HOME/.cargo/env"
source /home/rnd/ardupilot/Tools/completion/completion.bash


cd /home/rnd/workspace/trout_opener/
python3 trout_opener.py