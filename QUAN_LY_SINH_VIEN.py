import customtkinter as ctk
from tkinter import ttk, messagebox
import pyodbc

# --- CẤU HÌNH ---
SERVER_NAME = 'DESKTOP-HB6SM4A\SQLEXPRESS' 
DB_NAME = 'QuanLySinhVienDB'


ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

class StudentManagementApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Hệ Thống Quản Lý Đào Tạo Toàn Diện (Full Project)")
        self.geometry("1300x800")
        
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        style = ttk.Style()
        style.theme_use("clam")
        
        # 1. Chỉnh sửa nội dung bảng (Hàng dữ liệu)
        style.configure("Treeview", 
                        font=("Arial", 14),       
                        rowheight=40,             
                        background="white",
                        fieldbackground="white")
        
        # 2. Chỉnh sửa tiêu đề bảng (Header)
        style.configure("Treeview.Heading", 
                        font=("Arial", 16, "bold"), 
                        background="#e1e6eb",
                        foreground="#333")

        # 1. SIDEBAR
        self.setup_sidebar()

        # 2. CONTAINER CHÍNH
        self.main_container = ctk.CTkFrame(self, fg_color="#f0f2f5", corner_radius=0)
        self.main_container.grid(row=0, column=1, sticky="nsew")
        self.main_container.grid_rowconfigure(0, weight=1)
        self.main_container.grid_columnconfigure(0, weight=1)

        # 3. KHỞI TẠO CÁC MÀN HÌNH
        self.frame_school = ctk.CTkFrame(self.main_container, fg_color="transparent") 
        self.frame_faculty = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.frame_class = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.frame_student = ctk.CTkFrame(self.main_container, fg_color="transparent")

        self.setup_school_view(self.frame_school) # Setup giao diện Trường
        self.setup_faculty_view(self.frame_faculty)
        self.setup_class_view(self.frame_class)
        self.setup_student_view(self.frame_student)

        # Mặc định hiện màn hình Trường (Dashboard) đầu tiên cho chuyên nghiệp
        self.show_frame("school")

    def get_connection(self):
        try:
            conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={SERVER_NAME};DATABASE={DB_NAME};Trusted_Connection=yes;'
            return pyodbc.connect(conn_str)
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi kết nối SQL: {e}")
            return None

    def setup_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0, fg_color="#1a2b4c")
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        ctk.CTkLabel(self.sidebar, text="QL SINH VIÊN", font=("Arial", 18, "bold"), text_color="white").pack(pady=30)
        
        # Cập nhật các nút Menu
        self.create_menu_btn("  Trường", lambda: self.show_frame("school"))
        self.create_menu_btn("  Khoa", lambda: self.show_frame("faculty"))
        self.create_menu_btn("  Lớp", lambda: self.show_frame("class"))
        self.create_menu_btn("  Sinh viên", lambda: self.show_frame("student"))

    def create_menu_btn(self, text, command):
        ctk.CTkButton(self.sidebar, text=text, anchor="w", fg_color="transparent", text_color="white", hover_color="#2a3b5c", command=command).pack(fill="x", pady=5)

    def show_frame(self, name):
        # Ẩn hết các frame
        self.frame_school.grid_forget()
        self.frame_faculty.grid_forget()
        self.frame_class.grid_forget()
        self.frame_student.grid_forget()

        # Hiện frame được chọn và load dữ liệu mới nhất
        if name == "school":
            self.frame_school.grid(row=0, column=0, sticky="nsew")
            self.load_school_data()
        elif name == "faculty":
            self.frame_faculty.grid(row=0, column=0, sticky="nsew")
            self.load_faculty_data()
        elif name == "class":
            self.frame_class.grid(row=0, column=0, sticky="nsew")
            self.load_class_data()
        elif name == "student":
            self.frame_student.grid(row=0, column=0, sticky="nsew")
            self.load_student_data()

    # =========================================================================
    #  MÀN HÌNH "TRƯỜNG" (DASHBOARD)
    # =========================================================================
    def setup_school_view(self, parent):
        # 1. Phần Tổng quan (3 Cards ở trên)
        overview_frame = ctk.CTkFrame(parent, fg_color="transparent")
        overview_frame.pack(fill="x", padx=20, pady=20)
        
        # Card 1: Tổng số Khoa
        self.card_khoa = self.create_dashboard_card(overview_frame, "Tổng số Khoa", "🏫")
        self.card_khoa.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # Card 2: Tổng số Sinh viên
        self.card_sv = self.create_dashboard_card(overview_frame, "Tổng số Sinh viên", "👥")
        self.card_sv.pack(side="left", fill="both", expand=True, padx=10)
        
        # Card 3: Tổng số Lớp
        self.card_lop = self.create_dashboard_card(overview_frame, "Tổng số Lớp", "👨‍🏫")
        self.card_lop.pack(side="left", fill="both", expand=True, padx=(10, 0))

        # 2. Phần Danh sách thống kê (Bảng ở dưới)
        table_card = ctk.CTkFrame(parent, fg_color="white", corner_radius=10)
        table_card.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(table_card, text="Thống kê chi tiết các Khoa", font=("Arial", 16, "bold")).pack(anchor="w", padx=20, pady=15)

        # Treeview
        cols = ("STT", "TenKhoa", "TongSV", "TongLop")
        self.tree_school = ttk.Treeview(table_card, columns=cols, show="headings")
        
        headers = ["STT", "Tên Khoa", "Tổng số Sinh viên", "Tổng số Lớp"]
        widths = [50, 400, 200, 200]
        
        for c, h, w in zip(cols, headers, widths):
            self.tree_school.heading(c, text=h)
            self.tree_school.column(c, width=w, anchor="center" if c != "TenKhoa" else "w") # Tên khoa canh trái, số canh giữa

        self.tree_school.pack(fill="both", expand=True, padx=10, pady=10)

    def create_dashboard_card(self, parent, title, icon):
        card = ctk.CTkFrame(parent, fg_color="white", corner_radius=10, height=150)
        
        # Icon 
        ctk.CTkLabel(card, text=icon, font=("Arial", 40)).pack(pady=(20, 5))
        
        # Label Tiêu đề
        ctk.CTkLabel(card, text=title, font=("Arial", 14), text_color="gray").pack()
        
        # Label Số lượng 
        lbl_number = ctk.CTkLabel(card, text="0", font=("Arial", 30, "bold"), text_color="#1a2b4c")
        lbl_number.pack(pady=(5, 20))
        
        # Lưu tham chiếu để update số liệu sau này
        card.lbl_number = lbl_number 
        return card

    def load_school_data(self):
        # Clear bảng cũ
        for item in self.tree_school.get_children(): self.tree_school.delete(item)
        
        conn = self.get_connection()
        if conn:
            try:
                cur = conn.cursor()
                
                # 1. Lấy số liệu tổng quan (Dùng COUNT)
                cur.execute("SELECT COUNT(*) FROM Khoa")
                total_khoa = cur.fetchone()[0]
                
                cur.execute("SELECT COUNT(*) FROM SinhVien")
                total_sv = cur.fetchone()[0]
                
                cur.execute("SELECT COUNT(*) FROM Lop")
                total_lop = cur.fetchone()[0]

                # Update lên Card (Dùng .configure để đổi chữ)
                self.card_khoa.lbl_number.configure(text=str(total_khoa))
                self.card_sv.lbl_number.configure(text=str(total_sv))
                self.card_lop.lbl_number.configure(text=str(total_lop))

                # 2. Lấy dữ liệu cho Bảng Thống kê
                # Dùng Subquery để đếm số SV và Số Lớp cho từng khoa
                sql = """
                    SELECT 
                        k.TenKhoa,
                        (SELECT COUNT(*) FROM SinhVien sv JOIN Lop l ON sv.MaLop = l.MaLop WHERE l.MaKhoa = k.MaKhoa) as TongSV,
                        (SELECT COUNT(*) FROM Lop l WHERE l.MaKhoa = k.MaKhoa) as TongLop
                    FROM Khoa k
                """
                cur.execute(sql)
                rows = cur.fetchall()
                
                # Đổ dữ liệu vào bảng (Thêm số thứ tự i+1)
                for i, row in enumerate(rows):
                    self.tree_school.insert("", "end", values=(i+1, row[0], row[1], row[2]))
                    
            except Exception as e:
                messagebox.showerror("Lỗi SQL", str(e))
            finally:
                conn.close()

    # =========================================================================
    #  PHẦN CŨ: KHOA - LỚP - SINH VIÊN (GIỮ NGUYÊN)
    # =========================================================================
    
    # --- MÀN HÌNH KHOA ---
    def setup_faculty_view(self, parent):
        card = ctk.CTkFrame(parent, fg_color="white", corner_radius=10); card.pack(fill="x", padx=20, pady=20)
        ctk.CTkLabel(card, text="Quản lý Khoa", font=("Arial", 16, "bold")).pack(anchor="w", padx=20, pady=(15,5)); ctk.CTkFrame(card, height=2, fg_color="#e0e0e0").pack(fill="x") 
        form = ctk.CTkFrame(card, fg_color="transparent"); form.pack(fill="x", padx=20, pady=20)
        self.khoa_vars = {"MaKhoa": ctk.StringVar(), "TenKhoa": ctk.StringVar()}
        ctk.CTkLabel(form, text="Mã Khoa:").grid(row=0, column=0, sticky="w", padx=5); ctk.CTkEntry(form, textvariable=self.khoa_vars["MaKhoa"], width=150).grid(row=0, column=1, sticky="w", padx=5)
        ctk.CTkLabel(form, text="Tên Khoa:").grid(row=0, column=2, sticky="w", padx=5); ctk.CTkEntry(form, textvariable=self.khoa_vars["TenKhoa"], width=300).grid(row=0, column=3, sticky="w", padx=5)
        ctk.CTkButton(form, text="Xóa", width=80, fg_color="#D32F2F", hover_color="#B71C1C", command=self.delete_faculty).grid(row=0, column=5, sticky="e", padx=5)
        ctk.CTkButton(form, text="Lưu", width=80, fg_color="#1a2b4c", command=self.save_faculty).grid(row=0, column=4, sticky="e", padx=5)
        table_card = ctk.CTkFrame(parent, fg_color="white", corner_radius=10); table_card.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        cols = ("MaKhoa", "TenKhoa", "TongSV", "TongNam", "TongNu", "TopLop"); self.tree_khoa = ttk.Treeview(table_card, columns=cols, show="headings")
        for c, h in zip(cols, ["Mã", "Tên Khoa", "Tổng SV", "Nam", "Nữ", "Lớp Điểm Cao Nhất"]): self.tree_khoa.heading(c, text=h); self.tree_khoa.column(c, width=100, anchor="center" if c!="TenKhoa" else "w")
        self.tree_khoa.pack(fill="both", expand=True, padx=10, pady=10); self.tree_khoa.bind("<<TreeviewSelect>>", self.on_khoa_click)

    def load_faculty_data(self):
        for item in self.tree_khoa.get_children(): self.tree_khoa.delete(item)
        conn = self.get_connection()
        if conn:
            cur = conn.cursor()
            sql = "SELECT k.MaKhoa, k.TenKhoa, (SELECT COUNT(*) FROM SinhVien sv JOIN Lop l ON sv.MaLop = l.MaLop WHERE l.MaKhoa = k.MaKhoa) as TongSV, (SELECT COUNT(*) FROM SinhVien sv JOIN Lop l ON sv.MaLop = l.MaLop WHERE l.MaKhoa = k.MaKhoa AND sv.GioiTinh = N'Nam') as TongNam, (SELECT COUNT(*) FROM SinhVien sv JOIN Lop l ON sv.MaLop = l.MaLop WHERE l.MaKhoa = k.MaKhoa AND (sv.GioiTinh = N'Nữ' OR sv.GioiTinh = N'Nu')) as TongNu, (SELECT TOP 1 l.TenLop + ' (' + CAST(CAST(AVG(d.DiemTB) as DECIMAL(4,2)) as varchar) + ')' FROM Lop l JOIN SinhVien sv ON l.MaLop = sv.MaLop JOIN DiemHocTap d ON sv.MSSV = d.MSSV WHERE l.MaKhoa = k.MaKhoa GROUP BY l.TenLop ORDER BY AVG(d.DiemTB) DESC) as TopLop FROM Khoa k"
            cur.execute(sql)
            for row in cur.fetchall():
                 data = list(row); 
                 if data[5] is None: data[5] = "---"
                 self.tree_khoa.insert("", "end", values=data)
            conn.close()

    def save_faculty(self):
        mk = self.khoa_vars["MaKhoa"].get().strip(); tk = self.khoa_vars["TenKhoa"].get().strip()
        if not mk or not tk: messagebox.showwarning("Thiếu tin", "Nhập đủ Mã và Tên Khoa"); return
        conn = self.get_connection()
        if conn:
            try:
                cur = conn.cursor(); cur.execute("SELECT * FROM Khoa WHERE MaKhoa=?", mk)
                if cur.fetchone(): cur.execute("UPDATE Khoa SET TenKhoa=? WHERE MaKhoa=?", (tk, mk))
                else: cur.execute("INSERT INTO Khoa (MaKhoa, TenKhoa) VALUES (?,?)", (mk, tk))
                conn.commit(); messagebox.showinfo("OK", "Đã lưu!"); self.load_faculty_data(); self.khoa_vars["MaKhoa"].set(""); self.khoa_vars["TenKhoa"].set("")
            except Exception as e: messagebox.showerror("Lỗi", str(e))
            finally: conn.close()

    def delete_faculty(self):
        mk = self.khoa_vars["MaKhoa"].get()
        if not mk: return
        if not messagebox.askyesno("Xóa?", "Bạn có chắc muốn xóa Khoa này?"): return
        conn = self.get_connection()
        if conn:
            try:
                cur = conn.cursor(); cur.execute("DELETE FROM Khoa WHERE MaKhoa=?", mk); conn.commit()
                messagebox.showinfo("OK", "Đã xóa!"); self.load_faculty_data(); self.khoa_vars["MaKhoa"].set(""); self.khoa_vars["TenKhoa"].set("")
            except: messagebox.showerror("Lỗi", "Không thể xóa Khoa đang có Lớp!")
            finally: conn.close()

    def on_khoa_click(self, event):
        val = self.tree_khoa.item(self.tree_khoa.focus(), 'values')
        if val: self.khoa_vars["MaKhoa"].set(val[0]); self.khoa_vars["TenKhoa"].set(val[1])

    # --- MÀN HÌNH LỚP ---
    def setup_class_view(self, parent):
        card = ctk.CTkFrame(parent, fg_color="white", corner_radius=10); card.pack(fill="x", padx=20, pady=20)
        ctk.CTkLabel(card, text="Quản lý Lớp", font=("Arial", 16, "bold")).pack(anchor="w", padx=20, pady=(15,5)); ctk.CTkFrame(card, height=2, fg_color="#e0e0e0").pack(fill="x")
        form = ctk.CTkFrame(card, fg_color="transparent"); form.pack(fill="x", padx=20, pady=20)
        self.class_vars = {"MaLop": ctk.StringVar(), "CoVan": ctk.StringVar(), "MaKhoa": ctk.StringVar(), "SoLuong": ctk.StringVar(value="Auto")}
        ctk.CTkLabel(form, text="Mã lớp").pack(anchor="w"); ctk.CTkEntry(form, textvariable=self.class_vars["MaLop"]).pack(fill="x", pady=5)
        ctk.CTkLabel(form, text="Cố vấn HT").pack(anchor="w"); ctk.CTkEntry(form, textvariable=self.class_vars["CoVan"]).pack(fill="x", pady=5)
        ctk.CTkLabel(form, text="Mã Khoa").pack(anchor="w"); ctk.CTkEntry(form, textvariable=self.class_vars["MaKhoa"]).pack(fill="x", pady=5)
        ctk.CTkButton(form, text="Xóa", width=80, fg_color="#D32F2F", hover_color="#B71C1C", command=self.delete_class).pack(side="right", padx=5, pady=10)
        ctk.CTkButton(form, text="Lưu", width=80, command=self.save_class).pack(side="right", padx=5, pady=10)
        table_card = ctk.CTkFrame(parent, fg_color="white", corner_radius=10); table_card.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        cols = ("MaLop", "CoVan", "MaKhoa", "SoLuong"); self.tree_class = ttk.Treeview(table_card, columns=cols, show="headings")
        for c, h in zip(cols, ["Mã Lớp", "Cố vấn", "Khoa", "Số SV"]): self.tree_class.heading(c, text=h); self.tree_class.column(c, width=100, anchor="center")
        self.tree_class.pack(fill="both", expand=True, padx=10, pady=10); self.tree_class.bind("<<TreeviewSelect>>", self.on_class_click)

    def load_class_data(self):
        for item in self.tree_class.get_children(): self.tree_class.delete(item)
        conn = self.get_connection()
        if conn:
            cur = conn.cursor(); cur.execute("SELECT l.MaLop, l.CoVanHocTap, l.MaKhoa, (SELECT COUNT(*) FROM SinhVien sv WHERE sv.MaLop = l.MaLop) as SiSo FROM Lop l")
            for row in cur.fetchall(): self.tree_class.insert("", "end", values=[x if x is not None else "" for x in row])
            conn.close()

    def save_class(self):
        ml = self.class_vars["MaLop"].get(); mk = self.class_vars["MaKhoa"].get()
        if not ml or not mk: messagebox.showwarning("Lỗi", "Thiếu Mã Lớp/Khoa"); return
        conn = self.get_connection()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute("SELECT * FROM Khoa WHERE MaKhoa=?", mk)
                if not cur.fetchone(): cur.execute("INSERT INTO Khoa (MaKhoa, TenKhoa) VALUES (?,?)", (mk, mk))
                cur.execute("SELECT * FROM Lop WHERE MaLop=?", ml)
                if cur.fetchone(): cur.execute("UPDATE Lop SET CoVanHocTap=?, MaKhoa=? WHERE MaLop=?", (self.class_vars["CoVan"].get(), mk, ml))
                else: cur.execute("INSERT INTO Lop (MaLop, TenLop, MaKhoa, CoVanHocTap) VALUES (?, ?, ?, ?)", (ml, ml, mk, self.class_vars["CoVan"].get()))
                conn.commit(); messagebox.showinfo("OK", "Đã lưu!"); self.load_class_data()
            except Exception as e: messagebox.showerror("Lỗi", str(e))
            finally: conn.close()

    def delete_class(self):
        ml = self.class_vars["MaLop"].get()
        if not ml: return
        if not messagebox.askyesno("Xóa?", "Bạn có chắc muốn xóa Lớp này?"): return
        conn = self.get_connection()
        if conn:
            try:
                cur = conn.cursor(); cur.execute("DELETE FROM Lop WHERE MaLop=?", ml); conn.commit()
                messagebox.showinfo("OK", "Đã xóa!"); self.load_class_data(); self.class_vars["MaLop"].set("")
            except: messagebox.showerror("Lỗi", "Không thể xóa Lớp đang có Sinh viên!")
            finally: conn.close()

    def on_class_click(self, event):
        val = self.tree_class.item(self.tree_class.focus(), 'values')
        if val: self.class_vars["MaLop"].set(val[0]); self.class_vars["CoVan"].set(val[1]); self.class_vars["MaKhoa"].set(val[2]); self.class_vars["SoLuong"].set(val[3])

    # --- MÀN HÌNH SINH VIÊN ---
    def setup_student_view(self, parent):
        info_card = ctk.CTkFrame(parent, fg_color="white", corner_radius=10); info_card.pack(fill="x", padx=20, pady=20)
        ctk.CTkLabel(info_card, text="Nhập liệu Sinh viên", font=("Arial", 16, "bold")).pack(anchor="w", padx=20, pady=10)
        form = ctk.CTkFrame(info_card, fg_color="transparent"); form.pack(fill="x", padx=20, pady=10)
        self.sv_vars = {"HoTen": ctk.StringVar(), "GioiTinh": ctk.StringVar(value="Nữ"), "MSSV": ctk.StringVar(), "Lop": ctk.StringVar(), "Nganh": ctk.StringVar(), "Khoa": ctk.StringVar(), "Email": ctk.StringVar(), "SDT": ctk.StringVar(), "QueQuan": ctk.StringVar(), "Toan": ctk.DoubleVar(value=0), "Code": ctk.DoubleVar(value=0), "CSDL": ctk.DoubleVar(value=0), "Web": ctk.DoubleVar(value=0), "TB": ctk.DoubleVar(value=0)}
        self.entry_search_sv = ctk.CTkEntry(form, placeholder_text="Nhập MSSV...", width=200); self.entry_search_sv.grid(row=0, column=0, sticky="w", pady=10)
        ctk.CTkButton(form, text="Tìm", width=80, command=self.search_student).grid(row=0, column=1, sticky="w", padx=10)
        self.create_input(form, 1, 0, "Họ tên", self.sv_vars["HoTen"]); self.create_input(form, 1, 1, "Giới tính", self.sv_vars["GioiTinh"]); self.create_input(form, 1, 2, "MSSV", self.sv_vars["MSSV"]); self.create_input(form, 1, 3, "Lớp", self.sv_vars["Lop"]); self.create_input(form, 1, 4, "Ngành", self.sv_vars["Nganh"])
        self.create_input(form, 2, 0, "Khoa", self.sv_vars["Khoa"]); self.create_input(form, 2, 1, "Email", self.sv_vars["Email"]); self.create_input(form, 2, 2, "SĐT", self.sv_vars["SDT"]); self.create_input(form, 2, 3, "Quê quán", self.sv_vars["QueQuan"])
        ctk.CTkLabel(form, text="Điểm số:", font=("Arial", 14, "bold"), text_color="#555").grid(row=3, column=0, sticky="w", pady=(15,5))
        self.create_input(form, 4, 0, "Toán CC", self.sv_vars["Toan"]); self.create_input(form, 4, 1, "Lập trình", self.sv_vars["Code"]); self.create_input(form, 4, 2, "CSDL", self.sv_vars["CSDL"]); self.create_input(form, 4, 3, "Web", self.sv_vars["Web"])
        ctk.CTkLabel(form, text="Điểm TB:").grid(row=5, column=0, sticky="w", pady=10); ctk.CTkLabel(form, textvariable=self.sv_vars["TB"], font=("Arial", 16, "bold"), text_color="red").grid(row=5, column=0, padx=80, sticky="w")
        ctk.CTkButton(form, text="Tính TB", fg_color="gray", width=80, command=self.calculate_avg).grid(row=5, column=1, sticky="w")
        ctk.CTkButton(form, text="Xóa", width=100, fg_color="#D32F2F", hover_color="#B71C1C", command=self.delete_student).grid(row=5, column=3, pady=10, sticky="e", padx=10)
        ctk.CTkButton(form, text="Lưu", width=150, font=("Arial", 13, "bold"), command=self.save_student).grid(row=5, column=4, pady=10)
        table_frame = ctk.CTkFrame(parent, fg_color="white", corner_radius=10); table_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        cols = ("HoTen", "GioiTinh", "MSSV", "Lop", "Khoa", "TB"); self.tree_sv = ttk.Treeview(table_frame, columns=cols, show="headings")
        for c, h in zip(cols, ["Họ Tên", "Giới Tính", "MSSV", "Lớp", "Khoa", "Điểm TB"]): self.tree_sv.heading(c, text=h); self.tree_sv.column(c, width=100, anchor="center")
        self.tree_sv.column("HoTen", width=150, anchor="w"); self.tree_sv.pack(fill="both", expand=True, padx=10, pady=10); self.tree_sv.bind("<<TreeviewSelect>>", self.on_sv_click)

    def calculate_avg(self):
        try: t = float(self.sv_vars["Toan"].get()); c = float(self.sv_vars["Code"].get()); d = float(self.sv_vars["CSDL"].get()); w = float(self.sv_vars["Web"].get()); self.sv_vars["TB"].set(round((t+c+d+w)/4, 2))
        except: self.sv_vars["TB"].set(0.0)

    def save_student(self):
        self.calculate_avg(); mssv = self.sv_vars["MSSV"].get(); lop = self.sv_vars["Lop"].get(); khoa = self.sv_vars["Khoa"].get()
        if not mssv or not lop: messagebox.showwarning("Lỗi", "Thiếu MSSV/Lớp"); return
        conn = self.get_connection()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute("SELECT * FROM Khoa WHERE MaKhoa=?", khoa)
                if not cur.fetchone(): cur.execute("INSERT INTO Khoa (MaKhoa, TenKhoa) VALUES (?,?)", (khoa, khoa))
                cur.execute("SELECT * FROM Lop WHERE MaLop=?", lop)
                if not cur.fetchone(): cur.execute("INSERT INTO Lop (MaLop, TenLop, MaKhoa) VALUES (?,?,?)", (lop, lop, khoa))
                cur.execute("SELECT Count(*) FROM SinhVien WHERE MSSV=?", mssv)
                if cur.fetchone()[0] > 0:
                     cur.execute("UPDATE SinhVien SET HoTen=?, GioiTinh=?, MaLop=?, NganhHoc=?, Email=?, SDT=?, QueQuan=? WHERE MSSV=?", (self.sv_vars["HoTen"].get(), self.sv_vars["GioiTinh"].get(), lop, self.sv_vars["Nganh"].get(), self.sv_vars["Email"].get(), self.sv_vars["SDT"].get(), self.sv_vars["QueQuan"].get(), mssv))
                     cur.execute("DELETE FROM DiemHocTap WHERE MSSV=?", mssv) 
                else: cur.execute("INSERT INTO SinhVien (MSSV, HoTen, GioiTinh, MaLop, NganhHoc, Email, SDT, QueQuan) VALUES (?,?,?,?,?,?,?,?)", (mssv, self.sv_vars["HoTen"].get(), self.sv_vars["GioiTinh"].get(), lop, self.sv_vars["Nganh"].get(), self.sv_vars["Email"].get(), self.sv_vars["SDT"].get(), self.sv_vars["QueQuan"].get()))
                cur.execute("INSERT INTO DiemHocTap VALUES (?,?,?,?,?,?)", (mssv, self.sv_vars["Toan"].get(), self.sv_vars["Code"].get(), self.sv_vars["CSDL"].get(), self.sv_vars["Web"].get(), self.sv_vars["TB"].get()))
                conn.commit(); messagebox.showinfo("OK", "Đã lưu!"); self.load_student_data()
            except Exception as e: conn.rollback(); messagebox.showerror("Lỗi", str(e))
            finally: conn.close()

    def delete_student(self):
        mssv = self.sv_vars["MSSV"].get()
        if not mssv: return
        if not messagebox.askyesno("Xóa?", "Bạn có chắc xóa sinh viên này?"): return
        conn = self.get_connection()
        if conn:
            try:
                cur = conn.cursor(); cur.execute("DELETE FROM DiemHocTap WHERE MSSV=?", mssv); cur.execute("DELETE FROM SinhVien WHERE MSSV=?", mssv); conn.commit()
                messagebox.showinfo("OK", "Đã xóa!"); self.load_student_data(); self.sv_vars["MSSV"].set("")
            except Exception as e: conn.rollback(); messagebox.showerror("Lỗi", str(e))
            finally: conn.close()

    def load_student_data(self, query=None, params=None):
        for item in self.tree_sv.get_children(): self.tree_sv.delete(item)
        conn = self.get_connection()
        if conn:
            cur = conn.cursor()
            sql = query if query else "SELECT sv.HoTen, sv.GioiTinh, sv.MSSV, sv.MaLop, l.MaKhoa, d.DiemTB FROM SinhVien sv LEFT JOIN Lop l ON sv.MaLop = l.MaLop LEFT JOIN DiemHocTap d ON sv.MSSV = d.MSSV"
            cur.execute(sql, params) if params else cur.execute(sql)
            for row in cur.fetchall(): self.tree_sv.insert("", "end", values=[x if x is not None else "" for x in row])
            conn.close()

    def search_student(self):
        mssv = self.entry_search_sv.get()
        if not mssv: self.load_student_data(); return
        self.load_student_data("SELECT sv.HoTen, sv.GioiTinh, sv.MSSV, sv.MaLop, l.MaKhoa, d.DiemTB FROM SinhVien sv LEFT JOIN Lop l ON sv.MaLop = l.MaLop LEFT JOIN DiemHocTap d ON sv.MSSV = d.MSSV WHERE sv.MSSV LIKE ?", ('%'+mssv+'%',))

    def on_sv_click(self, event):
        sel = self.tree_sv.focus(); val = self.tree_sv.item(sel, 'values')
        if val:
            mssv = val[2]; self.sv_vars["MSSV"].set(mssv); self.sv_vars["HoTen"].set(val[0]); self.sv_vars["GioiTinh"].set(val[1]); self.sv_vars["Lop"].set(val[3]); self.sv_vars["Khoa"].set(val[4])
            conn = self.get_connection()
            if conn:
                cur = conn.cursor(); cur.execute("SELECT * FROM SinhVien WHERE MSSV=?", mssv); sv = cur.fetchone()
                if sv: self.sv_vars["Nganh"].set(sv.NganhHoc); self.sv_vars["Email"].set(sv.Email); self.sv_vars["SDT"].set(sv.SDT); self.sv_vars["QueQuan"].set(sv.QueQuan)
                cur.execute("SELECT * FROM DiemHocTap WHERE MSSV=?", mssv); diem = cur.fetchone()
                if diem: self.sv_vars["Toan"].set(diem.ToanCC); self.sv_vars["Code"].set(diem.LapTrinhCB); self.sv_vars["CSDL"].set(diem.CSDL); self.sv_vars["Web"].set(diem.LapTrinhWeb); self.sv_vars["TB"].set(diem.DiemTB)
                else: self.sv_vars["TB"].set(0)
                conn.close()

    def create_input(self, parent, r, c, label, var):
        f = ctk.CTkFrame(parent, fg_color="transparent"); f.grid(row=r, column=c, padx=5, pady=5, sticky="ew")
        ctk.CTkLabel(f, text=label, font=("Arial", 11)).pack(anchor="w"); ctk.CTkEntry(f, textvariable=var, height=30).pack(fill="x")

if __name__ == "__main__":
    app = StudentManagementApp()
    app.mainloop()