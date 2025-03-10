"""
MikroTik Management System Center
Main application file
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, session, g
from git import Repo
import datetime
import logging
import json
import os
import sys
import sqlite3
from werkzeug.utils import secure_filename

from utils import auth, notifications, mikrotik_utils, ip_monitoring

# Khởi tạo Flask app
app = Flask(__name__)
app.config.from_object('config')

# Thiết lập logging
logging.basicConfig(
    level=getattr(logging, app.config['LOG_LEVEL']),
    format=app.config['LOG_FORMAT'],
    datefmt=app.config['LOG_DATE_FORMAT'],
    handlers=[
        logging.FileHandler(app.config['LOG_FILE']),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Khởi tạo session
app.config['SESSION_TYPE'] = app.config['SESSION_TYPE']
app.config['UPLOAD_FOLDER'] = os.path.join(app.config['BASE_DIR'], 'uploads')

# Khởi tạo secret key
app.secret_key = app.config['SECRET_KEY']

# Tạo thư mục uploads nếu chưa tồn tại
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
@auth.login_required
def index():
    """Trang chủ"""
    return render_template('index.html')

@app.route('/dashboard')
@auth.login_required
def dashboard():
    """Trang dashboard"""
    return render_template('dashboard.html')

@app.route('/monitoring')
@auth.login_required
def monitoring():
    """Trang giám sát"""
    return render_template('monitoring.html')

@app.route('/clients')
@auth.login_required
def clients():
    """Trang quản lý client"""
    return render_template('clients.html')

@app.route('/interfaces')
@auth.login_required
def interfaces():
    """Trang quản lý interface"""
    return render_template('interfaces.html')

@app.route('/ip-monitor')
@auth.login_required
def ip_monitor():
    """Trang giám sát IP"""
    return render_template('ip_monitoring.html')

@app.route('/firewall')
@auth.login_required
def firewall():
    """Trang quản lý firewall"""
    return render_template('firewall.html')

@app.route('/vpn')
@auth.login_required
def vpn():
    """Trang quản lý VPN"""
    return render_template('vpn.html')

@app.route('/settings')
@auth.login_required
def settings():
    """Trang cài đặt"""
    return render_template('settings.html')

@app.route('/backup')
@auth.login_required
def backup():
    """Trang quản lý backup"""
    return render_template('backup.html')

@app.route('/logs')
@auth.login_required
def logs():
    """Trang quản lý log"""
    return render_template('logs.html')

# API routes
@app.route('/api/ip/list')
@auth.login_required
def api_ip_list():
    """API lấy danh sách IP"""
    try:
        # Lấy danh sách IP từ MikroTik
        device = mikrotik_utils.get_mikrotik_connection()
        if not device:
            return jsonify({'success': False, 'error': 'Không thể kết nối đến MikroTik'})
            
        ip_addresses = device.ip.address.get()
        
        # Xử lý và định dạng dữ liệu
        ips = []
        stats = {
            'total': 0,
            'active': 0,
            'inactive': 0,
            'monitored': 0
        }
        
        for ip in ip_addresses:
            ip_data = {
                'address': ip.get('address'),
                'interface': ip.get('interface'),
                'mac_address': mikrotik_utils.get_mac_address(ip.get('interface')),
                'status': 'active' if mikrotik_utils.is_ip_active(ip.get('address')) else 'inactive',
                'traffic_in': mikrotik_utils.get_interface_traffic(ip.get('interface'), 'in'),
                'traffic_out': mikrotik_utils.get_interface_traffic(ip.get('interface'), 'out'),
                'last_seen': mikrotik_utils.get_last_seen(ip.get('address')),
                'monitoring': ip_monitoring.is_ip_monitored(ip.get('address'))
            }
            
            ips.append(ip_data)
            
            # Cập nhật thống kê
            stats['total'] += 1
            if ip_data['status'] == 'active':
                stats['active'] += 1
            else:
                stats['inactive'] += 1
            if ip_data['monitoring']:
                stats['monitored'] += 1
        
        # Lấy dữ liệu cho biểu đồ
        charts = {
            'traffic': mikrotik_utils.get_traffic_chart_data(),
            'distribution': mikrotik_utils.get_ip_distribution_data()
        }
        
        return jsonify({
            'success': True,
            'data': {
                'ips': ips,
                'stats': stats,
                'charts': charts
            }
        })
    except Exception as e:
        logger.error(f"Lỗi khi lấy danh sách IP: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/ip/<ip_address>')
@auth.login_required
def api_ip_details(ip_address):
    """API lấy chi tiết IP"""
    try:
        # Lấy thông tin chi tiết về IP từ MikroTik
        device = mikrotik_utils.get_mikrotik_connection()
        if not device:
            return jsonify({'success': False, 'error': 'Không thể kết nối đến MikroTik'})
            
        ip_data = device.ip.address.get(address=ip_address)
        
        if not ip_data:
            return jsonify({'success': False, 'error': 'IP không tồn tại'})
        
        # Lấy thông tin bổ sung
        interface = ip_data[0].get('interface')
        mac_address = mikrotik_utils.get_mac_address(interface)
        
        # Lấy lịch sử của IP
        history = ip_monitoring.get_ip_history(ip_address)
        
        # Tạo đối tượng response
        response = {
            'address': ip_address,
            'interface': interface,
            'mac_address': mac_address,
            'status': 'active' if mikrotik_utils.is_ip_active(ip_address) else 'inactive',
            'traffic_in': mikrotik_utils.get_interface_traffic(interface, 'in'),
            'traffic_out': mikrotik_utils.get_interface_traffic(interface, 'out'),
            'last_seen': mikrotik_utils.get_last_seen(ip_address),
            'monitoring': ip_monitoring.is_ip_monitored(ip_address),
            'history': history
        }
        
        return jsonify({'success': True, 'data': response})
    except Exception as e:
        logger.error(f"Lỗi khi lấy thông tin IP {ip_address}: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/ip/add', methods=['POST'])
@auth.login_required
def api_add_ip():
    """API thêm IP mới"""
    try:
        data = request.json
        
        # Validate dữ liệu
        required_fields = ['address', 'interface']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'Thiếu trường {field}'})
        
        # Thêm IP vào MikroTik
        device = mikrotik_utils.get_mikrotik_connection()
        if not device:
            return jsonify({'success': False, 'error': 'Không thể kết nối đến MikroTik'})
            
        device.ip.address.add(
            address=data['address'],
            interface=data['interface']
        )
        
        # Bật monitoring nếu được yêu cầu
        if data.get('monitoring'):
            ip_monitoring.enable_ip_monitoring(data['address'])
        
        logger.info(f"Đã thêm IP {data['address']}")
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Lỗi khi thêm IP: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/ip/<ip_address>', methods=['DELETE'])
@auth.login_required
def api_delete_ip(ip_address):
    """API xóa IP"""
    try:
        # Xóa IP khỏi MikroTik
        device = mikrotik_utils.get_mikrotik_connection()
        if not device:
            return jsonify({'success': False, 'error': 'Không thể kết nối đến MikroTik'})
            
        device.ip.address.remove(address=ip_address)
        
        # Tắt monitoring nếu đang bật
        ip_monitoring.disable_ip_monitoring(ip_address)
        
        logger.info(f"Đã xóa IP {ip_address}")
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Lỗi khi xóa IP {ip_address}: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/ip/search')
@auth.login_required
def api_search_ip():
    """API tìm kiếm IP"""
    try:
        query = request.args.get('q', '')
        
        # Tìm kiếm IP từ MikroTik
        device = mikrotik_utils.get_mikrotik_connection()
        if not device:
            return jsonify({'success': False, 'error': 'Không thể kết nối đến MikroTik'})
            
        ip_addresses = device.ip.address.get()
        
        # Lọc kết quả theo query
        results = []
        for ip in ip_addresses:
            if query.lower() in ip.get('address', '').lower() or \
               query.lower() in ip.get('interface', '').lower():
                ip_data = {
                    'address': ip.get('address'),
                    'interface': ip.get('interface'),
                    'mac_address': mikrotik_utils.get_mac_address(ip.get('interface')),
                    'status': 'active' if mikrotik_utils.is_ip_active(ip.get('address')) else 'inactive',
                    'traffic_in': mikrotik_utils.get_interface_traffic(ip.get('interface'), 'in'),
                    'traffic_out': mikrotik_utils.get_interface_traffic(ip.get('interface'), 'out'),
                    'last_seen': mikrotik_utils.get_last_seen(ip.get('address')),
                    'monitoring': ip_monitoring.is_ip_monitored(ip.get('address'))
                }
                results.append(ip_data)
        
        return jsonify({'success': True, 'data': results})
    except Exception as e:
        logger.error(f"Lỗi khi tìm kiếm IP: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

# Route cho xác thực
@app.route('/login', methods=['GET', 'POST'])
def login():
    """Trang đăng nhập"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = 'remember' in request.form
        
        # Mô phỏng xác thực
        if username == 'admin' and password == 'admin':
            # Tạo token JWT và lưu vào session
            token = auth.generate_token('1', username, 'admin')
            session['token'] = token
            
            if remember:
                # Cài đặt cookie lâu dài (30 ngày)
                session.permanent = True
                app.permanent_session_lifetime = datetime.timedelta(days=30)
            
            # Redirect đến trang chính
            return redirect(url_for('index'))
        else:
            # Đăng nhập thất bại
            return render_template('auth/login.html', 
                                error='Tên đăng nhập hoặc mật khẩu không chính xác', 
                                current_year=datetime.datetime.now().year, 
                                version='1.0.0')
    
    # Hiển thị trang đăng nhập
    return render_template('auth/login.html', 
                        current_year=datetime.datetime.now().year, 
                        version='1.0.0')

@app.route('/logout')
def logout():
    """Đăng xuất"""
    session.clear()
    return redirect(url_for('login'))

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Trang quên mật khẩu"""
    if request.method == 'POST':
        email = request.form.get('email')
        
        # TODO: Gửi email reset mật khẩu
        notifications.send_email_notification(
            subject='Đặt lại mật khẩu MikroTik MSC',
            message='Hướng dẫn đặt lại mật khẩu của bạn.',
            recipients=[email]
        )
        
        # Thông báo thành công
        return render_template('auth/forgot_password.html', 
                            success='Hướng dẫn đặt lại mật khẩu đã được gửi đến email của bạn.',
                            current_year=datetime.datetime.now().year, 
                            version='1.0.0')
    
    # Hiển thị form quên mật khẩu
    return render_template('auth/forgot_password.html', 
                        current_year=datetime.datetime.now().year, 
                        version='1.0.0')

@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Trang đặt lại mật khẩu"""
    # TODO: Xác thực token và xử lý đặt lại mật khẩu
    return redirect(url_for('login'))

# Middleware để bảo vệ routes
@app.before_request
def check_authentication():
    """Kiểm tra xác thực cho mọi request"""
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
    user_data = auth.decode_token(session['token'])
    if not user_data:
        session.clear()
        return redirect(url_for('login'))
    
    # Lưu thông tin người dùng vào g để sử dụng trong request
    g.user = user_data
    
    return None

# Xử lý lỗi
@app.errorhandler(404)
def page_not_found(e):
    """Trang không tồn tại"""
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    """Lỗi máy chủ"""
    error_info = None
    if app.debug:
        error_info = str(e)
    return render_template('errors/500.html', error_info=error_info, debug=app.debug), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)