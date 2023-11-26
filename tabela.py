import mysql.connector
import tkinter as tk
from tkinter import ttk, messagebox


def conectar_bd():
    config = {
        'user': 'root',
        'password': '',
        'host': 'localhost',
        'database': 'lais',
        'raise_on_warnings': True
    }

    try:
        connection = mysql.connector.connect(**config)
        if connection.is_connected():
            print("Conectado ao MySQL")
            return connection

    except mysql.connector.Error as err:
        print(f"Erro: {err}")
        return None


def obter_dados_clientes():
    connection = conectar_bd()
    if connection:
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM clientes")
                dados = cursor.fetchall()
                return dados

        except mysql.connector.Error as err:
            print(f"Erro: {err}")

        finally:
            connection.close()
            print("Conexão ao MySQL fechada")


def excluir_cliente(id_cliente, tree):
    connection = conectar_bd()
    if connection:
        try:
            with connection.cursor() as cursor:
                sql = "DELETE FROM clientes WHERE id_cli = %s"
                cursor.execute(sql, (id_cliente,))
                connection.commit()
                messagebox.showinfo("Sucesso", "Cliente excluído com sucesso!")
                atualizar_tabela(tree)

        except mysql.connector.Error as err:
            print(f"Erro: {err}")
            messagebox.showerror("Erro", f"Erro: {err}")

        finally:
            connection.close()
            print("Conexão ao MySQL fechada")


def atualizar_tabela(tree):
    for item in tree.get_children():
        tree.delete(item)

    dados = obter_dados_clientes()
    for cliente in dados:
        tree.insert("", tk.END, values=cliente)


def pesquisar_cliente(tree, termo_pesquisa, tipo_pesquisa):
    for item in tree.get_children():
        tree.delete(item)

    connection = conectar_bd()
    if connection:
        try:
            with connection.cursor() as cursor:
                if tipo_pesquisa == "nome":
                    sql = "SELECT * FROM clientes WHERE nomecli LIKE %s"
                elif tipo_pesquisa == "data":
                    sql = "SELECT * FROM clientes WHERE data LIKE %s"
                elif tipo_pesquisa == "manu":
                    sql = "SELECT * FROM clientes WHERE datamanu LIKE %s"
                else:
                    return

                cursor.execute(sql, (f"%{termo_pesquisa}%",))
                dados = cursor.fetchall()

                for cliente in dados:
                    tree.insert("", tk.END, values=cliente)

        except mysql.connector.Error as err:
            print(f"Erro: {err}")

        finally:
            connection.close()
            print("Conexão ao MySQL fechada")


def adicionar_cliente(tree):
    janela_adicao = tk.Toplevel()
    janela_adicao.title("Adicionar Cliente")

    labels = ["Nome", "Telefone", "Idade", "Data", "Hora", "Estilo", "Valor", "Data Manutenção", "Valor Manutenção"]
    entries = []

    for label in labels:
        frame = tk.Frame(janela_adicao)
        frame.pack(padx=5, pady=5, fill="x")
        tk.Label(frame, text=label).pack(side=tk.LEFT)
        entry = tk.Entry(frame)
        entry.pack(side=tk.LEFT)
        entries.append(entry)

    def salvar_adicao():
        valores = [entry.get() for entry in entries]
        connection = conectar_bd()
        if connection:
            try:
                with connection.cursor() as cursor:
                    sql_insert = "INSERT INTO clientes (nomecli, telecli, idade, data, hora, estiloc, valorest, datamanu, valormanu) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
                    cursor.execute(sql_insert, tuple(valores))
                    connection.commit()
                    messagebox.showinfo("Sucesso", "Cliente adicionado com sucesso!")
                    janela_adicao.destroy()
                    atualizar_tabela(tree)
            except mysql.connector.Error as err:
                print(f"Erro: {err}")
            finally:
                connection.close()
                print("Conexão ao MySQL fechada")

    btn_salvar = tk.Button(janela_adicao, text="Salvar", command=salvar_adicao)
    btn_salvar.pack(pady=10)


def editar_cliente(tree, id_cliente):
    connection = conectar_bd()
    if connection:
        try:
            with connection.cursor() as cursor:
                sql = "SELECT * FROM clientes WHERE id_cli = %s"
                cursor.execute(sql, (id_cliente,))
                dados_cliente = cursor.fetchone()

                if dados_cliente:
                    janela_edicao = tk.Toplevel()
                    janela_edicao.title("Editar Cliente")

                    labels = ["Nome", "Telefone", "Idade", "Data", "Hora", "Estilo", "Valor", "Data Manutenção",
                              "Valor Manutenção"]
                    entries = []
                    for label, valor_atual in zip(labels, dados_cliente[1:]):
                        frame = tk.Frame(janela_edicao)
                        frame.pack(padx=5, pady=5, fill="x")
                        tk.Label(frame, text=label).pack(side=tk.LEFT)
                        entry = tk.Entry(frame)
                        entry.insert(tk.END, valor_atual)
                        entry.pack(side=tk.LEFT)
                        entries.append(entry)

                    def salvar_edicao():
                        novos_valores = [entry.get() for entry in entries]
                        connection = conectar_bd()
                        if connection:
                            try:
                                with connection.cursor() as cursor:
                                    sql_update = "UPDATE clientes SET nomecli=%s, telecli=%s, idade=%s, data=%s, hora=%s, estiloc=%s, valorest=%s, datamanu=%s, valormanu=%s WHERE id_cli=%s"
                                    cursor.execute(sql_update, (*novos_valores, id_cliente))
                                    connection.commit()
                                    messagebox.showinfo("Sucesso", "Informações do cliente atualizadas com sucesso!")
                                    janela_edicao.destroy()
                                    atualizar_tabela(tree)
                            except mysql.connector.Error as err:
                                print(f"Erro: {err}")
                                messagebox.showerror("Erro", f"Erro ao salvar as edições: {err}")
                            finally:
                                connection.close()
                                print("Conexão ao MySQL fechada")

                    btn_salvar = tk.Button(janela_edicao, text="Salvar Edição", command=salvar_edicao)
                    btn_salvar.pack(pady=10)

        except mysql.connector.Error as err:
            print(f"Erro: {err}")
            messagebox.showerror("Erro", f"Erro ao obter dados do cliente: {err}")
        finally:
            connection.close()


def exibir_tabela():
    root = tk.Tk()
    root.title("CLIENTES DA LAÍS")

    # Mudanças na aparência
    root.geometry("800x600")  # Ajuste as dimensões conforme necessário
    root.configure(bg="#F0F0F0")  # Cor de fundo

    tree = ttk.Treeview(root)
    tree["columns"] = (
        "ID", "Nome", "Telefone", "Idade", "Data", "Hora", "Estilo", "Valor", "Data Manutenção", "Valor Manutenção")

    for coluna in tree["columns"]:
        tree.column(coluna, anchor=tk.W, width=100)
        tree.heading(coluna, text=coluna, anchor=tk.W)

    tree.pack(expand=True, fill="both", padx=10, pady=10)

    entry_pesquisa = tk.Entry(root, width=20)
    entry_pesquisa.pack(side=tk.LEFT, padx=5, pady=5)

    btn_pesquisar = tk.Button(root, text="Pesquisar",
                              command=lambda: pesquisar_cliente(tree, entry_pesquisa.get(), tipo_pesquisa_var.get()))
    btn_pesquisar.pack(side=tk.LEFT, padx=5)

    tipo_pesquisa_var = tk.StringVar()
    tipo_pesquisa_var.set("nome")

    radio_nome = tk.Radiobutton(root, text="Pesquisar por Nome", variable=tipo_pesquisa_var, value="nome", bg="#F0F0F0")
    radio_nome.pack(side=tk.LEFT, padx=5)

    radio_data = tk.Radiobutton(root, text="Pesquisar por Data", variable=tipo_pesquisa_var, value="data", bg="#F0F0F0")
    radio_data.pack(side=tk.LEFT, padx=5)

    radio_manu = tk.Radiobutton(root, text="Pesquisar por manutenção", variable=tipo_pesquisa_var, value="manu", bg="#F0F0F0")
    radio_manu.pack(side=tk.LEFT, padx=5)

    btn_excluir = tk.Button(root, text="Excluir Cliente", command=lambda: excluir_selecionado(tree), bg="#FF4040")
    btn_excluir.pack(side=tk.LEFT, padx=5)

    btn_editar = tk.Button(root, text="Editar Cliente", command=lambda: editar_selecionado(tree), bg="#3CB371")
    btn_editar.pack(side=tk.LEFT, padx=5)

    btn_atualizar = tk.Button(root, text="Atualizar Tabela", command=lambda: atualizar_tabela(tree), bg="#87CEEB")
    btn_atualizar.pack(side=tk.RIGHT, padx=5)

    btn_adicionar = tk.Button(root, text="Adicionar Cliente", command=lambda: adicionar_cliente(tree), bg="#FFD700")
    btn_adicionar.pack(side=tk.LEFT, padx=5)

    try:
        atualizar_tabela(tree)
    except Exception as e:
        print(f"Erro ao atualizar a tabela: {e}")

    root.mainloop()


def excluir_selecionado(tree):
    selecionado = tree.selection()
    if selecionado:
        resposta = messagebox.askyesno("Confirmação", "Tem certeza que deseja excluir o cliente selecionado?")
        if resposta:
            id_cliente = tree.item(selecionado)["values"][0]
            excluir_cliente(id_cliente, tree)
    else:
        messagebox.showwarning("Aviso", "Selecione um cliente para excluir.")


def editar_selecionado(tree):
    selecionado = tree.selection()
    if selecionado:
        id_cliente = tree.item(selecionado)["values"][0]
        editar_cliente(tree, id_cliente)
    else:
        messagebox.showwarning("Aviso", "Selecione um cliente para editar.")


if __name__ == "__main__":
    exibir_tabela()
