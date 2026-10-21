"""Sistema Barbearia Navalha com PostgreSQL."""
import psycopg2
from datetime import datetime

HOST = "localhost"
PORTA = "5432"
BANCO = "barbearia_db"
USUARIO = "postgres"
SENHA = "root"


def executar(sql, parametros=(), retornar=False):
    """Executa comandos SQL e fecha a conexão."""
    conexao = psycopg2.connect(
        host=HOST, port=PORTA, dbname=BANCO,
        user=USUARIO, password=SENHA
    )
    try:
        with conexao:
            with conexao.cursor() as cursor:
                cursor.execute(sql, parametros)
                resultado = cursor.fetchall() if retornar else None
        return resultado
    finally:
        conexao.close()


def iniciar_banco():
    """Cria as tabelas e insere dados iniciais caso não existam."""
    # Tabela 1: Usuários (Atende ao requisito de Login)
    executar("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            senha VARCHAR(50) NOT NULL
        )
    """)

    # Tabela 2: Serviços
    executar("""
        CREATE TABLE IF NOT EXISTS servicos (
            id SERIAL PRIMARY KEY,
            nome VARCHAR(50) NOT NULL,
            preco NUMERIC(10,2) NOT NULL
        )
    """)

    # Tabela 3: Agendamentos (Relacionada com Serviços via Chave Estrangeira)
    executar("""
        CREATE TABLE IF NOT EXISTS agendamentos (
            id SERIAL PRIMARY KEY,
            cliente VARCHAR(100) NOT NULL,
            telefone VARCHAR(20) NOT NULL,
            servico_id INT REFERENCES servicos(id) ON DELETE CASCADE,
            data_agendamento DATE NOT NULL,
            horario TIME NOT NULL
        )
    """)

    # Insere um usuário padrão para teste se não existir
    usuario_existe = executar("SELECT * FROM usuarios WHERE username = 'admin'", retornar=True)
    if not usuario_existe:
        executar("INSERT INTO usuarios (username, senha) VALUES ('admin', '1234')")

    # Insere os serviços padrão se a tabela estiver vazia
    servicos_existem = executar("SELECT * FROM servicos", retornar=True)
    if not servicos_existem:
        servicos_iniciais = [
            ("Corte", 35.00),
            ("Barba", 25.00),
            ("Corte + barba", 50.00),
            ("Sobrancelha", 10.00)
        ]
        for nome, preco in servicos_iniciais:
            executar("INSERT INTO servicos (nome, preco) VALUES (%s, %s)", (nome, preco))

    print("Banco de dados conectado e tabelas configuradas com sucesso!")


def realizar_login():
    """Requisito: Possuir login de usuário."""
    print("\n===== LOGIN DO SISTEMA =====")
    while True:
        user = input("Usuário: ").strip()
        senha = input("Senha: ").strip()

        resultado = executar(
            "SELECT * FROM usuarios WHERE username = %s AND senha = %s",
            (user, senha), retornar=True
        )

        if resultado:
            print(f"\nLogin bem-sucedido! Bem-vindo, {user}.")
            return True
        else:
            print("Usuário ou senha incorretos. Tente novamente.")
            opcao = input("Deseja tentar novamente? (s/n): ").strip().lower()
            if opcao != 's':
                return False


def ler_texto(mensagem):
    while True:
        texto = input(mensagem).strip()
        if texto:
            return texto
        print("O campo não pode ficar vazio.")


def ler_id():
    try:
        return int(input("ID do agendamento: "))
    except ValueError:
        print("Digite um ID numérico válido.")
        return None


def escolher_servico():
    """Busca os serviços cadastrados na tabela servicos."""
    servicos = executar("SELECT id, nome, preco FROM servicos ORDER BY id", retornar=True)
    for s in servicos:
        print(f"{s[0]}. {s[1]} - R$ {s[2]:.2f}")
    try:
        escolha = int(input("Escolha o ID do serviço: "))
        for s in servicos:
            if s[0] == escolha:
                return s[0] # Retorna o ID do serviço
    except ValueError:
        pass
    print("Serviço inválido.")
    return None


def ler_data_hora():
    try:
        data = datetime.strptime(
            input("Data (DD/MM/AAAA): ").strip(), "%d/%m/%Y"
        ).date()
        horario = datetime.strptime(
            input("Horário (HH:MM): ").strip(), "%H:%M"
        ).time()
        return data, horario
    except ValueError:
        print("Data ou horário inválido.")
        return None


def cadastrar():
    cliente = ler_texto("Nome do cliente: ")
    telefone = ler_texto("Telefone: ")
    servico_id = escolher_servico()
    if servico_id is None:
        return

    dados_data = ler_data_hora()
    if dados_data is None:
        return

    data, horario = dados_data
    executar("""
        INSERT INTO agendamentos
        (cliente, telefone, servico_id, data_agendamento, horario)
        VALUES (%s, %s, %s, %s, %s)
    """, (cliente, telefone, servico_id, data, horario))
    print("Agendamento cadastrado com sucesso!")


def listar():
    """Usa JOIN para juntar as tabelas agendamentos e servicos."""
    registros = executar("""
        SELECT a.id, a.cliente, a.telefone, s.nome, s.preco,
               a.data_agendamento, a.horario
        FROM agendamentos a
        JOIN servicos s ON a.servico_id = s.id
        ORDER BY a.id
    """, retornar=True)

    if not registros:
        print("Nenhum agendamento cadastrado.")
        return

    for reg in registros:
        print(
            f"ID: {reg[0]} | Cliente: {reg[1]} | Telefone: {reg[2]} | "
            f"Serviço: {reg[3]} | R$ {reg[4]:.2f} | "
            f"Data: {reg[5].strftime('%d/%m/%Y')} | "
            f"Hora: {reg[6].strftime('%H:%M')}"
        )


def buscar():
    """Requisito: Filtros de dados utilizando consultas SQL (ILIKE)."""
    termo = input("Digite o ID ou parte do nome: ").strip()
    registros = executar("""
        SELECT a.id, a.cliente, a.telefone, s.nome, s.preco,
               a.data_agendamento, a.horario
        FROM agendamentos a
        JOIN servicos s ON a.servico_id = s.id
        WHERE a.cliente ILIKE %s OR a.id::text = %s
        ORDER BY a.id
    """, (f"%{termo}%", termo), retornar=True)

    if registros:
        for reg in registros:
            print(
                f"ID: {reg[0]} | Cliente: {reg[1]} | Telefone: {reg[2]} | "
                f"Serviço: {reg[3]} | R$ {reg[4]:.2f} | "
                f"Data: {reg[5].strftime('%d/%m/%Y')} | "
                f"Hora: {reg[6].strftime('%H:%M')}"
            )
    else:
        print("Agendamento não encontrado.")


def atualizar():
    identificador = ler_id()
    if identificador is None:
        return

    existe = executar(
        "SELECT id FROM agendamentos WHERE id = %s",
        (identificador,), retornar=True
    )
    if not existe:
        print("Agendamento não encontrado.")
        return

    cliente = ler_texto("Novo nome: ")
    telefone = ler_texto("Novo telefone: ")
    dados_data = ler_data_hora()
    if dados_data is None:
        return

    data, horario = dados_data
    trocar = input("Trocar serviço? (s/n): ").strip().lower()
    
    if trocar == "s":
        servico_id = escolher_servico()
        if servico_id is None:
            return
    else:
        atual = executar(
            "SELECT servico_id FROM agendamentos WHERE id = %s",
            (identificador,), retornar=True
        )[0]
        servico_id = atual[0]

    executar("""
        UPDATE agendamentos
        SET cliente=%s, telefone=%s, servico_id=%s,
            data_agendamento=%s, horario=%s
        WHERE id=%s
    """, (cliente, telefone, servico_id, data, horario, identificador))
    print("Agendamento atualizado!")


def excluir():
    identificador = ler_id()
    if identificador is None:
        return

    registro = executar(
        "SELECT cliente FROM agendamentos WHERE id=%s",
        (identificador,), retornar=True
    )
    if not registro:
        print("Agendamento não encontrado.")
        return

    confirmar = input(
        f"Excluir {registro[0][0]}? (s/n): "
    ).strip().lower()

    if confirmar == "s":
        executar("DELETE FROM agendamentos WHERE id=%s", (identificador,))
        print("Agendamento excluído.")
    else:
        print("Exclusão cancelada.")


def relatorio():
    resumo = executar("""
        SELECT COUNT(*), COALESCE(SUM(s.preco), 0)
        FROM agendamentos a
        JOIN servicos s ON a.servico_id = s.id
    """, retornar=True)[0]

    print("\n--- RELATÓRIO DA BARBEARIA ---")
    print(f"Agendamentos totais: {resumo[0]}")
    print(f"Faturamento previsto: R$ {resumo[1]:.2f}")

    contagem = executar("""
        SELECT s.nome, COUNT(a.id) FROM servicos s
        LEFT JOIN agendamentos a ON s.id = a.servico_id
        GROUP BY s.nome ORDER BY s.nome
    """, retornar=True)

    for nome, quantidade in contagem:
        print(f"{nome}: {quantidade} agendamento(s)")


def menu():
    while True:
        print("\n===== BARBEARIA NAVALHA =====")
        print("1 - Cadastrar agendamento")
        print("2 - Listar agendamentos")
        print("3 - Buscar agendamento")
        print("4 - Atualizar agendamento")
        print("5 - Excluir agendamento")
        print("6 - Relatório")
        print("0 - Sair")

        opcao = input("Escolha: ").strip()
        if opcao == "1":
            cadastrar()
        elif opcao == "2":
            listar()
        elif opcao == "3":
            buscar()
        elif opcao == "4":
            atualizar()
        elif opcao == "5":
            excluir()
        elif opcao == "6":
            relatorio()
        elif opcao == "0":
            print("Sistema encerrado.")
            break
        else:
            print("Opção inválida.")


if __name__ == "__main__":
    try:
        iniciar_banco()
        if realizar_login():
            menu()
    except psycopg2.Error as erro:
        print("Erro de conexão ou banco de dados:", erro)
        print("Confira servidor, banco, usuário, senha e porta.")