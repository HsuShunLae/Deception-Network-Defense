# bWAPP (buggy Web APP)

Please **download bWAPP from the official sources** (http://www.itsecgames.com/download.htm) and follow their instructions.

## Official downloads
- bWAPP (source / ZIP): https://sourceforge.net/projects/bwapp/files/bWAPP/
- bee-box (prebuilt VM for bWAPP): https://sourceforge.net/projects/bwapp/files/bee-box/

---

## SIEM/IDS Integration

Suricata: point traffic at monitored interface. Enable HTTP/TLS/DNS EVE outputs.

Wazuh Agent (on the host): add to `/var/ossec/etc/ossec.conf`:

```xml
<localfile>
  <log_format>apache</log_format>
  <location>/var/log/apache2/bwapp_access.log</location>
</localfile>
<localfile>
  <log_format>apache</log_format>
  <location>/var/log/apache2/bwapp_error.log</location>
</localfile>
```

Restart agent: `sudo systemctl restart wazuh-agent`

---
