import streamlit as st
import json
import os
from datetime import datetime
from pathlib import Path
from PIL import Image

# Configuração da página
st.set_page_config(
    page_title="Sistema de Busca Inteligente",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Diretórios
UPLOAD_DIR = Path("uploads")
DATABASE_FILE = Path("database/metadata.json")

# Criar diretórios se não existirem
UPLOAD_DIR.mkdir(exist_ok=True)
DATABASE_FILE.parent.mkdir(exist_ok=True)

# Inicializar banco de dados
if not DATABASE_FILE.exists():
    with open(DATABASE_FILE, 'w', encoding='utf-8') as f:
        json.dump([], f)

# Funções auxiliares
def load_database():
    """Carrega o banco de dados de metadados"""
    try:
        with open(DATABASE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

def save_database(data):
    """Salva o banco de dados de metadados"""
    with open(DATABASE_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def format_bytes(bytes_size):
    """Formata bytes para formato legível"""
    if bytes_size < 1024:
        return f"{bytes_size} B"
    elif bytes_size < 1024**2:
        return f"{bytes_size/1024:.1f} KB"
    else:
        return f"{bytes_size/(1024**2):.1f} MB"

def get_total_storage():
    """Calcula o espaço total usado"""
    total = 0
    for file in UPLOAD_DIR.glob("*"):
        if file.is_file():
            total += os.path.getsize(file)
    return total

def create_thumbnail(image_path, max_size=(300, 300)):
    """Cria thumbnail de imagem"""
    img = Image.open(image_path)
    img.thumbnail(max_size, Image.Resampling.LANCZOS)
    return img

def search_media(query, media_type=None, tag_filter=None):
    """Busca mídia por título, descrição ou tags"""
    db = load_database()
    results = []
    
    query_lower = query.lower() if query else ""
    
    for item in db:
        # Filtro por tipo
        if media_type and media_type != "Todos" and item['tipo'] != media_type:
            continue
        
        # Filtro por tag
        if tag_filter and tag_filter != "Todas":
            if tag_filter not in item['tags']:
                continue
        
        # Busca textual
        if query:
            titulo_match = query_lower in item['titulo'].lower()
            desc_match = query_lower in item.get('descricao', '').lower()
            tags_match = any(query_lower in tag.lower() for tag in item['tags'])
            
            if titulo_match or desc_match or tags_match:
                results.append(item)
        else:
            results.append(item)
    
    return results

# CSS customizado
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .stat-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
    }
    .stat-number {
        font-size: 2rem;
        font-weight: bold;
        color: #1f77b4;
    }
    .stat-label {
        font-size: 0.9rem;
        color: #666;
    }
    .tag-badge {
        background-color: #e1f5ff;
        color: #01579b;
        padding: 0.2rem 0.5rem;
        border-radius: 0.3rem;
        margin: 0.2rem;
        display: inline-block;
        font-size: 0.85rem;
    }
    .media-card {
        border: 1px solid #ddd;
        border-radius: 0.5rem;
        padding: 1rem;
        margin-bottom: 1rem;
        background-color: white;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar - Menu principal
with st.sidebar:
    st.markdown("### 📂 Menu Principal")
    menu = st.radio(
        "Escolha uma opção:",
        ["🏠 Dashboard", "➕ Adicionar Conteúdo", "🔍 Buscar e Explorar"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    # Estatísticas na sidebar
    db = load_database()
    total_items = len(db)
    total_images = len([x for x in db if x['tipo'] == 'Imagem'])
    total_videos = len([x for x in db if x['tipo'] == 'Vídeo'])
    storage_used = get_total_storage()
    
    st.markdown("### 📊 Estatísticas")
    st.metric("Total de Itens", total_items)
    st.metric("Imagens", total_images)
    st.metric("Vídeos", total_videos)
    st.metric("Armazenamento", format_bytes(storage_used))
    st.progress(min(storage_used / (200 * 1024 * 1024), 1.0))
    st.caption(f"Limite: 200 MB")

# DASHBOARD
if menu == "🏠 Dashboard":
    st.markdown('<p class="main-header">🔍 Sistema de Busca Inteligente</p>', unsafe_allow_html=True)
    st.markdown("### Bem-vindo ao seu gerenciador de conteúdo visual")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-number">{total_items}</div>
            <div class="stat-label">Total de Itens</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-number">{total_images}</div>
            <div class="stat-label">Imagens</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-number">{total_videos}</div>
            <div class="stat-label">Vídeos</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-number">{format_bytes(storage_used)}</div>
            <div class="stat-label">Armazenamento Usado</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Itens recentes
    st.markdown("### 📁 Conteúdo Recente")
    
    if db:
        # Ordenar por data (mais recente primeiro)
        db_sorted = sorted(db, key=lambda x: x['data_upload'], reverse=True)
        
        for item in db_sorted[:5]:  # Mostrar apenas os 5 mais recentes
            with st.container():
                col1, col2 = st.columns([1, 4])
                
                with col1:
                    if item['tipo'] == 'Imagem':
                        try:
                            img_path = UPLOAD_DIR / item['arquivo']
                            img = create_thumbnail(img_path, (150, 150))
                            st.image(img, use_container_width=True)
                        except:
                            st.write("🖼️")
                    else:
                        st.markdown("<div style='text-align: center; font-size: 4rem;'>🎬</div>", unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"**{item['titulo']}**")
                    st.caption(f"📅 {item['data_upload']} | 📦 {item['tamanho']}")
                    
                    if item['tags']:
                        tags_html = "".join([f'<span class="tag-badge">{tag}</span>' for tag in item['tags']])
                        st.markdown(tags_html, unsafe_allow_html=True)
                    
                    if item.get('descricao'):
                        st.caption(item['descricao'][:100] + "..." if len(item['descricao']) > 100 else item['descricao'])
                
                st.markdown("---")
    else:
        st.info("👋 Nenhum conteúdo adicionado ainda. Comece fazendo upload de suas imagens e vídeos!")

# ADICIONAR CONTEÚDO
elif menu == "➕ Adicionar Conteúdo":
    st.markdown('<p class="main-header">➕ Adicionar Novo Conteúdo</p>', unsafe_allow_html=True)
    
    # Verificar limite de armazenamento
    storage_used = get_total_storage()
    storage_limit = 200 * 1024 * 1024  # 200 MB
    
    if storage_used >= storage_limit:
        st.error("⚠️ Limite de armazenamento atingido (200 MB). Exclua alguns arquivos antes de adicionar novos.")
    else:
        st.info(f"💾 Espaço disponível: {format_bytes(storage_limit - storage_used)} de 200 MB")
        
        uploaded_file = st.file_uploader(
            "Arraste e solte seu arquivo aqui ou clique para selecionar",
            type=['png', 'jpg', 'jpeg', 'gif', 'mp4', 'avi', 'mov'],
            help="Formatos suportados: PNG, JPG, JPEG, GIF, MP4, AVI, MOV"
        )
        
        if uploaded_file:
            # Verificar tamanho do arquivo
            file_size = len(uploaded_file.getvalue())
            
            if storage_used + file_size > storage_limit:
                st.error(f"⚠️ Arquivo muito grande! Você tem apenas {format_bytes(storage_limit - storage_used)} disponível.")
            else:
                # Preview do arquivo
                st.markdown("### 👁️ Preview")
                col1, col2 = st.columns([1, 2])
                
                file_type = "Imagem" if uploaded_file.type.startswith('image') else "Vídeo"
                
                with col1:
                    if file_type == "Imagem":
                        st.image(uploaded_file, use_container_width=True)
                    else:
                        st.video(uploaded_file)
                
                with col2:
                    st.markdown("### 📝 Informações do Arquivo")
                    
                    # Título (obrigatório)
                    titulo = st.text_input(
                        "Título *",
                        placeholder="Ex: Logo da empresa versão 2024",
                        help="Campo obrigatório"
                    )
                    
                    # Tags (múltiplas)
                    tags_input = st.text_input(
                        "Tags (separadas por vírgula) *",
                        placeholder="Ex: logo, marca, 2024, oficial",
                        help="Adicione tags para facilitar a busca. Campo obrigatório."
                    )
                    
                    # Descrição (opcional)
                    descricao = st.text_area(
                        "Descrição (opcional)",
                        placeholder="Adicione detalhes ou contexto sobre este arquivo...",
                        height=100
                    )
                    
                    st.caption(f"📦 Tamanho: {format_bytes(file_size)}")
                    st.caption(f"📂 Tipo: {file_type}")
                
                # Botão de salvar
                if st.button("💾 Salvar Conteúdo", type="primary", use_container_width=True):
                    # Validações
                    if not titulo or not titulo.strip():
                        st.error("❌ O campo 'Título' é obrigatório!")
                    elif not tags_input or not tags_input.strip():
                        st.error("❌ Adicione pelo menos uma tag!")
                    else:
                        # Processar tags
                        tags = [tag.strip() for tag in tags_input.split(',') if tag.strip()]
                        
                        if not tags:
                            st.error("❌ Adicione pelo menos uma tag válida!")
                        else:
                            # Salvar arquivo
                            file_path = UPLOAD_DIR / uploaded_file.name
                            with open(file_path, 'wb') as f:
                                f.write(uploaded_file.getbuffer())
                            
                            # Adicionar ao banco de dados
                            db = load_database()
                            
                            new_item = {
                                "id": len(db) + 1,
                                "titulo": titulo.strip(),
                                "arquivo": uploaded_file.name,
                                "tipo": file_type,
                                "tags": tags,
                                "descricao": descricao.strip() if descricao else "",
                                "tamanho": format_bytes(os.path.getsize(file_path)),
                                "data_upload": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            }
                            
                            db.append(new_item)
                            save_database(db)
                            
                            st.success(f"✅ {file_type} '{titulo}' adicionado com sucesso!")
                            st.balloons()
                            st.rerun()

# BUSCAR E EXPLORAR
elif menu == "🔍 Buscar e Explorar":
    st.markdown('<p class="main-header">🔍 Buscar e Explorar Conteúdo</p>', unsafe_allow_html=True)
    
    db = load_database()
    
    if not db:
        st.info("📂 Nenhum conteúdo disponível. Adicione arquivos primeiro!")
    else:
        # Barra de busca
        col1, col2 = st.columns([3, 1])
        
        with col1:
            search_query = st.text_input(
                "🔎 Digite para buscar",
                placeholder="Busque por título, descrição ou tags...",
                label_visibility="collapsed"
            )
        
        with col2:
            if st.button("🔍 Buscar", type="primary", use_container_width=True):
                pass  # A busca é feita automaticamente
        
        # Filtros laterais
        col_filters, col_results = st.columns([1, 3])
        
        with col_filters:
            st.markdown("### 🎛️ Filtros")
            
            # Filtro por tipo
            tipo_filter = st.selectbox(
                "Tipo de Arquivo",
                ["Todos", "Imagem", "Vídeo"]
            )
            
            # Filtro por tag
            all_tags = set()
            for item in db:
                all_tags.update(item['tags'])
            all_tags = sorted(list(all_tags))
            
            tag_filter = st.selectbox(
                "Filtrar por Tag",
                ["Todas"] + all_tags
            )
            
            # Botão limpar filtros
            if st.button("🔄 Limpar Filtros"):
                st.rerun()
        
        with col_results:
            # Realizar busca
            results = search_media(
                search_query,
                media_type=tipo_filter,
                tag_filter=tag_filter
            )
            
            st.markdown(f"### 📊 Resultados: {len(results)} item(ns) encontrado(s)")
            
            if results:
                # Exibir em grid
                cols = st.columns(2)
                
                for idx, item in enumerate(results):
                    with cols[idx % 2]:
                        with st.container():
                            st.markdown('<div class="media-card">', unsafe_allow_html=True)
                            
                            # Thumbnail/Preview
                            if item['tipo'] == 'Imagem':
                                try:
                                    img_path = UPLOAD_DIR / item['arquivo']
                                    img = create_thumbnail(img_path, (400, 400))
                                    st.image(img, use_container_width=True)
                                except:
                                    st.error("Erro ao carregar imagem")
                            else:
                                # Preview de vídeo
                                video_path = UPLOAD_DIR / item['arquivo']
                                if video_path.exists():
                                    st.video(str(video_path))
                                else:
                                    st.error("Erro ao carregar vídeo")
                            
                            # Informações
                            st.markdown(f"**{item['titulo']}**")
                            st.caption(f"📅 {item['data_upload']} | 📦 {item['tamanho']}")
                            
                            # Tags
                            if item['tags']:
                                tags_html = "".join([f'<span class="tag-badge">{tag}</span>' for tag in item['tags']])
                                st.markdown(tags_html, unsafe_allow_html=True)
                            
                            # Descrição
                            if item.get('descricao'):
                                with st.expander("📄 Ver descrição"):
                                    st.write(item['descricao'])
                            
                            # Botão de download
                            file_path = UPLOAD_DIR / item['arquivo']
                            if file_path.exists():
                                with open(file_path, 'rb') as f:
                                    st.download_button(
                                        label="⬇️ Baixar arquivo",
                                        data=f,
                                        file_name=item['arquivo'],
                                        mime=f"{'image' if item['tipo'] == 'Imagem' else 'video'}/*",
                                        use_container_width=True
                                    )
                            
                            st.markdown('</div>', unsafe_allow_html=True)
                            st.markdown("<br>", unsafe_allow_html=True)
            else:
                st.warning("🔍 Nenhum resultado encontrado. Tente ajustar os filtros ou termo de busca.")

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666; padding: 1rem;'>"
    "💡 Sistema de Busca Inteligente | Desenvolvido por Jayron Soares"
    "</div>",
    unsafe_allow_html=True
)
