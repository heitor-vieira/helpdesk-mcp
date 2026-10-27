# Helpdesk MCP

Servidor MCP local para demonstração de gestão de chamados. Nesta primeira
fase, a tool `listar_chamados` lista chamados persistidos em SQLite e permite
filtrar pelo status `aberto`, `em_andamento`, `resolvido` ou `fechado`.
Chamados fictícios são adicionados na primeira inicialização; reiniciar o
servidor não restaura nem substitui chamados alterados ou removidos.

## Requisitos

- Python 3.10 ou superior (implementação e testes verificados com Python 3.10.12).
- `pip` e VS Code com suporte ao Model Context Protocol.

## Instalação e execução local

Na raiz do projeto, crie e ative o ambiente virtual e instale as dependências:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

No Windows, ative o ambiente com `.venv\Scripts\activate` no Prompt de
Comando ou `.venv\Scripts\Activate.ps1` no PowerShell.

Inicie o servidor usando o ambiente virtual:

```bash
python -m helpdesk_mcp.server
```

O servidor usa o transporte MCP `stdio`; por isso, mensagens do protocolo
ocupam `stdout`. O arquivo `data/helpdesk.db` e suas tabelas são criados
automaticamente. A tabela `ticket_history` registra a criação inicial e cada
consulta que efetivamente retorna chamados.

## Testes

Os testes usam bancos SQLite temporários e chamam a tool por um cliente MCP
em memória:

```bash
python -m unittest discover -s tests -v
```

## Registro no VS Code

O workspace inclui `.vscode/mcp.json`, que registra o servidor como
`helpdesk-mcp` usando `.venv`. Depois de criar o ambiente e instalar as
dependências, abra o workspace no VS Code e use a ação **Start** exibida no
arquivo `mcp.json` (ou reinicie o VS Code). Revise e aprove a configuração de
confiança do servidor local quando solicitado.

Para usar a tool no Copilot Chat, selecione o modo **Agent** e confirme em
**Configure Tools** que `helpdesk-mcp` / `listar_chamados` está habilitada.
Peça explicitamente ao agente para usar a tool MCP, por exemplo:

- “Use a tool MCP `listar_chamados` para listar todos os chamados.”
- “Use a tool MCP `listar_chamados` com status `aberto`.”
- “Use a tool MCP `listar_chamados` com status `pendente`.”

Expanda cada chamada na conversa e confirme que ela pertence ao servidor
`helpdesk-mcp` e retornou o resultado. Uma resposta plausível sem a chamada
visível não comprova o uso do MCP. As duas primeiras consultas devem refletir
os registros em `data/helpdesk.db`; a última deve apresentar erro de validação,
pois `pendente` não é um status permitido.

O comando configurado no arquivo usa o caminho de executável do ambiente
virtual para Linux/macOS. No Windows, altere `command` para
`${workspaceFolder}/.venv/Scripts/python.exe`.