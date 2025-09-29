# Wazuh SIEM Deployment

This guide explains how to install and configure **Wazuh** as the central SIEM for log collection, threat detection, and correlation.  
It integrates with **Suricata IDS** and honeypots for a complete security monitoring stack.

---

## 1. Prerequisites
- Ubuntu 22.04 (fresh installation recommended)
- Root/sudo privileges
- Minimum resources: 4 vCPU, 8 GB RAM, 50 GB disk
- Open ports:
  - `1514/udp` – Wazuh agent → manager
  - `1515/tcp` – Agent enrollment
  - `9200/tcp` – Indexer (Elasticsearch-like)
  - `55000/tcp` – Wazuh API

---

## 2. Importing the OVA

1. Download the latest **Wazuh OVA** from:  
   [https://packages.wazuh.com/4.x/vm/wazuh-4.13.1.ova](https://packages.wazuh.com/4.x/vm/wazuh-4.13.1.ova)
   
2. In VirtualBox/VMware:  
   - Import the `.ova` file.  
   - Assign network adapters (LAN interface).  
   - Start the VM.

3. Default VM credentials:  
   - **Username:** `wazuh-user`  
   - **Password:** `wazuh`  

---

## 3. Accessing the Dashboard

- Once booted, the VM will display the assigned IP address.  
- Access the dashboard at:

```
URL: https://<wazuh_server_ip>
user: admin
password: admin
```

You can find <wazuh_server_ip> by typing the following command in the VM:
```
ip a
```

---

## 4. Wazuh Agent Setup

On monitored host:

### Step 1. Install agent

1. Install the GPG key:
```
curl -s https://packages.wazuh.com/key/GPG-KEY-WAZUH | gpg --no-default-keyring --keyring gnupg-ring:/usr/share/keyrings/wazuh.gpg --import && chmod 644 /usr/share/keyrings/wazuh.gpg
```
2. Add the repository:
```
echo "deb [signed-by=/usr/share/keyrings/wazuh.gpg] https://packages.wazuh.com/4.x/apt/ stable main" | tee -a /etc/apt/sources.list.d/wazuh.list
```
3. Update the package information:
```
sudo apt-get update
```
4. Deploy Wazuh Agent
```
WAZUH_MANAGER="192.168.229.130" apt-get install wazuh-agent # Wazuh manager IP
```

### Step 2. Configure agent

Edit `/var/ossec/etc/ossec.conf`:

```xml
<client>
  <server>
    <address>192.168.229.130</address>   <!-- Wazuh manager IP -->
    <port>1514</port>
    <protocol>udp</protocol>
  </server>
</client>
```

For Local Web Server logs:

```xml
<localfile>
  <log_format>apache</log_format>
  <location>/var/log/apache2/access.log</location>
</localfile>

<localfile>
  <log_format>apache</log_format>
  <location>/var/log/apache2/error.log</location>
</localfile>
```

For Suricata log ingestion, add:

```xml
<localfile>
  <log_format>json</log_format>
  <location>/var/log/suricata/eve.json</location>
</localfile>
```

For Honeypot logs:

```xml
<localfile>
  <log_format>apache</log_format>
  <location>/var/log/struts-honeypot/access.log</location>
</localfile>

<localfile>
  <log_format>apache</log_format>
  <location>/var/log/struts-honeypot/error.log</location>
</localfile>
```

### Step 3. Start agent

```
sudo systemctl enable wazuh-agent
sudo systemctl start wazuh-agent
```

---

## 5. Verify Integration

1. In the **Wazuh Dashboard**, go to **Agents** → confirm that the new host appears and is active.
2. Trigger test logs:

   ```
   logger "Test Wazuh log event"
   ```

   Event should appear in the dashboard.
3. Run **nmap/nikto** scans against the honeypot/Suricata host → Suricata alerts should be visible in Wazuh.

---

## 6. Managing Wazuh

* Restart services:

```
sudo systemctl restart wazuh-manager
sudo systemctl restart wazuh-agent
```

* View agent logs:

```
sudo tail -f /var/ossec/logs/ossec.log
```

* View manager logs:

```
sudo tail -f /var/ossec/logs/ossec.log
```

---

## 7. Notes

* This is a **lab deployment**.
* Regularly update rules:

```
sudo /var/ossec/bin/update_ruleset
```

---
