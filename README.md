# Sistema de Seguros de Vida (SaaS)

Sistema multi-tenant de gestão de seguros de vida, feito em Python + Streamlit.

## Como rodar localmente

1. Crie um ambiente virtual (recomendado):
   ```
   python -m venv venv
   venv\Scripts\activate      # Windows
   source venv/bin/activate   # Mac/Linux
   ```

2. Instale as dependências:
   ```
   pip install -r requirements.txt
   ```

3. Rode o sistema:
   ```
   streamlit run app.py
   ```

4. O navegador vai abrir automaticamente em http://localhost:8501

## Como rodar os testes

```
python -m pytest tests/ -v
```

## Status do desenvolvimento

- [x] Etapa 1 — Estrutura do projeto
- [ ] Etapa 2 — Tela de login funcional
- [ ] Etapa 3 — Multi-tenant
- [ ] Etapa 4 — Cadastro de clientes
- [ ] Etapa 5 — Sistema de pagamentos
- [ ] Etapa 6 — Relatórios
- [ ] Etapa 7 — Deploy online
- [ ] Etapa 8 — Modelo de negócio
