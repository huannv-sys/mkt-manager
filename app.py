from flask import Flask, render_template, jsonify, request, redirect, url_for, session, flash, send_file
import os
import git
import sys
import datetime
import json
import logging
from functools import wraps
from werkzeug.utils import secure_filename

# Các module tự tạo
import config
from utils.auth import login_required, admin_required, has_permission
from utils.mikrotik_api import MikroTikAPI
from utils.notifications import send_system_notification

# Thiết lập logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(config.LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)

# Tạo logger
logger = logging.getLogger('mikrotik_msc')

# Khởi tạo ứng dụng Flask
app = Flask(__name__)
app.secret_key = config.SECRET_KEY
app.config['SESSION_TYPE'] = config.SESSION_TYPE
app.config['UPLOAD_FOLDER'] = os.path.join(config.BASE_DIR, 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

# Đảm bảo thư mục uploads tồn tại
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    # Analyze repository structure
    repo_analysis = analyze_repo()
    return render_template('index.html', repo_analysis=repo_analysis)

@app.route('/api/repo-analysis')
def get_repo_analysis():
    return jsonify(analyze_repo())

# Route for monitoring dashboard
@app.route('/monitoring/dashboard')
def monitoring_dashboard():
    return render_template('monitoring/dashboard.html')

# Route for client monitoring
@app.route('/monitoring/clients')
def client_monitoring():
    return render_template('monitoring/clients.html')

# Route for interface monitoring
@app.route('/monitoring/interfaces')
def interface_monitoring():
    return render_template('monitoring/interfaces.html')

# Route for IP monitoring
@app.route('/monitoring/ip')
def ip_monitoring():
    return render_template('monitoring/ip.html')

# Route for firewall management
@app.route('/management/firewall')
def firewall_management():
    return render_template('management/firewall.html')

# Mock API routes for client data (to be replaced with actual implementations)
@app.route('/api/clients')
def api_clients():
    # Example response structure for clients list
    clients = [
        {
            "id": "client1",
            "hostname": "laptop-01",
            "ip_address": "192.168.1.100",
            "mac_address": "AA:BB:CC:DD:EE:FF",
            "interface": "wlan1",
            "connection_type": "wireless",
            "tx_rate": 1024000,
            "rx_rate": 2048000,
            "status": "active"
        },
        {
            "id": "client2",
            "hostname": "desktop-02",
            "ip_address": "192.168.1.101",
            "mac_address": "11:22:33:44:55:66",
            "interface": "ether1",
            "connection_type": "wired",
            "tx_rate": 512000,
            "rx_rate": 1024000,
            "status": "active"
        }
    ]
    return jsonify(clients)

# Mock API route for dashboard data
@app.route('/api/monitoring/dashboard')
def api_dashboard():
    # Example response structure for dashboard
    data = {
        "system": {
            "cpu_load": 25,
            "memory_usage": 40,
            "uptime": "5d 12h 30m",
            "version": "RouterOS v7.11.2"
        },
        "clients": {
            "active": 12,
            "total": 15
        },
        "interfaces": [
            {
                "name": "ether1",
                "type": "ethernet",
                "tx_rate": 1024000,
                "rx_rate": 2048000,
                "status": "active"
            },
            {
                "name": "wlan1",
                "type": "wireless",
                "tx_rate": 512000,
                "rx_rate": 1024000,
                "status": "active"
            }
        ],
        "dhcp_leases": [
            {
                "hostname": "laptop-01",
                "address": "192.168.1.100",
                "mac_address": "AA:BB:CC:DD:EE:FF",
                "expires": "12h 30m"
            },
            {
                "hostname": "desktop-02",
                "address": "192.168.1.101",
                "mac_address": "11:22:33:44:55:66",
                "expires": "23h 45m"
            }
        ],
        "logs": [
            {
                "time": "2025-03-10 07:45:12",
                "topic": "system",
                "message": "System started"
            },
            {
                "time": "2025-03-10 07:46:23",
                "topic": "firewall",
                "message": "Blocked connection from 203.0.113.5"
            }
        ]
    }
    return jsonify(data)

# Mock API route for firewall rules
@app.route('/api/firewall/filter')
def api_firewall_filter():
    # Example response structure for filter rules
    rules = [
        {
            "id": "rule1",
            "chain": "input",
            "action": "accept",
            "src_address": "192.168.1.0/24",
            "dst_address": "",
            "protocol": "tcp",
            "src_port": "",
            "dst_port": "80,443",
            "comment": "Allow web access from LAN",
            "disabled": False
        },
        {
            "id": "rule2",
            "chain": "forward",
            "action": "drop",
            "src_address": "",
            "dst_address": "203.0.113.0/24",
            "protocol": "any",
            "src_port": "",
            "dst_port": "",
            "comment": "Block access to blacklisted IPs",
            "disabled": False
        }
    ]
    return jsonify(rules)

# Mock API route for IP addresses
@app.route('/api/ip/addresses')
def api_ip_addresses():
    # Example response structure for IP addresses
    addresses = [
        {
            "id": "addr1",
            "address": "192.168.1.1/24",
            "network": "192.168.1.0",
            "interface": "ether1",
            "type": "static",
            "status": "active",
            "comment": "LAN interface"
        },
        {
            "id": "addr2",
            "address": "10.0.0.1/24",
            "network": "10.0.0.0",
            "interface": "ether2",
            "type": "static",
            "status": "active",
            "comment": "Management interface"
        }
    ]
    return jsonify(addresses)

def analyze_repo():
    """Analyze the repository structure and return key information"""
    result = {
        "name": "mikrotik-msc",
        "description": "MikroTik Manager/Monitor System",
        "analysis_date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "components": [],
        "installation": {
            "requirements": [],
            "compatible_os": ["Ubuntu 24.04"],
            "database": "PostgreSQL",
            "services": ["Backend (FastAPI)", "Frontend (React)", "Nginx", "PostgreSQL"]
        }
    }
    
    # Check for repository
    if not os.path.exists("mikrotik-msc"):
        return {
            "error": "Repository not found. Please ensure mikrotik-msc is cloned properly."
        }
    
    # Add key components
    result["components"] = [
        {
            "name": "Dashboard",
            "file": "monitoring/dashboard.html",
            "description": "Main monitoring dashboard"
        },
        {
            "name": "Client Monitor",
            "file": "monitoring/clients.html",
            "description": "Client management and monitoring"
        },
        {
            "name": "Interface Monitor",
            "file": "monitoring/interfaces.html",
            "description": "Network interface monitoring"
        },
        {
            "name": "IP Management",
            "file": "monitoring/ip.html",
            "description": "IP and DNS management"
        },
        {
            "name": "Firewall",
            "file": "management/firewall.html",
            "description": "Firewall rule management"
        }
    ]
    
    # Add requirements
    if os.path.exists("mikrotik-msc/requirements.txt"):
        with open("mikrotik-msc/requirements.txt", "r") as f:
            requirements = f.readlines()
            result["installation"]["requirements"] = [
                req.strip() for req in requirements if req.strip() and not req.startswith("#")
            ]
    
    return result

# Route cho trang cài đặt
@app.route('/settings/general')
def settings_general():
    return render_template('settings/general.html')

@app.route('/settings/connection')
def settings_connection():
    return render_template('settings/connection.html')

@app.route('/settings/notification')
def settings_notification():
    return render_template('settings/notification.html', page='notification')

@app.route('/settings/users')
def settings_users():
    return render_template('settings/users.html', page='users')

# Route cho trang backup
@app.route('/backup/manager')
def backup_manager():
    return render_template('backup/manager.html')

# Route cho trang logs
@app.route('/logs/system')
def logs_system():
    return render_template('logs/system.html')

@app.route('/logs/firewall')
def logs_firewall():
    return render_template('logs/firewall.html')

@app.route('/logs/mikrotik')
def logs_mikrotik():
    return render_template('logs/mikrotik.html')

@app.route('/logs/application')
def logs_application():
    return render_template('logs/application.html')

# API cho settings
@app.route('/api/settings/general', methods=['GET', 'POST'])
def api_settings_general():
    if request.method == 'GET':
        # Mô phỏng dữ liệu cài đặt
        settings = {
            'display': {
                'refreshInterval': 5,
                'pageSize': 25,
                'chartDataPoints': 30,
                'darkMode': False
            },
            'system': {
                'logLevel': 'INFO',
                'logRetention': 30,
                'language': 'vi',
                'autoUpdate': True
            },
            'alerts': {
                'cpuThreshold': 80,
                'memoryThreshold': 80,
                'diskThreshold': 90,
                'interfaceThreshold': 80,
                'enableClientAlerts': True,
                'enableFirewallAlerts': True
            }
        }
        return jsonify({'success': True, 'data': settings})
    elif request.method == 'POST':
        # Xử lý lưu cài đặt
        try:
            settings = request.json
            # TODO: Lưu cài đặt vào cơ sở dữ liệu
            logger.info(f"Đã lưu cài đặt: {settings}")
            return jsonify({'success': True})
        except Exception as e:
            logger.error(f"Lỗi khi lưu cài đặt: {str(e)}")
            return jsonify({'success': False, 'error': str(e)})

@app.route('/api/settings/reset', methods=['POST'])
def api_settings_reset():
    try:
        # TODO: Reset cài đặt về mặc định
        logger.info("Đã reset cài đặt về mặc định")
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Lỗi khi reset cài đặt: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

# API cho backup
@app.route('/api/backup/list', methods=['GET'])
def api_backup_list():
    # Mô phỏng danh sách backup
    backups = [
        {
            'id': '1',
            'filename': 'backup_20250310_080000.backup',
            'deviceName': 'Router Chính',
            'size': 2621440,  # 2.5 MB in bytes
            'createdAt': '2025-03-10T08:00:00',
            'type': 'Manual'
        },
        {
            'id': '2',
            'filename': 'backup_20250309_080000.backup',
            'deviceName': 'Router Chính',
            'size': 2516582,  # 2.4 MB in bytes
            'createdAt': '2025-03-09T08:00:00',
            'type': 'Scheduled'
        }
    ]
    return jsonify({'success': True, 'data': backups})

@app.route('/api/backup/exports', methods=['GET'])
def api_backup_exports():
    # Mô phỏng danh sách export
    exports = [
        {
            'id': '1',
            'filename': 'export_20250310_080000.rsc',
            'deviceName': 'Router Chính',
            'size': 46080,  # 45 KB in bytes
            'createdAt': '2025-03-10T08:00:00',
            'type': 'Full'
        },
        {
            'id': '2',
            'filename': 'export_20250309_080000.rsc',
            'deviceName': 'Router Chính',
            'size': 45056,  # 44 KB in bytes
            'createdAt': '2025-03-09T08:00:00',
            'type': 'Compact'
        }
    ]
    return jsonify({'success': True, 'data': exports})

@app.route('/api/backup/schedules', methods=['GET'])
def api_backup_schedules():
    # Mô phỏng danh sách lịch backup
    schedules = [
        {
            'id': '1',
            'name': 'Backup Hàng Ngày',
            'deviceName': 'Router Chính',
            'deviceId': '1',
            'type': 'daily',
            'time': '03:00',
            'active': True,
            'nextRun': '2025-03-11T03:00:00',
            'retention': 7,
            'includeSensitive': False
        },
        {
            'id': '2',
            'name': 'Backup Hàng Tuần',
            'deviceName': 'Router Phòng Kỹ Thuật',
            'deviceId': '2',
            'type': 'weekly',
            'weekday': '0',  # Sunday
            'time': '04:00',
            'active': False,
            'nextRun': '2025-03-16T04:00:00',
            'retention': 4,
            'includeSensitive': False
        }
    ]
    return jsonify({'success': True, 'data': schedules})

# API cho logs
@app.route('/api/logs/system', methods=['GET'])
def api_logs_system():
    # Mô phỏng dữ liệu logs với phân trang
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 50))
    level = request.args.get('level', '')
    topic = request.args.get('topic', '')
    search_text = request.args.get('searchText', '')
    
    # Mô phỏng dữ liệu logs
    all_logs = [
        {
            'id': '1',
            'timestamp': '2025-03-10T08:30:15',
            'level': 'Info',
            'topic': 'System',
            'device': 'Server',
            'message': 'Hệ thống khởi động thành công'
        },
        {
            'id': '2',
            'timestamp': '2025-03-10T08:25:10',
            'level': 'Warning',
            'topic': 'Auth',
            'device': 'Router Chính',
            'message': 'Đăng nhập thất bại từ IP 192.168.1.100'
        },
        {
            'id': '3',
            'timestamp': '2025-03-10T08:20:05',
            'level': 'Error',
            'topic': 'Network',
            'device': 'Router Chính',
            'message': 'Không thể kết nối đến thiết bị ngoại vi trên cổng ether2'
        },
        {
            'id': '4',
            'timestamp': '2025-03-10T08:15:30',
            'level': 'Info',
            'topic': 'System',
            'device': 'Router Phòng Kỹ Thuật',
            'message': 'Cập nhật firmware thành công lên phiên bản 7.11.2'
        },
        {
            'id': '5',
            'timestamp': '2025-03-10T08:10:22',
            'level': 'Info',
            'topic': 'Auth',
            'device': 'Router Chính',
            'message': 'Đăng nhập thành công từ IP 192.168.1.10 (admin)'
        },
        {
            'id': '6',
            'timestamp': '2025-03-10T08:05:18',
            'level': 'Warning',
            'topic': 'Services',
            'device': 'Router Chính',
            'message': 'Dịch vụ DHCP tạm dừng'
        },
        {
            'id': '7',
            'timestamp': '2025-03-10T08:00:05',
            'level': 'Info',
            'topic': 'Services',
            'device': 'Router Chính',
            'message': 'Dịch vụ DHCP hoạt động trở lại'
        }
    ]
    
    # Lọc logs nếu có tham số
    filtered_logs = all_logs
    if level:
        filtered_logs = [log for log in filtered_logs if log['level'].lower() == level.lower()]
    if topic:
        filtered_logs = [log for log in filtered_logs if log['topic'].lower() == topic.lower()]
    if search_text:
        filtered_logs = [log for log in filtered_logs if search_text.lower() in log['message'].lower()]
    
    # Tính toán phân trang
    total = len(filtered_logs)
    total_pages = (total + limit - 1) // limit
    start = (page - 1) * limit
    end = min(start + limit, total)
    
    # Trả về kết quả
    return jsonify({
        'success': True,
        'data': {
            'logs': filtered_logs[start:end],
            'pagination': {
                'total': total,
                'totalPages': total_pages,
                'currentPage': page,
                'limit': limit
            }
        }
    })

# API cho các trang khác sẽ được thêm vào sau

# API cho quản lý người dùng
@app.route('/api/users', methods=['GET'])
@admin_required
def api_users():
    # Mô phỏng danh sách người dùng
    users = [
        {
            'id': '1',
            'username': 'admin',
            'email': 'admin@example.com',
            'role': 'admin',
            'created_at': '2025-03-01T08:00:00',
            'last_login': '2025-03-10T08:00:00',
            'status': 'active'
        },
        {
            'id': '2',
            'username': 'user',
            'email': 'user@example.com',
            'role': 'user',
            'created_at': '2025-03-05T10:00:00',
            'last_login': '2025-03-09T14:00:00',
            'status': 'active'
        },
        {
            'id': '3',
            'username': 'viewer',
            'email': 'viewer@example.com',
            'role': 'viewer',
            'created_at': '2025-03-08T09:00:00',
            'last_login': '2025-03-10T07:00:00',
            'status': 'active'
        }
    ]
    return jsonify({'success': True, 'data': users})

@app.route('/api/users', methods=['POST'])
@admin_required
def api_create_user():
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ['username', 'email', 'password', 'role']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'Thiếu trường {field}'})
        
        # TODO: Tạo người dùng mới trong cơ sở dữ liệu
        # Mô phỏng tạo người dùng thành công
        new_user = {
            'id': '4',  # ID giả định
            'username': data['username'],
            'email': data['email'],
            'role': data['role'],
            'created_at': datetime.datetime.now().isoformat(),
            'status': 'active'
        }
        
        logger.info(f"Tạo người dùng mới: {data['username']}")
        return jsonify({'success': True, 'data': new_user})
    except Exception as e:
        logger.error(f"Lỗi khi tạo người dùng: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/users/<user_id>', methods=['PUT'])
@admin_required
def api_update_user(user_id):
    try:
        data = request.json
        
        # TODO: Cập nhật thông tin người dùng trong cơ sở dữ liệu
        logger.info(f"Cập nhật người dùng {user_id}: {data}")
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Lỗi khi cập nhật người dùng: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/users/<user_id>', methods=['DELETE'])
@admin_required
def api_delete_user(user_id):
    try:
        # TODO: Xóa người dùng khỏi cơ sở dữ liệu
        logger.info(f"Xóa người dùng {user_id}")
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Lỗi khi xóa người dùng: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/users/change-password', methods=['POST'])
@login_required
def api_change_password():
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ['current_password', 'new_password']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'Thiếu trường {field}'})
        
        # TODO: Xác thực mật khẩu hiện tại và cập nhật mật khẩu mới
        logger.info("Đã thay đổi mật khẩu thành công")
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Lỗi khi thay đổi mật khẩu: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

# Route cho xác thực
@app.route('/login', methods=['GET', 'POST'])
def login():
    # Xử lý đăng nhập
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = 'remember' in request.form
        
        # Mô phỏng xác thực
        if username == 'admin' and password == 'admin':
            # Tạo token JWT và lưu vào session
            token = utils.auth.generate_token('1', username, 'admin')
            session['token'] = token
            
            if remember:
                # Cài đặt cookie lâu dài (30 ngày)
                session.permanent = True
                app.permanent_session_lifetime = datetime.timedelta(days=30)
            
            # Redirect đến trang chính
            return redirect(url_for('index'))
        else:
            # Đăng nhập thất bại
            return render_template('auth/login.html', error='Tên đăng nhập hoặc mật khẩu không chính xác', current_year=datetime.datetime.now().year, version='1.0.0')
    
    # Hiển thị trang đăng nhập
    return render_template('auth/login.html', current_year=datetime.datetime.now().year, version='1.0.0')

@app.route('/logout')
def logout():
    # Xóa session
    session.clear()
    return redirect(url_for('login'))

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    # Xử lý yêu cầu reset mật khẩu
    if request.method == 'POST':
        email = request.form.get('email')
        
        # TODO: Gửi email reset mật khẩu
        
        # Thông báo thành công
        return render_template('auth/forgot_password.html', success='Hướng dẫn đặt lại mật khẩu đã được gửi đến email của bạn.', current_year=datetime.datetime.now().year, version='1.0.0')
    
    # Hiển thị form quên mật khẩu
    return render_template('auth/forgot_password.html', current_year=datetime.datetime.now().year, version='1.0.0')

@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    # TODO: Xác thực token và xử lý đặt lại mật khẩu
    return redirect(url_for('login'))

# Middleware để bảo vệ routes
@app.before_request
def check_authentication():
    # Danh sách các routes không yêu cầu xác thực
    public_routes = ['/login', '/logout', '/forgot-password', '/static', '/favicon.ico']
    
    # Cho phép truy cập các routes công khai
    for route in public_routes:
        if request.path.startswith(route):
            return None
    
    # Kiểm tra xác thực cho các routes khác
    if 'token' not in session:
        return redirect(url_for('login'))
    
    # Xác thực token
    user_data = utils.auth.decode_token(session['token'])
    if not user_data:
        session.clear()
        return redirect(url_for('login'))
    
    # Lưu thông tin người dùng vào g để sử dụng trong request
    g.user = user_data
    
    return None

# Xử lý lỗi
@app.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    error_info = None
    if app.debug:
        error_info = str(e)
    return render_template('errors/500.html', error_info=error_info, debug=app.debug), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)