import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import io

# 1. CẤU HÌNH TRANG & CHỦ ĐỀ NỀN TỐI
st.set_page_config(
    page_title="Hòa Phát Logistics - Quản Lý Hàng Tồn & Bể Vỡ",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. TÙY CHỈNH CSS CHUYÊN NGHIỆP NỀN TỐI (DARK MODE HIGH-CONTRAST)
st.markdown("""
    <style>
    /* Nền tổng thể xanh đen đêm đậm */
    .stApp {
        background-color: #0b0f19 !important;
        color: #f1f5f9 !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    
    /* Header chính Nền Tối Neon Accent */
    .main-header {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
        padding: 24px 30px;
        border-radius: 16px;
        color: #ffffff;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
        margin-bottom: 25px;
        border: 1px solid #312e81;
        border-left: 6px solid #f43f5e;
    }
    .main-header h1 {
        font-size: 22px;
        font-weight: 700;
        margin: 0;
        color: #f8fafc;
        letter-spacing: -0.5px;
    }
    .main-header p {
        font-size: 13px;
        color: #a5b4fc;
        margin: 6px 0 0 0;
    }

    /* Thẻ thống kê Metric nổi bật trên nền tối */
    div[data-testid="stMetric"] {
        background-color: #1e293b !important;
        border: 1px solid #334155 !important;
        padding: 18px !important;
        border-radius: 14px !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3) !important;
    }
    div[data-testid="stMetricValue"] {
        font-size: 26px !important;
        font-weight: 700 !important;
        color: #38bdf8 !important;
    }
    div[data-testid="stMetricLabel"] {
        color: #94a3b8 !important;
        font-weight: 600 !important;
    }

    /* Đổi màu các ô nhập liệu (Inputs) sang giao diện tối */
    .stTextInput>div>div>input, .stSelectbox>div>div>div, .stNumberInput>div>div>input, .stTextArea>div>div>textarea {
        background-color: #1e293b !important;
        color: #f8fafc !important;
        border: 1px solid #475569 !important;
        border-radius: 10px !important;
    }
    
    /* Nút bấm nổi bật (Accent Color Buttons) */
    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #e11d48 0%, #be123c 100%) !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        border-radius: 10px !important;
        padding: 12px !important;
        border: none !important;
        box-shadow: 0 4px 15px rgba(225, 29, 72, 0.4) !important;
    }
    .stDownloadButton > button {
        width: 100%;
        background: linear-gradient(135deg, #059669 0%, #047857 100%) !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        border-radius: 10px !important;
        padding: 12px !important;
        border: none !important;
        box-shadow: 0 4px 15px rgba(5, 150, 105, 0.4) !important;
    }

    /* Bảng dữ liệu tương phản cao */
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid #334155 !important;
    }
    </style>
""", unsafe_allow_html=True)

# 3. KHO DỮ LIỆU TẠM (SESSION STATE)
if 'inventory_data' not in st.session_state:
    st.session_state.inventory_data = pd.DataFrame(columns=[
        "Mã_Biên_Bản", "Ngày_Giờ", "Biển_Số_Xe", "Tên_Tài_Xế", "Tên_Khách_Hàng",
        "Địa_Chỉ_Giao", "Tên_Mặt_Hàng", "Đơn_Vị_Tính", "Số_Lượng_Tồn",
        "Số_Lượng_Bể_Vỡ", "Phân_Loại", "Lý_Do_Lưu_Kho", "Trạng_Thái_Đối_Soát"
    ])

# 4. HEADER CHÍNH
st.markdown("""
    <div class="main-header">
        <h1>📦 QUẢN LÝ HÀNG TỒN GIAO CHƯA KỊP & BỂ VỠ</h1>
        <p>Hệ thống theo dõi sự cố giao hàng, lưu kho trả về và đối soát bồi thường Masan - Hòa Phát Logistics</p>
    </div>
""", unsafe_allow_html=True)

# 5. CÁC TÁC VỤ DẠNG TAB INTERACTIVE
tab_nhap, tab_danhsach, tab_baocao = st.tabs([
    "📝 Ghi Nhận Sự Cố Mới", 
    "📋 Bảng Đối Soát Trực Quan", 
    "📊 Thống Kê & Xuất Excel"
])

# ----------------------------------------------------
# TAB 1: FORM NHẬP DỮ LIỆU ĐƯỢC CHIA KHỐI RÕ RÀNG
# ----------------------------------------------------
with tab_nhap:
    st.markdown("#### 🚨 Khai báo biên bản sự cố vận chuyển")
    st.info("💡 Lưu ý: Điền thông tin chính xác từ tài xế/thủ kho để phục vụ đối soát bồi thường với Masan")
    
    with st.form(key="form_nhap_dark", clear_on_submit=True):
        st.markdown("##### 1. Thông tin Chuyến xe & Khách hàng")
        c1, c2, c3 = st.columns(3)
        with c1:
            ngay_gio = st.datetime_input("📅 Ngày giờ phát sinh", value=datetime.now())
            bien_so = st.text_input("🚚 Biển số xe", placeholder="VD: 65C-123.45")
        with c2:
            tai_xe = st.text_input("👨‍✈️ Tên tài xế phụ trách", placeholder="VD: Nguyễn Văn A")
            khach_hang = st.text_input("🏪 Tên NPP / Tạp hóa (Masan)", placeholder="VD: NPP Minh Phát")
        with c3:
            dia_chi = st.text_area("📍 Địa chỉ giao hàng chi tiết", placeholder="VD: Số 123 QL1A, Bình Minh, Vĩnh Long", height=105)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("##### 2. Chi tiết Hàng hóa & Mức độ Hư hỏng / Tồn")
        c4, c5, c6 = st.columns(3)
        with c4:
            ten_hang = st.text_input("📦 Tên mặt hàng Masan", placeholder="VD: Nước tương Chin-su 250ml")
            dvt = st.selectbox("📏 Đơn vị tính", ["Thùng", "Két", "Chai", "Gói", "Bao", "Hộp"])
        with c5:
            sl_ton = st.number_input("📦 Số lượng TỒN (Chưa giao được)", min_value=0, value=0, step=1)
            sl_be = st.number_input("💥 Số lượng BỂ VỠ / HƯ HỎNG", min_value=0, value=0, step=1)
        with c6:
            phan_loai = st.selectbox("🚨 Phân loại sự cố", [
                "Hàng tồn (Khách nghỉ / Không giao kịp)", 
                "Hàng bể vỡ / Hư hỏng trên xe",
                "Hàng bị khách từ chối (Sai quy cách/Sát date)",
                "Khác"
            ])
            ly_do = st.text_input("💬 Lý do chi tiết / Ghi chú", placeholder="VD: Khách đóng cửa / Sập ổ gà bể chai")

        st.markdown("<br>", unsafe_allow_html=True)
        btn_submit = st.form_submit_button("🚨 TẠO BIÊN BẢN & LƯU HỆ THỐNG")

        if btn_submit:
            if not bien_so or not khach_hang or not ten_hang:
                st.error("⚠️ Vui lòng điền đầy đủ các thông tin bắt buộc: Biển số xe, Tên khách hàng và Tên mặt hàng!")
            else:
                ma_bb = f"BB-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                new_row = {
                    "Mã_Biên_Bản": ma_bb,
                    "Ngày_Giờ": ngay_gio.strftime("%Y-%m-%d %H:%M"),
                    "Biển_Số_Xe": bien_so.upper(),
                    "Tên_Tài_Xế": tai_xe,
                    "Tên_Khách_Hàng": khach_hang,
                    "Địa_Chỉ_Giao": dia_chi,
                    "Tên_Mặt_Hàng": ten_hang,
                    "Đơn_Vị_Tính": dvt,
                    "Số_Lượng_Tồn": sl_ton,
                    "Số_Lượng_Bể_Vỡ": sl_be,
                    "Phân_Loại": phan_loai,
                    "Lý_Do_Lưu_Kho": ly_do,
                    "Trạng_Thái_Đối_Soát": "Chờ xử lý"
                }
                st.session_state.inventory_data = pd.concat([
                    st.session_state.inventory_data, 
                    pd.DataFrame([new_row])
                ], ignore_index=True)
                
                st.success(f"✅ Đã ghi nhận biên bản thành công! Mã Biên Bản: {ma_bb}")

# ----------------------------------------------------
# TAB 2: BẢNG DỮ LIỆU TRỰC QUAN TƯƠNG PHẢN CAO
# ----------------------------------------------------
with tab_danhsach:
    st.markdown("#### 📋 Bảng theo dõi đối soát hàng tồn & bể vỡ")
    
    df = st.session_state.inventory_data
    
    if df.empty:
        st.warning("Hiện chưa có biên bản sự cố nào được lưu trên hệ thống.")
    else:
        # Bộ lọc tương tác
        f1, f2 = st.columns(2)
        with f1:
            filter_bs = st.selectbox("🔍 Lọc nhanh theo Xe", ["Tất cả xe"] + list(df["Biển_Số_Xe"].unique()))
        with f2:
            filter_pl = st.selectbox("🔍 Lọc theo Loại sự cố", ["Tất cả loại"] + list(df["Phân_Loại"].unique()))
            
        filtered_df = df.copy()
        if filter_bs != "Tất cả xe":
            filtered_df = filtered_df[filtered_df["Biển_Số_Xe"] == filter_bs]
        if filter_pl != "Tất cả loại":
            filtered_df = filtered_df[filtered_df["Phân_Loại"] == filter_pl]

        # Bảng hiển thị giao diện tối với các định dạng màu sắc trực quan
        st.dataframe(
            filtered_df,
            use_container_width=True,
            column_config={
                "Mã_Biên_Bản": st.column_config.TextColumn("Mã BB", help="Mã biên bản duy nhất"),
                "Ngày_Giờ": "Thời Gian",
                "Biển_Số_Xe": "Biển Số",
                "Tên_Tài_Xế": "Tài Xế",
                "Tên_Khách_Hàng": "NPP / Khách Hàng",
                "Địa_Chỉ_Giao": "Địa Chỉ Chi Tiết",
                "Tên_Mặt_Hàng": "Mặt Hàng",
                "Số_Lượng_Tồn": st.column_config.NumberColumn("SL Tồn", format="%d 📦"),
                "Số_Lượng_Bể_Vỡ": st.column_config.NumberColumn("SL Bể Vỡ", format="%d 💥"),
                "Phân_Loại": "Phân Loại Sự Cố",
                "Trạng_Thái_Đối_Soát": "Trạng Thái"
            }
        )

# ----------------------------------------------------
# TAB 3: THỐNG KÊ & XUẤT EXCEL DỄ ĐỌC
# ----------------------------------------------------
with tab_baocao:
    st.markdown("#### 📊 Thống kê tổng hợp & Xuất báo cáo Excel")
    
    df = st.session_state.inventory_data
    if not df.empty:
        # Các con số tổng quan Dashboard
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Tổng Số Vụ Việc", f"{len(df)} vụ", delta="Biên bản")
        m2.metric("Tổng Thùng Tồn Chưa Giao", f"{df['Số_Lượng_Tồn'].sum():,.0f} thùng", delta="Lưu kho")
        m3.metric("Tổng Thùng Bể Vỡ", f"{df['Số_Lượng_Bể_Vỡ'].sum():,.0f} thùng", delta="Hư hỏng", delta_color="inverse")
        m4.metric("Tỷ Lệ Bể Vỡ / Tồn", f"{round((df['Số_Lượng_Bể_Vỡ'].sum() / (df['Số_Lượng_Tồn'].sum() + 1)) * 100, 1)}%", delta="Mức độ")

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("##### 📌 Thống kê chi tiết theo Tài xế & Xe phụ trách")
        
        summary_driver = df.groupby(['Biển_Số_Xe', 'Tên_Tài_Xế']).agg(
            So_Chuyen_Su_Co=('Mã_Biên_Bản', 'count'),
            Tong_So_Luong_Ton=('Số_Lượng_Tồn', 'sum'),
            Tong_So_Luong_Be_Vo=('Số_Lượng_Bể_Vỡ', 'sum')
        ).reset_index()
        
        st.dataframe(
            summary_driver,
            use_container_width=True,
            column_config={
                "Biển_Số_Xe": "Biển Số Xe",
                "Tên_Tài_Xế": "Tài Xế Phụ Trách",
                "So_Chuyen_Su_Co": "Số Lần Phát Sinh",
                "Tong_So_Luong_Ton": st.column_config.NumberColumn("Tổng Thùng Tồn", format="%d 📦"),
                "Tong_So_Luong_Be_Vo": st.column_config.NumberColumn("Tổng Thùng Bể Vỡ", format="%d 💥")
            }
        )

        st.markdown("<br>", unsafe_allow_html=True)
        
        # Tạo file Excel chất lượng cao
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Chi_Tiet_Su_Co', index=False)
            summary_driver.to_excel(writer, sheet_name='Tong_Hop_Tai_Xe', index=False)
        
        st.download_button(
            label="📥 TẢI BÁO CÁO ĐỐI SOÁT HÀNG TỒN & BỂ VỠ (EXCEL)",
            data=output.getvalue(),
            file_name=f"Bao_Cao_Hang_Ton_Be_Vo_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.info("Chưa có dữ liệu để lập báo cáo thống kê.")
