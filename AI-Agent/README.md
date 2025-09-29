# AI Agent - Suricata Log Classifier & IP Blocker

An offline **DistilBERT** pipeline analyzes Suricata alerts and decides whether to **log** or **block** the source IP.
Designed to run as a **systemd** service, with results forwarded to **Wazuh**.

## What it does

1. **Tails Suricata alerts** (e.g., `fast.log`) in near-real time.
2. Uses a **local** Transformers model to classify alert messages (no internet).
3. If an alert is “malicious” by policy, the agent **blocks** the IP (iptables by default).
4. Writes actions to `/var/log/ai_blocked.log` for audit and SIEM ingestion.

---

## 1) Prerequisites

* Ubuntu 22.04+
* Python 3.10+
* Suricata producing alerts (e.g., `/var/log/suricata/fast.log` or EVE -> a text channel)
* Root/sudo privileges (for firewall changes)

Python packages (CPU only):

```
sudo apt update && sudo apt install -y python3-pip
pip3 install --upgrade pip
pip3 install "transformers>=4.40" torch --index-url https://download.pytorch.org/whl/cpu
```

---

## 2) Offline model layout

Place local model under **`/opt/models/distilbert/`** :

```
/opt/models/distilbert/
├─ config.json
├─ model.safetensors
├─ tokenizer.json
├─ tokenizer_config.json
├─ special_tokens_map.json
└─ vocab.txt
```

> The agent loads this folder with `local_files_only=True` and sets `TRANSFORMERS_OFFLINE=1`.

---

## 3) Python agent

Download the script [`ai_suricata_blocker.py`](AI-Agent/ai_suricata_blocker.py) into `/usr/local/bin/`:
```
sudo cp ai_suricata_blocker.py /usr/local/bin/ai_suricata_blocker.py
```

Make it executable:

```
sudo chmod +x /usr/local/bin/ai_suricata_blocker.py
```

---

## 4) Systemd service

Download the service file [`ai_suricata_blocker.service`](AI-Agent/ai_suricata_blocker.service) into /etc/systemd/system/:

```
sudo cp ai_suricata_blocker.service /etc/systemd/system/ai_suricata_blocker.service
```

Enable & start:

```
sudo systemctl daemon-reload
sudo systemctl enable ai_suricata_blocker.service
sudo systemctl start ai_suricata_blocker.service
sudo systemctl status ai_suricata_blocker.service
```

---

## 5) Verify

Tail the agent log (matches your screenshot format):

```
sudo tail -f /var/log/ai_blocked.log
```

Typical line:

```
2025-01-01T12:34:56Z | BLOCKED IP: 192.0.2.13 | Alert: Nmap Scripting Engine User-Agent Detected | AI: NEGATIVE (0.99)
```

---

## 6) Send AI logs to Wazuh

Add to your Wazuh **agent** config (`/var/ossec/etc/ossec.conf`):

```xml
<localfile>
  <log_format>syslog</log_format>
  <location>/var/log/ai_blocked.log</location>
</localfile>
```

Restart the agent:

```
sudo systemctl restart wazuh-agent
```

Now AI actions can be seen in the Wazuh dashboard (search index for `ai_blocked.log` entries).

---

## 7) Notes & Policy

* **Blocking backend:** uses `iptables`. If prefer **nftables**, adjust `BLOCK_CMD`:

  ```python
  BLOCK_CMD = ["nft", "add", "rule", "inet", "filter", "input", "ip", "saddr"]
  # and append: ip, "drop"
  ```
* **Policy threshold:** change `0.85` to be more/less aggressive.
* **Direction logic:** by default, treats the **source IP** as attacker, and double-checks if the **destination** equals protected server (`WEB_SERVER_IP`).
* **Model:** any local HF-compatible sequence classifier will work if dropped into `/opt/models/<name>` and path updated.

---


## 8) Safety

Run this in a **lab** or controlled environment first. Automated blocking can disrupt traffic if mis-configured. Always keep a **console** access path to undo rules (`iptables -F`) if necessary.

---
