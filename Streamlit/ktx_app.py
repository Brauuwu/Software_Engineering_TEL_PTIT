import streamlit as st
import sqlite3
import hashlib
import pandas as pd
from datetime import datetime

def show_dashboard():
    # ----- Phần header với logo PTIT -----
    col1, col2 = st.columns([1, 4])
    with col1:
        # Logo PTIT (thay bằng URL hình ảnh thực tế của bạn)
        st.image("https://upload.wikimedia.org/wikipedia/commons/d/d7/Logo_PTIT.jpg"
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
    c.execute("SELECT username, role FROM accounts WHERE username=? AND password=?",
              (username, hash_password(password)))
    result = c.fetchone()
    conn.close()
    return result

def get_db_connection():
    return sqlite3.connect('ktx.db')

# ----- Account Management -----
def account_management():
    if st.session_state.user[1] != 'admin':
        st.warning("Chỉ quản trị viên được truy cập")
        return

    st.header("👤 Quản lý tài khoản")
    tab1, tab2 = st.tabs(["Tạo tài khoản", "Danh sách tài khoản"])

    with tab1:
        with st.form("create_account"):
            st.subheader("Tạo tài khoản mới")
            username = st.text_input("Tên người dùng*")
            password = st.text_input("Mật khẩu*", type="password")
            role = st.selectbox("Vai trò", ["admin", "staff", "student"])

            if st.form_submit_button("Tạo"):
                if not username or not password:
                    st.error("Vui lòng nhập các trường bắt buộc (*)")
                else:
                    try:
                        conn = get_db_connection()
                        conn.execute("INSERT INTO accounts VALUES (?,?,?)",
                                     (username, hash_password(password), role))
                        conn.commit()
                        st.success(f"Đã tạo tài khoản {username} với vai trò {role}!")
                    except sqlite3.IntegrityError:
                        st.error("Tên người dùng đã tồn tại!")
                    finally:
                        conn.close()

    with tab2:
        st.subheader("Danh sách tài khoản")
        conn = get_db_connection()
        df = pd.read_sql("SELECT username, role FROM accounts", conn)
        conn.close()
        st.dataframe(df)

        # Xóa tài khoản
        st.subheader("Xóa tài khoản")
        username_to_delete = st.selectbox("Chọn tài khoản để xóa", df['username'])
        if username_to_delete == "admin":
            st.warning("Không thể xóa tài khoản admin!")
        if st.button("Xóa tài khoản"):
            try:
                conn = get_db_connection()
                conn.execute("DELETE FROM accounts WHERE username=?", (username_to_delete,))
                conn.commit()
                st.success(f"Đã xóa tài khoản {username_to_delete}!")
                st.rerun()  # Refresh để cập nhật danh sách tài khoản
            except Exception as e:
                st.error(f"Lỗi khi xóa: {str(e)}")
            finally:
                conn.close()

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
            st.image("https://upload.wikimedia.org/wikipedia/commons/d/d7/Logo_PTIT.jpg"
                 , width=120)
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
                        st.session_state.user = user  # Lưu (username, role)
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

    # Kiểm tra quyền truy cập
    if st.session_state.user[1] not in ['admin', 'staff']:
        st.warning("Bạn không có quyền truy cập chức năng này.")
        return

    tab1, tab2, tab3, tab4 = st.tabs(["Thêm SV", "Cập nhật TT", "Danh sách SV", "Xóa SV"])

    with tab1:

        # Kiểm tra quyền truy cập
        if st.session_state.user[1] not in ['admin', 'staff']:
            st.warning("Bạn không có quyền thêm sinh viên.")
            return

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
        # Kiểm tra quyền truy cập
        if st.session_state.user[1] not in ['admin', 'staff']:
            st.warning("Bạn không có quyền cập nhật thông tin sinh viên.")
            return

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
        students = conn.execute("SELECT student_id, full_name, room_id FROM students").fetchall()
        conn.close()
        
        selected_student = st.selectbox("Chọn sinh viên cần xóa", 
                                      [f"{s[0]} - {s[1]}" for s in students],
                                      key="delete_student_select")
        
        if selected_student and st.button("Xóa sinh viên", key="delete_student_btn"):
            student_id = selected_student.split(" - ")[0]
            try:
                conn = get_db_connection()
                
                # Lấy thông tin sinh viên trước khi xóa
                student = conn.execute("SELECT room_id FROM students WHERE student_id=?", (student_id,)).fetchone()
                room_id = student[0] if student else None
                
                # Kiểm tra xem sinh viên có hóa đơn chưa thanh toán không
                unpaid_invoices = conn.execute("SELECT 1 FROM invoices WHERE student_id=? AND status='unpaid'", 
                                         (student_id,)).fetchone()
                if unpaid_invoices:
                    st.warning("Không thể xóa vì sinh viên có hóa đơn chưa thanh toán!")
                else:
                    # Xóa sinh viên
                    conn.execute("DELETE FROM students WHERE student_id=?", (student_id,))
                    
                    # Nếu sinh viên có phòng, giảm số lượng người trong phòng
                    if room_id:
                        conn.execute("UPDATE rooms SET current_occupancy = MAX(0, current_occupancy - 1) WHERE room_id=?", (room_id,))

                        # Cập nhật trạng thái phòng nếu số người ở = 0
                        conn.execute("UPDATE rooms SET status = 'available' WHERE room_id=? AND current_occupancy = 0", (room_id,))
                    
                    conn.commit()
                    st.success("Đã xóa sinh viên thành công!")
                    st.rerun()
            except Exception as e:
                st.error(f"Lỗi khi xóa: {str(e)}")
            finally:
                conn.close()

# ----- Staff Management -----
def staff_management():
    if st.session_state.user[1] != 'admin':
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

    # Kiểm tra quyền truy cập
    if st.session_state.user[1] not in ['admin', 'staff']:
        st.warning("Bạn không có quyền truy cập chức năng này.")
        return

    tab1, tab2, tab3, tab4 = st.tabs(["Thêm phòng", "Đăng ký phòng", "DS phòng", "Xóa phòng"])

    with tab1:
        with st.form("add_room"):
            st.subheader("Thêm phòng mới")
            room_id = st.text_input("Mã phòng*")
            room_type = st.selectbox("Loại phòng", ["Đơn", "Đôi", "4 người"])
            capacity = st.number_input("Số người tối đa", min_value=1, max_value=4, value=2)
            amenities_list = st.multiselect("Tiện nghi", ["Điều hòa", "Nóng lạnh", "Wifi", "Tủ lạnh"])
            
            # Chuyển đổi danh sách tiện nghi thành chuỗi
            amenities = ", ".join(amenities_list)
            
            if st.form_submit_button("Lưu"):
                if not room_id:
                    st.error("Vui lòng nhập mã phòng!")
                else:
                    try:
                        conn = get_db_connection()
                        conn.execute("INSERT INTO rooms VALUES (?,?,?,0,?,?)", 
                                    (room_id, room_type, capacity, amenities, 'available'))
                        conn.commit()
                        st.success(f"Đã thêm phòng {room_id}!")
                    except sqlite3.IntegrityError:
                        st.error("Mã phòng đã tồn tại!")
                    finally:
                        conn.close()

    with tab2:
        # Kiểm tra quyền truy cập
        if st.session_state.user[1] not in ['admin', 'staff']:
            st.warning("Bạn không có quyền đăng ký phòng.")
            return

        st.subheader("Đăng ký phòng cho sinh viên")
        conn = get_db_connection()
        available_rooms = conn.execute("SELECT room_id FROM rooms WHERE status='available'").fetchall()
        students = conn.execute("SELECT student_id, full_name FROM students WHERE room_id IS NULL").fetchall()
        conn.close()

        selected_room = st.selectbox("Chọn phòng trống",
                                    [r[0] for r in available_rooms])
        selected_student = st.selectbox("Chọn sinh viên",
                                       [f"{s[0]} - {s[1]}" for s in students])

        if st.button("Đăng ký"):
            if not selected_room or not selected_student:
                st.warning("Vui lòng chọn phòng và sinh viên!")
            else:
                student_id = selected_student.split(" - ")[0]
                try:
                    conn = get_db_connection()
                    # Cập nhật room_id cho sinh viên
                    conn.execute("UPDATE students SET room_id=? WHERE student_id=?",
                                (selected_room, student_id))
                    # Tăng số người ở hiện tại của phòng
                    conn.execute("UPDATE rooms SET current_occupancy = current_occupancy + 1 WHERE room_id=?",
                                (selected_room,))
                    # Nếu phòng đầy, đổi trạng thái
                    conn.execute("""
                        UPDATE rooms
                        SET status = 'occupied'
                        WHERE room_id=? AND current_occupancy >= capacity
                    """, (selected_room,))

                    conn.commit()
                    st.success(f"Đã đăng ký phòng {selected_room} cho sinh viên {student_id}!")
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
        # Kiểm tra quyền truy cập
        if st.session_state.user[1] != 'admin':
            st.warning("Bạn không có quyền xóa phòng.")
            return

        conn = get_db_connection()
        rooms = conn.execute("SELECT room_id FROM rooms").fetchall()
        conn.close()

        selected_room = st.selectbox("Chọn phòng cần xóa",
                                    [r[0] for r in rooms],
                                    key="delete_room_select")

        if selected_room and st.button("Xóa phòng", key="delete_room_btn"):
            try:
                conn = get_db_connection()
                # Kiểm tra xem phòng có sinh viên ở không
                students_in_room = conn.execute("SELECT 1 FROM students WHERE room_id=?",
                                               (selected_room,)).fetchone()
                if students_in_room:
                    st.warning("Không thể xóa phòng đang có sinh viên ở!")
                else:
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
    st.header("🧾 Quản lý Hóa đơn")

    # Kiểm tra quyền truy cập
    if st.session_state.user[1] not in ['admin', 'staff']:
        st.warning("Bạn không có quyền truy cập chức năng này.")
        return

    tab1, tab2, tab3 = st.tabs(["Tạo hóa đơn", "DS Hóa đơn", "Thanh toán"])

    with tab1:

        # Kiểm tra quyền truy cập
        if st.session_state.user[1] not in ['admin', 'staff']:
            st.warning("Bạn không có quyền tạo hóa đơn.")
            return

        with st.form("create_invoice"):
            st.subheader("Tạo hóa đơn mới")
            conn = get_db_connection()
            students = conn.execute("SELECT student_id, full_name FROM students").fetchall()
            conn.close()

            selected_student = st.selectbox("Chọn sinh viên",
                                       [f"{s[0]} - {s[1]}" for s in students])
            amount = st.number_input("Số tiền", min_value=10000, step=1000)
            issue_date = st.date_input("Ngày lập", value=datetime.now())
            due_date = st.date_input("Hạn thanh toán")

            if st.form_submit_button("Tạo"):
                if not selected_student:
                    st.warning("Vui lòng chọn sinh viên!")
                else:
                    student_id = selected_student.split(" - ")[0]
                    invoice_id = f"INV{datetime.now().strftime('%Y%m%d%H%M%S')}"
                    try:
                        conn = get_db_connection()
                        conn.execute("INSERT INTO invoices VALUES (?,?,?,?,?,?)",
                                    (invoice_id, student_id, amount, issue_date, due_date, 'unpaid'))
                        conn.commit()
                        st.success(f"Đã tạo hóa đơn {invoice_id} cho sinh viên {student_id}!")
                    except Exception as e:
                        st.error(f"Lỗi: {str(e)}")
                    finally:
                        conn.close()

    with tab2:
        conn = get_db_connection()
        df = pd.read_sql("SELECT * FROM invoices", conn)
        conn.close()
        st.dataframe(df)

    with tab3:

        # Kiểm tra quyền truy cập
        if st.session_state.user[1] not in ['admin', 'staff']:
            st.warning("Bạn không có quyền thanh toán hóa đơn.")
            return

        st.subheader("Thanh toán hóa đơn")
        conn = get_db_connection()
        unpaid_invoices = conn.execute("SELECT invoice_id, student_id FROM invoices WHERE status='unpaid'").fetchall()
        conn.close()

        selected_invoice = st.selectbox("Chọn hóa đơn cần thanh toán",
                                      [f"{i[0]} - {i[1]}" for i in unpaid_invoices])

        if selected_invoice and st.button("Xác nhận thanh toán"):
            invoice_id = selected_invoice.split(" - ")[0]
            try:
                conn = get_db_connection()
                conn.execute("UPDATE invoices SET status='paid' WHERE invoice_id=?", (invoice_id,))
                conn.commit()
                st.success(f"Đã thanh toán hóa đơn {invoice_id}!")
                st.rerun()
            except Exception as e:
                st.error(f"Lỗi: {str(e)}")
            finally:
                conn.close()

# ----- Student Info and Payment -----
def student_info():
    st.header("ℹ️ Thông tin cá nhân")
    student_id = st.session_state.user[0]  # Tên người dùng là student_id

    conn = get_db_connection()
    student = conn.execute("SELECT * FROM students WHERE student_id=?", (student_id,)).fetchone()

    # Thêm các câu lệnh in để gỡ lỗi
    print(f"student_id: {student_id}")
    if student:
        st.subheader("Thông tin sinh viên")
        st.write(f"**Mã SV:** {student[0]}")
        st.write(f"**Họ tên:** {student[1]}")
        st.write(f"**Ngày sinh:** {student[2]}")
        st.write(f"**Số điện thoại:** {student[3]}")
        st.write(f"**Lớp:** {student[4]}")
        st.write(f"**Phòng:** {student[5] or 'Chưa có'}")

        st.subheader("Hóa đơn")
        invoices = conn.execute("SELECT * FROM invoices WHERE student_id=?", (student_id,)).fetchall()
        if invoices:
            df = pd.DataFrame(invoices, columns=['Mã hóa đơn', 'Mã SV', 'Số tiền', 'Ngày lập', 'Hạn TT', 'Trạng thái'])
            st.dataframe(df)

            # Thanh toán hóa đơn
            st.subheader("Thanh toán hóa đơn")
            unpaid_invoices = [i for i in invoices if i[5] == 'unpaid']
            if unpaid_invoices:
                selected_invoice = st.selectbox("Chọn hóa đơn cần thanh toán", [i[0] for i in unpaid_invoices])
                if selected_invoice:
                    if st.button("Thanh toán", key=selected_invoice):
                        # Logic thanh toán (ví dụ: tích hợp cổng thanh toán)
                        conn.execute("UPDATE invoices SET status='paid' WHERE invoice_id=?", (selected_invoice,))
                        conn.commit()
                        st.success(f"Đã thanh toán hóa đơn {selected_invoice}!")
                        st.rerun()  # Refresh để cập nhật trạng thái hóa đơn
            else:
                st.info("Không có hóa đơn chưa thanh toán.")
        else:
            st.info("Không có hóa đơn.")
    else:
        st.error("Không tìm thấy thông tin sinh viên.")
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
    st.set_page_config(layout="wide")

    # Khởi tạo database
    init_db()

    # Trạng thái đăng nhập
    if 'user' not in st.session_state:
        st.session_state.user = None

    # Giao diện
    if not st.session_state.user:
        login_page()
    else:
        # Sidebar menu
        with st.sidebar:
            st.image("https://upload.wikimedia.org/wikipedia/commons/d/d7/Logo_PTIT.jpg", width=80)
            st.subheader(f"Xin chào, {st.session_state.user[0]}!")

            # Tạo menu dựa trên vai trò
            menu = ["Tổng quan"]
            if st.session_state.user[1] == 'student':
                menu.append("Thông tin cá nhân")
            if st.session_state.user[1] in ['admin', 'staff']:
                menu.extend(["Quản lý Sinh viên", "Quản lý Phòng", "Quản lý Hóa đơn", "Báo cáo"])
            if st.session_state.user[1] == 'admin':
                menu.extend(["Quản lý Nhân viên", "Quản lý tài khoản"])

            menu.extend(["Đổi mật khẩu", "Đăng xuất"])

            choice = st.sidebar.selectbox("Menu", menu)

        # Điều hướng
        if choice == "Tổng quan":
            # Rest of your code
            show_dashboard()
        elif choice == "Quản lý Sinh viên":
            student_management()
        elif choice == "Quản lý Nhân viên":
            staff_management()
        elif choice == "Quản lý Phòng":
            room_management()
        elif choice == "Quản lý Hóa đơn":
            invoice_management()
        elif choice == "Báo cáo":
            report()
        elif choice == "Quản lý tài khoản":
            account_management()
        elif choice == "Thông tin cá nhân":
            student_info()
        elif choice == "Đổi mật khẩu":
            st.warning("Chức năng đang phát triển")
        elif choice == "Đăng xuất":
            st.session_state.user = None
            st.rerun()

if __name__ == "__main__":
    main()
