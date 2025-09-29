# Struts Honeypot Deployment

This guide explains how to set up and run the **Struts Honeypot** inside an Ubuntu server using Docker.  
The honeypot is exposed at **192.168.229.128:8080** and logs attacker interactions for later analysis.

---

## 1. Prerequisites
- Ubuntu 22.04 (or similar Linux distribution)
- Root/sudo privileges
- Internet access to pull Docker images
- Don't forget to change your IP when implementing honeypot

---

## 2. Installation Steps

### Step 1. Install Docker
```
sudo apt update
sudo apt install -y docker.io docker-compose
```

Verify installation:
```bash
docker --version
```

---

### Step 2. Clone Honeypot Repository
```
git clone https://github.com/Cymmetria/StrutsHoneypot.git
cd StrutsHoneypot
```

---

### Step 3. Build the Docker Image
```
sudo docker build -t struts_honeypot strutspot_docker/
```

This will download dependencies and build the honeypot container image.

---

### Step 4. Run the Honeypot
```
sudo docker run -d --name honeypot -p 192.168.229.128:8080:80 -v /var/log/struts-honeypot:/var/log/apache2 struts_honeypot
```

- Container name: **honeypot**  
- Host binding: `192.168.229.128:8080`  
- Inside container: `:80`
- Log Path: `/var/log/struts-honeypot`

---

### Step 5. Verify Deployment
Open a browser and visit:

```
http://192.168.229.128:8080
```

You should see the **Uploader web interface** (fake vulnerable app).

---

## 3. Managing the Honeypot

- Stop container:
```
sudo docker stop honeypot
```

- Start container:
```
sudo docker start honeypot
```

- Remove container:
```
sudo docker rm -f honeypot
```

---

## 4. Automation
Instead of running all commands manually, you can simply use the provided **Makefile**:

```
make all
```

This will install dependencies, build the honeypot image, and run the container in one click.

---
