# Faze Dockerfile using Ubuntu as a base container.

FROM ubuntu:latest

# TODO: make sure I need all deez
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
WORKDIR /opt/altdns

# Install faze
WORKDIR /opt/faze
ADD . /opt/faze
RUN pip3 install -q -r requirements.txt &&\
  ln -s /opt/faze/faze /usr/local/bin/faze

# Install GoBuster
WORKDIR /usr/local/bin
RUN VER=$(curl --silent "https://api.github.com/repos/OJ/gobuster/releases/latest" |\
  grep -Po '"tag_name": "\K.*?(?=")') &&\
  curl --silent -O -L "https://github.com/OJ/gobuster/releases/download/$VER/gobuster-linux-amd64.7z" &&\
  7z e gobuster-linux-amd64.7z > /dev/null &&\
  rm -r gobuster-linux-amd64* &&\
  chmod a+x gobuster

# Install Nikto
WORKDIR /opt
RUN git clone --depth 1 https://github.com/sullo/nikto &&\
  ln -s /opt/nikto/program/nikto.pl /usr/local/bin/nikto

# Install recon-ng
WORKDIR /opt
RUN git clone --depth 1 https://LaNMaSteR53@bitbucket.org/LaNMaSteR53/recon-ng.git &&\
  pip install -q -r recon-ng/REQUIREMENTS &&\
  ln -s /opt/recon-ng/recon-ng /usr/local/bin/recon-ng
WORKDIR /opt/recon-ng

# Install Seclists
WORKDIR /opt
RUN curl --silent -O -L "https://github.com/danielmiessler/SecLists/archive/master.tar.gz" &&\
  tar xf master.tar.gz --exclude="Payloads/File-Names/max-length/*" &&\
  mv SecLists-master SecLists &&\
  rm master.tar.gz

# Install Sublist3r
WORKDIR /opt
RUN git clone --depth 1 https://github.com/aboul3la/Sublist3r.git &&\
  pip install -q -r Sublist3r/requirements.txt &&\
  ln -s /opt/Sublist3r/sublist3r.py /usr/local/bin/sublist3r.py
WORKDIR /opt/Sublist3r

# Temp Command
WORKDIR /data/work
ENTRYPOINT ["python3", "-u", "/opt/faze/faze"]
