/**
 * JavaScript cho trang quản lý backup
 */

// Khởi tạo khi trang đã tải xong
$(document).ready(function() {
    // Tải danh sách backup và export
    loadBackups();
    loadExports();
    loadSchedules();
    
    // Xử lý sự kiện tab
    $('a[data-bs-toggle="tab"]').on('shown.bs.tab', function (e) {
        // Refreshing tab data khi chuyển tab
        const targetTab = $(e.target).attr('href');
        if (targetTab === '#backups') {
            loadBackups();
        } else if (targetTab === '#exports') {
            loadExports();
        } else if (targetTab === '#schedules') {
            loadSchedules();
        }
    });
    
    // Xử lý nút tạo backup
    $('#createBackupBtn').on('click', function() {
        // Mở modal
        $('#createBackupModal').modal('show');
    });
    
    // Xử lý nút tạo export
    $('#createExportBtn').on('click', function() {
        // Mở modal
        $('#createExportModal').modal('show');
    });
    
    // Xử lý nút upload backup
    $('#uploadBackupBtn').on('click', function() {
        // Mở modal
        $('#uploadBackupModal').modal('show');
    });
    
    // Xử lý nút thêm lịch backup
    $('#addScheduleBtn').on('click', function() {
        // Reset form và mở modal
        $('#scheduleForm')[0].reset();
        $('#scheduleId').val('');
        $('#scheduleModalLabel').text('Thêm Lịch Backup');
        updateScheduleFields();
        $('#scheduleModal').modal('show');
    });
    
    // Xử lý thay đổi loại lịch để hiển thị các trường phù hợp
    $('#scheduleType').on('change', function() {
        updateScheduleFields();
    });
    
    // Xử lý sự kiện bật/tắt xác thực database
    $('#dbAuth').on('change', function() {
        if ($(this).is(':checked')) {
            $('#dbUserField, #dbPasswordField').removeClass('d-none');
        } else {
            $('#dbUserField, #dbPasswordField').addClass('d-none');
        }
    });
    
    // Xử lý nút xác nhận tạo backup
    $('#confirmCreateBackupBtn').on('click', function() {
        createBackup();
    });
    
    // Xử lý nút xác nhận tạo export
    $('#confirmCreateExportBtn').on('click', function() {
        createExport();
    });
    
    // Xử lý nút upload
    $('#confirmUploadBtn').on('click', function() {
        uploadBackup();
    });
    
    // Xử lý nút lưu lịch
    $('#saveScheduleBtn').on('click', function() {
        saveSchedule();
    });
    
    // Xử lý sự kiện nút xem export
    $(document).on('click', '.view-export', function() {
        const exportId = $(this).data('id');
        viewExport(exportId);
    });
    
    // Xử lý sự kiện nút download backup
    $(document).on('click', '.download-backup', function() {
        const backupId = $(this).data('id');
        downloadBackup(backupId);
    });
    
    // Xử lý sự kiện nút download export
    $(document).on('click', '.download-export', function() {
        const exportId = $(this).data('id');
        downloadExport(exportId);
    });
    
    // Xử lý sự kiện nút restore backup
    $(document).on('click', '.restore-backup', function() {
        const backupId = $(this).data('id');
        if (confirm('Bạn có chắc chắn muốn khôi phục backup này không?')) {
            restoreBackup(backupId);
        }
    });
    
    // Xử lý sự kiện nút restore export
    $(document).on('click', '.restore-export', function() {
        const exportId = $(this).data('id');
        if (confirm('Bạn có chắc chắn muốn áp dụng export này không?')) {
            restoreExport(exportId);
        }
    });
    
    // Xử lý sự kiện nút xóa backup
    $(document).on('click', '.delete-backup', function() {
        const backupId = $(this).data('id');
        if (confirm('Bạn có chắc chắn muốn xóa backup này không?')) {
            deleteBackup(backupId);
        }
    });
    
    // Xử lý sự kiện nút xóa export
    $(document).on('click', '.delete-export', function() {
        const exportId = $(this).data('id');
        if (confirm('Bạn có chắc chắn muốn xóa export này không?')) {
            deleteExport(exportId);
        }
    });
    
    // Xử lý sự kiện nút sửa lịch
    $(document).on('click', '.edit-schedule', function() {
        const scheduleId = $(this).data('id');
        editSchedule(scheduleId);
    });
    
    // Xử lý sự kiện nút bật/tắt lịch
    $(document).on('click', '.toggle-schedule', function() {
        const scheduleId = $(this).data('id');
        const isActive = $(this).data('active');
        toggleSchedule(scheduleId, !isActive);
    });
    
    // Xử lý sự kiện nút xóa lịch
    $(document).on('click', '.delete-schedule', function() {
        const scheduleId = $(this).data('id');
        if (confirm('Bạn có chắc chắn muốn xóa lịch backup này không?')) {
            deleteSchedule(scheduleId);
        }
    });
});

/**
 * Cập nhật hiển thị các trường trong form lịch
 */
function updateScheduleFields() {
    const scheduleType = $('#scheduleType').val();
    
    // Ẩn tất cả các trường đặc biệt
    $('#weekdaySelectField, #monthlySelectField').addClass('d-none');
    
    // Hiển thị trường phù hợp dựa trên loại lịch
    if (scheduleType === 'weekly') {
        $('#weekdaySelectField').removeClass('d-none');
    } else if (scheduleType === 'monthly') {
        $('#monthlySelectField').removeClass('d-none');
    }
}

/**
 * Tải danh sách các backup
 */
function loadBackups() {
    showLoading(true);
    
    $.ajax({
        url: '/api/backup/list',
        type: 'GET',
        dataType: 'json',
        success: function(response) {
            if (response.success) {
                updateBackupsTable(response.data);
            } else {
                showToast('error', 'Không thể tải danh sách backup: ' + response.error);
            }
        },
        error: function(xhr, status, error) {
            console.error('Lỗi khi tải danh sách backup:', error);
            showToast('error', 'Lỗi khi tải danh sách backup: ' + error);
        },
        complete: function() {
            showLoading(false);
        }
    });
}

/**
 * Tải danh sách các export
 */
function loadExports() {
    showLoading(true);
    
    $.ajax({
        url: '/api/backup/exports',
        type: 'GET',
        dataType: 'json',
        success: function(response) {
            if (response.success) {
                updateExportsTable(response.data);
            } else {
                showToast('error', 'Không thể tải danh sách export: ' + response.error);
            }
        },
        error: function(xhr, status, error) {
            console.error('Lỗi khi tải danh sách export:', error);
            showToast('error', 'Lỗi khi tải danh sách export: ' + error);
        },
        complete: function() {
            showLoading(false);
        }
    });
}

/**
 * Tải danh sách các lịch backup
 */
function loadSchedules() {
    showLoading(true);
    
    $.ajax({
        url: '/api/backup/schedules',
        type: 'GET',
        dataType: 'json',
        success: function(response) {
            if (response.success) {
                updateSchedulesTable(response.data);
            } else {
                showToast('error', 'Không thể tải danh sách lịch backup: ' + response.error);
            }
        },
        error: function(xhr, status, error) {
            console.error('Lỗi khi tải danh sách lịch backup:', error);
            showToast('error', 'Lỗi khi tải danh sách lịch backup: ' + error);
        },
        complete: function() {
            showLoading(false);
        }
    });
}

/**
 * Cập nhật bảng backup
 * @param {Array} backups - Danh sách backup
 */
function updateBackupsTable(backups) {
    const tableBody = $('#backupsTable tbody');
    tableBody.empty();
    
    if (backups.length === 0) {
        tableBody.append('<tr><td colspan="6" class="text-center">Không có backup nào</td></tr>');
        return;
    }
    
    backups.forEach(function(backup) {
        const row = `
            <tr>
                <td>${backup.filename}</td>
                <td>${backup.deviceName}</td>
                <td>${formatFileSize(backup.size)}</td>
                <td>${formatDate(backup.createdAt)}</td>
                <td>${backup.type}</td>
                <td>
                    <button class="btn btn-sm btn-success download-backup" data-id="${backup.id}">
                        <i class="fa-solid fa-download"></i>
                    </button>
                    <button class="btn btn-sm btn-primary restore-backup" data-id="${backup.id}">
                        <i class="fa-solid fa-sync"></i>
                    </button>
                    <button class="btn btn-sm btn-danger delete-backup" data-id="${backup.id}">
                        <i class="fa-solid fa-trash"></i>
                    </button>
                </td>
            </tr>
        `;
        tableBody.append(row);
    });
}

/**
 * Cập nhật bảng export
 * @param {Array} exports - Danh sách export
 */
function updateExportsTable(exports) {
    const tableBody = $('#exportsTable tbody');
    tableBody.empty();
    
    if (exports.length === 0) {
        tableBody.append('<tr><td colspan="6" class="text-center">Không có export nào</td></tr>');
        return;
    }
    
    exports.forEach(function(exp) {
        const row = `
            <tr>
                <td>${exp.filename}</td>
                <td>${exp.deviceName}</td>
                <td>${formatFileSize(exp.size)}</td>
                <td>${formatDate(exp.createdAt)}</td>
                <td>${exp.type}</td>
                <td>
                    <button class="btn btn-sm btn-success download-export" data-id="${exp.id}">
                        <i class="fa-solid fa-download"></i>
                    </button>
                    <button class="btn btn-sm btn-primary restore-export" data-id="${exp.id}">
                        <i class="fa-solid fa-sync"></i>
                    </button>
                    <button class="btn btn-sm btn-secondary view-export" data-id="${exp.id}">
                        <i class="fa-solid fa-eye"></i>
                    </button>
                    <button class="btn btn-sm btn-danger delete-export" data-id="${exp.id}">
                        <i class="fa-solid fa-trash"></i>
                    </button>
                </td>
            </tr>
        `;
        tableBody.append(row);
    });
}

/**
 * Cập nhật bảng lịch backup
 * @param {Array} schedules - Danh sách lịch backup
 */
function updateSchedulesTable(schedules) {
    const tableBody = $('#schedulesTable tbody');
    tableBody.empty();
    
    if (schedules.length === 0) {
        tableBody.append('<tr><td colspan="6" class="text-center">Không có lịch backup nào</td></tr>');
        return;
    }
    
    schedules.forEach(function(schedule) {
        const statusBadge = schedule.active ? 
            '<span class="badge bg-success">Đang hoạt động</span>' : 
            '<span class="badge bg-warning">Tạm dừng</span>';
        
        const toggleIcon = schedule.active ? 
            '<i class="fa-solid fa-pause"></i>' : 
            '<i class="fa-solid fa-play"></i>';
        
        const toggleClass = schedule.active ? 
            'btn-warning' : 
            'btn-success';
        
        const row = `
            <tr>
                <td>${schedule.name}</td>
                <td>${schedule.deviceName}</td>
                <td>${formatScheduleFrequency(schedule)}</td>
                <td>${formatDate(schedule.nextRun)}</td>
                <td>${statusBadge}</td>
                <td>
                    <button class="btn btn-sm btn-primary edit-schedule" data-id="${schedule.id}">
                        <i class="fa-solid fa-edit"></i>
                    </button>
                    <button class="btn btn-sm ${toggleClass} toggle-schedule" data-id="${schedule.id}" data-active="${schedule.active}">
                        ${toggleIcon}
                    </button>
                    <button class="btn btn-sm btn-danger delete-schedule" data-id="${schedule.id}">
                        <i class="fa-solid fa-trash"></i>
                    </button>
                </td>
            </tr>
        `;
        tableBody.append(row);
    });
}

/**
 * Tạo backup mới
 */
function createBackup() {
    // Thu thập dữ liệu từ form
    const deviceId = $('#backupDevice').val();
    const backupName = $('#backupName').val();
    const includeSensitive = $('#includeSensitive').is(':checked');
    
    // Hiển thị loading spinner
    showLoading(true);
    
    // Gọi API để tạo backup
    $.ajax({
        url: '/api/backup/create',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({
            deviceId: deviceId,
            name: backupName,
            includeSensitive: includeSensitive
        }),
        success: function(response) {
            if (response.success) {
                showToast('success', 'Đã tạo backup thành công');
                $('#createBackupModal').modal('hide');
                loadBackups();
            } else {
                showToast('error', 'Không thể tạo backup: ' + response.error);
            }
        },
        error: function(xhr, status, error) {
            console.error('Lỗi khi tạo backup:', error);
            showToast('error', 'Lỗi khi tạo backup: ' + error);
        },
        complete: function() {
            showLoading(false);
        }
    });
}

/**
 * Tạo export mới
 */
function createExport() {
    // Thu thập dữ liệu từ form
    const deviceId = $('#exportDevice').val();
    const exportName = $('#exportName').val();
    const compact = $('#exportCompact').is(':checked');
    const includeSensitive = $('#exportSensitive').is(':checked');
    
    // Hiển thị loading spinner
    showLoading(true);
    
    // Gọi API để tạo export
    $.ajax({
        url: '/api/backup/export',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({
            deviceId: deviceId,
            name: exportName,
            compact: compact,
            includeSensitive: includeSensitive
        }),
        success: function(response) {
            if (response.success) {
                showToast('success', 'Đã tạo export thành công');
                $('#createExportModal').modal('hide');
                loadExports();
            } else {
                showToast('error', 'Không thể tạo export: ' + response.error);
            }
        },
        error: function(xhr, status, error) {
            console.error('Lỗi khi tạo export:', error);
            showToast('error', 'Lỗi khi tạo export: ' + error);
        },
        complete: function() {
            showLoading(false);
        }
    });
}

/**
 * Upload backup file
 */
function uploadBackup() {
    // Kiểm tra file đã chọn chưa
    const fileInput = $('#backupFile')[0];
    if (fileInput.files.length === 0) {
        showToast('warning', 'Vui lòng chọn file backup');
        return;
    }
    
    // Kiểm tra thiết bị đã chọn chưa
    const deviceId = $('#uploadDevice').val();
    if (!deviceId) {
        showToast('warning', 'Vui lòng chọn thiết bị');
        return;
    }
    
    // Tạo form data để upload file
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    formData.append('deviceId', deviceId);
    
    // Hiển thị loading spinner
    showLoading(true);
    
    // Gọi API để upload backup
    $.ajax({
        url: '/api/backup/upload',
        type: 'POST',
        data: formData,
        contentType: false,
        processData: false,
        success: function(response) {
            if (response.success) {
                showToast('success', 'Đã upload backup thành công');
                $('#uploadBackupModal').modal('hide');
                loadBackups();
            } else {
                showToast('error', 'Không thể upload backup: ' + response.error);
            }
        },
        error: function(xhr, status, error) {
            console.error('Lỗi khi upload backup:', error);
            showToast('error', 'Lỗi khi upload backup: ' + error);
        },
        complete: function() {
            showLoading(false);
        }
    });
}

/**
 * Xem nội dung export
 * @param {string} exportId - ID của export
 */
function viewExport(exportId) {
    // Hiển thị loading spinner
    showLoading(true);
    
    // Gọi API để lấy nội dung export
    $.ajax({
        url: '/api/backup/export/' + exportId + '/content',
        type: 'GET',
        success: function(response) {
            if (response.success) {
                $('#exportContent').text(response.data.content);
                $('#viewExportModal').modal('show');
            } else {
                showToast('error', 'Không thể xem nội dung export: ' + response.error);
            }
        },
        error: function(xhr, status, error) {
            console.error('Lỗi khi xem nội dung export:', error);
            showToast('error', 'Lỗi khi xem nội dung export: ' + error);
        },
        complete: function() {
            showLoading(false);
        }
    });
}

/**
 * Tải xuống backup
 * @param {string} backupId - ID của backup
 */
function downloadBackup(backupId) {
    window.location.href = '/api/backup/' + backupId + '/download';
}

/**
 * Tải xuống export
 * @param {string} exportId - ID của export
 */
function downloadExport(exportId) {
    window.location.href = '/api/backup/export/' + exportId + '/download';
}

/**
 * Khôi phục backup
 * @param {string} backupId - ID của backup
 */
function restoreBackup(backupId) {
    // Hiển thị loading spinner
    showLoading(true);
    
    // Gọi API để khôi phục backup
    $.ajax({
        url: '/api/backup/' + backupId + '/restore',
        type: 'POST',
        success: function(response) {
            if (response.success) {
                showToast('success', 'Đã khôi phục backup thành công');
            } else {
                showToast('error', 'Không thể khôi phục backup: ' + response.error);
            }
        },
        error: function(xhr, status, error) {
            console.error('Lỗi khi khôi phục backup:', error);
            showToast('error', 'Lỗi khi khôi phục backup: ' + error);
        },
        complete: function() {
            showLoading(false);
        }
    });
}

/**
 * Khôi phục export
 * @param {string} exportId - ID của export
 */
function restoreExport(exportId) {
    // Hiển thị loading spinner
    showLoading(true);
    
    // Gọi API để khôi phục export
    $.ajax({
        url: '/api/backup/export/' + exportId + '/restore',
        type: 'POST',
        success: function(response) {
            if (response.success) {
                showToast('success', 'Đã áp dụng export thành công');
            } else {
                showToast('error', 'Không thể áp dụng export: ' + response.error);
            }
        },
        error: function(xhr, status, error) {
            console.error('Lỗi khi áp dụng export:', error);
            showToast('error', 'Lỗi khi áp dụng export: ' + error);
        },
        complete: function() {
            showLoading(false);
        }
    });
}

/**
 * Xóa backup
 * @param {string} backupId - ID của backup
 */
function deleteBackup(backupId) {
    // Hiển thị loading spinner
    showLoading(true);
    
    // Gọi API để xóa backup
    $.ajax({
        url: '/api/backup/' + backupId,
        type: 'DELETE',
        success: function(response) {
            if (response.success) {
                showToast('success', 'Đã xóa backup thành công');
                loadBackups();
            } else {
                showToast('error', 'Không thể xóa backup: ' + response.error);
            }
        },
        error: function(xhr, status, error) {
            console.error('Lỗi khi xóa backup:', error);
            showToast('error', 'Lỗi khi xóa backup: ' + error);
        },
        complete: function() {
            showLoading(false);
        }
    });
}

/**
 * Xóa export
 * @param {string} exportId - ID của export
 */
function deleteExport(exportId) {
    // Hiển thị loading spinner
    showLoading(true);
    
    // Gọi API để xóa export
    $.ajax({
        url: '/api/backup/export/' + exportId,
        type: 'DELETE',
        success: function(response) {
            if (response.success) {
                showToast('success', 'Đã xóa export thành công');
                loadExports();
            } else {
                showToast('error', 'Không thể xóa export: ' + response.error);
            }
        },
        error: function(xhr, status, error) {
            console.error('Lỗi khi xóa export:', error);
            showToast('error', 'Lỗi khi xóa export: ' + error);
        },
        complete: function() {
            showLoading(false);
        }
    });
}

/**
 * Chỉnh sửa lịch backup
 * @param {string} scheduleId - ID của lịch
 */
function editSchedule(scheduleId) {
    // Hiển thị loading spinner
    showLoading(true);
    
    // Gọi API để lấy thông tin lịch
    $.ajax({
        url: '/api/backup/schedule/' + scheduleId,
        type: 'GET',
        success: function(response) {
            if (response.success) {
                const schedule = response.data;
                
                // Điền dữ liệu vào form
                $('#scheduleModalLabel').text('Chỉnh Sửa Lịch Backup');
                $('#scheduleId').val(schedule.id);
                $('#scheduleName').val(schedule.name);
                $('#scheduleDevice').val(schedule.deviceId);
                $('#scheduleType').val(schedule.type);
                updateScheduleFields();
                
                if (schedule.type === 'weekly') {
                    $('#scheduleWeekday').val(schedule.weekday);
                } else if (schedule.type === 'monthly') {
                    $('#scheduleDay').val(schedule.day);
                }
                
                $('#scheduleTime').val(schedule.time);
                $('#scheduleRetention').val(schedule.retention);
                $('#scheduleIncludeSensitive').prop('checked', schedule.includeSensitive);
                
                // Hiển thị modal
                $('#scheduleModal').modal('show');
            } else {
                showToast('error', 'Không thể tải thông tin lịch: ' + response.error);
            }
        },
        error: function(xhr, status, error) {
            console.error('Lỗi khi tải thông tin lịch:', error);
            showToast('error', 'Lỗi khi tải thông tin lịch: ' + error);
        },
        complete: function() {
            showLoading(false);
        }
    });
}

/**
 * Lưu lịch backup
 */
function saveSchedule() {
    // Thu thập dữ liệu từ form
    const scheduleId = $('#scheduleId').val();
    const name = $('#scheduleName').val();
    const deviceId = $('#scheduleDevice').val();
    const type = $('#scheduleType').val();
    const time = $('#scheduleTime').val();
    const retention = $('#scheduleRetention').val();
    const includeSensitive = $('#scheduleIncludeSensitive').is(':checked');
    
    // Thông tin bổ sung dựa trên loại lịch
    let additionalData = {};
    if (type === 'weekly') {
        additionalData.weekday = $('#scheduleWeekday').val();
    } else if (type === 'monthly') {
        additionalData.day = $('#scheduleDay').val();
    }
    
    // Chuẩn bị dữ liệu
    const scheduleData = {
        name: name,
        deviceId: deviceId,
        type: type,
        time: time,
        retention: retention,
        includeSensitive: includeSensitive,
        ...additionalData
    };
    
    // Hiển thị loading spinner
    showLoading(true);
    
    // URL và method dựa trên việc tạo mới hay cập nhật
    const url = scheduleId ? '/api/backup/schedule/' + scheduleId : '/api/backup/schedule';
    const method = scheduleId ? 'PUT' : 'POST';
    
    // Gọi API để lưu lịch
    $.ajax({
        url: url,
        type: method,
        contentType: 'application/json',
        data: JSON.stringify(scheduleData),
        success: function(response) {
            if (response.success) {
                showToast('success', 'Đã lưu lịch backup thành công');
                $('#scheduleModal').modal('hide');
                loadSchedules();
            } else {
                showToast('error', 'Không thể lưu lịch backup: ' + response.error);
            }
        },
        error: function(xhr, status, error) {
            console.error('Lỗi khi lưu lịch backup:', error);
            showToast('error', 'Lỗi khi lưu lịch backup: ' + error);
        },
        complete: function() {
            showLoading(false);
        }
    });
}

/**
 * Bật/tắt lịch backup
 * @param {string} scheduleId - ID của lịch
 * @param {boolean} active - Trạng thái mới
 */
function toggleSchedule(scheduleId, active) {
    // Hiển thị loading spinner
    showLoading(true);
    
    // Gọi API để bật/tắt lịch
    $.ajax({
        url: '/api/backup/schedule/' + scheduleId + '/toggle',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({ active: active }),
        success: function(response) {
            if (response.success) {
                showToast('success', active ? 'Đã kích hoạt lịch backup' : 'Đã tạm dừng lịch backup');
                loadSchedules();
            } else {
                showToast('error', 'Không thể thay đổi trạng thái lịch: ' + response.error);
            }
        },
        error: function(xhr, status, error) {
            console.error('Lỗi khi thay đổi trạng thái lịch:', error);
            showToast('error', 'Lỗi khi thay đổi trạng thái lịch: ' + error);
        },
        complete: function() {
            showLoading(false);
        }
    });
}

/**
 * Xóa lịch backup
 * @param {string} scheduleId - ID của lịch
 */
function deleteSchedule(scheduleId) {
    // Hiển thị loading spinner
    showLoading(true);
    
    // Gọi API để xóa lịch
    $.ajax({
        url: '/api/backup/schedule/' + scheduleId,
        type: 'DELETE',
        success: function(response) {
            if (response.success) {
                showToast('success', 'Đã xóa lịch backup thành công');
                loadSchedules();
            } else {
                showToast('error', 'Không thể xóa lịch backup: ' + response.error);
            }
        },
        error: function(xhr, status, error) {
            console.error('Lỗi khi xóa lịch backup:', error);
            showToast('error', 'Lỗi khi xóa lịch backup: ' + error);
        },
        complete: function() {
            showLoading(false);
        }
    });
}

/**
 * Định dạng kích thước file
 * @param {number} bytes - Kích thước tính bằng bytes
 * @returns {string} Kích thước đã định dạng
 */
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

/**
 * Định dạng ngày
 * @param {string} dateString - Chuỗi ngày
 * @returns {string} Ngày đã định dạng
 */
function formatDate(dateString) {
    if (!dateString) return '';
    
    const date = new Date(dateString);
    return `${date.getDate().toString().padStart(2, '0')}/${(date.getMonth() + 1).toString().padStart(2, '0')}/${date.getFullYear()} ${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}:${date.getSeconds().toString().padStart(2, '0')}`;
}

/**
 * Định dạng tần suất lịch
 * @param {Object} schedule - Thông tin lịch
 * @returns {string} Tần suất đã định dạng
 */
function formatScheduleFrequency(schedule) {
    const timeString = schedule.time || '00:00';
    
    if (schedule.type === 'daily') {
        return `Hàng ngày, ${timeString}`;
    } else if (schedule.type === 'weekly') {
        const weekdays = ['Chủ Nhật', 'Thứ Hai', 'Thứ Ba', 'Thứ Tư', 'Thứ Năm', 'Thứ Sáu', 'Thứ Bảy'];
        const weekday = weekdays[parseInt(schedule.weekday)];
        return `Hàng tuần, ${weekday} ${timeString}`;
    } else if (schedule.type === 'monthly') {
        let dayString = '';
        if (schedule.day === 'last') {
            dayString = 'Ngày cuối tháng';
        } else {
            dayString = `Ngày ${schedule.day}`;
        }
        return `Hàng tháng, ${dayString} ${timeString}`;
    }
    
    return 'Không xác định';
}

/**
 * Hiển thị loading spinner
 * @param {boolean} show - true để hiển thị, false để ẩn
 */
function showLoading(show) {
    if (show) {
        // Nếu chưa có spinner, tạo mới
        if ($('#loadingSpinner').length === 0) {
            $('body').append('<div id="loadingSpinner" class="loading-spinner"><div class="spinner-border text-primary" role="status"><span class="visually-hidden">Đang tải...</span></div></div>');
        }
        $('#loadingSpinner').show();
    } else {
        $('#loadingSpinner').hide();
    }
}

/**
 * Hiển thị thông báo toast
 * @param {string} type - Kiểu thông báo (success, error, warning, info)
 * @param {string} message - Nội dung thông báo
 */
function showToast(type, message) {
    // Màu sắc theo loại
    var bgClass = 'bg-primary';
    switch (type) {
        case 'success':
            bgClass = 'bg-success';
            break;
        case 'error':
            bgClass = 'bg-danger';
            break;
        case 'warning':
            bgClass = 'bg-warning';
            break;
        case 'info':
            bgClass = 'bg-info';
            break;
    }
    
    // Tạo ID duy nhất cho toast
    var toastId = 'toast-' + Date.now();
    
    // HTML cho toast
    var toastHtml = `
        <div id="${toastId}" class="toast align-items-center ${bgClass} text-white border-0" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        </div>
    `;
    
    // Thêm toast vào container hoặc tạo mới nếu chưa có
    if ($('#toastContainer').length === 0) {
        $('body').append('<div id="toastContainer" class="toast-container position-fixed bottom-0 end-0 p-3"></div>');
    }
    
    // Thêm toast vào container và hiển thị
    $('#toastContainer').append(toastHtml);
    var toast = new bootstrap.Toast(document.getElementById(toastId), {
        delay: 5000
    });
    toast.show();
}