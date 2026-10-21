# Sistema Barbearia Navalha

## Descrição do Sistema
O **Sistema Barbearia Navalha** é uma aplicação em linha de comando desenvolvida em Python com integração ao banco de dados PostgreSQL. O sistema permite o gerenciamento completo de agendamentos de uma barbearia, oferecendo controle de acesso por login, cadastro de clientes, escolha de serviços, listagem, buscas dinâmicas, atualizações, exclusões e emissão de relatórios de faturamento.

## Tecnologias Utilizadas
* **Linguagem:** Python 3
* **Banco de Dados:** PostgreSQL
* **Biblioteca Python:** `psycopg2-binary` (para conexão e manipulação do PostgreSQL)

## Configuração do Banco de Dados
1. Certifique-se de ter o PostgreSQL e o pgAdmin instalados na sua máquina.
2. Crie um banco de dados vazio chamado `barbearia_db`:
   * No pgAdmin, clique com o botão direito em **Databases** > **Create** > **Database...**
   * Nome: `barbearia_db` e clique em **Save**.
3. O próprio script Python possui uma rotina automática (`iniciar_banco()`) que cria as tabelas necessárias (`usuarios`, `servicos`, `agendamentos`) e insere os dados iniciais assim que é executado pela primeira vez.

## Instruções para Execução
1. Clone o repositório ou baixe os arquivos do projeto para o seu computador.
2. Abra o terminal (PowerShell ou CMD) na pasta do projeto.
3. Instale a biblioteca necessária do PostgreSQL executando o comando:
   ```bash
   python -m pip install psycopg2-binary
 
