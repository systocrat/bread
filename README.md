# Bread
Bread is a reverse proxy written using the Twisted networking framework in Python for the express purpose of supporting multiple services on one single port.

Purposes for this include supporting multiple game servers on one port, obscuring the normal SSH port by placing it on something VERY nonstandard (such as port 80 or 443), supporting a web server and an OpenVPN instance on one machine.
There are many possibilities that the bread proxy can be used for.