"""中音薩克斯風練習室：Streamlit Community Cloud 版本。

把單檔 HTML 練習頁嵌進 Streamlit。真實薩克斯風錄音放在 static/builtin.json，
由 Streamlit 的靜態檔案功能提供（.streamlit/config.toml 已開啟 enableStaticServing），
網址是 /app/static/builtin.json。

本機執行：  streamlit run streamlit_app.py
"""

from __future__ import annotations

from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

APP_DIR = Path(__file__).parent
PAGE_FILE = APP_DIR / "alto-sax-practice.html"
STATIC_SAMPLES = APP_DIR / "static" / "builtin.json"
SAMPLE_NAME = "builtin.json"

# 練習頁原本從同一層的 samples/builtin.json 讀樣本。在 Streamlit 裡改成：
# 先用直接嵌進頁面的樣本（window.__SAX_SAMPLES__），沒有的話再依序嘗試靜態檔案網址。
ORIGINAL_FETCH = 'const res = await fetch("samples/builtin.json"); if (!res.ok) return;'
STREAMLIT_FETCH = (
    "let res = null;"
    " if (window.__SAX_SAMPLES__) { const data = window.__SAX_SAMPLES__; res = { ok: true, json: async () => data }; }"
    ' else for (const u of ["/app/static/builtin.json", "app/static/builtin.json", "samples/builtin.json"]) {'
    " try { const r = await fetch(u); if (r.ok) { res = r; break; } } catch (e) {} }"
    " if (!res) return;"
)


def find_samples() -> Path | None:
    """找錄音樣本檔：優先 static/builtin.json，其次 repo 裡任何位置的 builtin.json。"""
    if STATIC_SAMPLES.is_file():
        return STATIC_SAMPLES
    for candidate in [APP_DIR / SAMPLE_NAME, APP_DIR / "samples" / SAMPLE_NAME]:
        if candidate.is_file():
            return candidate
    found = sorted(p for p in APP_DIR.rglob(SAMPLE_NAME) if ".git" not in p.parts)
    return found[0] if found else None


def list_repo_files(limit: int = 40) -> list[str]:
    """列出 repo 裡的檔案，找不到樣本時給使用者對照。"""
    files = sorted(
        str(p.relative_to(APP_DIR)).replace("\\", "/")
        for p in APP_DIR.rglob("*")
        if p.is_file() and ".git" not in p.parts
    )
    return files[:limit]

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
def build_page(page_mtime: float, inline_samples: str | None, samples_mtime: float) -> tuple[str, bool]:
    """讀入練習頁並調整成能在 Streamlit 裡執行。

    inline_samples 是要直接嵌進頁面的樣本檔路徑（樣本不在 static/ 時使用）；
    兩個 mtime 只用來讓快取在檔案更新時失效。
    """
    html = PAGE_FILE.read_text(encoding="utf-8")
    patched = ORIGINAL_FETCH in html
    if patched:
        html = html.replace(ORIGINAL_FETCH, STREAMLIT_FETCH, 1)
    embed = ""
    if inline_samples:
        data = Path(inline_samples).read_text(encoding="utf-8").replace("</", "<\\/")
        embed = f"<script>window.__SAX_SAMPLES__ = {data};</script>\n"
    return DOC_HEAD + embed + html + DOC_TAIL, patched


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

    samples = find_samples()
    # 樣本在 static/ 裡就用網址載入（瀏覽器可快取）；在別的位置就直接嵌進頁面
    inline = str(samples) if samples and samples != STATIC_SAMPLES else None
    page, patched = build_page(
        PAGE_FILE.stat().st_mtime,
        inline,
        samples.stat().st_mtime if samples else 0.0,
    )

    if samples is None:
        st.warning(
            "找不到錄音樣本 builtin.json，練習頁會改用合成音色。"
            "請把 builtin.json 上傳到 GitHub repo（放在 static 資料夾或 repo 最上層都可以）。"
        )
        with st.expander("目前 repo 裡的檔案"):
            st.code("\n".join(list_repo_files()) or "（沒有檔案）")
    elif not patched:
        st.warning("練習頁的樣本載入程式和預期不同，可能會改用合成音色。")

    # 高度足以放下桌機版整頁；手機版較長時可在框內捲動
    components.html(page, height=2600, scrolling=True)


main()
