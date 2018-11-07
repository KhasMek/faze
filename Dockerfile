# Faze Dockerfile using Ubuntu as a base container.

FROM ubuntu:latest

RUN apt-get -qq update && apt-get -qq upgrade && apt-get -qq install -y\
  curl \
  fping \
  git \
  nmap \
  python-pip \
  python3-pip \
  p7zip-full > /dev/null &&\
  rm -rf /var/lib/apt/lists/*

# Install altdns
WORKDIR /opt
RUN git clone --depth 1 https://github.com/infosec-au/altdns.git &&\
pip install -q -r altdns/requirements.txt &&\
ln -s /opt/altdns/altdns.py /usr/local/bin/altdns.py

# Install python-faze
WORKDIR /opt/python-faze
ADD . /opt/python-faze
RUN python3 setup.py install

# Install GoBuster
WORKDIR /usr/local/bin
RUN VER=$(curl --silent "https://api.github.com/repos/OJ/gobuster/releases/latest" |\
  grep -Po '"tag_name": "\K.*?(?=")') &&\
  curl --silent -O -L "https://github.com/OJ/gobuster/releases/download/$VER/gobuster-linux-amd64.7z" &&\
  7z e gobuster-linux-amd64.7z > /dev/null &&\
  rm -r gobuster-linux-amd64* &&\
  chmod a+x gobuster

# Install Nikto
# TODO: Nikto has a serious issue reading the DTD while in a
# Docker container. This needs to get fixed.
WORKDIR /opt
RUN git clone --depth 1 https://github.com/sullo/nikto nikto

# Install recon-ng
RUN git clone --depth 1 https://LaNMaSteR53@bitbucket.org/LaNMaSteR53/recon-ng.git &&\
  pip install -q -r recon-ng/REQUIREMENTS &&\
  ln -s /opt/recon-ng/recon-ng /usr/local/bin/recon-ng

# Install Seclists
RUN curl --silent -O -L "https://github.com/danielmiessler/SecLists/archive/master.tar.gz" &&\
  tar xf master.tar.gz --exclude="Payloads/File-Names/max-length/*" &&\
  mv SecLists-master SecLists &&\
  rm master.tar.gz

WORKDIR /data/work
CMD ["faze"]