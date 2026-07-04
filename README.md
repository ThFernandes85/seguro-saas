# Sistema de Seguros de Vida (SaaS)

![Logo](assets/logo.png)

Sistema multi-tenant de gestão de seguros de vida, feito em Python + Streamlit.

## Identidade visual

Escudo (proteção) com um coração (cuidado com a vida das pessoas) no centro,
em tons de azul-marinho e dourado para transmitir seriedade e confiança.
Os arquivos ficam em `assets/logo.png` (logo) e `assets/favicon.png`
(ícone da aba do navegador), e as cores do app estão em `.streamlit/config.toml`.

## Página inicial (dashboard)

Depois do login, a página inicial mostra um painel com os principais
números do negócio (clientes, apólices ativas, total de apólices e
receita mensal recorrente) e cartões de acesso rápido para as
outras páginas do sistema. Todas as páginas usam layout largo (wide)
para uma aparência mais consistente de painel corporativo.

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

## Login e segurança

Além de empresa + usuário + senha, o login tem proteção contra força
bruta: depois de 5 tentativas erradas seguidas, a conta fica bloqueada
por 15 minutos (mesmo com a senha certa). Usuários logados podem
trocar a própria senha na página "Minha Conta".

## Multi-tenant (empresas)

O sistema atende várias empresas (corretoras) com o mesmo app, cada uma
com seus próprios usuários. No login, além de usuário e senha, é
preciso informar o "slug" da empresa (ex: `demo`).

A empresa de demonstração criada automaticamente na primeira execução é:
- Empresa: `demo`
- Usuário: `admin`
- Senha: `admin123`

### Cadastrando novas corretoras

Existem duas formas de cadastrar uma nova empresa e seu usuário
administrador:

1. **Painel de administração no site** (recomendado quando o app está
   publicado, já que o Streamlit Community Cloud não dá acesso a
   terminal): acesse a página "Admin Corretoras" no menu lateral e
   entre com a senha configurada em `ADMIN_PANEL_SENHA` (veja
   `.streamlit/secrets.toml.example`). Essa página não tem nenhuma
   relação com o login das corretoras -- é de uso exclusivo do dono do
   sistema.
2. **Script no terminal** (só cadastra na base de dados local da sua
   máquina, útil para testes):
   ```
   venv\Scripts\python.exe scripts\criar_tenant.py
   ```

**Importante:** enquanto o banco de dados for o SQLite local (veja
seção "Deploy online" abaixo), qualquer corretora cadastrada por
qualquer um dos dois métodos é perdida sempre que o app reinicia no
Streamlit Community Cloud. Migre para um banco externo antes de
cadastrar clientes reais.

## Pagamentos (Mercado Pago)

O prêmio do seguro é cobrado como uma assinatura mensal (cobrança
recorrente) via Mercado Pago, na página "Apolices Pagamentos".

Para habilitar cobranças de verdade:

1. Crie uma conta de desenvolvedor em https://www.mercadopago.com.br/developers
   e pegue o **Access Token de teste (sandbox)** no seu painel.
2. Copie `.streamlit/secrets.toml.example` para `.streamlit/secrets.toml`
   (esse arquivo não é versionado no Git) e cole seu token:
   ```
   MERCADOPAGO_ACCESS_TOKEN = "TEST-..."
   ```
3. Reinicie o `streamlit run app.py`.

Sem o token configurado, a tela funciona normalmente mas mostra um
aviso e não cria cobranças de verdade. A lógica de integração
(`pagamentos/mercado_pago.py`) tem testes automatizados que simulam
as respostas da API do Mercado Pago, então não é necessário ter o
token configurado para rodar a suíte de testes.

Como ainda não temos um domínio público, o app não recebe
notificações automáticas (webhook) do Mercado Pago quando o cliente
paga — o status de cada apólice é atualizado manualmente, clicando em
"Atualizar status no Mercado Pago".

## Relatórios

A página "Relatorios" mostra um panorama do negócio da empresa
logada: total de clientes, total de apólices, receita mensal
recorrente (soma do valor das apólices com assinatura ativa), um
gráfico de apólices por status e a lista de clientes que ainda não
têm uma apólice ativa (oportunidade de venda).

## Modelo de negócio (planos)

O SaaS tem 3 planos de assinatura (definidos em `planos.py`), cobrados
da própria corretora (não dos clientes finais dela) via Mercado Pago,
na página "Meu Plano":

| Plano    | Preço mensal | Limite de clientes | Limite de usuários |
|----------|--------------|---------------------|----------------------|
| Starter  | R$ 49,90     | 20                  | 1                    |
| Pro      | R$ 149,90    | 100                 | 5                    |
| Business | R$ 399,90    | Ilimitado           | Ilimitado            |

Os limites são aplicados de verdade: ao atingir o limite de clientes
ou usuários do plano, o cadastro é bloqueado com uma mensagem pedindo
upgrade. Downgrade para um plano menor que o uso atual também é
bloqueado, até a empresa reduzir o uso. Novas empresas começam no
plano Starter (`scripts/criar_tenant.py` permite escolher outro).

## Como rodar os testes

```
python -m pytest tests/ -v
```

## Deploy online (Streamlit Community Cloud)

O jeito mais rápido e gratuito de colocar o app no ar é o
[Streamlit Community Cloud](https://share.streamlit.io), que já se
conecta direto com o GitHub. Esse login é seu (usa sua conta do
GitHub), então os passos abaixo você faz manualmente:

1. Acesse https://share.streamlit.io e entre com sua conta do GitHub
   (a mesma que tem o repositório `seguro-saas`).
2. Clique em "New app" (ou "Create app").
3. Selecione:
   - Repository: `ThFernandes85/seguro-saas`
   - Branch: `main`
   - Main file path: `app.py`
4. Antes de clicar em "Deploy", abra "Advanced settings" e cole em
   "Secrets" o conteúdo do seu `.streamlit/secrets.toml` (se já tiver
   configurado o Mercado Pago):
   ```
   MERCADOPAGO_ACCESS_TOKEN = "TEST-..."
   ```
5. Clique em "Deploy". Em alguns minutos o app estará disponível em
   uma URL pública (algo como `seguro-saas.streamlit.app`).

**Importante — sobre o banco de dados:** o app usa SQLite, um arquivo
local (`database/seguro_saas.db`). No Streamlit Community Cloud, o
armazenamento é temporário: sempre que o app "dorme" por inatividade
e é reiniciado, ou quando você faz um novo deploy, esse arquivo é
recriado do zero (a empresa de demonstração `demo`/`admin`/`admin123`
volta, mas clientes e apólices cadastrados no site são perdidos).
Isso é aceitável para demonstração, mas antes de usar com clientes
reais vale migrar para um banco externo (ex: PostgreSQL gerenciado).

A versão do Python usada no deploy está fixada em `runtime.txt`
(3.12), para ficar igual ao ambiente de desenvolvimento local.

## Status do desenvolvimento

- [x] Etapa 1 — Estrutura do projeto
- [x] Etapa 2 — Tela de login funcional
- [x] Etapa 3 — Multi-tenant
- [x] Etapa 4 — Cadastro de clientes
- [x] Etapa 5 — Sistema de pagamentos
- [x] Etapa 6 — Relatórios
- [x] Etapa 7 — Deploy online
- [x] Etapa 8 — Modelo de negócio
