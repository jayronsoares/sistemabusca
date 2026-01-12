# 🔍 Sistema de Busca Inteligente

Protótipo para gerenciamento e busca de imagens e vídeos.

## Funcionalidades

- **Dashboard**: Estatísticas em tempo real
- **Upload**: Drag & drop com título, tags e descrição
- **Busca**: Por título, tags ou descrição com filtros

## Executar Localmente

```bash
pip install -r requirements.txt
streamlit run app.py
```

Acesse: `http://localhost:8501`

## Deploy no Streamlit Cloud

1. Suba o código para GitHub
2. Acesse https://share.streamlit.io
3. Connect repository → Deploy

## Estrutura

```
app.py              # Aplicação principal
requirements.txt    # Dependências
database/           # JSON metadata (auto-criado)
uploads/            # Arquivos (auto-criado)
```

## Limites do Protótipo

- 200 MB armazenamento
- Sem autenticação
- Arquivos temporários (reinicia no Streamlit Cloud)

## Desenvolvedor

Jayron Soares - Database Administrator & Data Engineer
