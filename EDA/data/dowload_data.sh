#!/bin/bash

curl -L -o ./data/appointment-schedule.zip https://www.kaggle.com/api/v1/datasets/download/carogonzalezgaltier/medical-appointment-scheduling-system
cd data 
unzip appointment-schedule.zip
rm appointment-schedule.zip