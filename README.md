# 💰 Desafio 4 - Sistema Bancário com POO e Persistência de Dados

Este é o **quarto desafio** do **Bootcamp Santander 2025 - Back-End com Python**.  
Nesta etapa, além dos conceitos de **Programação Orientada a Objetos (POO)**, foram adicionadas funcionalidades de **persistência de dados com arquivos JSON**, uso de **funções decoradoras** e **registro de logs** para rastreabilidade das operações realizadas.

---

## ⚙️ Funcionalidades Implementadas

### 📌 Funcionalidades Gerais

- **Depósito**: Adiciona saldo na conta do cliente, validando valores positivos.
- **Saque**: Permite sacar valores respeitando o limite diário de saques e o limite máximo por saque.
- **Extrato**: Lista todas as movimentações (depósitos e saques) realizadas com data e hora.
- **Criação de Usuário**: Permite cadastrar clientes com CPF, nome, data de nascimento e endereço, impedindo duplicações.
- **Criação de Conta**: Cria uma conta corrente para um cliente existente, permitindo múltiplas contas por cliente.
- **Listagem de Usuários e Contas**: Exibe informações dos clientes e suas contas bancárias.

---

## 🆕 Atualizações da Parte 4

### 🔧 Funcionalidades Adicionadas

- ✅ **Persistência de Dados com JSON**  
  Clientes e contas agora são armazenados em arquivos `.json`.  
  Os dados são carregados automaticamente ao iniciar o sistema.

- ✅ **Funções Decoradoras**  
  Algumas funções principais como `depositar`, `sacar`, `criarCliente`, `criarConta` e `exibir_extrato` foram decoradas com `@log_transacao`, responsável por registrar logs.

- ✅ **Registro de Logs**  
  Toda operação executada no sistema é registrada no arquivo `log.txt`, incluindo:
  - Nome da função executada
  - Argumentos utilizados
  - Data e hora da execução

---

## 🧱 Estruturas do Projeto

| Classe         | Descrição |
|----------------|-----------|
| `Cliente`      | Classe base para qualquer cliente. Armazena endereço e lista de contas. |
| `PessoaFisica` | Herda de `Cliente`, adiciona CPF, nome e data de nascimento. |
| `Conta`        | Classe base de contas. Gerencia saldo, saque, depósito e histórico. |
| `ContaCorrente`| Herda de `Conta`, com regras específicas de limite de saque e número máximo de saques. |
| `Historico`    | Armazena todas as transações feitas por uma conta. |
| `Transacao`    | Classe abstrata que define a interface para `Deposito` e `Saque`. |
| `Deposito`     | Representa uma transação de depósito. |
| `Saque`        | Representa uma transação de saque. |

---

## 🧠 Conceitos de POO Utilizados

- **Herança**: Ex: `PessoaFisica` herda de `Cliente`, `ContaCorrente` herda de `Conta`.
- **Polimorfismo**: O método `registrar()` é sobrescrito nas transações.
- **Abstração**: A classe `Transacao` é abstrata e exige implementação de `registrar()` nas subclasses.
- **Composição**: A `Conta` possui (`tem um`) objeto `Historico`.

---

## 🚀 Como Executar

1. Certifique-se de ter o **Python** instalado.
2. Salve o código em um arquivo, por exemplo `sistema_bancario.py`.
3. Execute no terminal com:

```bash
python sistema_bancario.py
```

---

## 📁 Arquivos Gerados
- clientes.json: Armazena os dados dos clientes cadastrados.
- contas.json: Armazena os dados das contas correntes associadas aos clientes.
- log.txt: Armazena os registros de operações realizadas no sistema.

---

## 🛠 Tecnologias Utilizadas
- Python: Linguagem principal usada no desenvolvimento do sistema.
- JSON: Utilizado para persistência de dados.
- Funções Decoradoras: Para registrar ações no log.
