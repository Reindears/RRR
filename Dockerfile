FROM archlinux:latest

RUN pacman -Syyu --noconfirm

RUN pacman -Syu --noconfirm jre8-openjdk-headless ffmpeg unzip

RUN pip3 install -U pip
RUN mkdir /app/
WORKDIR /app/
COPY . /app/
RUN pip3 install -U setuptools
RUN pip3 install -U -r requirements.txt
CMD python3 -m bot
