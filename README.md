# mail2telegram

IMAP to Telegram forwarder. Monitors email inbox and forwards messages from specified senders to Telegram.

## Requirements

- Python 3.6+
- requests

## Install

```bash
pip install requests
```

## Configuration

Set environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| IMAP_SERVER | IMAP server address | mail.privateemail.com |
| IMAP_PORT | IMAP port | 993 |
| EMAIL_USER | Email username | required |
| EMAIL_PASS | Email password | required |
| TELEGRAM_TOKEN | Telegram bot token | required |
| TELEGRAM_CHAT_ID | Telegram chat/channel ID | required |
| FROM_FILTERS | Comma-separated sender emails to monitor | required |
| CHECK_INTERVAL | Check interval in seconds | 300 |

## Usage

```bash
export EMAIL_USER="your@email.com"
export EMAIL_PASS="yourpassword"
export TELEGRAM_TOKEN="123456:ABC-DEF"
export TELEGRAM_CHAT_ID="-100123456789"
export FROM_FILTERS="alerts@example.com,notifications@example.com"

python3 mail2telegram.py
```

## Systemd Service

Create :

```ini
[Unit]
Description=mail2telegram
After=network-online.target

[Service]
Type=simple
User=youruser
Environment="EMAIL_USER=your@email.com"
Environment="EMAIL_PASS=yourpassword"
Environment="TELEGRAM_TOKEN=123456:ABC-DEF"
Environment="TELEGRAM_CHAT_ID=-100123456789"
Environment="FROM_FILTERS=alerts@example.com"
ExecStart=/usr/bin/python3 /path/to/mail2telegram.py
Restart=always
RestartSec=30

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl enable --now mail2telegram
```

## License

MIT
