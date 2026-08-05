"""
Hotel Processor — thử các tính năng MỚI của Streamlit
=====================================================
Chạy:  streamlit run app_streamlit_moi.py

Demo 4 thứ:
  1. st.data_editor + column_config  -> sửa bảng tại chỗ, dropdown, định dạng tiền
  2. ButtonColumn                    -> nút "Tạo regcard" trên từng dòng
  3. st.dialog                       -> popup xem trước regcard
  4. @st.fragment                    -> kéo tỷ giá chỉ chạy lại 1 phần, không cả script
"""

import streamlit as st
import pandas as pd

st.set_page_config(page_title="Hotel Processor - tính năng mới", layout="wide")

# --- Đếm số lần chạy lại TOÀN BỘ script (để chứng minh tác dụng của fragment) ---
st.session_state.setdefault("full_runs", 0)
st.session_state.full_runs += 1

# --- Dữ liệu khách ban đầu (giữ trong session_state để nhớ phần đã sửa) ---
if "df_khach" not in st.session_state:
    st.session_state.df_khach = pd.DataFrame({
        "Họ tên": ["Nguyễn Văn A", "John Smith", "Trần Thị B", "Wang Wei", "Lê Văn C"],
        "Quốc tịch": ["Việt Nam", "United States", "Việt Nam", "China", "Việt Nam"],
        "Số phòng": [101, 102, 103, 104, 105],
        "Giá phòng (USD)": [50, 120, 45, 80, 60],
    })

st.title("🏨 Hotel Processor — thử tính năng mới của Streamlit")
st.caption(f"🔁 Số lần chạy lại **TOÀN BỘ** script: **{st.session_state.full_runs}**")
st.divider()


# ---------- (3) DIALOG: popup xem trước regcard ----------
@st.dialog("Xem trước Regcard")
def xem_regcard(row_idx: int):
    df = st.session_state.df_khach
    if row_idx is None or row_idx >= len(df):
        st.warning("Không tìm thấy khách.")
        return
    k = df.iloc[row_idx]
    st.markdown(f"### 📄 Regcard — {k['Họ tên']}")
    st.write(f"- **Quốc tịch:** {k['Quốc tịch']}")
    st.write(f"- **Số phòng:** {k['Số phòng']}")
    st.write(f"- **Giá phòng:** {k['Giá phòng (USD)']} USD")
    st.info("Đây là bản xem trước demo. App thật sẽ sinh file PDF regcard tại đây.")
    if st.button("Đóng"):
        st.rerun()


# callback khi bấm nút regcard trong bảng — lưu lại dòng vừa bấm
def on_regcard_click():
    click = st.session_state.get("btn_regcard")
    if click:
        st.session_state["regcard_row"] = click["row"]


# ---------- (1)+(2) BẢNG KHÁCH: data_editor + ButtonColumn ----------
st.subheader("1 + 2. Bảng khách — sửa tại chỗ & nút Regcard mỗi dòng")
st.caption("Thử: đổi quốc tịch bằng dropdown, sửa giá phòng, hoặc bấm 📄 Tạo ở cột cuối.")

df_show = st.session_state.df_khach.copy()
df_show["Regcard"] = "📄 Tạo"   # giá trị ô = nhãn nút

edited = st.data_editor(
    df_show,
    key="editor_khach",
    hide_index=True,
    width="stretch",
    column_config={
        "Quốc tịch": st.column_config.SelectboxColumn(
            "Quốc tịch",
            options=["Việt Nam", "United States", "China", "Japan", "Korea", "Spain"],
        ),
        "Giá phòng (USD)": st.column_config.NumberColumn(
            "Giá phòng (USD)", format="$%d", min_value=0,
        ),
        "Regcard": st.column_config.ButtonColumn(
            "Regcard",
            help="Tạo regcard cho khách ở dòng này",
            key="btn_regcard",
            on_click=on_regcard_click,
        ),
    },
)

# Lưu lại phần vừa sửa (bỏ cột nút đi)
st.session_state.df_khach = edited.drop(columns=["Regcard"]).reset_index(drop=True)

# Nếu vừa bấm nút regcard -> mở dialog xem trước
if st.session_state.get("regcard_row") is not None:
    xem_regcard(st.session_state.pop("regcard_row"))

st.divider()


# ---------- (4) FRAGMENT: kéo tỷ giá chỉ chạy lại phần này ----------
st.subheader("4. @st.fragment — kéo tỷ giá chỉ chạy lại phần này")

st.session_state.setdefault("frag_runs", 0)

@st.fragment
def phan_convert():
    st.session_state.frag_runs += 1
    ty_gia = st.slider("Tỷ giá USD → VND", 20000, 30000, 26000, step=500)
    df = st.session_state.df_khach
    tong_usd = pd.to_numeric(df["Giá phòng (USD)"], errors="coerce").sum()
    tong_vnd = tong_usd * ty_gia
    c1, c2 = st.columns(2)
    c1.metric("Tổng USD", f"${tong_usd:,.0f}")
    c2.metric("Tổng VND", f"{tong_vnd:,.0f} đ")
    st.caption(f"🔁 Số lần chạy lại **RIÊNG fragment này**: **{st.session_state.frag_runs}**")

phan_convert()

st.info(
    "👉 Kéo thanh tỷ giá: số **chạy lại riêng fragment** tăng, nhưng số "
    "**chạy lại toàn bộ script** ở trên cùng **KHÔNG tăng**. "
    "Đó là điểm mà trước đây Gradio hơn — giờ Streamlit làm được."
)
