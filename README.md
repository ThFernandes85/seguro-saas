# Sistema de Seguros de Vida (SaaS)

![Logo](assets/logo.png)

Sistema multi-tenant de gestão de seguros de vida, feito em Python + Streamlit.

## Identidade visual

Escudo (proteção) com um coração (cuidado com a vida das pessoas) no centro,
em tons de azul-marinho e dourado para transmitir seriedade e confiança.
Os arquivos ficam em `assets/logo.png` (logo) e `assets/favicon.png`
(ícone da aba do navegador), e as cores do app estão em `.streamlit/config.toml`.

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

## Como rodar os testes

```
python -m pytest tests/ -v
```

## Status do desenvolvimento

- [x] Etapa 1 — Estrutura do projeto
- [ ] Etapa 2 — Tela de login funcional
- [x] Etapa 3 — Multi-tenant
- [x] Etapa 4 — Cadastro de clientes
- [ ] Etapa 5 — Sistema de pagamentos
- [ ] Etapa 6 — Relatórios
- [ ] Etapa 7 — Deploy online
- [ ] Etapa 8 — Modelo de negócio
