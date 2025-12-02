USE QuanLySinhVienDB;
GO

-- 1. XÓA BẢNG CŨ (Nếu có) ĐỂ TẠO LẠI CHO SẠCH SẼ
IF OBJECT_ID('DiemHocTap', 'U') IS NOT NULL DROP TABLE DiemHocTap;
IF OBJECT_ID('SinhVien', 'U') IS NOT NULL DROP TABLE SinhVien;
IF OBJECT_ID('Lop', 'U') IS NOT NULL DROP TABLE Lop;
IF OBJECT_ID('Khoa', 'U') IS NOT NULL DROP TABLE Khoa;
GO

-- 2. TẠO BẢNG KHOA
CREATE TABLE Khoa (
    MaKhoa NVARCHAR(50) PRIMARY KEY,
    TenKhoa NVARCHAR(100)
);

-- 3. TẠO BẢNG LỚP (Đã bao gồm cột Cố Vấn Học Tập)
CREATE TABLE Lop (
    MaLop NVARCHAR(50) PRIMARY KEY,
    TenLop NVARCHAR(100),
    MaKhoa NVARCHAR(50) REFERENCES Khoa(MaKhoa),
    CoVanHocTap NVARCHAR(100) -- Cột mới thêm từ file 3
);

-- 4. TẠO BẢNG SINH VIÊN
CREATE TABLE SinhVien (
    MSSV NVARCHAR(20) PRIMARY KEY,
    HoTen NVARCHAR(100),
    GioiTinh NVARCHAR(10),
    MaLop NVARCHAR(50) REFERENCES Lop(MaLop),
    NganhHoc NVARCHAR(100),
    Email NVARCHAR(100),
    SDT NVARCHAR(20),
    QueQuan NVARCHAR(200)
);

-- 5. TẠO BẢNG ĐIỂM
CREATE TABLE DiemHocTap (
    MSSV NVARCHAR(20) PRIMARY KEY REFERENCES SinhVien(MSSV),
    ToanCC FLOAT DEFAULT 0,
    LapTrinhCB FLOAT DEFAULT 0,
    CSDL FLOAT DEFAULT 0,
    LapTrinhWeb FLOAT DEFAULT 0,
    DiemTB FLOAT DEFAULT 0
);
GO

-- 6. (TÙY CHỌN) THÊM VÀI DỮ LIỆU MẪU ĐỂ TEST
INSERT INTO Khoa VALUES ('CNTT', N'Công nghệ Thông tin');
INSERT INTO Lop VALUES ('DH25PM', N'Đại học Phần mềm 25', 'CNTT', N'Nguyễn Văn A');