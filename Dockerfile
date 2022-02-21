FROM archlinux:latest

RUN pacman -Syyu --noconfirm

RUN pacman -Syu --noconfirm jre8-openjdk-headless ffmpeg unzip

WORKDIR /app/
COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

COPY . .

CMD python3 -m bot
