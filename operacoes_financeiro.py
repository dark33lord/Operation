import tkinter as tk
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk

def centralizar_janela(root, largura, altura):
    # Obtém a largura e altura da tela
    largura_tela = root.winfo_screenwidth()
    altura_tela = root.winfo_screenheight()

    # Calcula a posição x e y para centralizar a janela
    x = (largura_tela // 2) - (largura // 2)
    y = (altura_tela // 2) - (altura // 2)

    # Define a geometria da janela
    root.geometry(f'{largura}x{altura}+{x}+{y}')
    root.resizable(False, False)  # Desabilita o redimensionamento

def sobre():
    messagebox.showinfo("Sobre", "Versão 1.5\nPowered by Marcelo Costa")

def atualizar_mensagem(mensagem):
    label_progresso.config(text=mensagem)
    root.update_idletasks()

def tratamento_txt():
    arquivo = filedialog.askopenfilename(title="Selecione o arquivo")
    abrir_arquivo = open(arquivo, 'r')
    linhas = abrir_arquivo.readlines()
    abrir_arquivo.close()
    
    root_texto = tk.Tk()
    root_texto.title("Tratamento de TXT")

    centralizar_janela(root_texto, 200, 100)

    label = tk.Label(root_texto, text="Texto a ser procurado")
    label.pack()

    entry = tk.Entry(root_texto)
    entry.pack()

    button = tk.Button(root_texto, text="Enviar", command=root_texto.quit)
    button.pack()
    root_texto.mainloop()
    texto_procurado = entry.get()
    root_texto.destroy()

    texto_modificado = []

    arquivo2 = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt"), ("All files", "*.*")], title="Salvar Arquivo")

    for linha in linhas:
        if texto_procurado not in linha:
            texto_modificado.append(linha)

    salvar_arquivo = open(arquivo2, 'w')
    salvar_arquivo.writelines(texto_modificado)
    salvar_arquivo.close()    



# Configuração da interface Tkinter
root = tk.Tk()
root.title("Operações - American Pet")

centralizar_janela(root, 400, 200)

menu = tk.Menu(root)
root.config(menu=menu)

submenu = tk.Menu(menu, tearoff=0)
menu.add_cascade(label="Operações", menu=submenu)

# Submenu de Financeiro
financeiro_menu = tk.Menu(submenu, tearoff=0)
financeiro_menu.add_command(label="Tratamento TXT", command=tratamento_txt)
submenu.add_cascade(label="Financeiro", menu=financeiro_menu)

submenu3 = tk.Menu(menu, tearoff=0)
menu.add_cascade(label="Sobre", menu=submenu3)
submenu3.add_command(label="Sobre", command=sobre)

menu.add_command(label="Sair", command=root.quit)

rodape = tk.Label(root, text="Tecnologia - American Pet", bd=1, relief=tk.SUNKEN, anchor=tk.W)
rodape.pack(side=tk.BOTTOM, fill=tk.X)

imagem = Image.open("C:/Operation/bg.png")
imagem = imagem.resize((150, 100), Image.LANCZOS)
imagem_tk = ImageTk.PhotoImage(imagem)

label_imagem = tk.Label(root, image=imagem_tk)
label_imagem.pack(expand=True, fill=tk.BOTH)

label_progresso = tk.Label(root, text="Status")
label_progresso.pack(pady=20)

icone = Image.open("C:/Operation/bg.png")
icone_tk = ImageTk.PhotoImage(icone)
root.iconphoto(True, icone_tk)

root.mainloop()