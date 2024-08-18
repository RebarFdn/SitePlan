echo "Starting Site Servers"
source vnv/bin/activate
pm2 stop Site
nodemon siteplan/application.py
