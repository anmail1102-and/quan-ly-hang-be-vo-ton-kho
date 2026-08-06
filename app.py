import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import io

# 1. CẤU HÌNH TRANG & GIAO DIỆN DOANH NGHIỆP
st.set_page_config(
    page_title="Hòa Phát Logistics - Quản Lý Hàng Tồn & Bể Vỡ",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom UI CSS
st.markdown("""
    <style>
    .stApp {
        background-color: #f8fafc;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    .main-header {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        padding: 22px 28px;
        border-radius: 16px;
        color: #ffffff;
        box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.15);
        margin-bottom: 25px;
        border-left: 6px solid #dc2626;
    }
    .main-header h1 {
        font-size: 22px;
        font-weight: 700;
        margin: 0;
        color: #f8fafc;
    }
    .main-header p {
        font-size: 13px;
        color: #94a3b8;
        margin: 6px 0 0 0;
    }
    div[data-testid="stMetric"] {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        padding: 16px;
        border-radius: 12px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }
    .stButton > button {
        width: 100%;
        background-color: #dc2626 !important;
        color: #ffffff !important;
        font-weight: 600 !important;
        border-radius: 10px !important;
        padding: 10px !important;
        border: none !important;
    }
    .stDownloadButton > button {
        width: 100%;
        background-color: #059669 !important;
        color: #ffffff !important;
        font-weight: 600 !important;
        border-radius: 10px !important;
        padding: 10px !important;
        border: none !important;
    }
    </style>
""", unsafe_allow_html=True)

# 2. KHỞI TẠO BỘ TRỚ DỮ LIỆU (SESSION STATE)
if 'inventory_data' not in st.session_state:
    st.session_state.inventory_data = pd.DataFrame(columns=[
        "Mã_Biên_Bản", "Ngày_Giờ", "Biển_Số_Xe", "Tên_Tài_Xế", "Tên_Khách_Hàng",
        "Địa_Chỉ_Giao", "Tên_Mặt_Hàng", "Đơn_Vị_Tính", "Số_Lượng_Tồn",
        "Số_Lượng_Bể_Vỡ", "Phân_Loại", "Lý_Do_Lưu_Kho", "Trạng_Thái_Đối_Soát"
    ])

# 3. HEADER
st.markdown("""
    <div class="main-header">
        <h1>📦 HỆ THỐNG QUẢN LÝ HÀNG TỒN GIAO CHƯA KỊP & HÀNG BỂ VỠ</h1>
        <p>Công cụ ghi nhận sự cố giao hàng, theo dõi tồn kho trả về và lập biên bản đối soát Masan</p>
    </div>
""", unsafe_allow_html=True)

# 4. THANH ĐIỀU HƯỚNG TÁC VỤ (TAB)
tab_nhap, tab_danhsach, tab_baocao = st.tabs([
    "📝 1. Ghi Nhận Hàng Tồn / Bể Vỡ Mới", 
    "📋 2. Danh Sách Đối Soát Hàng Tồn & Hư Hỏng", 
    "📊 3. Báo Cáo Thống Kê & Xuất Excel"
])

# ----------------------------------------------------
# TAB 1: FORM NHẬP DỮ LIỆU SỰ CỐ
# ----------------------------------------------------
with tab_nhap:
    st.markdown("##### 📝 Khai báo thông tin sự cố / Hàng tồn chuyến giao")
    
    with st.form(key="form_nhap_su_co", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            ngay_gio = st.datetime_input("📅 Ngày giờ phát sinh", value=datetime.now())
            bien_so = st.text_input("🚚 Biển số xe (VD: 65C-123.45)")
            tai_xe = st.text_input("👨‍✈️ Tên tài xế phụ trách")
            
        with col2:
            khach_hang = st.text_input("🏪 Tên Khách hàng / NPP (Masan)")
            dia_chi = st.text_area("📍 Địa chỉ giao hàng chi tiết", height=105)
            
        with col3:
            ten_hang = st.text_input("📦 Tên mặt hàng (Masan)")
            dvt = st.selectbox("📏 Đơn vị tính", ["Thùng", "Két", "Chai", "Gói", "Bao", "Hộp"])
            phan_loai = st.selectbox("🚨 Phân loại sự cố", [
                "Hàng tồn (Khách nghỉ / Không giao kịp)", 
                "Hàng bể vỡ / Hư hỏng trên xe",
                "Hàng bị khách từ chối (Sai quy cách/Sát date)",
                "Khác"
            ])

        st.markdown("---")
        col4, col5, col6 = st.columns(3)
        with col4:
            sl_ton = st.number_input("📦 Số lượng TỒN (Chưa giao được)", min_value=0, value=0)
        with col5:
            sl_be = st.number_input("💥 Số lượng BỂ VỠ / HƯ HỎNG", min_value=0, value=0)
        with col6:
            ly_do = st.text_input("💬 Lý do chi tiết / Ghi chú", placeholder="VD: Khách đóng cửa sớm / Sập ổ gà bể chai")

        btn_submit = st.form_submit_button("🚨 GHI NHẬN VÀO HỆ THỐNG")

        if btn_submit:
            if not bien_so or not khach_hang or not ten_hang:
                st.error("⚠️ Vui lòng điền đầy đủ: Biển số xe, Khách hàng và Tên mặt hàng!")
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
                    "Trạng_Thái_Đối_Soát": "Chờ xử lý / Đang lưu kho"
                }
                st.session_state.inventory_data = pd.concat([
                    st.session_state.inventory_data, 
                    pd.DataFrame([new_row])
                ], ignore_index=True)
                
                st.success(f"✅ Đã ghi nhận biên bản thành công! Mã: {ma_bb}")

# ----------------------------------------------------
# TAB 2: DANH SÁCH & BỘ LỌC ĐỐI SOÁT
# ----------------------------------------------------
with tab_danhsach:
    st.markdown("##### 📋 Bảng theo dõi & Cập nhật trạng thái xử lý đối soát")
    
    df = st.session_state.inventory_data
    
    if df.empty:
        st.info("Chưa có dữ liệu hàng tồn/bể vỡ nào được ghi nhận.")
    else:
        # Bộ lọc nhanh trên điện thoại
        c_filter1, c_filter2 = st.columns(2)
        with c_filter1:
            filter_bs = st.selectbox("Lọc theo Biển số xe", ["Tất cả"] + list(df["Biển_Số_Xe"].unique()))
        with c_filter2:
            filter_tt = st.selectbox("Lọc theo Trạng thái", ["Tất cả", "Chờ xử lý / Đang lưu kho", "Đã giao lại", "Đã bồi thường / Xuất hủy"])
            
        filtered_df = df.copy()
        if filter_bs != "Tất cả":
            filtered_df = filtered_df[filtered_df["Biển_Số_Xe"] == filter_bs]
        if filter_tt != "Tất cả":
            filtered_df = filtered_df[filtered_df["Trạng_Thái_Đối_Soát"] == filter_tt]

        st.dataframe(
            filtered_df,
            use_container_width=True,
            column_config={
                "Mã_Biên_Bản": "Mã BB",
                "Ngày_Giờ": "Thời Gian",
                "Biển_Số_Xe": "Biển Số",
                "Tên_Tài_Xế": "Tài Xế",
                "Tên_Khách_Hàng": "NPP / Khách Hàng",
                "Địa_Chỉ_Giao": "Địa Chỉ",
                "Tên_Mặt_Hàng": "Sản Phẩm",
                "Số_Lượng_Tồn": st.column_config.NumberColumn("SL Tồn", format="%d"),
                "Số_Lượng_Bể_Vỡ": st.column_config.NumberColumn("SL Bể/Vỡ", format="%d"),
            }
        )

# ----------------------------------------------------
# TAB 3: BÁO CÁO THỐNG KÊ & XUẤT EXCEL
# ----------------------------------------------------
with tab_baocao:
    st.markdown("##### 📊 Thống kê tổng hợp & Xuất đối soát Masan")
    
    df = st.session_state.inventory_data
    if not df.empty:
        b1, b2, b3 = st.columns(3)
        b1.metric("Tổng Số Vụ Việc", f"{len(df)} vụ")
        b2.metric("Tổng Thùng Tồn Chưa Giao", f"{df['Số_Lượng_Tồn'].sum():,.0f} đơn vị")
        b3.metric("Tổng Thùng Bể Vỡ / Hư Hỏng", f"{df['Số_Lượng_Bể_Vỡ'].sum():,.0f} đơn vị", delta_color="inverse")

        st.markdown("---")
        
        # Bảng tổng hợp theo Tài xế / Biển số xe
        st.markdown("<h6>📌 Tổng hợp tỷ lệ sự cố theo Xe / Tài xế</h6>", unsafe_allow_html=True)
        summary_driver = df.groupby(['Biển_Số_Xe', 'Tên_Tài_Xế']).agg(
            So_Lan_Su_Co=('Mã_Biên_Bản', 'count'),
            Tong_Ton=('Số_Lượng_Tồn', 'sum'),
            Tong_Be_Vo=('Số_Lượng_Bể_Vỡ', 'sum')
        ).reset_index()
        st.dataframe(summary_driver, use_container_width=True)

        # Xuất file Excel báo cáo
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Chi_Tiet_Su_Co', index=False)
            summary_driver.to_excel(writer, sheet_name='Tong_Hop_Tai_Xe', index=False)
        
        st.download_button(
            label="📥 TẢI BẢNG ĐỐI SOÁT HÀNG TỒN & BỂ VỠ (EXCEL)",
            data=output.getvalue(),
            file_name=f"Doi_Soat_Hang_Ton_Be_Vo_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.info("Chưa có dữ liệu để xuất báo cáo.")
      
