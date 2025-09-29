# Deception-Network-Defense

Lab demonstrating **proactive deception** (web honeypot in DMZ), **reactive detection** (Suricata IDS on LAN), and **centralized analysis** (Wazuh SIEM). The design follows a segmented **WAN-DMZ-LAN** topology with a virtual gateway, NAT, and restrictive firewall policies.

> This repository mirrors the lab architecture implemented in the accompanying report and demo. It focuses on a Dockerized **StrutsHoneypot** on Ubuntu (DMZ), Suricata in IDS mode (LAN), and Wazuh (OVA) for log collection, analysis, and ATT&CK-aligned investigation.

## Architecture Overview

```
[WAN (VMNet10, NAT)]  ─┐
                       │  DNAT tcp/80 → 192.168.229.128:8080 (DMZ honeypot)
[Gateway Host: Ubuntu]─┼──────────────────────────────┐
  - ens37: WAN (e.g., 192.168.192.133)                │
  - ens38: DMZ 192.168.229.0/24  (honeypot)           │
  - ens33: LAN 192.168.32.0/24   (Suricata, Wazuh)    │
  - docker0: 172.17.0.0/16 (container bridge)         │
  - IPv4 forwarding enabled                           │
                                                      ▼
[DMZ (VMNet1)]  → StrutsHoneypot (Docker) → logs → Wazuh (via agent)
[LAN (VMNet0)]  → Suricata (IDS mode, EVE JSON) → Wazuh (ingest & dashboards)
               → Local web server 
               → AI module 
```

## Network Topology

The lab uses a three-zone design (**WAN – DMZ – LAN**) with a virtual gateway providing strict inter-zone filtering.

![Network topology](img/Network-Topology.png)

- **Honeypot:** StrutsHoneypot container bound to `192.168.229.128:8080` in DMZ.
- **External access:** DNAT from `WAN:tcp/80` to DMZ:8080.
- **Wazuh:** Official OVA (manager/indexer/dashboards) on LAN.
- **Suricata:** IDS mode on LAN interface with EVE JSON enabled.
- **Isolation:** Strict inter-zone firewall. Only required flows permitted.

## Quick Start

### 1) **Honeypot (DMZ)**
   - Deploy the web honeypot and expose `DMZ:8080`.
   - See: [`honeypot/README.md`](honeypot/README.md)  
   - One-liner:
     
     ```
     cd honeypot && make all
     ```
### 2) **Wazuh (SIEM on LAN)**
   - Import the **Wazuh OVA**, set the LAN IP, then enroll agents.
   - See: [`wazuh/README.md`](wazuh/README.md)

### 3) **Suricata (IDS on LAN)**
   - Install Suricata in **IDS mode**, enable **EVE JSON**, and point logs to Wazuh.
   - See: [`suricata/README.md`](suricata/README.md)

### 4) **AI Agent**
   - Local DistilBERT classifier watches Suricata alerts and (optionally) blocks IPs.
   - See: [`AI-Agent/README.md`](AI-Agent/README.md)

### 5) **Vulnerable Web App**
   - For local vulnerable web server, follow the minimal pointers.
   - See: [`vulnerable-web-app/README.md`](vulnerable-web-app/README.md)

---

## Configure Firewall

```
# Reset rules
sudo iptables -F
sudo iptables -t nat -F
sudo iptables -t mangle -F

# Default policies
sudo iptables -P INPUT DROP
sudo iptables -P FORWARD DROP
sudo iptables -P OUTPUT ACCEPT

# Allow loopback & established connections
sudo iptables -A INPUT -i lo -j ACCEPT
sudo iptables -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
sudo iptables -A FORWARD -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT

# Allow SSH on gateway (LAN only)
sudo iptables -A INPUT -i ens33 -p tcp --dport 22 -j ACCEPT

# DNAT: forward WAN:80 to honeypot (DMZ:8080)
sudo iptables -t nat -A PREROUTING -i ens37 -p tcp --dport 80 \
  -j DNAT --to-destination 192.168.229.128:8080

# Allow forwarded WAN → DMZ traffic to honeypot
sudo iptables -A FORWARD -i ens37 -o ens38 -p tcp -d 192.168.229.128 --dport 8080 \
  -m conntrack --ctstate NEW,ESTABLISHED -j ACCEPT

# Wazuh agent traffic from LAN
sudo iptables -A INPUT -i ens33 -p udp --dport 1514 -j ACCEPT
sudo iptables -A INPUT -i ens33 -p tcp --dport 1515 -j ACCEPT
sudo iptables -A INPUT -i ens33 -p tcp --dport 5601 -j ACCEPT

# NAT masquerade for outbound traffic via WAN
sudo iptables -t nat -A POSTROUTING -o ens37 -j MASQUERADE

# Enable IP forwarding (temporary until reboot)
echo 1 | sudo tee /proc/sys/net/ipv4/ip_forward
```

This configuration does the following:

  - Drops everything by default (INPUT, FORWARD).
  - Allows SSH from LAN, Wazuh traffic, and DNAT from WAN → Honeypot.
  - Applies NAT masquerading for outbound DMZ/WAN traffic.

## Generate traffic from WAN attacker (Kali)
- Recon: `nikto -h http://<WAN_ip>/`
- Exploit demo: Use the StrutsHoneypot test scripts `./test-struts2.py http://<WAN_ip>`.

## Investigate in Wazuh
- Dashboards: alerts, HTTP activity, and archive indices for full log search.
- Build DQL/Kibana queries around honeypot fields to isolate patterns.

## Safety & Scope

- This is a **interactive lab**. Keep it isolated.
- The honeypot intentionally attracts hostile scans/traffic—never expose without proper containment.

## Demo Video

The demonstration video for this lab can be accessed [here](https://www.youtube.com/watch?v=zQeACGav-rw).

## License

MIT
