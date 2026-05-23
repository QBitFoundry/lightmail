<p align=center><img alt="LightMail Logo" src=".github/assets/Logo.png" width=200></p>

<h1 align=center>LightMail</h1>

<!-- # Light Mail -->

A **lightweight**, high-performance local mail server with built-in **SMTP** support and a modern web-based interface. Designed for development, testing, and self-hosted environments, it runs efficiently with in-memory email storage by default for minimal resource usage. Persistent email storage can be enabled anytime from the web app with a simple toggle. Supports Macvlan networking for advanced local network setups and can be fully managed directly from the browser.

---
## Docker
### Run
```
docker run -d \
 --name lightmail-container \
  -p 8000:8000 \
  -p 2525:2525 \
  -e HOST_IP=0.0.0.0 \
  -e HOST_PORT=8000 \
  -e SMTP_PORT=2525 \
   lightmail
```

---
## System Architecture
### Stateless (**Non-Persistent**) Architecture
<p align=center><img alt="workflow" src=".github/assets/uwsgi flow(non-persistence).svg"></p>


### **Persistent** Storage Architecture
<p align=center><img alt="workflow" src=".github/assets/uwsgi flow(persistence).svg"></p>

---