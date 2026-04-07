# 📊 Sistema Automático de Inteligência Fiscal - cBenef (SP)

**Status do Projeto:** `Produção - Estável` | **Integração ERP:** `Thor` | **Matrizes Homologadas:** `8 Bases PostgreSQL`

O **cBenef Engine** é um autômato fiscal projetado para ler, interpretar e aplicar as regras da Secretaria da Fazenda do Estado de São Paulo (SEFAZ-SP) em Notas Fiscais Eletrônicas (NFe e NFCe - Modelos 55 e 65). 
Sua função primária é **substituir a digitação humana** na classificação da tag XML `<cBenef>`, garantindo que operações complexas aduaneiras e de suspensão tributária nunca sofram multas por preenchimento errado no faturamento.

---

## 🛠️ Tecnologias e Ambiente
- **OS Requerido:** Windows com WSL (Ubuntu/Linux) ou Servidor Linux Nativo.
- **Linguagem:** Python 3.10+
- **Bibliotecas Principais:** 
  - `psycopg2-binary` (Conexão nativa veloz com PostgreSQL do ERP)
  - `thefuzz` (Motor de Similaridade Algorítmica para cruzamento de Leis/Decretos)
  - `Flask` & `Flask-Cors` (Web Server para rodar como API REST em Background)
  - `roman` (Equiparação lógica Romano-Arábica em Artigos de Lei)

Para instalar as dependências no ambiente virtual (`venv`):
```bash
source venv/bin/activate
pip install -r requirements.txt
```

---

## 📂 Arquitetura de Scripts e Fluxo do Autômato

O projeto opera em três grandes pilares: **Geração de Base Legal, API de Sugestão Contínua, e Auditoria/Radar.**

### 1. Base Jurídica e Extração (SEFAZ)
O coração da inteligência. Transforma PDFs e planilhas da SEFAZ que pesam milhares de linhas em um cérebro digital mapeado para o bot.
- **`parse_table.py`**: O script que deve ser executado quando a Fazenda atualizar as leis. Ele lê a tabela crua (excel/json) e compila o Data Lake otimizado `cbenef_db.json`. Nele, NCMs e CSTs são atrelados com precisos índices algorítmicos.

### 2. O Motor Python (Core Engine)
- **`cbenef_engine.py`**: Aqui reside a Inteligência de Negócio. Quando o ERP não sabe qual Código Fiscal apontar, ele instila `CST`, `NCM` e `CFOP` neste objeto. 
    - Ele aplica "Táticas Contábeis" diretas (ex: *Forçar a CST 50 e a tag `SP054020` caso a nota possua CFOP de Retorno de Industrialização 5901, 6901 e etc*).
    - Ele avalia o "Distanciamento de Leis" via theFuzz, priorizando `Matches == 100`.

### 3. API Integrada do ERP (Modo Autônomo)
O Faturador (ex: **Thor ERP**) se comunica com o motor em tempo real:
- **`app.py`**: Inicializa um servidor na porta `5000`. Funciona mapeando chamadas HTTP `POST` no formato:
  ```json
  POST http://localhost:5000/suggest
  {
    "cst": "50",
    "cfop": "5901",
    "ncm": "73251000",
    "legal_text": "Isento conf. artigo IV"
  }
  ```

---

## 📈 Ferramentas de Fechamento Contábil (Auditorias CSV)
Ao final do mês, contadores precisam de provas de adequação da malha fiscal. O projeto conta com scripts que rasgam massivamente as bases PostgreSQL de todas as matrizes (`solutionsp`, `tavaresdb`, `comfitasdb`, etc) e compilam Excel automatizado:

*   **`run_all_audits.py`**: 
    Um consolidado absoluto das 8 matrizes corporativas (Ecotech, Juncao, SolutionSP, etc). Ele extrai TODAS as notas fiscais (innotapropria='S', status='131'), cruza os dados que estão gravados na placa *versus* o que nossa inteligência apontaria, e gera 8 arquivos CSV (`Auditoria_cBenef_...`) omitindo o "lixo atômico" (notas CST 00 regulares e sem benefício) e flagrando apenas as Notas Válidas vs AI.

*   **`audit_erros_fiscais.py` (O Radar Anti-Multa):**
    Script punitivo desenhado especificamente para encontrar furos lógicos dos operadores faturistas.
    Gera o CSV `Radar_Erros_Fiscais_..._V2.csv`, com as regras vitais:
    1. **Regra Aduaneira Absoluta:** O radar filtra notas da família `3000` (Importações) empurrando-as para as Linhas de Topo 1 do Excel, avisando o escritório que tais notas com entrada de alto valor precisam de análise fiscal refinada (II, IPI, etc).
    2.  Remessa de Conserto (`5901/6901`) emitidas equivocadamente sem `CST 50`.
    3. Comerciais de Venda Rápida vendidas irregularmente flagradas com `CST 50`.

**⚠️ Atenção Contadores:** Todos os CSVs gerados por estes scripts contém na linha 1 o fragmento mágico `sep=;` e são codificados em `utf-8-sig`. Basta **um clique duplo no Windows** para o Excel abrir a planilha perfeitamente mapeada com acentuação e colunada.

---

## 🖥️ Procedimento de Operação a Longo Prazo

Para iniciar o robô do ERP no servidor para rodar "para sempre" de forma assíncrona (após um boot ou queda de luz):
```bash
cd /caminho/do/projeto/cbenef
source venv/bin/activate
nohup python3 app.py > api_thor.log 2>&1 &
```

> *Desenvolvido e homologado integralmente de Janeiro a Abril/2026 perante grandes massas de dados de Produção.*
