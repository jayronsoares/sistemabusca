import streamlit as st
import json
import os
from datetime import datetime
from pathlib import Path
from PIL import Image

# Configuração
st.set_page_config(
    page_title="ESPRO - Sistema de Busca",
    page_icon="📁",
    layout="wide"
)

# Diretórios
UPLOAD_DIR = Path("uploads")
DATABASE_FILE = Path("database/metadata.json")
UPLOAD_DIR.mkdir(exist_ok=True)
DATABASE_FILE.parent.mkdir(exist_ok=True)

if not DATABASE_FILE.exists():
    with open(DATABASE_FILE, 'w', encoding='utf-8') as f:
        json.dump([], f)

def load_database():
    try:
        with open(DATABASE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

def save_database(data):
    with open(DATABASE_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def format_bytes(bytes_size):
    if bytes_size < 1024:
        return f"{bytes_size} B"
    elif bytes_size < 1024**2:
        return f"{bytes_size/1024:.1f} KB"
    else:
        return f"{bytes_size/(1024**2):.1f} MB"

def get_total_storage():
    total = 0
    for file in UPLOAD_DIR.glob("*"):
        if file.is_file():
            total += os.path.getsize(file)
    return total

def create_thumbnail(image_path, max_size=(300, 300)):
    img = Image.open(image_path)
    img.thumbnail(max_size, Image.Resampling.LANCZOS)
    return img

def search_media(query, media_type=None, tag_filter=None):
    db = load_database()
    results = []
    query_lower = query.lower() if query else ""
    
    for item in db:
        if media_type and media_type != "Todos" and item['tipo'] != media_type:
            continue
        if tag_filter and tag_filter != "Todas" and tag_filter not in item['tags']:
            continue
        if query:
            titulo_match = query_lower in item['titulo'].lower()
            desc_match = query_lower in item.get('descricao', '').lower()
            tags_match = any(query_lower in tag.lower() for tag in item['tags'])
            if not (titulo_match or desc_match or tags_match):
                continue
        results.append(item)
    return results

# CSS ESPRO
st.markdown("""
<style>
    :root {
        --espro-azul: #003C7E;
        --espro-azul-claro: #0056B3;
    }
    .espro-header {
        background: linear-gradient(135deg, var(--espro-azul) 0%, var(--espro-azul-claro) 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0,60,126,0.1);
    }
    .espro-titulo {
        color: white;
        font-size: 2.2rem;
        font-weight: bold;
        margin: 0;
        text-align: center;
    }
    .espro-subtitulo {
        color: #E0E0E0;
        font-size: 1.1rem;
        text-align: center;
        margin-top: 0.5rem;
    }
    .stat-card {
        background: white;
        padding: 1.5rem;
        border-radius: 8px;
        text-align: center;
        border-left: 4px solid var(--espro-azul);
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .stat-number {
        font-size: 2.5rem;
        font-weight: bold;
        color: var(--espro-azul);
    }
    .stat-label {
        font-size: 0.9rem;
        color: #666;
        margin-top: 0.5rem;
    }
    .tag-badge {
        background-color: var(--espro-azul);
        color: white;
        padding: 0.3rem 0.7rem;
        border-radius: 15px;
        margin: 0.2rem;
        display: inline-block;
        font-size: 0.85rem;
    }
    .media-card {
        border: 1px solid #E0E0E0;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1rem;
        background: white;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .espro-footer {
        text-align: center;
        color: #666;
        padding: 2rem;
        margin-top: 3rem;
        border-top: 2px solid var(--espro-azul);
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="espro-header">
    <h1 class="espro-titulo">📁 ESPRO - Sistema de Busca Inteligente</h1>
    <p class="espro-subtitulo">Gestão de Conteúdo Visual | Educação, Transformação e Inclusão</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### 📋 Menu")
    menu = st.radio("", ["🏠 Dashboard", "➕ Adicionar", "🔍 Buscar"], label_visibility="collapsed")
    
    st.markdown("---")
    db = load_database()
    total_items = len(db)
    total_images = len([x for x in db if x['tipo'] == 'Imagem'])
    total_videos = len([x for x in db if x['tipo'] == 'Vídeo'])
    storage_used = get_total_storage()
    
    st.markdown("### 📊 Estatísticas")
    st.metric("Total", total_items)
    st.metric("Imagens", total_images)
    st.metric("Vídeos", total_videos)
    st.metric("Armazenamento", format_bytes(storage_used))
    st.progress(min(storage_used / (200 * 1024 * 1024), 1.0))
    st.caption("Limite: 200 MB")
    
    st.markdown("---")
    st.markdown("### 🌐 ESPRO")
    st.caption("46 anos transformando vidas através da educação profissional")
    st.link_button("🔗 espro.org.br", "https://www.espro.org.br")

# DASHBOARD
if menu == "🏠 Dashboard":
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f'<div class="stat-card"><div class="stat-number">{total_items}</div><div class="stat-label">Total</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="stat-card"><div class="stat-number">{total_images}</div><div class="stat-label">Imagens</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="stat-card"><div class="stat-number">{total_videos}</div><div class="stat-label">Vídeos</div></div>', unsafe_allow_html=True)
    with col4:
        st.markdown(f'<div class="stat-card"><div class="stat-number">{format_bytes(storage_used)}</div><div class="stat-label">Armazenamento</div></div>', unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 📁 Recentes")
    
    if db:
        db_sorted = sorted(db, key=lambda x: x['data_upload'], reverse=True)
        for item in db_sorted[:5]:
            col1, col2 = st.columns([1, 4])
            with col1:
                if item['tipo'] == 'Imagem':
                    try:
                        st.image(create_thumbnail(UPLOAD_DIR / item['arquivo'], (150, 150)), use_container_width=True)
                    except:
                        st.write("🖼️")
                else:
                    st.markdown("<div style='text-align:center;font-size:4rem;'>🎬</div>", unsafe_allow_html=True)
            with col2:
                st.markdown(f"**{item['titulo']}**")
                st.caption(f"📅 {item['data_upload']} | 📦 {item['tamanho']}")
                if item['tags']:
                    st.markdown("".join([f'<span class="tag-badge">{tag}</span>' for tag in item['tags']]), unsafe_allow_html=True)
            st.markdown("---")
    else:
        st.info("Nenhum conteúdo adicionado")

# ADICIONAR
elif menu == "➕ Adicionar":
    storage_used = get_total_storage()
    storage_limit = 200 * 1024 * 1024
    
    if storage_used >= storage_limit:
        st.error("Limite de 200 MB atingido")
    else:
        st.info(f"Disponível: {format_bytes(storage_limit - storage_used)}")
        uploaded_file = st.file_uploader("Arraste o arquivo", type=['png', 'jpg', 'jpeg', 'gif', 'mp4', 'avi', 'mov'])
        
        if uploaded_file:
            file_size = len(uploaded_file.getvalue())
            if storage_used + file_size > storage_limit:
                st.error("Arquivo muito grande")
            else:
                col1, col2 = st.columns([1, 2])
                file_type = "Imagem" if uploaded_file.type.startswith('image') else "Vídeo"
                
                with col1:
                    if file_type == "Imagem":
                        st.image(uploaded_file, use_container_width=True)
                    else:
                        st.video(uploaded_file)
                
                with col2:
                    titulo = st.text_input("Título *", placeholder="Ex: Logo ESPRO")
                    tags_input = st.text_input("Tags *", placeholder="Ex: logo, 2024")
                    descricao = st.text_area("Descrição", placeholder="Opcional...")
                    st.caption(f"{format_bytes(file_size)} | {file_type}")
                
                if st.button("💾 Salvar", type="primary", use_container_width=True):
                    if not titulo or not tags_input:
                        st.error("Título e tags são obrigatórios")
                    else:
                        tags = [t.strip() for t in tags_input.split(',') if t.strip()]
                        if tags:
                            file_path = UPLOAD_DIR / uploaded_file.name
                            with open(file_path, 'wb') as f:
                                f.write(uploaded_file.getbuffer())
                            
                            db = load_database()
                            db.append({
                                "id": len(db) + 1,
                                "titulo": titulo.strip(),
                                "arquivo": uploaded_file.name,
                                "tipo": file_type,
                                "tags": tags,
                                "descricao": descricao.strip(),
                                "tamanho": format_bytes(os.path.getsize(file_path)),
                                "data_upload": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            })
                            save_database(db)
                            st.success("Salvo!")
                            st.balloons()
                            st.rerun()

# BUSCAR
elif menu == "🔍 Buscar":
    db = load_database()
    
    if not db:
        st.info("Nenhum conteúdo")
    else:
        col1, col2 = st.columns([3, 1])
        with col1:
            search_query = st.text_input("🔎", placeholder="Buscar...", label_visibility="collapsed")
        with col2:
            st.button("🔍 Buscar", type="primary", use_container_width=True)
        
        col_f, col_r = st.columns([1, 3])
        
        with col_f:
            st.markdown("### 🎛️ Filtros")
            tipo_filter = st.selectbox("Tipo", ["Todos", "Imagem", "Vídeo"])
            all_tags = sorted(set(tag for item in db for tag in item['tags']))
            tag_filter = st.selectbox("Tag", ["Todas"] + all_tags)
        
        with col_r:
            results = search_media(search_query, tipo_filter, tag_filter)
            st.markdown(f"### 📊 {len(results)} resultado(s)")
            
            if results:
                cols = st.columns(2)
                for idx, item in enumerate(results):
                    with cols[idx % 2]:
                        st.markdown('<div class="media-card">', unsafe_allow_html=True)
                        
                        if item['tipo'] == 'Imagem':
                            try:
                                st.image(create_thumbnail(UPLOAD_DIR / item['arquivo'], (400, 400)), use_container_width=True)
                            except:
                                st.error("Erro ao carregar")
                        else:
                            video_path = UPLOAD_DIR / item['arquivo']
                            if video_path.exists():
                                st.video(str(video_path))
                        
                        st.markdown(f"**{item['titulo']}**")
                        st.caption(f"📅 {item['data_upload']} | 📦 {item['tamanho']}")
                        
                        if item['tags']:
                            st.markdown("".join([f'<span class="tag-badge">{tag}</span>' for tag in item['tags']]), unsafe_allow_html=True)
                        
                        if item.get('descricao'):
                            with st.expander("📄 Descrição"):
                                st.write(item['descricao'])
                        
                        file_path = UPLOAD_DIR / item['arquivo']
                        if file_path.exists():
                            with open(file_path, 'rb') as f:
                                st.download_button("⬇️ Baixar", f, item['arquivo'], use_container_width=True)
                        
                        st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.warning("Nenhum resultado")

# Footer
st.markdown("""
<div class="espro-footer">
    <p><strong>ESPRO - Ensino Social Profissionalizante</strong></p>
    <p>Educação, Transformação e Inclusão | 46 anos transformando vidas</p>
    <p><a href="https://www.espro.org.br" target="_blank">www.espro.org.br</a></p>
</div>
""", unsafe_allow_html=True)
