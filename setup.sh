#!/bin/bash


apt-get update
apt install git
apt install python3
apt install python3-pip

mkdir /opt/CoursesWebAPP
git clone https://github.com/Avichiii/courses_website /opt/CoursesWebAPP
pip install -r requirements.txt
python3 app.py
