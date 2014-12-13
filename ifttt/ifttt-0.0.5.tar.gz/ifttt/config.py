import os

IFTTT_USERNAME = os.getenv('IFTTT_USERNAME', 'brian@newslynx.org')
IFTTT_PASSWORD = os.getenv('IFTTT_PASSWORD','qp7orjmKEfTMszZc9rizWhLFgyaRtQ')
IFTTT_IMAP_SERVER = os.getenv('IFTTT_IMAP_SERVER', 'mail.gandi.net')
IFTTT_SMTP_SERVER  = os.getenv('IFTTT_SMTP_SERVER', IFTTT_IMAP_SERVER)
IFTTT_IMAP_PORT = os.getenv('IFTTT_IMAP_PORT', 993)
IFTTT_SMTP_PORT = os.getenv('IFTTT_SMTP_PORT', 587)