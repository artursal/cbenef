# Especificação de Projeto: Motor de Inteligência Fiscal cBenef (São Paulo)

## 📌 Visão Geral
O projeto **cBenef Engine** é uma API de Inteligência Artificial e heurística desenhada especificamente para automatizar com **100% de autonomia** o preenchimento da tag `<cBenef>` (Código de Benefício Fiscal) nas NFes e NFCes (Modelos 55 e 65) autorizadas no estado de São Paulo pela Secretaria da Fazenda (SEFAZ). 

Foi projetado para operar interligado ao **Thor ERP**, substituindo a antiga necessidade de validação humana e digitação baseada em grandes tabelas de Excel que a SEFAZ divulga.

## 🏗️ Stack e Arquitetura Tecnológica
1. **Ambiente:** WSL (Windows Subsystem for Linux) / Python 3.
2. **Bibliotecas Core:** 
   - `thefuzz` (Tratamento algorítmico de strings para buscar regras fiscais)
   - `roman` (Equiparação de números romanos em Artigos)
   - `psycopg2-binary` (Para extrações e simulações do banco PostgreSQL)
   - `Flask` & `Flask-CORS` (API REST contínua)
3. **Banco de Dados (Produção):** PostgreSQL local de produção (`solutionsp`), do qual os scripts retiram massa crua de auditoria via `innotapropria = 'S'` e `status = '131'`.

## ⚙️ Arquitetura do Sistema e Componentes

### 1. `parse_table.py` / Data Lake Oficial (`cbenef_db.json`)
O sistema inicia convertendo a intrincada tabela de Excel da SEFAZ em um banco de conhecimento (Data Lake JSON) contendo as colunas originais higienizadas:
- **Keys:** `code`, `csts`, `ncms`, `cests`, `norm_dispositivo`, `norm_descricao`.

### 2. `cbenef_engine.py` (O Motor Algorítmico)
Este é o coração do sistema, possuindo capacidade de dedução fiscal. Dada as entradas (CST, CFOP, NCM e Texto Legal), a função `engine.suggest()` executa a seguinte cadeia de prioridades:

*   **Peneira Primária:** Ignora automaticamente CST's que a SEFAZ não exige o cBenef (Ex: 00, 10, 60, etc.) garantindo performance.
*   **Heurística de Suspensão / Divertimento por CFOP (Táticas Contábeis):** Como alguns códigos da SEFAZ (ex: **SP054020** - Retorno de Industrialização) não limitam um NCM exato nem trazem descrições legais claras na integração com o ERP, o motor injeta uma regra inteligente de checar se `CST = 50` + `CFOPs = 5901, 6901, 5924, etc`. Isso força uma classificação 100% certeira.
*   **Regex Engine (Tradução Jurídica):** O motor extrai "Artigos" e "Anexos" do banco convertendo de romano para decimal e faz batimentos perfeitos (Rate == 50 e 30 points).
*   **Machine Match (NCM):** Confirma se o NCM emitido é um dos atrelados ao dispositivo fiscal, somando `60 pontos` na assertividade da Inteligência e devolvendo a resposta ideal.

### 3. `app.py` (A Camada de Interoperabilidade com o Thor ERP)
Fica rodando assíncronamente ouvindo chamadas REST.
O faturador (ERP) não precisa de tabelas internas, ele manda:
```json
POST /suggest
{
  "cst": "50",
  "ncm": "73251000",
  "cfop": "5901"
}
```
E sempre obterá o preenchimento, blindando a tabela SEFAZ atualizada de falhas humanas.

### 4. Automação de Auditoria e Conformidade Contábil
Ferramentas construídas para "Comprovação de Funcionalidade" perante a diretoria e área de contabilidade (como foi usado no caso da filial `Solution` com todo o ano de `2026`):

*   **`generate_csv_report.py`**:
    Cruza notas modelo *55* e *65*, varre o status *131* e retira nomes de cliente (`nmcli`), gerando relatórios super-enxutos.
    *   **Recurso Excel-Ready:** Emprega `utf-8-sig` e o comando `sep=;` na linha de cabeça para que o contador possa abrir *nativamente* o arquivo sem intervenções em configuração do Windows, acelerando a auditoria.
    *   **Omissão Inteligente:** Exclui lixo contábil do CSV. CST 00 e `SEM CBENEF` não entram no arquivo, focando 100% da leitura em "Omissões Reais" (ex: Vazio onde devia e códigos velhos digitados errados onde não devia).

## 🚀 Como Inicializar e Manter
Sempre que o servidor Windows reiniciar ou o ambiente WSL for desativado, rodar os comandos abaixo reativará o bot-faturador:

```bash
cd y:\Projetos\cbenef
source venv/bin/activate
nohup python3 app.py > api.log 2>&1 &
```

> **Futuro:** Quando a Sefaz soltar uma nova tabela de cBenef de Janeiro, o desenvolvedor apenas joga o `.xlsx` na pasta e roda o `parse_table.py` novamente. O Motor assumirá as novas regras no ato.
