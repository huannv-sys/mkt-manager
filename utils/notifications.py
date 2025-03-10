"""
Module quản lý thông báo
"""

import os
import json
import logging
import smtplib
import requests
import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

# Khởi tạo logger
logger = logging.getLogger(__name__)

# Khởi tạo Twilio client
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')

twilio_client = None
if TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN:
    twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

def send_sms_notification(phone_number, message):
    """Gửi thông báo qua SMS sử dụng Twilio"""
    if not twilio_client:
        logger.error("Chưa cấu hình Twilio")
        return False
    
    try:
        message = twilio_client.messages.create(
            body=message,
            from_=TWILIO_PHONE_NUMBER,
            to=phone_number
        )
        logger.info(f"Đã gửi SMS đến {phone_number}: {message.sid}")
        return True
    except TwilioRestException as e:
        logger.error(f"Lỗi khi gửi SMS: {str(e)}")
        return False

def send_email_notification(subject, message, recipients=None):
    """Gửi thông báo qua email"""
    if not recipients:
        recipients = [os.getenv('DEFAULT_ADMIN_EMAIL')]
    
    try:
        # Cấu hình SMTP
        smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        smtp_port = int(os.getenv('SMTP_PORT', 587))
        smtp_username = os.getenv('SMTP_USERNAME')
        smtp_password = os.getenv('SMTP_PASSWORD')
        
        if not all([smtp_server, smtp_port, smtp_username, smtp_password]):
            logger.error("Thiếu thông tin cấu hình SMTP")
            return False
        
        # Tạo email
        msg = MIMEMultipart()
        msg['Subject'] = subject
        msg['From'] = smtp_username
        msg['To'] = ', '.join(recipients)
        msg.attach(MIMEText(message, 'html'))
        
        # Gửi email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.send_message(msg)
        
        logger.info(f"Đã gửi email đến {recipients}")
        return True
    except Exception as e:
        logger.error(f"Lỗi khi gửi email: {str(e)}")
        return False

def send_slack_notification(title, message):
    """Gửi thông báo qua Slack webhook"""
    slack_webhook_url = os.getenv('SLACK_WEBHOOK_URL')
    if not slack_webhook_url:
        logger.error("Chưa cấu hình Slack webhook")
        return False
    
    try:
        payload = {
            "text": f"*{title}*\n{message}",
            "mrkdwn": True
        }
        response = requests.post(slack_webhook_url, json=payload)
        response.raise_for_status()
        
        logger.info("Đã gửi thông báo đến Slack")
        return True
    except requests.exceptions.RequestException as e:
        logger.error(f"Lỗi khi gửi thông báo đến Slack: {str(e)}")
        return False

def send_system_notification(title, message, level='info', notify_email=True, notify_slack=True, notify_sms=False, phone_numbers=None):
    """Gửi thông báo hệ thống"""
    # Log thông báo
    log_func = getattr(logger, level, logger.info)
    log_func(f"{title}: {message}")
    
    # Tạo nội dung thông báo
    notification_text = f"{title}\n\n{message}\n\nThời gian: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    # Gửi thông báo qua các kênh
    results = []
    
    if notify_email:
        email_success = send_email_notification(title, notification_text)
        results.append(('email', email_success))
    
    if notify_slack:
        slack_success = send_slack_notification(title, message)
        results.append(('slack', slack_success))
    
    if notify_sms and phone_numbers:
        for phone in phone_numbers:
            sms_success = send_sms_notification(phone, notification_text)
            results.append(('sms', sms_success))
    
    return all(success for _, success in results)

def notify_device_connection_status(device_name, status, ip_address=None):
    """Thông báo về trạng thái kết nối thiết bị"""
    title = f"Trạng thái thiết bị: {device_name}"
    message = f"Thiết bị {device_name}"
    if ip_address:
        message += f" ({ip_address})"
    message += f" hiện đang {status}"
    
    level = 'warning' if status.lower() == 'offline' else 'info'
    notify_sms = status.lower() == 'offline'  # Chỉ gửi SMS khi thiết bị offline
    
    return send_system_notification(
        title=title,
        message=message,
        level=level,
        notify_sms=notify_sms
    )

def notify_high_resource_usage(device_name, resource_type, value, threshold):
    """Thông báo về việc sử dụng tài nguyên cao"""
    title = f"Cảnh báo tài nguyên: {device_name}"
    message = f"Thiết bị {device_name} có mức sử dụng {resource_type} cao: {value}% (ngưỡng: {threshold}%)"
    
    return send_system_notification(
        title=title,
        message=message,
        level='warning',
        notify_sms=True
    )

def notify_new_client_connected(client_name, client_ip, client_mac, interface):
    """Thông báo về việc có client mới kết nối"""
    title = "Client mới kết nối"
    message = f"""
    Phát hiện client mới:
    - Tên: {client_name}
    - IP: {client_ip}
    - MAC: {client_mac}
    - Interface: {interface}
    """
    
    return send_system_notification(
        title=title,
        message=message,
        level='info'
    )

def notify_firewall_block(ip_address, reason=None):
    """Thông báo về việc firewall chặn kết nối"""
    title = "Cảnh báo Firewall"
    message = f"Firewall đã chặn IP {ip_address}"
    if reason:
        message += f"\nLý do: {reason}"
    
    return send_system_notification(
        title=title,
        message=message,
        level='warning',
        notify_sms=True
    )