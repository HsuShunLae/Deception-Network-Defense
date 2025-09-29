import time
import subprocess
from datetime import datetime
import os
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification

# === Offline Setup ===
os.environ["TRANSFORMERS_OFFLINE"] = "1"

MODEL_PATH = "/opt/models/distilbert"
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, local_files_only=True)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH, local_files_only=True)
ai_classifier = pipeline("sentiment-analysis", model=model, tokenizer=tokenizer)

# === Log Paths ===
FAST_LOG_PATH = "/var/log/suricata/fast.log"
AI_LOG_PATH = "/var/log/ai_blocked.log"
WEB_SERVER_IP = "192.168.32.140"
blocked_ips = set()

def block_ip(ip):
    if ip not in blocked_ips:
        print(f"[!] Blocking IP: {ip}")
        subprocess.run(["sudo", "iptables", "-I", "INPUT", "1", "-s", ip, "-j", "DROP"])
        blocked_ips.add(ip)

def write_log(ip, message, result):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{now}] BLOCKED IP: {ip} | Alert: {message} | AI: {result['label']} ({result['score']:.2f})\n"
    with open(AI_LOG_PATH, "a") as f:
        f.write(log_line)

def follow(file):
    file.seek(0, 2)
    while True:
        line = file.readline()
        if not line:
            time.sleep(0.1)
            continue
        yield line

with open(FAST_LOG_PATH, "r") as log_file:
    log_lines = follow(log_file)
    for line in log_lines:
        try:
            parts = line.strip().split()
            if len(parts) < 8 or "->" not in parts:
                continue

            message_start = line.find("]") + 2
            message_end = line.rfind("[**]")
            message = line[message_start:message_end].strip()

            src_part = parts[-3]  
            dst_part = parts[-1]  

            src_ip = src_part.split(":")[0]
            dst_ip = dst_part.split(":")[0]

            # Identify the IP that is NOT the web server
            suspicious_ip = dst_ip if src_ip == WEB_SERVER_IP else src_ip

            # Skip if already blocked
            if suspicious_ip in blocked_ips:
                continue


            result = ai_classifier(message)[0]
            if result['label'] == "NEGATIVE" and result['score'] > 0.85:
                print(f"[AI] Malicious Alert: {message} (score: {result['score']})")
                block_ip(suspicious_ip)
                write_log(suspicious_ip, message, result)

        except Exception:
            continue
