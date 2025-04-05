import streamlit as st
import sqlite3
import hashlib
import pandas as pd
import base64
from datetime import datetime

def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')

def show_dashboard():
    # ----- Phần header với logo PTIT -----
    col1, col2 = st.columns([1, 4])
    with col1:
        # Logo PTIT (thay bằng URL hình ảnh thực tế của bạn)
        st.image("https://www.google.com/url?sa=i&url=https%3A%2F%2Fdownloadlogomienphi.com%2Flogo%2Fdownload-logo-vector-hoc-vien-cong-nghe-buu-chinh-vien-thong-ptit-mien-phi&psig=AOvVaw0-7dXW-7Ou0xPEgU7csBQI&ust=1743920545834000&source=images&cd=vfe&opi=89978449&ved=0CBUQjRxqFwoTCNC27LagwIwDFQAAAAAdAAAAABAE"
                 , width=120)
    with col2:
        st.title("HỆ THỐNG QUẢN LÝ KÝ TÚC XÁ")
        st.markdown("**DỊCH VỤ SỐ DÀNH CHO SINH VIÊN LƯU TRÚ**")
    
    st.divider()
    
    # ----- 4 chỉ số chính -----
    st.subheader("📊 THỐNG KÊ NHANH")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Tổng sinh viên", 150, "+5 so với tháng trước")
    with col2:
        st.metric("Phòng đang sử dụng", "85/120", "71% lấp đầy")
    with col3:
        st.metric("Doanh thu tháng", "45,200,000₫", "+12%")
    with col4:
        st.metric("Hóa đơn chờ", 8, "2 quá hạn")

    # ----- Biểu đồ -----
    st.subheader("📈 BIỂU ĐỒ THỐNG KÊ")
    tab1, tab2 = st.tabs(["DOANH THU", "PHÂN BỔ PHÒNG"])
    
    with tab1:
        # Dữ liệu mẫu - thay bằng query từ database
        revenue_data = pd.DataFrame({
            'Tháng': ['1/2024', '2/2024', '3/2024', '4/2024'],
            'Doanh thu': [42000000, 38000000, 45000000, 45200000]
        })
        st.bar_chart(revenue_data.set_index('Tháng'))
        
    with tab2:
        room_data = pd.DataFrame({
            'Loại phòng': ['Đơn', 'Đôi', '4 người'],
            'Số lượng': [30, 60, 30],
            'Trống': [5, 10, 8]
        })
        st.bar_chart(room_data.set_index('Loại phòng'))

    # ----- Cảnh báo -----
    st.subheader("⚠️ CẢNH BÁO HỆ THỐNG")
    
    with st.expander("Hóa đơn chưa thanh toán (5)"):
        # Dữ liệu mẫu
        overdue_invoices = pd.DataFrame({
            'Mã hóa đơn': ['INV2024001', 'INV2024002', 'INV2024005'],
            'Sinh viên': ['Nguyễn Văn A', 'Trần Thị B', 'Lê Văn C'],
            'Số tiền': [1500000, 1800000, 2000000],
            'Hạn thanh toán': ['15/04/2024', '20/04/2024', '25/04/2024'],
            'Trạng thái': ['Quá hạn', 'Sắp hết hạn', 'Sắp hết hạn']
        })
        st.dataframe(overdue_invoices, hide_index=True, use_container_width=True)
    
    with st.expander("Phòng sắp hết hợp đồng (3)"):
        expiring_rooms = pd.DataFrame({
            'Phòng': ['A101', 'B205', 'C302'],
            'Tòa nhà': ['A', 'B', 'C'],
            'Số SV': [1, 2, 4],
            'Hạn hợp đồng': ['30/04/2024', '02/05/2024', '05/05/2024']
        })
        st.dataframe(expiring_rooms, hide_index=True, use_container_width=True)

    # ----- Footer -----
    st.divider()
    st.caption("© 2024 Học viện Công nghệ Bưu chính Viễn thông - Phát triển bởi Nhóm SV Khoa VT1")

# ----- Database Setup -----
def init_db():
    conn = sqlite3.connect('ktx.db')
    c = conn.cursor()
    
    # Bảng tài khoản
    c.execute('''CREATE TABLE IF NOT EXISTS accounts (
                 username TEXT PRIMARY KEY,
                 password TEXT,
                 role TEXT CHECK(role IN ('student', 'staff', 'admin'))
              )''')
    
    # Bảng sinh viên
    c.execute('''CREATE TABLE IF NOT EXISTS students (
                 student_id TEXT PRIMARY KEY,
                 full_name TEXT NOT NULL,
                 dob DATE,
                 phone TEXT,
                 class TEXT,
                 room_id TEXT
              )''')
    
    # Bảng nhân viên
    c.execute('''CREATE TABLE IF NOT EXISTS staff (
                 staff_id TEXT PRIMARY KEY,
                 full_name TEXT NOT NULL,
                 position TEXT,
                 department TEXT
              )''')
    
    # Bảng phòng
    c.execute('''CREATE TABLE IF NOT EXISTS rooms (
                 room_id TEXT PRIMARY KEY,
                 type TEXT,
                 capacity INTEGER,
                 current_occupancy INTEGER DEFAULT 0,
                 amenities TEXT,
                 status TEXT DEFAULT 'available'
              )''')
    
    # Bảng hóa đơn
    c.execute('''CREATE TABLE IF NOT EXISTS invoices (
                 invoice_id TEXT PRIMARY KEY,
                 student_id TEXT,
                 amount REAL,
                 issue_date DATE,
                 due_date DATE,
                 status TEXT DEFAULT 'unpaid',
                 FOREIGN KEY(student_id) REFERENCES students(student_id)
              )''')
    
    # Tài khoản admin mặc định
    c.execute("INSERT OR IGNORE INTO accounts VALUES (?,?,?)", 
              ("admin", hash_password("admin123"), "admin"))
    conn.commit()
    conn.close()

# ----- Helper Functions -----
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def authenticate(username, password):
    conn = sqlite3.connect('ktx.db')
    c = conn.cursor()
    c.execute("SELECT * FROM accounts WHERE username=? AND password=?", 
              (username, hash_password(password)))
    result = c.fetchone()
    conn.close()
    return result

def get_db_connection():
    return sqlite3.connect('ktx.db')

# ----- Authentication -----
def login_page():
    # Custom CSS tối giản
    st.markdown("""
    <style>
        .login-container {
            max-width: 400px;
            margin: 0 auto;
            padding: 2rem;
            border-radius: 2px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            background: white;
            margin-top: 0.5vh;
        }
        .ptit-logo {
            display: block;
            margin: 0 auto 1rem;
            height: 60px;
        }
        .login-title {
            text-align: center;
            color: #0062cc;
            margin-bottom: 0.5rem;
            font-size: 1.5rem;
            font-weight: bold;
        }
        .login-subtitle {
            text-align: center;
            color: red;
            margin-bottom: 2rem;
            font-size: 0.9rem;
        }
        .stTextInput>div>div>input {
            padding: 10px;
            border-radius: 4px;
        }
        .stButton>button {
            width: 100%;
            padding: 10px;
            background: #0062cc;
            color: white;
            border: none;
            border-radius: 4px;
            font-weight: bold;
        }
        .forgot-link {
            text-align: right;
            margin-top: -10px;
            margin-bottom: 1rem;
        }
        .forgot-link a {
            color: #0062cc;
            font-size: 0.8rem;
            text-decoration: none;
        }
        .footer {
            text-align: center;
            margin-top: 2rem;
            color: #666;
            font-size: 0.8rem;
        }
    </style>
    """, unsafe_allow_html=True)

    # Container chính
    with st.container():
        col1, col2 = st.columns([1, 10], gap="medium")
        with col1:
            st.image("images/Logo_PTIT.png", width=120, output_format="auto")
        with col2:
            st.markdown("""
            <div class="login-container">
                <div class="login-title">HỆ THỐNG QUẢN LÝ KÝ TÚC XÁ</div>
                <div class="login-subtitle">DỊCH VỤ SỐ DÀNH CHO SINH VIÊN LƯU TRÚ</div>
            """, unsafe_allow_html=True)

        # Form đăng nhập
        with st.form("login_form"):
            username = st.text_input("Tên đăng nhập", placeholder="Username")
            password = st.text_input("Mật khẩu", type="password", placeholder="Password")
            
            st.markdown('<div class="forgot-link"><a href="#">Quên mật khẩu?</a></div>', unsafe_allow_html=True)
            
            if st.form_submit_button("ĐĂNG NHẬP", use_container_width=True):
                user = authenticate(username, password)
                if user:
                    st.session_state.user = user
                    st.rerun()
                else:
                    st.error("Tài khoản hoặc mật khẩu không chính xác")

        st.markdown("""
            <div class="footer">
                © 2025 Học viện Công nghệ Bưu chính Viễn thông<br>
                Phiên bản 1.0.0
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Ẩn các element không cần thiết
    hide_streamlit_style = """
        <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
        </style>
    """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# ----- Student Management -----
def student_management():
    st.header("👨‍🎓 Quản lý Sinh viên")
    tab1, tab2, tab3, tab4 = st.tabs(["Thêm SV", "Cập nhật TT", "Danh sách SV", "Xóa SV"])
    
    with tab1:
        with st.form("add_student"):
            st.subheader("Thêm sinh viên mới")
            student_id = st.text_input("Mã SV*")
            full_name = st.text_input("Họ tên*")
            dob = st.date_input("Ngày sinh")
            phone = st.text_input("Số điện thoại")
            student_class = st.text_input("Lớp")
            
            if st.form_submit_button("Lưu"):
                if not student_id or not full_name:
                    st.error("Vui lòng nhập các trường bắt buộc (*)")
                else:
                    try:
                        conn = get_db_connection()
                        conn.execute("INSERT INTO students VALUES (?,?,?,?,?,NULL)", 
                                    (student_id, full_name, dob, phone, student_class))
                        conn.commit()
                        st.success("Thêm sinh viên thành công!")
                    except sqlite3.IntegrityError:
                        st.error("Mã sinh viên đã tồn tại!")
                    finally:
                        conn.close()
    
    with tab2:
        conn = get_db_connection()
        students = conn.execute("SELECT student_id, full_name FROM students").fetchall()
        conn.close()
        
        selected_student = st.selectbox("Chọn sinh viên", 
                                      [f"{s[0]} - {s[1]}" for s in students])
        
        if selected_student:
            student_id = selected_student.split(" - ")[0]
            conn = get_db_connection()
            student = conn.execute("SELECT * FROM students WHERE student_id=?", 
                                 (student_id,)).fetchone()
            conn.close()
            
            with st.form("update_student"):
                new_phone = st.text_input("Số điện thoại mới", value=student[3])
                new_class = st.text_input("Lớp mới", value=student[4])
                
                if st.form_submit_button("Cập nhật"):
                    conn = get_db_connection()
                    conn.execute("UPDATE students SET phone=?, class=? WHERE student_id=?", 
                               (new_phone, new_class, student_id))
                    conn.commit()
                    conn.close()
                    st.success("Cập nhật thành công!")

    with tab3:
        conn = get_db_connection()
        df = pd.read_sql("SELECT * FROM students", conn)
        conn.close()
        st.dataframe(df)
    with tab4:
        conn = get_db_connection()
        students = conn.execute("SELECT student_id, full_name FROM students").fetchall()
        conn.close()
        
        selected_student = st.selectbox("Chọn sinh viên cần xóa", 
                                      [f"{s[0]} - {s[1]}" for s in students],
                                      key="delete_student_select")
        
        if selected_student and st.button("Xóa sinh viên", key="delete_student_btn"):
            student_id = selected_student.split(" - ")[0]
            try:
                conn = get_db_connection()
                
                # Kiểm tra ràng buộc trước khi xóa
                has_invoice = conn.execute("SELECT 1 FROM invoices WHERE student_id=?", 
                                         (student_id,)).fetchone()
                if has_invoice:
                    st.warning("Không thể xóa vì sinh viên có hóa đơn liên quan!")
                else:
                    conn.execute("DELETE FROM students WHERE student_id=?", (student_id,))
                    conn.commit()
                    st.success("Đã xóa sinh viên thành công!")
                    st.rerun()
            except Exception as e:
                st.error(f"Lỗi khi xóa: {str(e)}")
            finally:
                conn.close()

# ----- Staff Management -----
def staff_management():
    if st.session_state.user[2] != 'admin':
        st.warning("Chỉ quản trị viên được truy cập")
        return
    
    st.header("👔 Quản lý Nhân viên")
    tab1, tab2, tab3 = st.tabs(["Thêm NV", "Danh sách NV", "Xóa NV"])
    
    with tab1:
        with st.form("add_staff"):
            staff_id = st.text_input("Mã nhân viên*")
            full_name = st.text_input("Họ tên*")
            position = st.selectbox("Chức vụ", ["Quản lý", "Nhân viên", "Bảo vệ"])
            department = st.text_input("Phòng ban")
            
            if st.form_submit_button("Lưu"):
                if not staff_id or not full_name:
                    st.error("Vui lòng nhập các trường bắt buộc (*)")
                else:
                    try:
                        conn = get_db_connection()
                        # Thêm vào bảng staff
                        conn.execute("INSERT INTO staff VALUES (?,?,?,?)", 
                                    (staff_id, full_name, position, department))
                        # Tạo tài khoản đăng nhập
                        conn.execute("INSERT INTO accounts VALUES (?,?,?)", 
                                    (staff_id, hash_password("123456"), "staff"))
                        conn.commit()
                        st.success(f"Đã thêm nhân viên {full_name}!")
                    except sqlite3.IntegrityError:
                        st.error("Mã nhân viên đã tồn tại!")
                    finally:
                        conn.close()
    
    with tab2:
        conn = get_db_connection()
        df = pd.read_sql("SELECT * FROM staff", conn)
        conn.close()
        st.dataframe(df)
    
    with tab3:
        conn = get_db_connection()
        staff_list = conn.execute("SELECT staff_id, full_name FROM staff").fetchall()
        conn.close()
        
        selected_staff = st.selectbox("Chọn nhân viên cần xóa", 
                                    [f"{s[0]} - {s[1]}" for s in staff_list],
                                    key="delete_staff_select")
        
        if selected_staff and st.button("Xóa nhân viên", key="delete_staff_btn"):
            staff_id = selected_staff.split(" - ")[0]
            try:
                conn = get_db_connection()
                
                # Xóa cả tài khoản đăng nhập
                conn.execute("DELETE FROM staff WHERE staff_id=?", (staff_id,))
                conn.execute("DELETE FROM accounts WHERE username=?", (staff_id,))
                conn.commit()
                st.success("Đã xóa nhân viên thành công!")
                st.rerun()
            except Exception as e:
                st.error(f"Lỗi khi xóa: {str(e)}")
            finally:
                conn.close()

# ----- Room Management -----
def room_management():
    st.header("🏠 Quản lý Phòng ở")
    tab1, tab2, tab3, tab4 = st.tabs(["Thêm phòng", "Đăng ký phòng", "DS phòng", "Xóa phòng"])
    
    with tab1:
        with st.form("add_room"):
            room_id = st.text_input("Mã phòng*")
            room_type = st.selectbox("Loại phòng*", ["Phòng đơn", "Phòng đôi", "Phòng 4 người"])
            capacity = st.number_input("Sức chứa*", min_value=1, value=2)
            amenities = st.multiselect("Tiện nghi", ["Điều hòa", "Nóng lạnh", "Wifi", "Tủ lạnh"])
            
            if st.form_submit_button("Thêm phòng"):
                if not room_id:
                    st.error("Vui lòng nhập mã phòng")
                else:
                    try:
                        conn = get_db_connection()
                        conn.execute("INSERT INTO rooms (room_id, type, capacity, amenities) VALUES (?,?,?,?)",
                                   (room_id, room_type, capacity, ",".join(amenities)))
                        conn.commit()
                        st.success("Thêm phòng thành công!")
                    except sqlite3.IntegrityError:
                        st.error("Mã phòng đã tồn tại!")
                    finally:
                        conn.close()
    
    with tab2:
        conn = get_db_connection()
        students = conn.execute("SELECT student_id, full_name FROM students WHERE room_id IS NULL").fetchall()
        rooms = conn.execute("SELECT room_id FROM rooms WHERE status='available'").fetchall()
        conn.close()
        
        with st.form("assign_room"):
            student = st.selectbox("Chọn sinh viên", [f"{s[0]} - {s[1]}" for s in students])
            room = st.selectbox("Chọn phòng", [r[0] for r in rooms])
            
            if st.form_submit_button("Đăng ký phòng"):
                student_id = student.split(" - ")[0]
                try:
                    conn = get_db_connection()
                    # Cập nhật phòng cho sinh viên
                    conn.execute("UPDATE students SET room_id=? WHERE student_id=?", 
                               (room, student_id))
                    # Cập nhật trạng thái phòng
                    conn.execute("UPDATE rooms SET current_occupancy = current_occupancy + 1 WHERE room_id=?", 
                               (room,))
                    conn.commit()
                    st.success("Đăng ký phòng thành công!")
                except Exception as e:
                    st.error(f"Lỗi: {str(e)}")
                finally:
                    conn.close()
    
    with tab3:
        conn = get_db_connection()
        df = pd.read_sql("SELECT * FROM rooms", conn)
        conn.close()
        st.dataframe(df)
    
    with tab4:
        conn = get_db_connection()
        rooms = conn.execute("SELECT room_id FROM rooms WHERE current_occupancy = 0").fetchall()
        conn.close()
        
        selected_room = st.selectbox("Chọn phòng trống cần xóa", 
                                   [r[0] for r in rooms],
                                   key="delete_room_select")
        
        if selected_room and st.button("Xóa phòng", key="delete_room_btn"):
            try:
                conn = get_db_connection()
                conn.execute("DELETE FROM rooms WHERE room_id=?", (selected_room,))
                conn.commit()
                st.success("Đã xóa phòng thành công!")
                st.rerun()
            except Exception as e:
                st.error(f"Lỗi khi xóa: {str(e)}")
            finally:
                conn.close()

# ----- Invoice Management -----
def invoice_management():
    st.header("💰 Quản lý Hóa đơn")
    tab1, tab2, tab3 = st.tabs(["Tạo hóa đơn", "Thanh toán", "Xóa hóa đơn"])
    
    with tab1:
        conn = get_db_connection()
        students = conn.execute("SELECT student_id, full_name FROM students").fetchall()
        conn.close()
        
        with st.form("create_invoice"):
            student = st.selectbox("Chọn sinh viên", [f"{s[0]} - {s[1]}" for s in students])
            amount = st.number_input("Số tiền*", min_value=0)
            due_date = st.date_input("Hạn thanh toán*")
            
            if st.form_submit_button("Tạo hóa đơn"):
                student_id = student.split(" - ")[0]
                invoice_id = f"INV{datetime.now().strftime('%Y%m%d%H%M%S')}"
                try:
                    conn = get_db_connection()
                    conn.execute("INSERT INTO invoices VALUES (?,?,?,?,?,?)",
                               (invoice_id, student_id, amount, datetime.now().date(), due_date, "unpaid"))
                    conn.commit()
                    st.success(f"Đã tạo hóa đơn {invoice_id}")
                except Exception as e:
                    st.error(f"Lỗi: {str(e)}")
                finally:
                    conn.close()
    
    with tab2:
        conn = get_db_connection()
        invoices = conn.execute('''SELECT i.invoice_id, s.full_name, i.amount, i.due_date, i.status 
                                FROM invoices i JOIN students s ON i.student_id = s.student_id''').fetchall()
        conn.close()
        
        selected_invoice = st.selectbox("Chọn hóa đơn", 
                                      [f"{inv[0]} - {inv[1]} - {inv[2]}đ - {inv[4]}" for inv in invoices])
        
        if selected_invoice and st.button("Đánh dấu đã thanh toán"):
            invoice_id = selected_invoice.split(" - ")[0]
            try:
                conn = get_db_connection()
                conn.execute("UPDATE invoices SET status='paid' WHERE invoice_id=?", (invoice_id,))
                conn.commit()
                st.success("Cập nhật trạng thái thành công!")
                st.rerun()
            except Exception as e:
                st.error(f"Lỗi: {str(e)}")
            finally:
                conn.close()
        
    with tab3:
        conn = get_db_connection()
        invoices = conn.execute('''SELECT i.invoice_id, s.full_name, i.amount 
                                FROM invoices i JOIN students s ON i.student_id = s.student_id
                                WHERE i.status='unpaid' ''').fetchall()
        conn.close()
        
        selected_invoice = st.selectbox("Chọn hóa đơn chưa thanh toán cần xóa", 
                                      [f"{inv[0]} - {inv[1]} - {inv[2]}đ" for inv in invoices],
                                      key="delete_invoice_select")
        
        if selected_invoice and st.button("Xóa hóa đơn", key="delete_invoice_btn"):
            invoice_id = selected_invoice.split(" - ")[0]
            try:
                conn = get_db_connection()
                conn.execute("DELETE FROM invoices WHERE invoice_id=?", (invoice_id,))
                conn.commit()
                st.success("Đã xóa hóa đơn thành công!")
                st.rerun()
            except Exception as e:
                st.error(f"Lỗi khi xóa: {str(e)}")
            finally:
                conn.close()

# ----- Report -----
def report():
    st.header("📊 Báo cáo thống kê")
    
    conn = get_db_connection()
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Thống kê phòng")
        room_stats = pd.read_sql('''
            SELECT type, COUNT(*) as total, 
                   SUM(CASE WHEN status='available' THEN 1 ELSE 0 END) as available
            FROM rooms
            GROUP BY type
        ''', conn)
        st.dataframe(room_stats)
        
    with col2:
        st.subheader("Doanh thu")
        revenue = pd.read_sql('''
            SELECT strftime('%Y-%m', issue_date) as month,
                   SUM(CASE WHEN status='paid' THEN amount ELSE 0 END) as paid,
                   SUM(CASE WHEN status='unpaid' THEN amount ELSE 0 END) as unpaid
            FROM invoices
            GROUP BY month
        ''', conn)
        st.dataframe(revenue)
    
    if st.button("Xuất báo cáo"):
        with st.spinner("Đang tạo báo cáo..."):
            report_data = pd.read_sql('''
                SELECT s.student_id, s.full_name, r.room_id, 
                       i.amount, i.status, i.due_date
                FROM students s
                LEFT JOIN rooms r ON s.room_id = r.room_id
                LEFT JOIN invoices i ON s.student_id = i.student_id
            ''', conn)
            
            st.download_button(
                label="Tải xuống Excel",
                data=report_data.to_csv(index=False).encode('utf-8'),
                file_name="bao_cao_ktx.csv",
                mime="text/csv"
            )
    
    conn.close()

# ----- Main App -----
def main():
    st.set_page_config(
        page_title="Hệ thống QL KTX",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    init_db()
    
    if 'user' not in st.session_state:
        login_page()
    else:
        st.sidebar.title(f"Xin chào {st.session_state.user[0]}")
        if st.sidebar.button("Đăng xuất"):
            del st.session_state.user
            st.rerun()
        
        menu_options = {
            "Dashboard": show_dashboard,
            "Quản lý Sinh viên": student_management,
            "Quản lý Nhân viên": staff_management,
            "Quản lý Phòng ở": room_management,
            "Quản lý Hóa đơn": invoice_management,
            "Báo cáo": report
        }
        
        selected = st.sidebar.selectbox("Menu", list(menu_options.keys()))
        menu_options[selected]()

if __name__ == "__main__":
    main()
