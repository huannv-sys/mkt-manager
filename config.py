"""
Tập tin cấu hình cho MikroTik MSC
Chứa các hằng số và cấu hình toàn cục cho hệ thống
"""

import os
from dotenv import load_dotenv

# Tải biến môi trường từ file .env nếu có
load_dotenv()

# Cấu hình cơ bản
DEBUG = True
SECRET_KEY = os.getenv('SECRET_KEY', 'mikrotik-msc-secret-key')
SESSION_TYPE = 'filesystem'

# Thư mục dự án
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Cấu hình MongoDB
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
MONGO_DB = os.getenv('MONGO_DB', 'mikrotik_msc')

# Cấu hình JWT
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'mikrotik-msc-jwt-secret')
JWT_ACCESS_TOKEN_EXPIRES = 86400  # 24 giờ

# Cấu hình backup
BACKUP_DIR = os.path.join(BASE_DIR, 'backups')

# Cấu hình MikroTik API
MIKROTIK_API_PORT = 8728  # Port mặc định của MikroTik API
MIKROTIK_API_SSL_PORT = 8729  # Port SSL của MikroTik API

# Thời gian cập nhật dữ liệu (giây)
REFRESH_INTERVAL = 5

# Cấu hình thông báo
ENABLE_EMAIL_NOTIFICATIONS = os.getenv('ENABLE_EMAIL_NOTIFICATIONS', 'False').lower() == 'true'
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
SMTP_USERNAME = os.getenv('SMTP_USERNAME', '')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')
NOTIFICATION_EMAIL = os.getenv('NOTIFICATION_EMAIL', '')

# Cấu hình Slack Webhook
ENABLE_SLACK_NOTIFICATIONS = os.getenv('ENABLE_SLACK_NOTIFICATIONS', 'False').lower() == 'true'
SLACK_WEBHOOK_URL = os.getenv('SLACK_WEBHOOK_URL', '')

# Cấu hình logging
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = os.path.join(BASE_DIR, 'logs', 'mikrotik_msc.log')
FIREWALL_LOG_FILE = os.path.join(BASE_DIR, 'logs', 'firewall.log')
SYSTEM_LOG_FILE = os.path.join(BASE_DIR, 'logs', 'system.log')

# Đảm bảo thư mục logs tồn tại
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)