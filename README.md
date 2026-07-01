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

## Multi-tenant (empresas)

O sistema atende várias empresas (corretoras) com o mesmo app, cada uma
com seus próprios usuários. No login, além de usuário e senha, é
preciso informar o "slug" da empresa (ex: `demo`).

Para cadastrar uma nova empresa e seu usuário administrador:

```
venv\Scripts\python.exe scripts\criar_tenant.py
```

A empresa de demonstração criada automaticamente na primeira execução é:
- Empresa: `demo`
- Usuário: `admin`
- Senha: `admin123`

## Status do desenvolvimento

- [x] Etapa 1 — Estrutura do projeto
- [ ] Etapa 2 — Tela de login funcional
- [x] Etapa 3 — Multi-tenant
- [ ] Etapa 4 — Cadastro de clientes
- [ ] Etapa 5 — Sistema de pagamentos
- [ ] Etapa 6 — Relatórios
- [ ] Etapa 7 — Deploy online
- [ ] Etapa 8 — Modelo de negócio
