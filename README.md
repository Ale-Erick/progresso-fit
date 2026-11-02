# ProgressoFit

Sistema web para acompanhamento da evolução física de praticantes de musculação,
com registro de métricas corporais, treinos e planos alimentares revisados por
profissionais habilitados.

> **Status:** Etapa 1 (entrega parcial): telas com navegação, modelos de dados e banco configurado.

## Equipe
- Alejandro (alejandro.messias@escolar.ifrn.edu.br)
- Erick (douglas.erick@escolar.ifrn.edu.br)

## Tecnologias
- **Backend:** Python 3, Django 6.1 (padrão MVT)
- **Banco de dados:** SQLite (via Django ORM)
- **Frontend:** HTML5, CSS3, JavaScript, Bootstrap 5, Bootstrap Icons e Chart.js
- **Versionamento e gestão:** Git, GitHub e GitHub Projects

## O que foi entregue na Etapa 1

| Item | Entrega |
|---|---|
| 01. Repositório | Repositório no GitHub com branches `main`, `develop` e `feature/*` |
| 02. Board | Quadro Kanban no [GitHub Projects](https://github.com/orgs/Ale-Erick/projects/3) com as tarefas da etapa |
| 03. Tema e protótipos | Descrição do tema e protótipos das telas em [`docs/tema.md`](docs/tema.md); visão geral, regras de negócio, requisitos funcionais e diagrama de casos de uso no [PDS](docs/PDS-ProgressoFit.pdf) |
| 04. Telas com navegação | Todas as telas em HTML/CSS/JS com rotas funcionando, no tema escuro dos protótipos |
| 05. Modelos de dados | Models, migrações e banco SQLite prontos, com cadastro pelo Django Admin |

### Telas e rotas

| Tela | Rota |
|---|---|
| Página inicial | `/` |
| Entrar | `/login/` |
| Cadastro | `/cadastro/` |
| Confirmação de e-mail | `/cadastro/confirme-email/` |
| Recuperar senha | `/recuperar-senha/` |
| Perfil | `/perfil/` |
| Editar perfil | `/perfil/editar/` |
| Verificação de especialista | `/especialista/verificacao/` |
| Registrar medição | `/metricas/registrar/` |
| Evolução corporal (indicadores, gráfico e histórico) | `/metricas/evolucao/` |
| Detalhe da medição | `/metricas/detalhe/<id>/` |
| Treinos | `/planos/treinos/` |
| Plano alimentar | `/planos/nutricao/` |
| Painel do especialista | `/planos/validacoes/` |
| Revisão de plano alimentar | `/planos/validacoes/<id>/` |
| Administração | `/admin/` |

As telas de evolução, detalhe, treinos, nutrição e painel do especialista **leem os dados do banco**.
Os formulários (login, cadastro, registro de medição etc.) já têm validação no navegador,
mas o processamento e a gravação dos dados ficam para a Etapa 2.

### Modelos de dados

| App | Model | Descrição |
|---|---|---|
| `contas` | `Perfil` | Dados do usuário: nome, descrição, visibilidade e nível de conhecimento corporal (Iniciante, Intermediário ou Avançado) |
| `contas` | `Especialista` | Área de atuação, registro profissional e status de verificação (Pendente, Verificado ou Rejeitado) |
| `metricas` | `MetricaCorporal` | Medição com data, peso e altura (obrigatórios), % de gordura, gordura visceral, metabolismo basal e circunferências |
| `planos` | `Treino` | Ficha de treino do aluno |
| `planos` | `PlanoAlimentar` | Plano do aluno com status (Pendente, Aprovado, Ajustado ou Rejeitado) e o especialista que o revisou |

## Como executar

**Pré-requisito:** ter o [Python 3](https://www.python.org/downloads/) instalado.

1. Clone o repositório:
   ```bash
   git clone https://github.com/Ale-Erick/progresso-fit.git
   cd progresso-fit
   ```

2. Crie e ative o ambiente virtual:
   ```bash
   python -m venv venv
   ```
   - Windows: `.\venv\Scripts\activate`
   - Linux ou macOS: `source venv/bin/activate`

3. Instale as dependências (com o ambiente virtual ativado):
   ```bash
   pip install -r requirements.txt
   ```

4. Crie o banco de dados aplicando as migrações:
   ```bash
   python manage.py migrate
   ```

5. Crie um usuário administrador:
   ```bash
   python manage.py createsuperuser
   ```

6. Rode o servidor:
   ```bash
   python manage.py runserver
   ```
   Acesse <http://127.0.0.1:8000> no navegador.

### Cadastrando dados de exemplo
O banco começa vazio. Para ver as listagens e o gráfico de evolução preenchidos:

1. Acesse <http://127.0.0.1:8000/admin> e entre com o superusuário.
2. Cadastre algumas **Métricas corporais**, com datas diferentes, para o gráfico mostrar a evolução.
3. Cadastre **Treinos** e **Planos alimentares**, com status variados, para ver como cada status aparece na tela de nutrição.

> Se o visual não atualizar depois de uma mudança no CSS, recarregue a página com **Ctrl + F5**.

## Organização do repositório
- **Branches:** `main` (estável) ← `develop` (integração) ← `feature/<nome>`
- **Commits:** padrão `tipo: descrição` (`feat`, `fix`, `docs`, `style`, `chore`)
- **Board:** [ProgressoFit - Board](https://github.com/orgs/Ale-Erick/projects/3)

## Estrutura
```
progresso-fit/
├── core/        # configurações e rotas principais
├── contas/      # Perfil, Especialista e telas de acesso
├── metricas/    # MetricaCorporal e telas de evolução
├── planos/      # Treino, PlanoAlimentar e telas de treino/nutrição
├── templates/   # base.html, includes/ (header, footer, aside) e home
├── static/      # css/style.css e js/main.js
├── docs/        # tema, protótipos e PDS (requisitos e casos de uso)
└── manage.py
```
