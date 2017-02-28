# FAZE

##### next thing you know we'll be joining Optic

---

### WHAT IS FAZE

A modular pentesting tool with next to no documentation (so far). In it's inception faze has not been designed for hardcore red team activities. In the future that may change. Until then one can invoke the plethora of nse scripts available. 

---

### INSTALLATION

Faze is tested on Kali Linux and Mac OS 10.12.x, but _should_ work on OS/Distro if you install the necessary packages.

Clone faze to a location of your choosing and install the required python modules via pip.

Install [httpscreenshot](https://github.com/breenmachine/httpscreenshot)

```shell
git clone https://github.com/breenmachine/httpscreenshot
cd httpscreenshot
sudo ./install-dependencies.sh
cd ..
git clone https://github.com/KhasMek/faze.git
cd faze
pip3 install -r requirements.txt
```

Clone it wherever you want, /opt may be a good idea. Alternatively, install it to a location in your $PATH, or just make an alias in your rc file. Be Cartman.

---

### USAGE

For this section we will assume that faze is in your $PATH. If you haven't done this, just substitute `/path/to/your/faze` for `faze`.


#### To Run

Add your targets file to the location (or whatever directory you have defined in faze.cfg) and confirm scope. Then execute
```
faze
```

It's just that easy, on the surface. This will run faze in your pwd, created the default directories and files. The real power comes from customizing the config file on a by project basis. Any values set in the local (pwd) config file will overwrite default set values, other will be retained. Keep that in mind. **Note:** Only disable the nmap module if you're resuming a project in which the nmap scans have already completed.

##### EXAMPLE OUTPUT

```bash
.
├── faze.cfg
├── faze.log
├── notes.md
├── Phase-1
│   ├── nmap-sS-sV_script_vulscan_vulscan_nse-192.168.1.213.xml
│   ├── nmap-sV-sF-192.168.1.213.xml
│   ├── nmap-sV-sn-192.168.1.213.xml
│   └── nmap-sV-sT-sU-192.168.1.213.xml
├── Phase-2
│   ├── httpscreenshot
│   │   ├── ghostdriver.log
│   │   ├── http%3A%2F%2F192.168.1.213%3A80.html
│   │   ├── http%3A%2F%2F192.168.1.213%3A80.png
│   │   ├── http%3A%2F%2F192.168.1.213%3A8180.html
│   │   └── http%3A%2F%2F192.168.1.213%3A8180.png
│   ├── MetaSploitable-2.0.nessus
│   ├── nikto
│   │   └── nikto-8180-192.168.1.213.txt
│   └── tcp_port_results.md
├── port_targets.csv
├── Reporting
└── targets

5 directories, 17 files
```
###### *Example output is from [Metasploitable 2.0](https://sourceforge.net/projects/metasploitable/files/Metasploitable2/)*

---

### MODULES
- nmap
- httpscreenshot
- nikto
- nessus

---

### TODO

- [ ] **TONS** of exception handling. Please file Issue Reports to help me find all the areas I need to add it.
- [ ] Remove dependency for libnmap-parser and use python-nmap across the board
- [ ] Upload to Elastic
- [ ] Slack integration
- [ ] Clean up variable declaration/calling (especially in the nmap module)
- [ ] Scheduling
- [ ] ...
