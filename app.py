import streamlit as st
import pandas as pd
import random
import io
import json
import os
from datetime import datetime, timedelta, date

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="LGS Koç Pro v9", layout="wide", page_icon="🎓")

# --- TASARIM (CSS) ---
st.markdown("""
<style>
    .stApp {background: linear-gradient(135deg, #fdfbfb 0%, #ebedee 100%);}
    .main .block-container {
        background-color: rgba(255, 255, 255, 0.95);
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
    }
    h1 {color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px;}
    
    .live-net-box {
        background-color: #e1f5fe;
        color: #0277bd;
        border: 1px solid #81d4fa;
        padding: 5px;
        border-radius: 5px;
        text-align: center;
        font-weight: bold;
        margin-top: 2px;
    }
    
    .date-badge {
        font-size: 0.8em;
        color: #666;
        background-color: #eee;
        padding: 2px 6px;
        border-radius: 4px;
        margin-bottom: 10px;
        display: inline-block;
    }

    .alert-box {padding: 15px; border-radius: 10px; margin-bottom: 10px; border-left: 5px solid;}
    .alert-red {background-color: #ffebee; border-color: #c62828; color: #b71c1c;}
    .alert-orange {background-color: #fff3e0; border-color: #ef6c00; color: #e65100;}
    
    .motivasyon-banner {
        background: linear-gradient(90deg, #4b6cb7 0%, #182848 100%);
        color: white;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        font-size: 1.2em;
        font-weight: bold;
        margin-bottom: 20px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.2);
    }
    
    /* Kaydedilmedi Uyarısı */
    .unsaved-warning {
        background-color: #fff3e0;
        color: #e65100;
        padding: 10px;
        border-radius: 5px;
        text-align: center;
        border: 1px dashed #e65100;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# --- VERİ & AYARLAR ---
DOSYA_ADI = "ogrenciler.json"

dersler_config = {
    "Matematik": {"katsayi": 4}, "Fen Bilimleri": {"katsayi": 4}, "Türkçe": {"katsayi": 4},
    "İnkılap/Sosyal": {"katsayi": 1}, "İngilizce": {"katsayi": 1}, "Din Kültürü": {"katsayi": 1}
}

balikesir_liseleri = [
    {"ad": "Şehit Turgut Solak Fen Lisesi", "puan": 488},
    {"ad": "Sırrı Yırcalı Anadolu Lisesi [SYAL]", "puan": 475},
    {"ad": "Enerjisa Bandırma Fen Lisesi", "puan": 472},
    {"ad": "Şehit Mustafa Serin Fen Lisesi (Edremit)", "puan": 468},
    {"ad": "Fatma-Emin Kutvar Anadolu Lisesi [FEKAL]", "puan": 462},
    {"ad": "Rahmi Kula Anadolu Lisesi", "puan": 450},
    {"ad": "Gönen Ticaret Odası Fen Lisesi", "puan": 445},
    {"ad": "Balıkesir Anadolu Lisesi", "puan": 435},
    {"ad": "Yavuz Sultan Selim Anadolu Lisesi", "puan": 430},
    {"ad": "İstanbulluoğlu Sosyal Bilimler Lisesi", "puan": 420},
    {"ad": "Edremit Anadolu Lisesi", "puan": 415},
    {"ad": "Burhaniye Celal Toraman AL", "puan": 412},
    {"ad": "15 Temmuz Şehitler Anadolu Lisesi", "puan": 405},
    {"ad": "Bandırma Anadolu Lisesi", "puan": 402},
    {"ad": "Ayvalık Anadolu Lisesi", "puan": 398},
    {"ad": "Gülser-Mehmet Bolluk Anadolu Lisesi", "puan": 390}
]
balikesir_liseleri = sorted(balikesir_liseleri, key=lambda x: x["puan"], reverse=True)

youtube_kanallari = {
    "Matematik": ["Tonguç Akademi", "Rehber Matematik", "Partikül Matematik", "İmt Hoca", "Şenol Hoca", "LGS Hocam"],
    "Fen Bilimleri": ["Tonguç Fen", "Fen Kuşağı", "Hocalara Geldik", "Bizim Hocalar"],
    "Türkçe": ["Rüştü Hoca", "Benim Hocam", "Önder Hoca", "Tonguç Türkçe"],
    "İngilizce": ["English with Burak", "Tonguç İngilizce", "Özer Kiraz"],
    "İnkılap/Sosyal": ["Sosyal Kale", "Benim Hocam", "Tonguç Sosyal"],
    "Din Kültürü": ["Din Dersi Materyal", "Tonguç Din", "Benim Hocam Din"]
}

teknikler = [
    {"baslik": "🍅 Pomodoro", "detay": "25 dk Ders + 5 dk Mola."},
    {"baslik": "🧠 Zihin Haritalama", "detay": "Konuyu merkeze yaz, dallara ayır."},
    {"baslik": "🔁 Aralıklı Tekrar", "detay": "1. gün, 3. gün ve 7. gün tekrar."},
    {"baslik": "🗣️ Feynman", "detay": "Basitleştirerek anlat."},
    {"baslik": "📦 Kutu Tekniği", "detay": "Yapamadığın soruları biriktir."},
    {"baslik": "⚡ Aktif Hatırlama", "detay": "Kitabı kapat, aklında kalanları yaz."},
    {"baslik": "📊 Eisenhower", "detay": "Acil ve Önemli dersi önce yap."}
]

motivasyon_sozleri = {
    "dusuk": ["🚀 Başlamak başarmanın yarısıdır. Yükseleceğiz!", "💪 Zorlanıyorsan gelişiyorsun demektir."],
    "orta": ["🔥 Harika gidiyorsun, hedefe az kaldı!", "⚡ Potansiyelin yüksek, gaza bas!"],
    "yuksek": ["🏆 Şampiyonlar detaylarda gizlidir.", "🌟 Mükemmelsin! Aynen devam."]
}

# --- FONKSİYONLAR ---
def verileri_yukle():
    if not os.path.exists(DOSYA_ADI): return {}
    with open(DOSYA_ADI, "r", encoding="utf-8") as f: return json.load(f)

def verileri_kaydet(data):
    with open(DOSYA_ADI, "w", encoding="utf-8") as f: json.dump(data, f, ensure_ascii=False, indent=4)

def puan_hesapla(deneme_data):
    puan = 194.76
    puan += deneme_data["Matematik"]["net"] * 4.39
    puan += deneme_data["Fen Bilimleri"]["net"] * 4.07
    puan += deneme_data["Türkçe"]["net"] * 3.89
    puan += deneme_data["İnkılap/Sosyal"]["net"] * 1.68
    puan += deneme_data["Din Kültürü"]["net"] * 1.65
    puan += deneme_data["İngilizce"]["net"] * 1.50
    return min(500, puan)

def temizle_state():
    """Giriş alanlarını ve programı temizler"""
    keys_to_clear = [key for key in st.session_state.keys() if key.startswith("d_") or key.startswith("y_") or key.startswith("h_")]
    for key in keys_to_clear:
        del st.session_state[key]
    # Programı da sıfırla ki yeni moda temiz geçilsin
    st.session_state.df_program = pd.DataFrame()
    st.session_state.is_saved = False # Kaydedildi bilgisini sıfırla

def sifirla_her_seyi():
    """Kaydetmeden çıkma durumunda"""
    st.session_state.df_program = pd.DataFrame()
    temizle_state()
    st.rerun()

# --- YAN MENÜ ---
kayitli_veriler = verileri_yukle()

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3429/3429149.png", width=80)
    st.title("⚙️ Yönetim Paneli")
    
    # Mod değişince temizle
    mod = st.radio("İşlem", ["Yeni Kayıt", "Kayıtlı Öğrenci"], on_change=temizle_state)
    
    secili_ogrenci = ""
    varsayilan = {}
    son_guncelleme = ""
    
    if mod == "Kayıtlı Öğrenci":
        isimler = list(kayitli_veriler.keys())
        if isimler:
            secili_ogrenci = st.selectbox("Öğrenci Seç", isimler, on_change=temizle_state)
            varsayilan = kayitli_veriler[secili_ogrenci]
            son_guncelleme = varsayilan.get("tarih", "Tarih Yok")
            st.markdown(f"<div class='date-badge'>🕒 Son Güncelleme: {son_guncelleme}</div>", unsafe_allow_html=True)
        else:
            st.warning("Kayıtlı öğrenci yok.")
            mod = "Yeni Kayıt"

    if mod == "Yeni Kayıt":
        ogrenci_adi = st.text_input("Ad Soyad Giriniz")
        varsayilan = {} 
    else:
        ogrenci_adi = st.text_input("Öğrenci Adı", value=secili_ogrenci, disabled=True)

    with st.expander("🎯 Hedefler", expanded=True):
        def_hedef = varsayilan.get("gunluk_hedef", 150)
        gunluk_hedef = st.number_input("Günlük Soru Hedefi", 50, 1000, def_hedef, step=10)
        okul_cikis = st.time_input("Okul Çıkış", value=datetime.strptime("15:30", "%H:%M").time())

    st.markdown("### 📊 Net Girişi")
    deneme_sonuclari = {}
    
    for ders, detay in dersler_config.items():
        limit = 20 if detay['katsayi']==4 else 10
        
        k_d, k_y, k_h = 0, 0, float(limit)
        if varsayilan and "dersler" in varsayilan:
            if ders in varsayilan["dersler"]:
                veriler = varsayilan["dersler"][ders]
                k_d = veriler.get("d", 0)
                k_y = veriler.get("y", 0)
                k_h = veriler.get("hedef", float(limit))
        
        with st.expander(f"📘 {ders}", expanded=False):
            c1, c2 = st.columns(2)
            d = c1.number_input("D", 0, limit, k_d, key=f"d_{ders}")
            y = c2.number_input("Y", 0, limit-d, k_y, key=f"y_{ders}")
            hedef = st.number_input("Hedef", 0.0, float(limit), k_h, step=0.5, key=f"h_{ders}")
            
            net = max(0, d - (y/3))
            st.markdown(f"<div class='live-net-box'>NET: {net:.2f}</div>", unsafe_allow_html=True)
            
            deneme_sonuclari[ders] = {
                "d": d, "y": y, "net": net, "hedef": hedef, 
                "limit": limit, "katsayi": detay['katsayi']
            }
            
    st.divider()
    st.markdown("### ⭐ Manuel Öncelik")
    ders_yildizlari = {d: st.slider(f"{d}", 1, 5, 3) for d in dersler_config.keys()}

# --- ALGORİTMA ---
def motivasyon_sec(sonuclar):
    toplam_h = sum([v['hedef'] for v in sonuclar.values()])
    toplam_n = sum([v['net'] for v in sonuclar.values()])
    if toplam_h == 0: return motivasyon_sozleri["orta"][0]
    oran = toplam_n / toplam_h
    if oran < 0.5: return random.choice(motivasyon_sozleri["dusuk"])
    elif oran < 0.8: return random.choice(motivasyon_sozleri["orta"])
    else: return random.choice(motivasyon_sozleri["yuksek"])

def saatleri_ayarla(cikis):
    saatler = []
    basla = datetime.combine(date.today(), cikis) + timedelta(minutes=60)
    saatler.append(f"{basla.strftime('%H:%M')}-{(basla+timedelta(minutes=30)).strftime('%H:%M')} (Rutin)")
    basla += timedelta(minutes=40)
    for i in range(3):
        saatler.append(f"{basla.strftime('%H:%M')}-{(basla+timedelta(minutes=40)).strftime('%H:%M')} ({i+1}. Etüt)")
        basla += timedelta(minutes=50)
    return saatler

def akilli_ders_sec(onceki=None):
    havuz = []
    for ders in dersler_config.keys():
        v = deneme_sonuclari[ders]
        yildiz = ders_yildizlari[ders]
        fark = max(1.0, v['hedef'] - v['net'])
        puan = int((fark * v['katsayi'] * 3) + (yildiz * 5) + 10)
        havuz.extend([ders] * puan)
    
    secilen = random.choice(havuz)
    tries = 0
    while secilen == onceki and tries < 10:
        secilen = random.choice(havuz)
        tries += 1
    return secilen

def program_olustur():
    zamanlar = saatleri_ayarla(okul_cikis)
    gunler = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]
    rows = []
    rutin_soru = 20
    kalan = max(0, gunluk_hedef - rutin_soru)
    etut_soru = int(kalan / 3)
    
    if "prev_map" not in st.session_state: st.session_state.prev_map = {g:None for g in gunler}
    
    for z in zamanlar:
        row = {"Saat": z}
        for g in gunler:
            if "Rutin" in z:
                row[g] = "Paragraf / Kitap"
                row[f"{g}_Soru"] = rutin_soru
            else:
                prev = st.session_state.prev_map[g]
                secilen = akilli_ders_sec(prev)
                st.session_state.prev_map[g] = secilen
                row[g] = secilen
                if dersler_config[secilen]["katsayi"] == 1:
                    row[f"{g}_Soru"] = min(20, etut_soru)
                else:
                    row[f"{g}_Soru"] = etut_soru
        rows.append(row)
    del st.session_state.prev_map
    return pd.DataFrame(rows)

# --- EXCEL ---
def excel_indir(df_prog, net_data, tekniks, mot_sozu):
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df_prog.to_excel(writer, sheet_name='Plan', startrow=4, index=False)
        wb = writer.book
        ws = writer.sheets['Plan']
        
        fmt_title = wb.add_format({'bold':True, 'font_size':16, 'bg_color':'#1565c0', 'font_color':'white', 'align':'center', 'border':1})
        fmt_mot = wb.add_format({'bold':True, 'italic':True, 'font_size':12, 'bg_color':'#6a1b9a', 'font_color':'white', 'align':'center', 'border':1})
        fmt_head = wb.add_format({'bold':True, 'bg_color':'#37474f', 'font_color':'white', 'border':1, 'align':'center'})
        fmt_cell = wb.add_format({'border':1, 'align':'center', 'valign':'vcenter', 'text_wrap':True})
        fmt_yellow = wb.add_format({'bold':True, 'bg_color':'#fff176', 'border':1, 'align':'center'})
        fmt_sect = wb.add_format({'bold':True, 'font_size':14, 'font_color':'#c62828', 'bottom':2})
        
        ws.merge_range('A1:O1', f"{ogrenci_adi} - HAFTALIK ÇALIŞMA PROGRAMI", fmt_title)
        ws.merge_range('A2:O2', f"💡 {mot_sozu}", fmt_mot)
        ws.write('A3', f"Tarih: {datetime.now().strftime('%d.%m.%Y')}")

        ws.set_column(0,0, 20)
        ws.set_column(1,14, 11)
        
        for c, val in enumerate(df_prog.columns): ws.write(4, c, val, fmt_head)
        for r, row in enumerate(df_prog.values):
            for c, val in enumerate(row): ws.write(r+5, c, val, fmt_cell)
        
        last_row = len(df_prog) + 6
        ws.write(last_row, 0, "GÜNLÜK HEDEF", fmt_yellow)
        c_idx = 1
        total_w = 0
        gunler = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]
        for g in gunler:
            if f"{g}_Soru" in df_prog.columns:
                s = df_prog[f"{g}_Soru"].sum()
                total_w += s
                ws.write(last_row, c_idx+1, s, fmt_yellow)
            c_idx += 2
        ws.write(last_row, c_idx, "TOPLAM:", fmt_yellow)
        ws.write(last_row, c_idx+1, total_w, fmt_yellow)
        
        row_n = last_row + 3
        ws.write(row_n, 0, "📊 NET KARNESİ", fmt_sect)
        row_n += 1
        headers = ["Ders", "Doğru", "Yanlış", "NET", "Hedef", "Durum"]
        for i, h in enumerate(headers): ws.write(row_n, i, h, fmt_head)
        row_n += 1
        for d, v in net_data.items():
            durum = "✅" if v['net'] >= v['hedef'] else "🔻"
            ws.write(row_n, 0, d, fmt_cell)
            ws.write(row_n, 1, v['d'], fmt_cell)
            ws.write(row_n, 2, v['y'], fmt_cell)
            ws.write(row_n, 3, v['net'], fmt_yellow) 
            ws.write(row_n, 4, v['hedef'], fmt_cell)
            ws.write(row_n, 5, durum, fmt_cell)
            row_n += 1
            
        row_rec = row_n + 2
        ws.write(row_rec, 0, "📺 TAVSİYELER", fmt_sect)
        row_rec += 1
        for d, v in net_data.items():
            if v['net'] < v['hedef']:
                msg = "Konu çalış" if v['net'] < v['limit']*0.5 else "Soru çöz"
                ws.write(row_rec, 0, d, fmt_yellow)
                ws.write(row_rec, 1, msg, fmt_cell)
                if d in youtube_kanallari:
                    ws.merge_range(row_rec, 2, row_rec, 8, ", ".join(youtube_kanallari[d]), fmt_cell)
                row_rec += 1
        
        row_t = row_rec + 2
        ws.write(row_t, 0, "🧠 TEKNİKLER", fmt_sect)
        row_t += 1
        for t in tekniks:
            ws.write(row_t, 0, t['baslik'], fmt_yellow)
            ws.merge_range(row_t, 1, row_t, 10, t['detay'], fmt_cell)
            row_t += 1
            
        ws.set_landscape()
        ws.fit_to_pages(1, 0)
    return buffer.getvalue()

# --- ANA AKIŞ ---
st.title(f"🎓 LGS Akıllı Koç: {ogrenci_adi}")

if 'df_program' not in st.session_state: st.session_state.df_program = pd.DataFrame()
if 'motivasyon' not in st.session_state: st.session_state.motivasyon = ""
if 'is_saved' not in st.session_state: st.session_state.is_saved = False

# Buton Stili ve Mantığı
# Önce programı oluşturup gösteriyoruz, kaydetme butonu sonra çıkıyor.

if st.button("📊 Programı Hazırla (Önizle)", type="primary", use_container_width=True):
    if not ogrenci_adi:
        st.error("Lütfen bir öğrenci ismi girin!")
    else:
        st.session_state.df_program = program_olustur()
        st.session_state.motivasyon = motivasyon_sec(deneme_sonuclari)
        st.session_state.is_saved = False # Yeni program henüz kaydedilmedi

# PROGRAM EKRANDA VARSA
if not st.session_state.df_program.empty:
    
    # -- KAYDETME VE VAZGEÇME ALANI (Sidebarda veya Üstte) --
    # Sidebara butonları ekleyelim
    st.sidebar.markdown("---")
    st.sidebar.subheader("📝 İşlem Seçimi")
    
    c_save, c_cancel = st.sidebar.columns(2)
    
    # KAYDET BUTONU
    if c_save.button("💾 KAYDET", type="primary"):
        guncel_tarih = datetime.now().strftime("%d.%m.%Y %H:%M")
        kayitli_veriler[ogrenci_adi] = {
            "tarih": guncel_tarih,
            "gunluk_hedef": gunluk_hedef,
            "dersler": deneme_sonuclari
        }
        verileri_kaydet(kayitli_veriler)
        st.session_state.is_saved = True
        st.toast(f"{ogrenci_adi} başarıyla kaydedildi!", icon="✅")
    
    # VAZGEÇ BUTONU
    if c_cancel.button("❌ Temizle"):
        sifirla_her_seyi()
        
    # KAYDEDİLMEDİ UYARISI
    if not st.session_state.is_saved:
        st.markdown("<div class='unsaved-warning'>⚠️ Bu program şu an <strong>ÖNİZLEME MODUNDA</strong>. Veritabanına kaydetmek için soldaki <strong>'KAYDET'</strong> butonuna basın.</div>", unsafe_allow_html=True)
    
    st.markdown(f"<div class='motivasyon-banner'>💡 {st.session_state.motivasyon}</div>", unsafe_allow_html=True)
    
    # 1. LİSE TAHMİNİ
    st.markdown("### 🏫 Balıkesir Geneli Lise Tahmini")
    tahmini_puan = puan_hesapla(deneme_sonuclari)
    
    with st.container(border=True):
        c1, c2 = st.columns([1, 3])
        c1.metric("TAHMİNİ PUAN", f"{tahmini_puan:.2f}", "Yaklaşık Hesap")
        
        with c2:
            st.write("**Puanının Yetebileceği Liseler:**")
            girebilir = False
            for lise in balikesir_liseleri:
                if tahmini_puan >= lise["puan"]:
                    st.success(f"✅ **{lise['ad']}** (Taban: {lise['puan']})")
                    girebilir = True
                elif tahmini_puan >= lise["puan"] - 15:
                    st.warning(f"⚠️ **{lise['ad']}** (Taban: {lise['puan']}) - Az kaldı!")
            if not girebilir:
                st.info("Henüz listedeki liseler için biraz daha çalışmalısın. Pes etmek yok! 💪")

    # 2. NET ANALİZ
    st.markdown("### 📊 Net Durumu")
    with st.container(border=True):
        cols = st.columns(len(dersler_config))
        for i, (d, v) in enumerate(deneme_sonuclari.items()):
            cols[i].metric(d, f"{v['net']:.2f}", f"{v['net']-v['hedef']:.2f} Hedef")

    # 3. PROGRAM EDİTÖRÜ
    st.markdown("### 📅 Haftalık Plan")
    gunler = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]
    cfg = {"Saat": st.column_config.TextColumn("Zaman", disabled=True)}
    for g in gunler:
        cfg[g] = st.column_config.SelectboxColumn(g, options=list(dersler_config.keys())+["Paragraf / Kitap","Mola","Boş"])
        cfg[f"{g}_Soru"] = st.column_config.NumberColumn("Soru", width="small")

    edited_df = st.data_editor(
        st.session_state.df_program,
        column_config=cfg,
        use_container_width=True,
        hide_index=True,
        key="editor_main"
    )
    
    # 4. HEDEF KONTROLÜ
    st.markdown("### 🔢 Hedef Kontrolü")
    with st.container(border=True):
        cols = st.columns(8)
        total_w = 0
        for i, g in enumerate(gunler):
            if f"{g}_Soru" in edited_df.columns:
                s = edited_df[f"{g}_Soru"].sum()
                total_w += s
                delta_txt = "✅ Tamam" if s >= gunluk_hedef else f"⚠️ {gunluk_hedef-s} Eksik"
                cols[i].metric(g, s, delta_txt)
            else:
                cols[i].metric(g, 0)
        cols[7].metric("TOPLAM", total_w, f"Hedef: {gunluk_hedef*7}")

    # 5. UYARILAR & ÖNERİLER
    st.markdown("---")
    t1, t2 = st.tabs(["🚨 Eksik Analizi & Kaynaklar", "🧠 Teknikler"])
    
    with t1:
        cnt = 0
        for d, v in deneme_sonuclari.items():
            if v['net'] < v['hedef']:
                cnt += 1
                msg = "KONU EKSİĞİ! Video izle." if v['net'] < v['limit']*0.5 else "PRATİK EKSİĞİ! Soru çöz."
                renk = "alert-red" if "KONU" in msg else "alert-orange"
                st.markdown(f"""<div class='alert-box {renk}'><strong>{d}:</strong> {msg}</div>""", unsafe_allow_html=True)
                with st.expander(f"📺 {d} Kaynakları"):
                    if d in youtube_kanallari:
                        for k in youtube_kanallari[d]: st.write(f"• {k}")
        if cnt == 0: st.success("Tüm hedeflere ulaştın!")

    with t2:
        c1, c2 = st.columns(2)
        for i, t in enumerate(teknikler):
            with (c1 if i%2==0 else c2):
                st.info(f"**{t['baslik']}**: {t['detay']}")

    # İNDİRME
    excel_data = excel_indir(edited_df, deneme_sonuclari, teknikler, st.session_state.motivasyon)
    
    st.download_button(
        label="📥 Excel Raporunu İndir",
        data=excel_data,
        file_name=f"{ogrenci_adi}_Program_{datetime.now().strftime('%Y%m%d')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        type="primary"
    )