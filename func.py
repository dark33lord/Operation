from tkinter import messagebox, filedialog

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

def limpar_caracteres_invalidos(df):
    return df.applymap(lambda x: ''.join([i if i.isprintable() else '' for i in str(x)]))

def salvar_arquivo(df):
    arquivo = filedialog.asksaveasfilename(defaultextension=".xlsx", 
                                           filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
                                           title="Salvar arquivo como")
    if arquivo:
        try:
            df_limpo = limpar_caracteres_invalidos(df)
            df_limpo.to_excel(arquivo, index=False)
            messagebox.showinfo("Sucesso", f"Arquivo gerado com sucesso: {arquivo}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar o arquivo: {e}")
            print(f"Erro ao salvar o arquivo: {e}")

def sobre():
    messagebox.showinfo("Sobre", "Versão 1.6\nPowered by Marcelo Costa")

def atualizar_mensagem(root, label_progresso, mensagem):
    label_progresso.config(text=mensagem)
    root.update_idletasks()