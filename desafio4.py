import json
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path

ROOT_PATH = Path(__file__).parent


class ContasIterador:
    def __init__(self, contas):
        self.contas = contas
        self._index = 0

    def __iter__(self):
        return self

    def __next__(self):
        try:
            conta = self.contas[self._index]
            return (
                "\n"
                + f" CONTA {conta.numero} ".center(50, "=")
                + "\n"
                + f"Agência: {conta.agencia}".center(50)
                + "\n"
                + f"CPF: {conta.cliente.cpf}".center(50)
                + "\n"
                + f"Titular: {conta.cliente.nome}".center(50)
                + "\n"
                + f"Saldo: R${conta.saldo:.2f}".center(50)
                + "\n"
                + "=" * 50
            )
        except IndexError:
            raise StopIteration
        finally:
            self._index += 1


# ----- Transações ----- #
class Historico:
    def __init__(self):
        self._transacoes = []

    @property
    def transacoes(self):
        return self._transacoes

    def adicionar_transacao(self, transacao):
        self._transacoes.append(
            {
                "tipo": transacao.__class__.__name__,
                "valor": transacao.valor,
                "data": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            }
        )

    # Filtra e envia as transações
    def gerar_relatorio(self, tipo_transacao=None):
        for transacao in self._transacoes:
            # Retorna todas se não tiver especificado ou apenas de um tipo específico
            if tipo_transacao is None or transacao["tipo"].lower() == tipo_transacao.lower():
                yield transacao

    # Lista das trasações diárias
    def transacoes_do_dia(self):
        data_atual = datetime.now().date()
        transacoes = []

        for transacao in self._transacoes:
            data_transacao = datetime.strptime(transacao["data"], "%d/%m/%Y %H:%M:%S").date()

            if data_atual == data_transacao:
                transacoes.append(transacao)

        return transacoes


class Transacao(ABC):
    @abstractmethod
    def registrar(self, conta):
        pass


class Deposito(Transacao):
    def __init__(self, valor):
        self.valor = valor

    def registrar(self, conta):
        if conta.depositar(self.valor):
            conta.historico.adicionar_transacao(self)


class Saque(Transacao):
    def __init__(self, valor):
        self.valor = valor

    def registrar(self, conta):
        if conta.sacar(self.valor):
            conta.historico.adicionar_transacao(self)


# ----- Clientes ----- #
class Cliente:
    def __init__(self, endereco):
        self.endereco = endereco
        self.contas = []

    def realizar_transacao(self, conta, transacao):
        if len(conta.historico.transacoes_do_dia()) >= 10:
            print("\n[!] Você atingiu o limite diário de transações!")
            return

        transacao.registrar(conta)

    def adicionar_conta(self, conta):
        self.contas.append(conta)


class PessoaFisica(Cliente):
    def __init__(self, endereco, cpf, nome, data_nascimento):
        super().__init__(endereco)
        self.cpf = cpf
        self.nome = nome
        self.data_nascimento = data_nascimento

    def to_dict(self):
        return {
            "endereco": self.endereco,
            "cpf": self.cpf,
            "nome": self.nome,
            "data_nascimento": self.data_nascimento,
        }

    @classmethod
    def novo_cliente(cls, endereco, cpf, nome, data_nascimento):
        return cls(endereco, cpf, nome, data_nascimento)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: (CPF: {self.cpf})>"


# ----- Contas ----- #
class Conta:
    def __init__(self, numero, cliente):
        self._saldo = 0
        self._numero = numero
        self._agencia = "0001"
        self._cliente = cliente
        self._historico = Historico()

    @classmethod
    def nova_conta(cls, numero, cliente):
        return cls(numero, cliente)

    @property
    def saldo(self):
        return self._saldo

    @property
    def numero(self):
        return self._numero

    @property
    def agencia(self):
        return self._agencia

    @property
    def cliente(self):
        return self._cliente

    @property
    def historico(self):
        return self._historico

    def sacar(self, valor):
        saldo = self.saldo
        saldo_excedido = valor > saldo

        # Valor maior que o saldo
        if saldo_excedido:
            print("\n[!] Saque falhou! Saldo insuficiente")

        # Valor válido
        elif valor > 0:
            self._saldo -= valor
            print(f"\n[+] Saque de R${valor} realizado com sucesso!")

            return True

        # Valor inválido
        else:
            print("\n[!] Saque falhou! Valor informado é inválido")

        return False

    def depositar(self, valor):
        if valor > 0:
            self._saldo += valor
            print(f"\n[+] Depósito de R${valor} realizado com sucesso!")

            return True
        else:
            print("\n[!] Depósito falhou! Valor Inválido")

        return False


class ContaCorrente(Conta):
    def __init__(self, numero, cliente, limite=500, limite_saques=3):
        super().__init__(numero, cliente)
        self._limite = limite
        self._limite_saques = limite_saques

    def to_dict(self):
        return {
            "numero": self.numero,
            "cliente": self.cliente.to_dict(),
            "limite": self._limite,
            "limite_saques": self._limite_saques,
        }

    def sacar(self, valor):
        # Validação: Quantidade Limite de Saques
        num_saques = 1
        for transacao in self._historico.transacoes:
            if transacao["tipo"] == "Saque":
                num_saques += 1

        quantidade_excedida = num_saques > self._limite_saques

        # Validação: Valor Limite de Saque
        valor_excedido = valor > self._limite

        if quantidade_excedida:
            print("\n[!] Saque falhou! Número de saques diários atingido")

        elif valor_excedido:
            print("\n[!] Saque falhou! Valor limite atingido")

        else:
            # Valição específica CC + Validação geral
            return super().sacar(valor)

        return False

    def __repr__(self):
        return f"<{self.__class__.__name__}: ('{self.agencia}', '{self.numero}', '{self.cliente.nome}')>"

    def __str__(self):
        return (
            "\n"
            + f" CONTA {self._numero} ".center(30, "=")
            + f"\n\tAgência: {self._agencia}"
            + f"\n\tCPF: {self._cliente.cpf}"
            + f"\n\tTitular: {self._cliente.nome}\n"
            + f"{"=" * 30}"
        )


# ----- Funções ----- #
def menu():
    menu = """ 
-- || Opções de operações || -- 

[0] Depositar
[1] Sacar
[2] Extrato
[3] Criar Usuário
[4] Criar Conta

[5] Listar Usuários
[6] Listar Contas
[7] Sair

Escolha: """

    opcao = input(menu)

    return opcao


def buscar_cliente(clientes, cpf):
    cliente = [cliente for cliente in clientes if cliente.cpf == cpf]
    if len(cliente) == 0:
        print("\n[!] Não foi encontrado cliente com este CPF!")
        cliente = None
    else:
        cliente = cliente[0]

    return cliente


def obter_cliente_por_cpf(clientes):
    cpf = input("Informe o CPF do usuário: ")
    cliente = buscar_cliente(clientes, cpf)

    if cliente is None:
        return None

    return cliente


def log_transacao(func):
    def envelope(*args, **kwargs):
        resultado = func(*args, **kwargs)

        argumentos = ", ".join(str(a) for a in args)

        with open(ROOT_PATH / "log.txt", "a") as arquivo_log:
            arquivo_log.write(
                f"[{datetime.now().strftime("%d/%m/%Y %H:%M:%S")}] - Funcao: {func.__name__}() || Argumentos: {argumentos}\n"
            )
            # print(f"Ação: {func.__name__.upper()} | Argumentos: {args} || {kwargs} - [{datetime.now().strftime("%d/%m/%Y %H:%M:%S")}]")
        return resultado

    return envelope


@log_transacao
def deposito(clientes):
    cliente = obter_cliente_por_cpf(clientes)

    if cliente is None:
        return

    # Validar se o cliente tem conta
    if not cliente.contas:
        print("\n[-] Cliente não possui contas!")
        return
    else:
        valor = float(input("Informe o valor do depósito: R$"))
        transacao = Deposito(valor)

        conta = cliente.contas[0]
        cliente.realizar_transacao(conta, transacao)


@log_transacao
def sacar(clientes):
    cliente = obter_cliente_por_cpf(clientes)

    if cliente is None:
        return

    # Validar se o cliente tem conta
    if not cliente.contas:
        print("[-] Cliente não possui contas!")
        return
    else:
        valor = float(input("Informe o valor do saque: R$"))
        transacao = Saque(valor)

        conta = cliente.contas[0]
        cliente.realizar_transacao(conta, transacao)


@log_transacao
def exibir_extrato(clientes, extrato):
    cliente = obter_cliente_por_cpf(clientes)

    # Valida se há o cliente com o cpf
    if cliente is None:
        return

    # Validar se o cliente tem conta
    if not cliente.contas:
        print("\n[-] Cliente não possui contas!")
        return
    else:
        conta = cliente.contas[0]

    tipo_transacao = "deposito"
    transacoes = conta.historico.gerar_relatorio(tipo_transacao)

    for transacao in transacoes:
        if transacao["tipo"] == "Saque":
            extrato += f"\n[{transacao["data"]}]\n[-] {transacao["tipo"]}: R${transacao["valor"]:.2f} \n"
        else:
            extrato += f"\n[{transacao["data"]}]\n[+] {transacao["tipo"]}: R${transacao["valor"]:.2f}\n"

    print("\n" + " EXTRATO ".center(30, "="))

    if tipo_transacao == "saque":
        print("Não foi realizado nenhum saque!." if not extrato else extrato)
    elif tipo_transacao == "deposito":
        print("Não foi realizado nenhum depósito!." if not extrato else extrato)
    else:
        print("Não foram realiadas movimentações." if not extrato else extrato)

    print(f"\nSaldo Atual: R${conta.saldo:.2f}")
    print("=".center(30, "="))


@log_transacao
def criar_cliente(clientes):
    print("\n--- Cadastro de Novo Cliente ---")
    cpf = input("Informe o CPF do usuário: ")

    # Validar usuário
    for cliente_existente in clientes:
        if cpf == cliente_existente.cpf:
            print("\n[!] Usuário com esse CPF já existente!")
            return

    nome = input("Nome Completo: ")
    data_nascimento = input("Data de Nascimento(DD/MM/YYYY): ")
    endereco = input("Endereço(Logadouro, Nº - Bairro - Cidade/Sigla Estado): ")

    # Adiciona
    cliente = PessoaFisica.novo_cliente(endereco, cpf, nome, data_nascimento)
    clientes.append(cliente)

    clientes_lista = [cliente.to_dict() for cliente in clientes]

    with open(ROOT_PATH / "clientes.json", "w") as arquivo:
        json.dump(clientes_lista, arquivo, indent=4)

    print("\n[+] Usuário Adicionado com Sucesso!")


@log_transacao
def criar_conta(contas, clientes, numero_conta):
    cliente = obter_cliente_por_cpf(clientes)

    if cliente is None:
        return

    conta = ContaCorrente.nova_conta(numero_conta, cliente)

    # Adiciona na lista de contas geral e do cliente
    contas.append(conta)
    cliente.contas.append(conta)

    # Trasnsforma em dicionário p/ salvar no json
    contas_lista = [conta.to_dict() for conta in contas]

    # Lê o json
    with open(ROOT_PATH / "contas.json", "r") as arquivo:
        dados_contas = json.load(arquivo)

    # Sobrescreve json com as contas e atualiza o próximo número
    dados_contas["contas"] = contas_lista
    dados_contas["num"] += 1
    with open(ROOT_PATH / "contas.json", "w") as arquivo:
        json.dump(dados_contas, arquivo, indent=4)

    print("\n[+] Conta Criada com Sucesso!")


def listar_contas(contas):

    if len(contas) == 0:
        print("\n[!] Sem contas disponíveis")
    else:
        for conta in ContasIterador(contas):
            print(conta)


def listar_usuarios(clientes):
    print("\n" + f" USUÁRIOS ".center(50, "="))

    if len(clientes) == 0:
        print("\tSem usuários disponíveis")
    else:
        for cliente in clientes:
            print(f"CPF: {cliente.cpf}")
            print(f"Nome: {cliente.nome}")
            print(f"Data Nascimento: {cliente.data_nascimento}")
            print(f"Endereco: {cliente.endereco}")
            print("=" * 30)

    print("\n" + "=" * 50)


def main():
    clientes = []
    contas = []

    CAMINHO_CLIENTES = ROOT_PATH / "clientes.json"
    CAMINHO_CONTAS = ROOT_PATH / "contas.json"

    # Carregar clientes
    if not CAMINHO_CLIENTES.exists():
        with open(CAMINHO_CLIENTES, "w") as arquivo:
            json.dump([], arquivo)
    else:
        with open(CAMINHO_CLIENTES, "r") as arquivo:
            dados_clientes = json.load(arquivo)

            clientes = [
                PessoaFisica.novo_cliente(
                    dados["endereco"],
                    dados["cpf"],
                    dados["nome"],
                    dados["data_nascimento"],
                )
                for dados in dados_clientes
            ]
            
    # Carregar Contas
    if not CAMINHO_CONTAS.exists():
        with open(CAMINHO_CONTAS, "w") as arquivo:
            json.dump({"num": 1, "contas": []}, arquivo)
    else:
        with open(CAMINHO_CONTAS, "r") as arquivo:
            dados_json = json.load(arquivo)
            dados_contas = dados_json["contas"]

            for dados in dados_contas:
                dados_cliente = dados["cliente"]

                # Converte o dicionário em objeto Cliente novamente
                cliente = PessoaFisica.novo_cliente(
                    dados_cliente["endereco"],
                    dados_cliente["cpf"],
                    dados_cliente["nome"],
                    dados_cliente["data_nascimento"],
                )

                conta = ContaCorrente.nova_conta(dados["numero"], cliente)
                contas.append(conta)

    extrato = ""

    # Número da próxima conta
    with open(CAMINHO_CONTAS, "r") as arquivo:
        dados_json = json.load(arquivo)
        num_conta = dados_json["num"]

    while True:
        opcao = menu()

        # Depósito
        if opcao == "0":
            deposito(clientes)

        # Sacar
        elif opcao == "1":
            sacar(clientes)

        # Extrato
        elif opcao == "2":
            # Vinculo entre as listas, necessidade de return
            exibir_extrato(clientes, extrato)

        # Usuário
        elif opcao == "3":
            criar_cliente(clientes)

        # Conta
        elif opcao == "4":
            criar_conta(contas, clientes, num_conta)
            num_conta += 1

        # Listar Usuário
        elif opcao == "5":
            listar_usuarios(clientes)

        # Listar Usuário
        elif opcao == "6":
            listar_contas(contas)

        # Sair
        elif opcao == "7":
            print("\n" + "APLICAÇÃO ENCERRADA".center(30, "-") + "\n")
            break

        else:
            print("[!] Operação inválida! Selecione novamente a operação desejada")


main()
