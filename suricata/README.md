# Suricata IDS Deployment

This guide explains how to install and configure **Suricata** in IDS mode.  
It captures traffic on the LAN interface, generates alerts in **EVE JSON format**, and forwards them for centralized analysis (e.g., Wazuh).

---

## 1. Prerequisites
- Ubuntu 22.04 (or similar Linux distribution)
- Root/sudo privileges
- Network interface in **promiscuous mode** (SPAN, TAP, or AF_PACKET)
- Internet access to fetch rules and packages

---

## 2. Installation

Update system and install Suricata:
```bash
sudo apt update
sudo apt install -y suricata
````

Verify installation:

```bash
suricata --build-info
```

---

## 3. Configuration

Suricata config file: `/etc/suricata/suricata.yaml`

### a) Set default interface

Find LAN interface (e.g., `ens33`):

```
ip a
```

Edit `suricata.yaml`:

```yaml
af-packet:
  - interface: ens33 <should be inteface to monitor>
    cluster-type: cluster_flow
    cluster-id: 99
    defrag: yes
```

### b) Enable EVE JSON output

In `suricata.yaml`, ensure:

```yaml
outputs:
  - eve-log:
      enabled: yes
      filetype: regular
      filename: /var/log/suricata/eve.json
      community-id: yes
      types:
        - alert
        - dns
        - http
        - tls
        - flow
        - stats
```
### c) Update rules:

```
sudo suricata-update
sudo systemctl restart suricata
```

---

## 4. Running Suricata

### Test configuration

```
sudo suricata -T -c /etc/suricata/suricata.yaml -i ens33
```

### Start Suricata (IDS mode)

```
sudo systemctl enable suricata
sudo systemctl start suricata
```

Check status:

```
sudo systemctl status suricata
```

---

## 5. Logs & Verification

* Alerts and logs: `/var/log/suricata/eve.json`
* Tail logs in real-time:

```
sudo tail -f /var/log/suricata/eve.json
```

Generate test traffic with **nmap** or **nikto** from another host:

```
nmap -sS <target-ip>
nikto -h http://<target-ip>
```

Suricata should generate alerts in EVE JSON.

---

## 6. Integration with Wazuh 

To forward Suricata logs to **Wazuh**:

1. Edit Wazuh agent config (`ossec.conf`) to monitor `/var/log/suricata/eve.json`.
2. Restart the Wazuh agent:

   ```
   sudo systemctl restart wazuh-agent
   ```
3. Alerts will appear in the **Wazuh dashboard**.

---

