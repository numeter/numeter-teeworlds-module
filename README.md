numeter-teeworlds-module
========================

Teeworlds module for Numeter poller.

Installation
--------------

You need to have logtail :

    apt-get install logtail

After than just clone the repo and launch the setup.py :

    git clone https://github.com/shaftmx/numeter-teeworlds-module/
    cd numeter-teeworlds-module
    python setup.py install

Configuration
---------------

Edit the poller configuration file :

    vim /etc/numeter/numeter_poller.cfg

Add your new module in numeter poller module list **teeworldsModule** :

    modules = myMuninModule|teeworldsModule

Add the configuration section for this module :

    [teeworldsModule]
    logfile = /myserverpath/teeworlds.log

You can change the path for **logtail** default /usr/sbin/logtail :

    logtail = /usr/sbin/logtail
