import streamlit as st
import streamlit.components.v1 as components
import cv2
import numpy as np
import os
import sys
import tempfile
import subprocess
import time
from math import floor, ceil

# ==============================================================================
# 1. הגדרות עמוד ומנגנון Themes & Device Mode
# ==============================================================================
st.set_page_config(page_title="Velocity Pro Editor ⚡", page_icon="🎬", layout="wide")

# אתחול Session State
if 'system_verified' not in st.session_state:
    st.session_state['system_verified'] = False
if 'theme_mode' not in st.session_state:
    st.session_state['theme_mode'] = 'Dark 🌙'
if 'device_mode' not in st.session_state:
    st.session_state['device_mode'] = '💻 Desktop'

# ==============================================================================
# 2. STEP 1: SYSTEM SETUP & LOCK VERIFICATION
# ==============================================================================
def check_and_install_dependencies():
    status = {}
    
    # 1. בדיקת FFmpeg
    try:
        res = subprocess.run(["ffmpeg", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        status['ffmpeg'] = (res.returncode == 0)
    except Exception:
        status['ffmpeg'] = False

    # 2. בדיקת OpenCV
    try:
        import cv2
        status['opencv'] = True
    except ImportError:
        status['opencv'] = False

    # 3. בדיקת NumPy
    try:
        import numpy
        status['numpy'] = True
    except ImportError:
        status['numpy'] = False

    return status

if not st.session_state['system_verified']:
    st.markdown("<div style='text-align: center; padding: 20px;'>", unsafe_allow_html=True)
    st.markdown("## 🔒 Step 1: System Setup & Requirements Check")
    st.markdown("Verifying system software and video engines before launching...")
    st.markdown("</div>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.status("🔍 Checking required video tools...", expanded=True) as status_box:
            time.sleep(0.5)
            deps = check_and_install_dependencies()
            
            # הצגת סטטוס FFmpeg
            if deps['ffmpeg']:
                st.write("✅ **FFmpeg Engine:** Installed & Ready")
            else:
                st.write("⏳ **FFmpeg Engine:** Installing binaries...")
                try:
                    subprocess.run([sys.executable, "-m", "pip", "install", "imageio-ffmpeg"], check=True)
                    st.write("✅ **FFmpeg Engine:** Successfully installed")
                    deps['ffmpeg'] = True
                except Exception:
                    st.write("⚠️ **FFmpeg Warning:** Ensure FFmpeg is added to system PATH.")

            # הצגת סטטוס OpenCV
            if deps['opencv']:
                st.write("✅ **OpenCV Video Processor:** Installed & Ready")
            else:
                st.write("⏳ **OpenCV:** Installing package...")
                subprocess.run([sys.executable, "-m", "pip", "install", "opencv-python-headless"], check=True)
                st.write("✅ **OpenCV:** Successfully installed")
                deps['opencv'] = True

            # הצגת סטטוס NumPy
            if deps['numpy']:
                st.write("✅ **NumPy Math Engine:** Installed & Ready")
            else:
                st.write("⏳ **NumPy:** Installing package...")
                subprocess.run([sys.executable, "-m", "pip", "install", "numpy"], check=True)
                st.write("✅ **NumPy:** Successfully installed")
                deps['numpy'] = True

            status_box.update(label="🎉 All dependencies verified successfully!", state="complete", expanded=True)

        st.write("")
        if st.button("🚀 Enter Velocity Editor"):
            st.session_state['system_verified'] = True
            st.rerun()

    st.stop()  # עצירת ההרצה עד לסיום האימות המלא

# ==============================================================================
# 3. עיצוב ממשק, צבעים ו-Theme CSS
# ==============================================================================

# סרגל כלים עליון
header_container = st.container()

with header_container:
    t_col1, t_col2, t_col3 = st.columns([1.8, 1.1, 1.1])
    with t_col1:
        st.markdown("<h2 style='margin:0; padding:2px 0; font-weight:900;'>Velocity Pro Editor ⚡</h2>", unsafe_allow_html=True)
    with t_col2:
        device_mode = st.radio("📱 Viewport:", ["💻 Desktop", "📱 Phone"], horizontal=True, key="dev_radio")
    with t_col3:
        theme_mode = st.radio("🎨 Theme:", ["Dark 🌙", "Light ☀️"], horizontal=True, key="theme_radio")

is_dark = "Dark" in theme_mode
is_phone = "Phone" in device_mode

if is_dark:
    bg_body = "#0B0F19"
    card_bg = "#111827"
    card_border = "#374151"
    text_primary = "#F9FAFB"
    text_sub = "#D1D5DB"
    input_bg = "#1F2937"
    input_text = "#F9FAFB"
    btn_grad = "linear-gradient(90deg, #EC4899 0%, #8B5CF6 100%)"
    radio_bg = "#1F2937"
else:
    bg_body = "#F8FAFC"
    card_bg = "#FFFFFF"
    card_border = "#94A3B8"
    text_primary = "#0F172A"
    text_sub = "#334155"
    input_bg = "#F1F5F9"
    input_text = "#0F172A"
    btn_grad = "linear-gradient(90deg, #2563EB 0%, #7C3AED 100%)"
    radio_bg = "#E2E8F0"

vid_max_height = "180px" if is_phone else "280px"
font_base = "13px" if is_phone else "14px"
card_pad = "10px" if is_phone else "16px"
container_max_w = "520px" if is_phone else "1400px"

st.markdown(f"""
    <style>
    /* מרווח עליון ומניעת חיתוך סרגל כלים */
    .block-container {{
        padding-top: 3.2rem !important;
        padding-bottom: 2rem !important;
        padding-left: 0.8rem !important;
        padding-right: 0.8rem !important;
        max-width: {container_max_w} !important;
    }}
    
    html, body, [class*="st-"] {{
        background-color: {bg_body} !important;
        color: {text_primary} !important;
        font-size: {font_base} !important;
        direction: ltr !important;
        text-align: left !important;
        font-family: 'Inter', -apple-system, sans-serif;
    }}

    label, .stMarkdown, p, span {{
        color: {text_primary} !important;
    }}

    /* עיצוב כרטיסיות (Boxes) */
    div[data-testid="stVerticalBlockBorderWrapper"] {{
        border: 2px solid {card_border} !important;
        border-radius: 12px !important;
        padding: {card_pad} !important;
        background-color: {card_bg} !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        margin-bottom: 12px !important;
    }}

    .card-title {{
        color: {text_primary} !important;
        font-size: {"1rem" if is_phone else "1.1rem"};
        font-weight: 800;
        margin-bottom: 8px;
    }}

    /* תיקון מלא של Selectbox, Inputs & Dropdowns - קריאות מלאה ב-Light & Dark */
    div[data-baseweb="select"] > div {{
        background-color: {input_bg} !important;
        color: {input_text} !important;
        border: 1px solid {card_border} !important;
        border-radius: 8px !important;
    }}
    div[data-baseweb="select"] * {{
        color: {input_text} !important;
    }}
    div[data-baseweb="popover"] div {{
        background-color: {card_bg} !important;
        color: {text_primary} !important;
    }}

    input {{
        color: {input_text} !important;
        background-color: {input_bg} !important;
        border: 1px solid {card_border} !important;
        border-radius: 6px !important;
    }}

    /* עיצוב כפתורי Radio */
    div[data-testid="stRadio"] {{
        background: {radio_bg} !important;
        padding: 4px 8px !important;
        border-radius: 8px !important;
        border: 1px solid {card_border} !important;
    }}
    div[data-testid="stRadio"] label {{
        color: {text_primary} !important;
        font-weight: 700 !important;
    }}

    /* נגני וידאו */
    div[data-testid="stImage"] img, video {{
        width: 100% !important;
        max-height: {vid_max_height} !important;
        object-fit: contain;
        border-radius: 8px;
        border: 1px solid {card_border};
        background: #000000;
    }}

    /* תיקון כפתורי Render & Download - הוסרת הצל השחור/הצלליות סביב הטקסט */
    .stButton > button, .stDownloadButton > button {{
        background: {btn_grad} !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 10px 14px !important;
        width: 100%;
        min-height: {"42px" if is_phone else "48px"};
        box-shadow: 0 4px 14px rgba(0,0,0,0.15) !important;
    }}

    .stButton > button p, .stDownloadButton > button p, .stButton > button span, .stDownloadButton > button span {{
        color: #FFFFFF !important;
        font-weight: 800 !important;
        font-size: {"0.95rem" if is_phone else "1.05rem"} !important;
        text-shadow: none !important;
        background: transparent !important;
        margin: 0 !important;
    }}

    .stDownloadButton > button {{
        background: linear-gradient(90deg, #059669 0%, #10B981 100%) !important;
    }}
    </style>
""", unsafe_allow_html=True)


# ==============================================================================
# 4. רכיב BEZIER CANVAS אינטראקטיבי
# ==============================================================================

COMPONENT_DIR = os.path.join(tempfile.gettempdir(), "bezier_component_dir")
os.makedirs(COMPONENT_DIR, exist_ok=True)
component_html_path = os.path.join(COMPONENT_DIR, "index.html")

c_bg = "#0F172A" if is_dark else "#F8FAFC"
c_box_bg = "#1E293B" if is_dark else "#FFFFFF"
c_border = "#475569" if is_dark else "#CBD5E1"
c_stroke = "#38BDF8" if is_dark else "#2563EB"

COMPONENT_HTML = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
<style>
    body {{ background: {c_bg}; color: #000; font-family: sans-serif; margin: 0; padding: 2px; display: flex; gap: 6px; align-items: center; justify-content: center; touch-action: none; }}
    .toolbar {{ display: flex; flex-direction: column; gap: 4px; }}
    .btn {{ width: 32px; height: 32px; background: {c_box_bg}; border: 1px solid {c_border}; border-radius: 6px; color: #2563EB; cursor: pointer; display: flex; align-items: center; justify-content: center; font-size: 13px; font-weight: bold; }}
    .btn:active {{ background: #EC4899; color: #FFF; }}
    .canvas-box {{ position: relative; border: 1px solid {c_border}; border-radius: 8px; background: {c_box_bg}; padding: 4px; display: flex; align-items: center; justify-content: center; }}
    canvas {{ background: {c_bg}; border: 1px solid {c_border}; border-radius: 4px; touch-action: none; }}
</style>
</head>
<body>
    <div class="toolbar">
        <button class="btn" title="Linear" onclick="setPreset(0.0, 0.0, 1.0, 1.0)">╱</button>
        <button class="btn" title="Fast Start" onclick="setPreset(0.05, 0.95, 0.1, 0.95)">⚡</button>
        <button class="btn" title="Smooth Ease" onclick="setPreset(0.42, 0.0, 0.58, 1.0)">∿</button>
        <button class="btn" title="Ease Out" onclick="setPreset(0.8, 0.0, 0.9, 0.2)">◣</button>
    </div>
    <div class="canvas-box">
        <canvas id="bezierCanvas" width="210" height="135"></canvas>
    </div>

    <script>
        function sendToStreamlit(type, data) {{
            window.parent.postMessage(Object.assign({{ isStreamlitMessage: true, type: type }}, data), "*");
        }}

        const canvas = document.getElementById('bezierCanvas');
        const ctx = canvas.getContext('2d');
        let p1 = {{ x: 0.05, y: 0.95 }};
        let p2 = {{ x: 0.1, y: 0.95 }};
        let dragging = null;
        let isInitialized = false;

        const pad = 16;
        const w = canvas.width - pad * 2;
        const h = canvas.height - pad * 2;

        function toCanvas(p) {{ return {{ x: pad + p.x * w, y: pad + (1 - p.y) * h }}; }}
        function toNorm(cx, cy) {{ return {{ x: Math.max(0, Math.min(1, (cx - pad) / w)), y: Math.max(0, Math.min(1, 1 - (cy - pad) / h)) }}; }}

        function updateValue() {{
            sendToStreamlit("streamlit:setComponentValue", {{ value: {{ p1x: p1.x, p1y: p1.y, p2x: p2.x, p2y: p2.y }} }});
        }}

        function draw() {{
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            ctx.strokeStyle = '{c_border}'; ctx.lineWidth = 1; ctx.beginPath();
            ctx.moveTo(pad, pad); ctx.lineTo(pad, canvas.height - pad); ctx.lineTo(canvas.width - pad, canvas.height - pad); ctx.stroke();

            const cStart = toCanvas({{x: 0, y: 0}}), cEnd = toCanvas({{x: 1, y: 1}});
            const cP1 = toCanvas(p1), cP2 = toCanvas(p2);

            ctx.strokeStyle = '#EAB308'; ctx.lineWidth = 1.5; ctx.beginPath();
            ctx.moveTo(cStart.x, cStart.y); ctx.lineTo(cP1.x, cP1.y);
            ctx.moveTo(cEnd.x, cEnd.y); ctx.lineTo(cP2.x, cP2.y); ctx.stroke();

            ctx.strokeStyle = '{c_stroke}'; ctx.lineWidth = 3; ctx.beginPath();
            ctx.moveTo(cStart.x, cStart.y); ctx.bezierCurveTo(cP1.x, cP1.y, cP2.x, cP2.y, cEnd.x, cEnd.y); ctx.stroke();

            [cP1, cP2].forEach(p => {{
                ctx.fillStyle = '#FFFFFF'; ctx.beginPath(); ctx.arc(p.x, p.y, 6, 0, Math.PI * 2); ctx.fill();
                ctx.strokeStyle = '#2563EB'; ctx.lineWidth = 2; ctx.stroke();
            }});
        }}

        function getPos(e) {{
            const rect = canvas.getBoundingClientRect();
            const clientX = e.touches ? e.touches[0].clientX : e.clientX;
            const clientY = e.touches ? e.touches[0].clientY : e.clientY;
            return {{ x: clientX - rect.left, y: clientY - rect.top }};
        }}

        function startDrag(e) {{
            const pos = getPos(e), cP1 = toCanvas(p1), cP2 = toCanvas(p2);
            if (Math.hypot(pos.x - cP1.x, pos.y - cP1.y) < 20) dragging = 'p1';
            else if (Math.hypot(pos.x - cP2.x, pos.y - cP2.y) < 20) dragging = 'p2';
        }}

        function moveDrag(e) {{
            if (!dragging) return;
            if (e.preventDefault) e.preventDefault();
            const norm = toNorm(getPos(e).x, getPos(e).y);
            if (dragging === 'p1') p1 = norm;
            if (dragging === 'p2') p2 = norm;
            draw();
        }}

        function endDrag() {{
            if (dragging) {{
                dragging = null;
                updateValue();
            }}
        }}

        canvas.addEventListener('mousedown', startDrag);
        canvas.addEventListener('mousemove', moveDrag);
        window.addEventListener('mouseup', endDrag);

        canvas.addEventListener('touchstart', startDrag, {{passive: false}});
        canvas.addEventListener('touchmove', moveDrag, {{passive: false}});
        window.addEventListener('touchend', endDrag);

        function setPreset(x1, y1, x2, y2) {{
            p1 = {{ x: x1, y: y1 }};
            p2 = {{ x: x2, y: y2 }};
            draw();
            updateValue();
        }}

        window.addEventListener("message", (event) => {{
            if (event.data.type === "streamlit:render") {{
                if (!isInitialized) {{
                    const args = event.data.args;
                    if (args && args.default) {{
                        p1 = {{ x: args.default.p1x, y: args.default.p1y }};
                        p2 = {{ x: args.default.p2x, y: args.default.p2y }};
                    }}
                    draw();
                    isInitialized = true;
                }}
            }}
        }});

        sendToStreamlit("streamlit:componentReady", {{ apiVersion: 1 }});
        sendToStreamlit("streamlit:setFrameHeight", {{ height: 155 }});
    </script>
</body>
</html>
"""

with open(component_html_path, "w", encoding="utf-8") as f:
    f.write(COMPONENT_HTML)

bezier_interactive_editor = components.declare_component("bezier_editor", path=COMPONENT_DIR)


# ==============================================================================
# 5. מנוע מתמטי לעיבוד תמונה
# ==============================================================================

def crop_frame_with_padding(frame, cx, cy, crop_w, crop_h, out_w, out_h):
    h_img, w_img = frame.shape[:2]
    x1, x2 = cx - crop_w / 2.0, cx + crop_w / 2.0
    y1, y2 = cy - crop_h / 2.0, cy + crop_h / 2.0
    
    canvas_w, canvas_h = max(1, int(round(crop_w))), max(1, int(round(crop_h)))
    canvas = np.zeros((canvas_h, canvas_w, 3), dtype=np.uint8)
    
    src_x1, src_x2 = max(0, int(floor(x1))), min(w_img, int(ceil(x2)))
    src_y1, src_y2 = max(0, int(floor(y1))), min(h_img, int(ceil(y2)))
    
    dst_x1 = max(0, min(canvas_w, int(round(src_x1 - x1))))
    dst_x2 = max(0, min(canvas_w, dst_x1 + (src_x2 - src_x1)))
    dst_y1 = max(0, min(canvas_h, int(round(src_y1 - y1))))
    dst_y2 = max(0, min(canvas_h, dst_y1 + (src_y2 - src_y1)))
    
    src_w, src_h = dst_x2 - dst_x1, dst_y2 - dst_y1
    if src_w > 0 and src_h > 0:
        canvas[dst_y1:dst_y2, dst_x1:dst_x2] = frame[src_y1:src_y1+src_h, src_x1:src_x1+src_w]
        
    return cv2.resize(canvas, (out_w, out_h), interpolation=cv2.INTER_LANCZOS4)


def evaluate_cubic_bezier(p1x, p1y, p2x, p2y, num_samples=1000):
    t = np.linspace(0, 1, 500)
    x_vals = 3 * (1 - t)**2 * t * p1x + 3 * (1 - t) * t**2 * p2x + t**3
    y_vals = 3 * (1 - t)**2 * t * p1y + 3 * (1 - t) * t**2 * p2y + t**3
    
    grid = np.linspace(0, 1, num_samples)
    interpolated_y = np.interp(grid, x_vals, y_vals)
    return grid, np.clip(interpolated_y, 0.0, 1.0)


# ==============================================================================
# 6. ממשק העלאת קבצים ותהליך העבודה
# ==============================================================================

uploaded_file = st.file_uploader("📁 Select Video Clip", type=['mp4', 'mov', 'avi'])

if uploaded_file is not None:
    if 'last_uploaded' not in st.session_state or st.session_state['last_uploaded'] != uploaded_file.name:
        st.session_state['last_uploaded'] = uploaded_file.name
        if 'rendered_video' in st.session_state:
            del st.session_state['rendered_video']

if uploaded_file is not None:
    with tempfile.TemporaryDirectory() as temp_dir:
        input_path = os.path.join(temp_dir, "input.mp4")
        input_trimmed_preview = os.path.join(temp_dir, "trimmed_preview.mp4")
        cropped_preview_path = os.path.join(temp_dir, "cropped_preview.mp4")
        raw_output = os.path.join(temp_dir, "raw_output.mp4")
        final_output = os.path.join(temp_dir, "velocity_final.mp4")
        final_trimmed_path = os.path.join(temp_dir, "final_trimmed.mp4")
        
        with open(input_path, "wb") as f:
            f.write(uploaded_file.read())
            
        cap = cv2.VideoCapture(input_path)
        fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        total_frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        full_duration = total_frame_count / fps if fps > 0 else 0
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        cap.release()
        
        if total_frame_count > 0:
            if is_phone:
                col_left, col_right = st.container(), st.container()
            else:
                col_left, col_right = st.columns([1, 1], gap="small")
            
            # ------------------------------------------------------------------
            # עמודת חיתוך ומהירות (BOX 2)
            # ------------------------------------------------------------------
            with col_right:
                with st.container(border=True):
                    st.markdown("<div class='card-title'>⏱️ Box 2: Trim & Speed Curve</div>", unsafe_allow_html=True)
                    
                    trim_range = st.slider("Drag Trim Range (s):", 0.0, float(round(full_duration, 2)), (0.0, min(1.0, float(round(full_duration, 2)))), step=0.05)
                    
                    t_col1, t_col2 = st.columns(2)
                    with t_col1: start_time = st.number_input("Start (s):", 0.0, float(round(full_duration, 3)), trim_range[0], step=0.05, format="%.2f")
                    with t_col2: end_time = st.number_input("End (s):", 0.0, float(round(full_duration, 3)), trim_range[1], step=0.05, format="%.2f")
                    
                    clip_duration = max(0.0, end_time - start_time)
                    st.caption(f"⏱️ **Trimmed Clip Duration:** `{clip_duration:.2f}`s")
                    
                    # Preview 1: הראו קליפ מקורי חתוך
                    if end_time > start_time:
                        cmd_preview = [
                            "ffmpeg", "-y", "-ss", str(start_time), "-to", str(end_time),
                            "-i", input_path, "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "ultrafast", input_trimmed_preview
                        ]
                        subprocess.run(cmd_preview, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

                        if os.path.exists(input_trimmed_preview):
                            st.markdown("##### 🎬 Raw Trimmed Clip Preview:")
                            st.video(input_trimmed_preview)

                    st.markdown("##### ⚡ Speed Bezier Graph")
                    speed_canvas_data = bezier_interactive_editor(
                        key="speed_canvas",
                        default={"p1x": 0.05, "p1y": 0.95, "p2x": 0.1, "p2y": 0.95}
                    ) or {"p1x": 0.05, "p1y": 0.95, "p2x": 0.1, "p2y": 0.95}
                    
                    sp_col1, sp_col2 = st.columns(2)
                    with sp_col1: max_speed_val = st.number_input("Max Speed (x):", 0.5, 10.0, 4.0, step=0.5)
                    with sp_col2: min_speed_val = st.number_input("Min Speed (x):", 0.01, 2.0, 0.1, step=0.05)

                    cut_junction_frames = st.number_input("Drop Junction Frames:", min_value=0, max_value=60, value=0, step=1)

            # ------------------------------------------------------------------
            # עמודת מסגור ו-Aspect Ratio (BOX 1)
            # ------------------------------------------------------------------
            with col_left:
                with st.container(border=True):
                    st.markdown("<div class='card-title'>🖼️ Box 1: Framing & Aspect Ratio Preview</div>", unsafe_allow_html=True)
                    
                    aspect_ratio_option = st.selectbox(
                        "📐 Aspect Ratio Preset:",
                        ["Original", "9:16 (TikTok / Reels)", "16:9 (YouTube)", "1:1 (Instagram)", "4:3 (Classic)", "3:4 (Feed)"]
                    )
                    
                    if aspect_ratio_option == "9:16 (TikTok / Reels)": target_ar = 9.0 / 16.0
                    elif aspect_ratio_option == "16:9 (YouTube)": target_ar = 16.0 / 9.0
                    elif aspect_ratio_option == "1:1 (Instagram)": target_ar = 1.0
                    elif aspect_ratio_option == "4:3 (Classic)": target_ar = 4.0 / 3.0
                    elif aspect_ratio_option == "3:4 (Feed)": target_ar = 3.0 / 4.0
                    else: target_ar = width / height

                    if (width / height) > target_ar:
                        base_h, base_w = height, int(height * target_ar)
                    else:
                        base_w, base_h = width, int(width / target_ar)
                        
                    base_w = base_w if base_w % 2 == 0 else base_w - 1
                    base_h = base_h if base_h % 2 == 0 else base_h - 1
                    
                    framing_scale = st.slider("🔍 Framing Scale:", 0.3, 3.0, 1.0, step=0.05)
                    
                    f_col1, f_col2 = st.columns(2)
                    with f_col1: frame_x = st.slider("Framing Box X (%)", -50, 150, 50)
                    with f_col2: frame_y = st.slider("Framing Box Y (%)", -50, 150, 50)

                    fcx, fcy = int(width * (frame_x / 100.0)), int(height * (frame_y / 100.0))
                    eff_box_w, eff_box_h = int(base_w * framing_scale), int(base_h * framing_scale)

                    # Preview 2: הראו קליפ חתוך + ממוסגר לפי ה-Aspect Ratio
                    if os.path.exists(input_trimmed_preview):
                        crop_w = min(width, max(2, eff_box_w))
                        crop_h = min(height, max(2, eff_box_h))
                        
                        crop_x = max(0, min(width - crop_w, int(fcx - crop_w / 2.0)))
                        crop_y = max(0, min(height - crop_h, int(fcy - crop_h / 2.0)))
                        
                        crop_w, crop_h = crop_w - (crop_w % 2), crop_h - (crop_h % 2)
                        crop_x, crop_y = crop_x - (crop_x % 2), crop_y - (crop_y % 2)
                        
                        cmd_crop_preview = [
                            "ffmpeg", "-y", "-i", input_trimmed_preview,
                            "-vf", f"crop={crop_w}:{crop_h}:{crop_x}:{crop_y},scale={base_w}:{base_h}",
                            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "ultrafast", cropped_preview_path
                        ]
                        subprocess.run(cmd_crop_preview, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        
                        if os.path.exists(cropped_preview_path):
                            st.markdown("##### 📐 Aspect Ratio & Framed Preview:")
                            st.video(cropped_preview_path)

            # ------------------------------------------------------------------
            # כפתור רינדור ו-BOX 3 (תוצאה סופית)
            # ------------------------------------------------------------------
            st.write(" ")
            process_btn = st.button("🚀 Render Velocity Effect")
            
            if process_btn:
                progress_bar = st.progress(0)
                status_text = st.empty()
                status_text.text("⏳ Reading raw video frames...")

                cap = cv2.VideoCapture(input_path)
                start_idx = int(start_time * fps)
                end_idx = int(end_time * fps)
                if end_idx <= start_idx: end_idx = start_idx + 1
                
                cap.set(cv2.CAP_PROP_POS_FRAMES, start_idx)
                frames = []
                for _ in range(start_idx, end_idx):
                    r, f_frame = cap.read()
                    if not r: break
                    frames.append(f_frame)
                cap.release()
                
                if len(frames) > 0:
                    status_text.text("⚡ Applying Velocity Ramping...")
                    total_frames = len(frames)
                    duration = total_frames / fps
                    out_fps = 60.0
                    
                    sp_p1x, sp_p1y = speed_canvas_data["p1x"], speed_canvas_data["p1y"]
                    sp_p2x, sp_p2y = speed_canvas_data["p2x"], speed_canvas_data["p2y"]
                    
                    _, s_y = evaluate_cubic_bezier(sp_p1x, sp_p1y, sp_p2x, sp_p2y, num_samples=1000)
                    s_curve_fwd = max_speed_val - (max_speed_val - min_speed_val) * s_y

                    s_cumsum_fwd = np.cumsum(s_curve_fwd)
                    s_cumsum_fwd = np.insert(s_cumsum_fwd, 0, 0.0)
                    s_cdf_fwd = s_cumsum_fwd / s_cumsum_fwd[-1]

                    avg_speed = np.mean(s_curve_fwd)
                    t_out_total = duration / avg_speed
                    num_out_frames = max(2, int(round(t_out_total * out_fps)))

                    ramped_frames_fwd = []
                    for i in range(num_out_frames):
                        u = i / max(1, num_out_frames - 1)
                        idx = min(int(u * 1000), 1000)
                        src_progress = s_cdf_fwd[idx]
                        
                        frame_idx = min(int(src_progress * (total_frames - 1)), total_frames - 1)
                        curr_frame = frames[frame_idx]
                        
                        resized = crop_frame_with_padding(curr_frame, fcx, fcy, eff_box_w, eff_box_h, base_w, base_h)
                        ramped_frames_fwd.append(resized)
                        progress_bar.progress(int((i / num_out_frames) * 45))

                    status_text.text("🔄 Generating Ping-Pong Reverse...")
                    s_curve_rev = s_curve_fwd[::-1]

                    s_cumsum_rev = np.cumsum(s_curve_rev)
                    s_cumsum_rev = np.insert(s_cumsum_rev, 0, 0.0)
                    s_cdf_rev = s_cumsum_rev / s_cumsum_rev[-1]

                    ramped_frames_rev = []
                    for i in range(num_out_frames):
                        u = i / max(1, num_out_frames - 1)
                        idx = min(int(u * 1000), 1000)
                        
                        src_progress_rev = s_cdf_rev[idx]
                        src_progress = 1.0 - src_progress_rev
                        frame_idx = max(0, min(int(src_progress * (total_frames - 1)), total_frames - 1))
                        curr_frame = frames[frame_idx]
                        
                        resized = crop_frame_with_padding(curr_frame, fcx, fcy, eff_box_w, eff_box_h, base_w, base_h)
                        ramped_frames_rev.append(resized)
                        progress_bar.progress(45 + int((i / num_out_frames) * 45))

                    if cut_junction_frames > 0:
                        fwd_cut = ramped_frames_fwd[:-cut_junction_frames] if cut_junction_frames < len(ramped_frames_fwd) else ramped_frames_fwd
                        rev_cut = ramped_frames_rev[cut_junction_frames:] if cut_junction_frames < len(ramped_frames_rev) else ramped_frames_rev
                        final_frames = fwd_cut + rev_cut
                    else:
                        final_frames = ramped_frames_fwd + ramped_frames_rev
                    
                    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                    out = cv2.VideoWriter(raw_output, fourcc, out_fps, (base_w, base_h))
                    for f in final_frames: out.write(f)
                    out.release()
                    
                    cmd = [
                        "ffmpeg", "-y", "-i", raw_output,
                        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "fast", final_output
                    ]
                    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    
                    progress_bar.progress(100)
                    status_text.empty()
                    progress_bar.empty()
                    
                    with open(final_output, "rb") as rendered_file:
                        st.session_state['rendered_video'] = rendered_file.read()
                        st.rerun()

            if 'rendered_video' in st.session_state:
                with st.container(border=True):
                    st.markdown("<div class='card-title'>🎬 Box 3: Final Rendered Video</div>", unsafe_allow_html=True)
                    
                    temp_rendered_path = os.path.join(temp_dir, "temp_rendered.mp4")
                    with open(temp_rendered_path, "wb") as f:
                        f.write(st.session_state['rendered_video'])
                    
                    cap_rendered = cv2.VideoCapture(temp_rendered_path)
                    r_fps = cap_rendered.get(cv2.CAP_PROP_FPS) or 60.0
                    r_frames = int(cap_rendered.get(cv2.CAP_PROP_FRAME_COUNT))
                    r_duration = r_frames / r_fps if r_fps > 0 else 0
                    cap_rendered.release()
                    
                    post_trim_range = st.slider("✂️ Output Trim (s):", 0.0, float(round(r_duration, 2)), (0.0, float(round(r_duration, 2))), step=0.05)
                    
                    actual_start, actual_end = min(post_trim_range[0], post_trim_range[1]), max(post_trim_range[0], post_trim_range[1])
                    
                    if actual_end > actual_start:
                        cmd_final_trim = [
                            "ffmpeg", "-y", "-ss", str(actual_start), "-to", str(actual_end),
                            "-i", temp_rendered_path, "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "ultrafast", final_trimmed_path
                        ]
                        subprocess.run(cmd_final_trim, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        
                        if os.path.exists(final_trimmed_path):
                            st.video(final_trimmed_path)
                            with open(final_trimmed_path, "rb") as file:
                                st.download_button("📥 Download Final Video", data=file, file_name="velocity_final_edit.mp4", mime="video/mp4")