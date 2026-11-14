# 中音薩克斯風練習室（Streamlit 版）

E♭ 中音薩克斯風的練習網頁：35 課由易而難的課程、50 首樂譜庫、五線譜與指法圖、真實薩克斯風錄音示範、跟著吹、練習進度與樂器照顧說明。

## 檔案

```
streamlit_app.py          Streamlit 主程式
alto-sax-practice.html    練習頁本體
static/builtin.json       真實薩克斯風錄音樣本（愛荷華大學 MIS，公有領域）
.streamlit/config.toml    開啟靜態檔案功能
requirements.txt          套件需求
```

## 本機執行

```
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## 部署到 Streamlit Community Cloud

1. 把這整個資料夾（含 `.streamlit` 和 `static`）推到一個 GitHub repo。
2. 到 https://share.streamlit.io 用 GitHub 登入，按 **Create app**。
3. 選這個 repo、分支 `main`，Main file path 填 `streamlit_app.py`，可在 App URL 自訂網址名稱，按 **Deploy**。

## 說明

- 練習進度存在瀏覽器裡（localStorage），換瀏覽器或清除網站資料會不見。
- 錄音樣本來源：University of Iowa Electronic Music Studios, Musical Instrument Samples（Eb Alto Saxophone，non-vibrato，ff）。
