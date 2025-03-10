"""
Module quản lý thông báo
"""

import os
import smtplib
import requests
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import config

# Thiết lập logger
logger = logging.getLogger('notifications')

def send_email_notification(subject, message, recipients=None):
    """Gửi thông báo qua email"""
    if not config.ENABLE_EMAIL_NOTIFICATIONS:
        logger.info("Thông báo email bị tắt trong cấu hình")
        return False
    
    if not recipients:
        recipients = [config.NOTIFICATION_EMAIL]
    
    # Kiểm tra cấu hình email
    if not config.SMTP_SERVER or not config.SMTP_USERNAME or not config.SMTP_PASSWORD:
        logger.error("Thiếu thông tin cấu hình SMTP")
        return False
    
    try:
        # Tạo message
        msg = MIMEMultipart()
        msg['From'] = config.SMTP_USERNAME
        msg['To'] = ', '.join(recipients)
        msg['Subject'] = f"MikroTik MSC: {subject}"
        
        # Thêm body
        msg.attach(MIMEText(message, 'plain'))
        
        # Kết nối đến SMTP server
        server = smtplib.SMTP(config.SMTP_SERVER, config.SMTP_PORT)
        server.starttls()
        server.login(config.SMTP_USERNAME, config.SMTP_PASSWORD)
        
        # Gửi email
        server.send_message(msg)
        server.quit()
        
        logger.info(f"Đã gửi thông báo email thành công: {subject}")
        return True
    except Exception as e:
        logger.error(f"Lỗi khi gửi thông báo email: {str(e)}")
        return False

def send_slack_notification(title, message):
    """Gửi thông báo qua Slack webhook"""
    if not config.ENABLE_SLACK_NOTIFICATIONS:
        logger.info("Thông báo Slack bị tắt trong cấu hình")
        return False
    
    if not config.SLACK_WEBHOOK_URL:
        logger.error("Thiếu URL webhook Slack")
        return False
    
    try:
        # Chuẩn bị payload
        payload = {
            "text": f"*MikroTik MSC: {title}*\n{message}"
        }
        
        # Gửi request đến webhook
        response = requests.post(config.SLACK_WEBHOOK_URL, json=payload)
        
        # Kiểm tra kết quả
        if response.status_code == 200:
            logger.info(f"Đã gửi thông báo Slack thành công: {title}")
            return True
        else:
            logger.error(f"Lỗi khi gửi thông báo Slack: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        logger.error(f"Lỗi khi gửi thông báo Slack: {str(e)}")
        return False

def send_system_notification(title, message, level='info', notify_email=True, notify_slack=True):
    """Gửi thông báo hệ thống"""
    # Log thông báo
    if level == 'error':
        logger.error(f"{title}: {message}")
    elif level == 'warning':
        logger.warning(f"{title}: {message}")
    else:
        logger.info(f"{title}: {message}")
    
    # Gửi email nếu được yêu cầu
    if notify_email:
        send_email_notification(title, message)
    
    # Gửi Slack nếu được yêu cầu
    if notify_slack:
        send_slack_notification(title, message)
    
    return True

def notify_device_connection_status(device_name, status, ip_address=None):
    """Thông báo về trạng thái kết nối thiết bị"""
    if status:
        title = f"Kết nối thành công đến thiết bị {device_name}"
        message = f"Đã kết nối thành công đến thiết bị MikroTik {device_name}"
        if ip_address:
            message += f" tại địa chỉ {ip_address}"
        level = 'info'
    else:
        title = f"Mất kết nối đến thiết bị {device_name}"
        message = f"Không thể kết nối đến thiết bị MikroTik {device_name}"
        if ip_address:
            message += f" tại địa chỉ {ip_address}"
        level = 'error'
    
    return send_system_notification(title, message, level)

def notify_high_resource_usage(device_name, resource_type, value, threshold):
    """Thông báo về việc sử dụng tài nguyên cao"""
    title = f"Cảnh báo sử dụng {resource_type} cao trên {device_name}"
    message = f"Thiết bị {device_name} có mức sử dụng {resource_type} là {value}%, vượt ngưỡng {threshold}%"
    
    return send_system_notification(title, message, 'warning')

def notify_new_client_connected(client_name, client_ip, client_mac, interface):
    """Thông báo về việc có client mới kết nối"""
    title = f"Client mới kết nối: {client_name}"
    message = f"Client mới đã kết nối vào hệ thống:\n"
    message += f"- Tên: {client_name}\n"
    message += f"- Địa chỉ IP: {client_ip}\n"
    message += f"- Địa chỉ MAC: {client_mac}\n"
    message += f"- Interface: {interface}\n"
    
    return send_system_notification(title, message, 'info', notify_email=False)

def notify_firewall_block(ip_address, reason=None):
    """Thông báo về việc firewall chặn kết nối"""
    title = f"Firewall đã chặn kết nối từ {ip_address}"
    message = f"Hệ thống firewall đã chặn kết nối từ địa chỉ IP {ip_address}"
    if reason:
        message += f"\nLý do: {reason}"
    
    return send_system_notification(title, message, 'warning')