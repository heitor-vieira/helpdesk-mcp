# Missão do servidor Helpdesk MCP

O servidor Helpdesk MCP tem como propósito facilitar a gestão dos chamados de
suporte feitos pelos colaboradores de uma empresa. Ele disponibiliza operações
de helpdesk por meio do Model Context Protocol (MCP), permitindo que clientes
compatíveis consultem e atualizem chamados sem precisar interagir diretamente
com a implementação interna do sistema.

## Público-alvo

As ferramentas do servidor serão utilizadas por agentes de IA e por aplicações
clientes compatíveis com MCP. Esses clientes poderão apoiar os colaboradores
na consulta e na manutenção das informações dos chamados.

## Escopo inicial

A primeira versão será entregue em três etapas:

- listar chamados, com filtro opcional por status;
- consultar os chamados associados a um cliente;
- atualizar o status de um chamado existente.

Na segunda etapa, “histórico do cliente” significa o conjunto de chamados
associados a esse cliente. O histórico de eventos de consulta e atualização é
um registro interno separado. O escopo é intencionalmente limitado a essas
operações, servindo como exemplo de integração entre um servidor MCP e um
fluxo básico de helpdesk.

## Limites do exemplo

- Os dados utilizados são fictícios e destinados apenas a demonstração.
- O servidor deve ser executado em ambiente local; não representa um serviço
  pronto para uso em produção.
- O exemplo não implementa autenticação real nem deve ser usado para acessar
  dados ou sistemas reais sem as adaptações e proteções necessárias.