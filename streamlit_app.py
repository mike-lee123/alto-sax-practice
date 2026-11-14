"""中音薩克斯風練習室：Streamlit Community Cloud 版本。

把單檔 HTML 練習頁嵌進 Streamlit。真實薩克斯風錄音放在 static/builtin.json，
由 Streamlit 的靜態檔案功能提供（.streamlit/config.toml 已開啟 enableStaticServing），
網址是 /app/static/builtin.json。

本機執行：  streamlit run streamlit_app.py
"""

from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

APP_DIR = Path(__file__).parent
PAGE_FILE = APP_DIR / "alto-sax-practice.html"
SAMPLE_FILE = APP_DIR / "static" / "builtin.json"

# 練習頁原本從同一層的 samples/builtin.json 讀樣本；在 Streamlit 裡改成依序嘗試靜態檔案網址
ORIGINAL_FETCH = 'const res = await fetch("samples/builtin.json"); if (!res.ok) return;'
STREAMLIT_FETCH = (
    "let res = null;"
    ' for (const u of ["/app/static/builtin.json", "app/static/builtin.json", "samples/builtin.json"]) {'
    " try { const r = await fetch(u); if (r.ok) { res = r; break; } } catch (e) {} }"
    " if (!res) return;"
)

# Artifact 發布時會自動包上的文件外殼與基本樣式，這裡自己補上
DOC_HEAD = """<!doctype html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<style>
:root{color-scheme:light;padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}
body{margin:0;font:14px/1.5 system-ui,-apple-system,"Segoe UI",sans-serif}
img{max-width:100%}
[hidden]{display:none!important}
</style>
</head>
<body>
"""
DOC_TAIL = "\n</body>\n</html>\n"

# 讓練習頁佔滿整個畫面：隱藏 Streamlit 的頁首、頁尾與預設留白
STREAMLIT_CSS = """
<style>
#MainMenu, header, footer, [data-testid="stHeader"], [data-testid="stToolbar"] {display:none !important;}
.block-container, [data-testid="stMainBlockContainer"] {padding:0 !important; max-width:100% !important;}
[data-testid="stAppViewContainer"] > .main {padding:0 !important;}
iframe {display:block; border:0;}
</style>
"""


@st.cache_data(show_spinner=False)
def build_page(page_mtime: float) -> tuple[str, bool]:
    """讀入練習頁並調整成能在 Streamlit 裡執行。page_mtime 只用來讓快取在檔案更新時失效。"""
    html = PAGE_FILE.read_text(encoding="utf-8")
    patched = ORIGINAL_FETCH in html
    if patched:
        html = html.replace(ORIGINAL_FETCH, STREAMLIT_FETCH, 1)
    return DOC_HEAD + html + DOC_TAIL, patched


def main() -> None:
    st.set_page_config(
        page_title="中音薩克斯風練習室",
        page_icon="🎷",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    st.markdown(STREAMLIT_CSS, unsafe_allow_html=True)

    if not PAGE_FILE.exists():
        st.error(f"找不到練習頁檔案：{PAGE_FILE.name}，請確認它和 streamlit_app.py 放在同一個資料夾。")
        st.stop()

    page, patched = build_page(PAGE_FILE.stat().st_mtime)

    if not SAMPLE_FILE.exists():
        st.warning("找不到 static/builtin.json，練習頁會改用合成音色。把錄音樣本放進 static 資料夾即可使用真實薩克斯風聲音。")
    elif not patched:
        st.warning("練習頁的樣本載入程式和預期不同，可能會改用合成音色。")

    # 高度足以放下桌機版整頁；手機版較長時可在框內捲動
    components.html(page, height=2600, scrolling=True)


main()
