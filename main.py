from func import centralizar_janela, salvar_arquivo, sobre, atualizar_mensagem
import tkinter as tk
from tkinter import messagebox, filedialog
from tkcalendar import DateEntry
import pandas as pd
from sqlalchemy import create_engine, text
from PIL import Image, ImageTk
from dotenv import load_dotenv
import os

load_dotenv()
db_erp = os.getenv('DB_ERP')
conexao_sqlalchemy = create_engine(db_erp)

def compras():
    try:
        # Configuração da interface Tkinter para seleção de datas
        root_data = tk.Tk()
        root_data.title("Seleção de Datas")

        centralizar_janela(root_data, 150, 200)

        tk.Label(root_data, text="Data Inicial").pack(pady=5)
        date_entry_inicial = DateEntry(root_data, date_pattern='yyyy-mm-dd')
        date_entry_inicial.pack(pady=5)

        tk.Label(root_data, text="Data Final").pack(pady=5)
        date_entry_final = DateEntry(root_data, date_pattern='yyyy-mm-dd')
        date_entry_final.pack(pady=5)

        def execucao():
            data_inicial = date_entry_inicial.get()
            data_final = date_entry_final.get()
            root_data.quit()
            root_data.destroy()
            atualizar_mensagem(root, label_progresso, "Gerando Arquivo...")

            query = f"""
            SELECT 
                de.num_doc AS 'NFe', 
                pe.nome  AS 'Fornecedor', 
                de.dt_doc AS 'Data Compra', 
                c.hierarquia_nome AS 'Categoria', 
                di.nome AS 'Descrição do produto', 
                di.quantidade_comercial AS 'Quantidade',
                di.valor_unit_tributavel_escriturado AS 'valor unitário', 
                di.valor_total_escriturado AS 'Total', 
                pp.nome AS 'Perfil comprador'
            FROM 
                ideiaerp.documentonferecebido de
            INNER JOIN 
                ideiaerp.documentonferecebidoitem di ON(di.documentonferecebido_id = de.documentonferecebido_id)
            INNER JOIN 
                ideiaerp.pessoa pe ON(pe.pessoa_id = de.pessoa_emitente_id)
            INNER JOIN 
                ideiaerp.produto p ON(p.produto_id = di.produto_id)
            INNER JOIN 
                ideiaerp.categoria c ON(c.categoria_id = p.categoria_id)    
            INNER JOIN 
                ideiaerp.perfilcomprador pp ON(pp.perfilcomprador_id = c.perfilcomprador_id)
            WHERE
                de.naturezaoperacao_id ='FEBA77D7-6E63-4854-8B22-B5C390B33F68' and     
                coalesce(de.flagexcluido,0)=0  and
                coalesce(de.flagcancelado,0)=0  and
                de.dt_doc BETWEEN '{data_inicial}' AND '{data_final}'
                ORDER BY de.documentonferecebido_id, di.numero_item;"""
            
            with conexao_sqlalchemy.connect() as conexao:
                resultado = conexao.execute(text(query))
                df = pd.DataFrame(resultado.fetchall(), columns=resultado.keys())

            salvar_arquivo(df)

        btn_obter_datas = tk.Button(root_data, text="Enviar", command=execucao)
        btn_obter_datas.pack(pady=20)
        root_data.mainloop()
        atualizar_mensagem(root, label_progresso, "Aguardando Operação")

    except Exception as e:
        messagebox.showerror("Erro", f"Erro na operação de Compras: {e}")

def vendas():
    try:        
        # Configuração da interface Tkinter para seleção de datas
        root_data = tk.Tk()
        root.title("Seleção de Datas")

        centralizar_janela(root_data, 150, 200)

        tk.Label(root_data, text="Data Inicial").pack(pady=5)
        date_entry_inicial = DateEntry(root_data, date_pattern='yyyy-mm-dd', locale='pt_BR')
        date_entry_inicial.pack(pady=5)

        tk.Label(root_data, text="Data Final").pack(pady=5)
        date_entry_final = DateEntry(root_data, date_pattern='yyyy-mm-dd', locale='pt_BR')
        date_entry_final.pack(pady=5)

        def execucao():
            data_inicial = date_entry_inicial.get()
            data_final = date_entry_final.get()
            root_data.quit()
            root_data.destroy()
            atualizar_mensagem(root, label_progresso, "Gerando Arquivo...")
            query = f"""
            SELECT
                  e.empresa_nome,
                  de.num_doc AS 'NF',
                  de.dt_doc AS 'Data',
                  c.hierarquia_nome AS 'Categoria',
                  COALESCE(di.codigo, di.ean_comercial) AS 'Cod/EAN',
                  di.nome AS 'Descrição do produto',
                  SUM(di.quantidade_comercial) AS 'Quantidade',	
                  di.valor_unit_comercial AS 'valor unitário',
                  SUM(di.quantidade_comercial * di.valor_unit_comercial) AS 'Total'
                FROM
                  ideiaerp.documentonfe de
                INNER JOIN 
                  ideiaerp.documentonfeitem di ON (di.documentonfe_id = de.documentonfe_id)
                INNER JOIN ideiaerp.produto p ON
                  (p.produto_id = di.produto_id)
                LEFT JOIN ideiaerp.empresa e ON
                  (e.empresa_id = de.empresa_id)
                LEFT JOIN ideiaerp.categoria c ON
                  (c.categoria_id = p.categoria_id)
                WHERE
                  de.naturezaoperacao_id = 'DBA758CC-2E10-4F1A-9455-6E1DD67ADA1B'
                  AND 	
                  COALESCE(de.flagexcluido, 0)= 0
                  AND
                  COALESCE(de.flagcancelado, 0)= 0
                  AND
                  de.dt_doc BETWEEN '{data_inicial}' AND '{data_final}'
                GROUP BY
                  de.empresa_id,
                  di.produto_id
                ORDER BY
                  e.empresa_nome,
                  di.produto_id;"""
            
            df = pd.read_sql(query, conexao_sqlalchemy)
            salvar_arquivo(df)

        btn_obter_datas = tk.Button(root_data, text="Enviar", command=execucao)
        btn_obter_datas.pack(pady=20)
        root.mainloop()
        atualizar_mensagem(root, label_progresso, "Aguardando Operação")

    except Exception as e:
        messagebox.showerror("Erro", f"Erro na operação de Vendas: {e}")

def pagmaquininhas():
    try:      
        # Configuração da interface Tkinter para seleção de datas
        root_data = tk.Tk()
        root.title("Seleção de Datas")

        centralizar_janela(root_data, 150, 200)

        tk.Label(root_data, text="Data Inicial").pack(pady=5)
        date_entry_inicial = DateEntry(root_data, date_pattern='yyyy-mm-dd', locale='pt_BR')
        date_entry_inicial.pack(pady=5)

        tk.Label(root_data, text="Data Final").pack(pady=5)
        date_entry_final = DateEntry(root_data, date_pattern='yyyy-mm-dd', locale='pt_BR')
        date_entry_final.pack(pady=5)

        def execucao():
            data_inicial = date_entry_inicial.get()
            data_final = date_entry_final.get()
            root_data.quit()
            root_data.destroy()
            atualizar_mensagem(root, label_progresso, "Gerando Arquivo...")
            query = f"""
                SELECT
                    dc.documentoconvenio_id,
                    dc.datalancamento,
                    pe.codigo codigo_empresa,
                    pe.nome nome_empresa,
                    cc.codigo codigo_contrato,
                    cc.nome nome_contrato, 
                    b.nome nome_bandeira,
                    dc.codigoautorizacao, 
                    CASE 
                    WHEN dc.flagtipopagamento = 0 THEN 'Débito'
                    WHEN dc.flagtipopagamento = 1 THEN 'Crédito Rotativo'
                    WHEN dc.flagtipopagamento = 2 THEN 'Crédito Parcelado'
                    END tipo,
                    CONCAT_WS('/', dcp.parcela, dc.parcelaspagamento) AS parcelamento, 
                    dc.nomerede,
                    dc.nomeautorizadora,
                    dc.aliquotaretencao,
                    dc.nsu,
                    dc.valortotal,
                    dcp.datavencimento, 
                    dcp.valorbrutoparcela,
                    dcp.valorretencaoparcela,
                    dcp.valorliquidoparcela
                FROM
                    ideiaerp.documentoconvenio dc
                INNER JOIN ideiaerp.documentoconvenioparcela dcp ON
                    (dc.documentoconvenio_id = dcp.documentoconvenio_id)
                INNER JOIN ideiaerp.empresa e ON
                    (e.empresa_id = dc.empresa_id)
                INNER JOIN ideiaerp.pessoa pe ON
                    (e.pessoa_id = pe.pessoa_id)
                LEFT JOIN ideiaerp.pessoa p ON
                    (p.pessoa_id = dc.pessoa_id)
                LEFT JOIN ideiaerp.contratoconvenio cc ON
                    (cc.contratoconvenio_id = dc.contratoconvenio_id)
                LEFT JOIN ideiaerp.bandeiraconvenio b ON
                    (dc.bandeiraconvenio_id = b.bandeiraconvenio_id)
                WHERE
                    (1 = 1)
                    AND dc.datalancamento BETWEEN '{data_inicial}' AND '{data_final}'
                    AND (COALESCE(dcp.flagquitado, '0') = '0') 
                    AND (COALESCE(dc.flagcancelado,'0') ='0')
                ORDER BY e.empresa_nome, dc.datalancamento;"""
            
            df = pd.read_sql(query, conexao_sqlalchemy)
            salvar_arquivo(df)

        btn_obter_datas = tk.Button(root_data, text="Enviar", command=execucao)
        btn_obter_datas.pack(pady=20)
    
        root.mainloop()
        atualizar_mensagem(root, label_progresso, "Aguardando Operação")

    except Exception as e:
        messagebox.showerror("Erro", f"Erro na operação de Pagamento de Maquininhas: {e}")

def despesas():
    try:       
        # Configuração da interface Tkinter para seleção de datas
        root_data = tk.Tk()
        root.title("Seleção de Datas")

        centralizar_janela(root_data, 150, 200)

        tk.Label(root_data, text="Data Inicial").pack(pady=5)
        date_entry_inicial = DateEntry(root_data, date_pattern='yyyy-mm-dd', locale='pt_BR')
        date_entry_inicial.pack(pady=5)

        tk.Label(root_data, text="Data Final").pack(pady=5)
        date_entry_final = DateEntry(root_data, date_pattern='yyyy-mm-dd', locale='pt_BR')
        date_entry_final.pack(pady=5)

        def execucao():
            data_inicial = date_entry_inicial.get()
            data_final = date_entry_final.get()
            root_data.quit()
            root_data.destroy()
            atualizar_mensagem(root, label_progresso, "Gerando Arquivo...")
            query = f"""
                SELECT
                    e.empresa_nome AS 'Filial',
                    t.numerodocumento,
                    t.datadocumento,
                    pe.cnpj,
                    p.nome,
                    t.datacompetencia,
                    c.nome 'Centro de custo', 
                        pl.nome AS 'Plano de Conta',
                    t.datavencimento AS 'Data Vencimento',
                    COALESCE(t.valor, 0) AS 'Valor'
                FROM
                    ideiaerp.titulopagar t
                LEFT JOIN ideiaerp.empresa e ON
                    (e.empresa_id = t.empresa_id)
                LEFT JOIN ideiaerp.pessoa p ON
                    (p.pessoa_id = t.pessoa_id)
                LEFT JOIN ideiaerp.pessoa pe ON
                    (pe.pessoa_id = e.pessoa_id)
                LEFT JOIN ideiaerp.planodeconta pl ON
                    (pl.planodeconta_id = t.planodeconta_id)
                LEFT JOIN ideiaerp.centrodecusto c ON
                    (c.centrodecusto_id = t.centrodecusto_id)
                WHERE
                    (1 = 1)
                    AND COALESCE(t.flagcancelado, 0)= 0
                    AND COALESCE(t.flagexcluido, 0)= 0
                    AND t.datavencimento BETWEEN '{data_inicial}' AND '{data_final}'
                    AND t.planodeconta_id <> 'E6892FEC-DBEF-4704-99EE-462A0F687F1E'
                ORDER BY
                    e.empresa_nome,
                    t.datavencimento;"""
            
            df = pd.read_sql(query, conexao_sqlalchemy)
            salvar_arquivo(df)

        btn_obter_datas = tk.Button(root_data, text="Enviar", command=execucao)
        btn_obter_datas.pack(pady=20)
        
        
        root.mainloop()
        atualizar_mensagem(root, label_progresso, "Aguardando Operação")

    except Exception as e:
        messagebox.showerror("Erro", f"Erro na operação de Despesas: {e}")

def rma():
    try:        
        # Configuração da interface Tkinter para seleção de datas
        root_data = tk.Tk()
        root.title("Seleção de Datas")

        centralizar_janela(root_data, 150, 200)

        tk.Label(root_data, text="Data Inicial").pack(pady=5)
        date_entry_inicial = DateEntry(root_data, date_pattern='yyyy-mm-dd', locale='pt_BR')
        date_entry_inicial.pack(pady=5)

        tk.Label(root_data, text="Data Final").pack(pady=5)
        date_entry_final = DateEntry(root_data, date_pattern='yyyy-mm-dd', locale='pt_BR')
        date_entry_final.pack(pady=5)

        def execucao():
            data_inicial = date_entry_inicial.get()
            data_final = date_entry_final.get()
            root_data.quit()
            root_data.destroy()
            atualizar_mensagem(root, label_progresso, "Gerando Arquivo...")
            query = f"""
            SELECT
                e.empresa_codigo,
                e.empresa_nome,
                d.dt_doc,
                d.chv_nfe,
                di.codigo,
                di.nome,
                p.codigo destinatario_codigo,
                p.nome destinatario_nome,
                di.quantidade_tributavel,
                di.valor_unit_comercial,
                di.valor_produto,
                f.codigo codigo_fornecedor,
                f.nome nome_fornecedor,
                c.hierarquia_nome categoria,
                pc.nome perfil_comprador
            FROM
                ideiaerp.documentonfe d
            LEFT JOIN ideiaerp.empresa e ON
                (e.empresa_id = d.empresa_id)
            LEFT JOIN ideiaerp.pessoa p ON
                (p.pessoa_id = d.pessoa_destinatario_id)
            LEFT JOIN ideiaerp.documentonfeitem di ON
                (di.documentonfe_id = d.documentonfe_id)
            LEFT JOIN ideiaerp.produto pr ON
                (pr.produto_id = di.produto_id)
            LEFT JOIN ideiaerp.pessoa f ON
                (pr.fornecedor_pessoa_id = f.pessoa_id)
            LEFT JOIN ideiaerp.categoria c ON
                (c.categoria_id = pr.categoria_id)
            LEFT JOIN ideiaerp.perfilcomprador pc ON
                (pc.perfilcomprador_id = c.perfilcomprador_id)
            WHERE
                d.naturezaoperacao_id = '01E2B0B9-2382-4174-9FAC-75E3247C50FD'
                AND d.dt_doc BETWEEN '{data_inicial}' AND '{data_final}'
            ORDER BY
                e.empresa_codigo,
                d.dt_doc"""
            
            df = pd.read_sql(query, conexao_sqlalchemy)
            salvar_arquivo(df)

        btn_obter_datas = tk.Button(root_data, text="Enviar", command=execucao)
        btn_obter_datas.pack(pady=20)
        
        
        root.mainloop()
        atualizar_mensagem(root, label_progresso, "Aguardando Operação")

    except Exception as e:
        messagebox.showerror("Erro", f"Erro na operação de RMA: {e}")

def cmv():
    try:       
        # Configuração da interface Tkinter para seleção de datas
        root_data = tk.Tk()
        root_data.title("Seleção de Datas")

        centralizar_janela(root_data, 150, 200)

        tk.Label(root_data, text="Data Inicial").pack(pady=5)
        date_entry_inicial = DateEntry(root_data, date_pattern='yyyy-mm-dd', locale='pt_BR')
        date_entry_inicial.pack(pady=5)

        tk.Label(root_data, text="Data Final").pack(pady=5)
        date_entry_final = DateEntry(root_data, date_pattern='yyyy-mm-dd', locale='pt_BR')
        date_entry_final.pack(pady=5)

        def execucao():
            data_inicial = date_entry_inicial.get()
            data_final = date_entry_final.get()
            root_data.quit()
            root_data.destroy()

            with conexao_sqlalchemy.connect() as connection:
                #Passo 1 de 14
                atualizar_mensagem(root, label_progresso, "Passo 1 de 14: Excluindo tabela temporária 1...")
                try:
                    drop_table_query = text("DROP TEMPORARY TABLE IF EXISTS ideiaerp.tmp_produto_ultima_compra")
                    connection.execute(drop_table_query)

                except Exception as e:
                    messagebox.showerror("Erro", f"Falha no passo 1: {e}")

                #Passo 2 de 14
                atualizar_mensagem(root, label_progresso, "Passo 2 de 14: Criando tabela temporária 1...") 
                try:
                    create_table_query = text(f"""
                                            CREATE TEMPORARY TABLE ideiaerp.tmp_produto_ultima_compra AS (
                                                SELECT
                                                    di.produto_id,
                                                    max(d.dt_doc) DATA
                                                FROM
                                                    ideiaerp.documentonferecebido d
                                                INNER JOIN ideiaerp.documentonferecebidoitem di ON
                                                    (di.documentonferecebido_id = d.documentonferecebido_id)
                                                WHERE
                                                    d.naturezaoperacao_id = 'FEBA77D7-6E63-4854-8B22-B5C390B33F68'
                                                    AND dt_doc < '{data_inicial}'
                                                    AND di.produto_id IS NOT NULL
                                                    AND d.flagprocessado = '1'
                                                GROUP BY
                                                    di.produto_id);
                                            """)
                    connection.execute(create_table_query)
                    
                except Exception as e:
                    messagebox.showerror("Erro", f"Falha no passo 2: {e}")

                #Passo 3 de 14
                atualizar_mensagem(root, label_progresso, "Passo 3 de 14: Alterando chave primária tabela temporária 1...") 
                try:
                    alter_table_query = text("ALTER TABLE ideiaerp.tmp_produto_ultima_compra ADD PRIMARY KEY (produto_id, DATA)")
                    connection.execute(alter_table_query)
                    
                except Exception as e:
                    messagebox.showerror("Erro", f"Falha no passo 3: {e}")

                #Passo 4 de 14
                atualizar_mensagem(root, label_progresso, "Passo 4 de 14: Excluindo tabela temporária 2...") 
                try:
                    drop_table_query = text("DROP TEMPORARY TABLE IF EXISTS ideiaerp.tmp_ultimacompra")
                    connection.execute(drop_table_query)
                    
                except Exception as e:
                    messagebox.showerror("Erro", f"Falha no passo 4: {e}")

                #Passo 5 de 14
                atualizar_mensagem(root, label_progresso, "Passo 5 de 14: Criando tabela temporária 2...") 
                try:
                    create_table_query = text("""
                          CREATE TEMPORARY TABLE ideiaerp.tmp_ultimacompra AS (
                            SELECT
                                di.produto_id,
                                max(c.data) DATA,
                                pc.flagcreditopiscofins,  
                                    sum(di.valor_total_escriturado) valor_total_calculado,
                                max(di.valor_unit_tributavel_escriturado) valor_unit_tributavel,
                                    sum(di.quantidade_tributavel_escriturada) quantidade_tributavel,
                                sum(di.vl_desc) vl_desc,
                                sum(di.vl_frete) vl_frete, 
                                    sum(di.vl_icms_st) vl_icms_st,
                                sum(di.vl_icmsfecp_st) vl_icmsfecp_st, 
                                    sum(di.vl_ipi) vl_ipi,
                                sum(di.vl_out_da) vl_out_da,
                                sum(di.vl_seg) vl_seg,
                                    max(di.aliq_icms) aliq_icms, 
                                    sum(di.vl_icms) vl_icms,
                                max(di.aliq_icmsfecp) aliq_icmsfecp,
                                sum(di.vl_icmsfecp) vl_icmsfecp,
                                    pc.saida_aliquotapis,
                                pc.saida_aliquotacofins,
                                    IF(sum(di.vl_icms_st)>0,
                                0,
                                1) flagicms
                            FROM
                                ideiaerp.documentonferecebido d
                            INNER JOIN ideiaerp.documentonferecebidoitem di ON
                                (di.documentonferecebido_id = d.documentonferecebido_id)
                            INNER JOIN ideiaerp.produto p ON
                                (p.produto_id = di.produto_id)
                            INNER JOIN ideiaerp.grupoprodutopiscofins pc ON
                                (pc.grupoprodutopiscofins_id = p.grupoprodutopiscofins_id)
                            INNER JOIN ideiaerp.tmp_produto_ultima_compra c ON
                                (c.produto_id = p.produto_id
                                AND c.data = d.dt_doc)
                            WHERE
                                d.naturezaoperacao_id = 'FEBA77D7-6E63-4854-8B22-B5C390B33F68'
                                AND COALESCE(d.flagprocessado, '0')= '1'
                            GROUP BY
                                di.produto_id);
                            """)
      
                    connection.execute(create_table_query)
                    
                except Exception as e:
                    messagebox.showerror("Erro", f"Falha no passo 5: {e}")

                #Passo 6 de 14
                atualizar_mensagem(root, label_progresso, "Passo 6 de 14: Alterando chave primária tabela temporária 2...") 
                try:
                    alter_table_query = text("ALTER TABLE ideiaerp.tmp_ultimacompra ADD PRIMARY KEY (produto_id);")
                    connection.execute(alter_table_query)
                    
                except Exception as e:
                    messagebox.showerror("Erro", f"Falha no passo 6: {e}")

                #Passo 7 de 14
                atualizar_mensagem(root, label_progresso, "Passo 7 de 14: Excluindo tabela temporária 3...")
                try:
                    drop_table_query = text("DROP TEMPORARY TABLE IF EXISTS ideiaerp.tmp_ultimacompra_detalhes")
                    connection.execute(drop_table_query)
                    
                except Exception as e:
                    messagebox.showerror("Erro", f"Falha no passo 7: {e}")

                #Passo 8 de 14
                atualizar_mensagem(root, label_progresso, "Passo 8 de 14: Criando tabela temporária 3...") 
                try:
                    create_table_query = text("""
                                            CREATE TEMPORARY TABLE ideiaerp.tmp_ultimacompra_detalhes AS (
                                                SELECT
                                                    x.produto_id,
                                                    DATA,
                                                    valor_unit_tributavel,
                                                    quantidade_tributavel,
                                                    (valor_unit_tributavel * quantidade_tributavel) total_bruto,
                                                    vl_total,
                                                        vl_total - icms_deduzir valor_sem_icms,
                                                        icms_deduzir icms_rec,
                                                        IF(flagcreditopiscofins = 1,
                                                    (vl_total - icms_deduzir)*(saida_aliquotacofins / 100.00),
                                                    0) cofins_rec,
                                                        IF(flagcreditopiscofins = 1,
                                                    (vl_total - icms_deduzir)*(saida_aliquotapis / 100.00),
                                                    0) pis_rec
                                                FROM
                                                    (
                                                    SELECT
                                                        t.data,
                                                        t.produto_id,
                                                        flagcreditopiscofins,
                                                        saida_aliquotapis,
                                                        saida_aliquotacofins,
                                                        valor_unit_tributavel,
                                                        IF(COALESCE(flagicms, 1)= 1,
                                                        (COALESCE(vl_icms, 0) + COALESCE(vl_icmsfecp, 0)),
                                                        0) icms_deduzir,
                                                        valor_total_calculado vl_total, 
                                                                t.quantidade_tributavel,
                                                                t.valor_total_calculado
                                                    FROM
                                                        ideiaerp.tmp_ultimacompra t ) x );
                                            """)
      
                    connection.execute(create_table_query)
                    
                except Exception as e:
                    messagebox.showerror("Erro", f"Falha no passo 8: {e}") 

                #Passo 9 de 14
                atualizar_mensagem(root, label_progresso, "Passo 9 de 14: Alterando chave primária tabela temporária 3...") 
                try:
                    alter_table_query = text("ALTER TABLE ideiaerp.tmp_ultimacompra_detalhes ADD PRIMARY KEY (produto_id);")
                    connection.execute(alter_table_query)

                except Exception as e:
                    messagebox.showerror("Erro", f"Falha no passo 9: {e}")

                #Passo 10 de 14
                atualizar_mensagem(root, label_progresso, "Passo 10 de 14: Excluindo tabela temporária 4...")
                try:
                    drop_table_query = text("DROP TEMPORARY TABLE IF EXISTS ideiaerp.tmp_bi_custo")
                    connection.execute(drop_table_query)
                    
                except Exception as e:
                    messagebox.showerror("Erro", f"Falha no passo 10: {e}")

                #Passo 11 de 14
                atualizar_mensagem(root, label_progresso, "Passo 11 de 14: Criando tabela temporária 4...") 
                try:
                    create_table_query = text("""
                          CREATE TEMPORARY TABLE ideiaerp.tmp_bi_custo AS (
                            SELECT
                                t.produto_id,
                                ((vl_total - icms_rec - cofins_rec - pis_rec)/ quantidade_tributavel) custo_final
                            FROM
                                ideiaerp.tmp_ultimacompra_detalhes t
                                );
                           """)
      
                    connection.execute(create_table_query)
                    
                except Exception as e:
                    messagebox.showerror("Erro", f"Falha no passo 11: {e}")

                #Passo 12 de 14
                atualizar_mensagem(root, label_progresso, "Passo 12 de 14: Alterando chave primária tabela temporária 4...") 
                try:
                    alter_table_query = text("ALTER TABLE ideiaerp.tmp_bi_custo ADD PRIMARY KEY(produto_id);")
                    connection.execute(alter_table_query)

                except Exception as e:
                    messagebox.showerror("Erro", f"Falha no passo 12: {e}") 

                #Passo 13 de 14
                atualizar_mensagem(root, label_progresso, "Passo 13 de 14: Excluindo tabela temporária 5...")
                try:
                    drop_table_query = text("DROP TABLE IF EXISTS ideiaerp.tmp_cmv_resultfinal")
                    connection.execute(drop_table_query)
                    
                except Exception as e:
                    messagebox.showerror("Erro", f"Falha no passo 13: {e}")

                #Passo 14 de 14
                atualizar_mensagem(root, label_progresso, "Passo 14 de 14: Criando tabela temporária 5...") 
                try:
                    create_table_query = text(f"""
                                            CREATE TABLE ideiaerp.tmp_cmv_resultfinal AS (
                                                SELECT
                                                    dn.empresa_id,
                                                    sum(di.valor_unit_tributavel * di.quantidade_tributavel) valor_subtotal,
                                                    sum(di.vl_frete + di.vl_out_da) valor_acrescimo_sobre_total,
                                                    sum(di.vl_desc) valor_desconto_sobre_total,
                                                    sum((di.valor_unit_tributavel * di.quantidade_tributavel) + 
                                                        COALESCE(di.vl_frete, 0) - 
                                                        COALESCE(di.vl_desc, 0) + 
                                                        COALESCE(di.vl_seg, 0) + 
                                                        COALESCE(di.vl_out_da, 0) + 
                                                        COALESCE(di.vl_icms_st, 0) + 
                                                        COALESCE(di.vl_icmsfecp_st, 0) + 
                                                        COALESCE(di.vl_ipi, 0)) valor_faturamento,
                                                        sum(quantidade_tributavel * custo.custo_final) custo_sem_impostos,
                                                        sum(di.vl_icms) vl_icms, 
                                                        sum(di.vl_icmsfecp) vl_icmsfecp,
                                                        sum(di.vl_pis) vl_pis,
                                                        sum(di.vl_cofins) vl_cofins
                                                FROM
                                                    ideiaerp.documentonfe dn
                                                INNER JOIN ideiaerp.naturezaoperacao n ON
                                                    (dn.naturezaoperacao_id = n.naturezaoperacao_id)
                                                INNER JOIN ideiaerp.documentonfeitem di ON
                                                    (di.documentonfe_id = dn.documentonfe_id)
                                                LEFT JOIN ideiaerp.tmp_bi_custo custo ON
                                                    (custo.produto_id = di.produto_id)
                                                WHERE
                                                    n.flagtipooperacao = '1'
                                                    AND n.naturezaoperacao_id = 'DBA758CC-2E10-4F1A-9455-6E1DD67ADA1B'
                                                    AND dn.dt_doc >= '{data_inicial}'
                                                    AND dn.dt_doc <= '{data_final}'
                                                    AND dn.codigoretorno IN ('100', '150')
                                                GROUP BY
                                                    dn.empresa_id
                                                    );
                                                """)
                        
                    connection.execute(create_table_query)
                    
                except Exception as e:
                    messagebox.showerror("Erro", f"Falha no passo 14: {e}")


                try: 
                    query = f"""
                        SELECT
                            e.empresa_codigo,
                            e.empresa_nome,
                            t.valor_faturamento, 
                            t.vl_icms,
                            t.vl_icmsfecp, 
                            t.vl_pis,
                            t.vl_cofins,
                            CAST(t.custo_sem_impostos AS decimal(15, 4)) cmv_calculado
                        FROM
                            ideiaerp.tmp_cmv_resultfinal t
                        INNER JOIN ideiaerp.empresa e ON
                            (e.empresa_id = t.empresa_id)
                        ORDER BY
                            e.empresa_codigo;
                            """
            
                    df = pd.read_sql(query, conexao_sqlalchemy)
                    salvar_arquivo(df)

                except Exception as e:
                    messagebox.showerror("Erro", f"Falha ao exportar o arquivo: {e}")

                atualizar_mensagem(root, label_progresso, "Processo concluído com sucesso!")

        btn_obter_datas = tk.Button(root_data, text="Enviar", command=execucao)
        btn_obter_datas.pack(pady=20)
        
        
        
        root.mainloop()
        atualizar_mensagem(root, label_progresso, "Aguardando Operação")
        
    except Exception as e:
        messagebox.showerror("Erro", f"Erro na operação de RMA: {e}")

def vendas_delivery():

    try:
        root = tk.Tk()
        root.title("Seleção de data")

        centralizar_janela(root, 200, 250)

        tk.Label(root, text="Data Inicial").pack(pady=5)
        date_entry_inicial = DateEntry(root, date_pattern='yyyy-mm-dd', locale='pt_BR')
        date_entry_inicial.pack(pady=5)

        tk.Label(root, text="Data Final").pack(pady=5)
        date_entry_final = DateEntry(root, date_pattern='yyyy-mm-dd', locale='pt_BR')
        date_entry_final.pack(pady=5)

        def execucao():
            data_inicial = date_entry_inicial.get()
            data_final = date_entry_final.get()
            root.quit()
            root.destroy()
            atualizar_mensagem(root, label_progresso, "Gerando Arquivo...")
            query = f"""
                    SELECT 
                        e.empresa_codigo,
                        e.empresa_nome,
                        m.`data`,
                        m.numeromovimento, 
                        m.nomepessoa,
                        m.cpfcnpjpessoa,
                        p.eantributavel,
                        mp.nomeproduto, 
                        mp.valorunitariotributario AS valor,
                        mp.quantidadetributaria AS quantidade, 
                        mp.valortotal
                    FROM 
                        ideiaerp.movimentosaida m
                    INNER JOIN ideiaerp.movimentosaidaproduto mp ON 
                        mp.movimentosaida_id = m.movimentosaida_id
                    LEFT JOIN ideiaerp.empresa e ON 
                        e.empresa_id = m.empresa_id
                    LEFT JOIN ideiaerp.produto p ON 
                        p.produto_id = mp.produto_id
                    WHERE 
                        (m.lojavirtual_id IS NULL OR m.lojavirtual_id = '')
                        AND m.flagentrega = 1
                        AND m.datacadastro >= '{data_inicial}'  -- Ajustar conforme necessário
                        AND m.datacadastro <= '{data_final}'  -- Ajustar conforme necessário
                        AND coalesce(mp.flagcancelado,0) <> 1 
                    ORDER BY 
                        e.empresa_codigo, m.numeromovimento, m.`data`;
                    """
            df = pd.read_sql(query, conexao_sqlalchemy)
            salvar_arquivo(df)

        btn_obter_datas = tk.Button(root, text="Enviar", command=execucao)
        btn_obter_datas.pack(pady=20)
        root.mainloop()
        atualizar_mensagem(root, label_progresso, "Aguardando...")

    except Exception as e:
        messagebox.showerror("Erro", f"Erro na operação de Vendas Delivery: {e}")

def rma_fiscal():

    try:
        atualizar_mensagem("Gerando Arquivo...")

        query = f"""
                SELECT 
                    dn.dt_doc, 
                    dn.num_doc, 
                    p.codigo, 
                    p.nome, 
                    dni.quantidade_comercial,
                    dni.valor_produto
                FROM 
                    ideiaerp.documentonfeitem dni
                INNER JOIN ideiaerp.produto p ON 
                    (p.produto_id = dni.produto_id)
                INNER JOIN ideiaerp.documentonfe dn ON 
                    (dn.documentonfe_id = dni.documentonfe_id)
                WHERE 
                    dn.naturezaoperacao_id = '3A62BC42-0636-4962-ACA1-EB080DAB1EB7'
                    AND p.fornecedor_pessoa_id = '65BED91F-2726-4ACA-AA6F-92FC61BFCBE9'
                    AND dn.dt_doc >= '2024-01-01'
                    AND dn.codigoretorno = '100'
                ORDER BY dn.dt_doc
                """
        df = pd.read_sql(query, conexao_sqlalchemy)
        salvar_arquivo(df)

        root.mainloop()
        atualizar_mensagem("Aguardando...")

    except Exception as e:
        messagebox.showerror("Erro", f"Erro na operação de Vendas Delivery: {e}")

def clientes_delivery():

    try: 
        atualizar_mensagem("Gerando Arquivo...")

        query = f"""
                SELECT 
                    p.codigo,
                    p.nome,
                    p.endereco,
                    p.endereconumero,
                    p.enderecobairro,
                    p.telefone,
                    p.telefonecontato,
                    p.emailcontato,
                    c.nome AS cidade,
                    p.uf,
                    p.emailecommerce
                FROM ideiaerp.pessoa p
                INNER JOIN ideiaerp.movimentosaida m ON p.pessoa_id = m.pessoa_id
                LEFT JOIN ideiaerp.cidade c ON c.cidade_id = p.cidade_id
                WHERE 
                    (m.lojavirtual_id IS NULL OR m.lojavirtual_id = '')
                    AND m.flagentrega = 1
                    AND p.flagcliente = 1
                    AND p.flagexcluido <> 1
                    AND p.flagempresa  <> 1
                    AND p.nome IS NOT null
                GROUP BY p.pessoa_id 

                ORDER BY p.nome, p.codigo;
                """
        df = pd.read_sql(query, conexao_sqlalchemy)
        salvar_arquivo(df)

        root.mainloop()
        atualizar_mensagem("Aguardando...")

    except Exception as e:
        messagebox.showerror("Erro", f"Erro na operação de Clientes Delivery: {e}")
        print(f"Erro na operação de Clientes Delivery: {e}")

def lojas_dados():

    try:
        atualizar_mensagem(root, label_progresso, "Gerando Arquivo...")
        query = f"""
                SELECT 
                    b.codigo,
                    b.nome,
                    b.endereco, 
                    b.endereconumero as numero,
                    b.enderecocep as CEP,
                    b.enderecobairro as bairro,
                    e.nome as cidade,
                    b.uf,
                    c.nome as tamanho,
                    d.nome as qualidade,
                    a.pessoa_id,
                    a.empresa_id
                FROM 
                    ideiaerp.empresa a
                LEFT JOIN ideiaerp.pessoa b ON 
                    a.pessoa_id = b.pessoa_id
                LEFT JOIN ideiaerp.perfiltamanho c ON 
                    a.perfil_tamanho = c.codigo
                LEFT JOIN ideiaerp.perfilqualidade d ON 
                    a.perfil_qualidade = d.codigo
                LEFT JOIN ideiaerp.cidade e ON 
                    b.cidade_id = e.cidade_id 
                WHERE 
                    b.codigo NOT IN (100, 1000, 000064)
                ORDER BY 
                    b.codigo
                """
        with conexao_sqlalchemy.connect() as conn:
            resultado = conn.execute(text(query))
            df = pd.DataFrame(resultado.fetchall(), columns=resultado.keys())

        salvar_arquivo(df)

        root.mainloop()
        atualizar_mensagem(root, label_progresso, "Aguardando...")

    except Exception as e:
        messagebox.showerror("Erro", f"Erro na operação de Lojas dados: {e}")

def vendas_fornecedor():
    
    try:
        atualizar_mensagem(root, label_progresso, "Gerando Arquivo...")

         # Configuração da interface Tkinter para seleção de datas
        root_data = tk.Tk()
        root.title("Seleção de Datas")

        centralizar_janela(root_data, 150, 250)

        tk.Label(root_data, text="Data Inicial").pack(pady=5)
        date_entry_inicial = DateEntry(root_data, date_pattern='yyyy-mm-dd', locale='pt_BR')
        date_entry_inicial.pack(pady=5)

        tk.Label(root_data, text="Data Final").pack(pady=5)
        date_entry_final = DateEntry(root_data, date_pattern='yyyy-mm-dd', locale='pt_BR')
        date_entry_final.pack(pady=5)

        tk.Label(root_data, text="Fornecedor").pack(pady=5)
        fornecedor_entry = tk.Entry(root_data)
        fornecedor_entry.pack(pady=5)

        def execucao():
            data_inicial = date_entry_inicial.get()
            data_final = date_entry_final.get()
            fornecedor = fornecedor_entry.get()
            root_data.quit()
            root_data.destroy()
            query = f"""
            SELECT
                  e.empresa_nome,
                  de.dt_doc AS 'Data',
                  COALESCE(di.codigo, di.ean_comercial) AS 'Cod/EAN',
                  di.nome AS 'Descrição do produto',
                  SUM(di.quantidade_comercial) AS 'Quantidade',	
                  di.valor_unit_comercial AS 'valor unitário',
                  SUM(di.quantidade_comercial * di.valor_unit_comercial) AS 'Total'
                FROM
                  ideiaerp.documentonfe de
                INNER JOIN 
                  ideiaerp.documentonfeitem di ON (di.documentonfe_id = de.documentonfe_id)
                INNER JOIN ideiaerp.produto p ON
                  (p.produto_id = di.produto_id)
                LEFT JOIN ideiaerp.empresa e ON
                  (e.empresa_id = de.empresa_id)
                WHERE
                  de.naturezaoperacao_id = 'DBA758CC-2E10-4F1A-9455-6E1DD67ADA1B'
                  AND 	
                  COALESCE(de.flagexcluido, 0)= 0
                  AND
                  COALESCE(de.flagcancelado, 0)= 0
                  AND
                  de.dt_doc BETWEEN '{data_inicial}' AND '{data_final}'
                  AND
                  p.fornecedor_pessoa_id =  '{fornecedor}'
                  AND

                GROUP BY
                  de.empresa_id,
                  di.produto_id
                ORDER BY
                  e.empresa_nome,
                  di.produto_id;"""
            
            
            df = pd.read_sql(query, conexao_sqlalchemy)
            salvar_arquivo(df)
            atualizar_mensagem(root, label_progresso, "Aguardando Operação")
        
        btn_obter_datas = tk.Button(root_data, text="Enviar", command=execucao)
        btn_obter_datas.pack(pady=20)
        root.mainloop()       

    except Exception as e:
        messagebox.showerror("Erro", f"Erro na operação de Vendas fornecedor: {e}")

def vendas_grandfood():
    try:

        # Configuração da interface Tkinter para seleção de datas
        root_data = tk.Tk()
        root.title("Seleção de Datas")

        centralizar_janela(root_data, 150, 200)

        tk.Label(root_data, text="Data Inicial").pack(pady=5)
        date_entry_inicial = DateEntry(root_data, date_pattern='yyyy-mm-dd', locale='pt_BR')
        date_entry_inicial.pack(pady=5)

        tk.Label(root_data, text="Data Final").pack(pady=5)
        date_entry_final = DateEntry(root_data, date_pattern='yyyy-mm-dd', locale='pt_BR')
        date_entry_final.pack(pady=5)

        def execucao():
            data_inicial = date_entry_inicial.get()
            data_final = date_entry_final.get()
            root_data.quit()
            root_data.destroy()
            atualizar_mensagem(root, label_progresso, "Gerando Arquivo...")
            query = f"""
            SELECT
                  e.empresa_nome,
                  de.num_doc AS 'NF',
                  de.dt_doc AS 'Data',
                  c.hierarquia_nome AS 'Categoria',
                  COALESCE(di.codigo, di.ean_comercial) AS 'Cod/EAN',
                  di.nome AS 'Descrição do produto',
                  SUM(di.quantidade_comercial) AS 'Quantidade',	
                  di.valor_unit_comercial AS 'valor unitário',
                  SUM(di.quantidade_comercial * di.valor_unit_comercial) AS 'Total',
                  p.pesoliquido,
	              p.pesobruto,
                  p2.nome AS 'Fornecedor'
                FROM
                  ideiaerp.documentonfe de
                INNER JOIN 
                  ideiaerp.documentonfeitem di ON (di.documentonfe_id = de.documentonfe_id)
                INNER JOIN ideiaerp.produto p ON
                  (p.produto_id = di.produto_id)
                LEFT JOIN ideiaerp.empresa e ON
                  (e.empresa_id = de.empresa_id)
                LEFT JOIN ideiaerp.categoria c ON
                  (c.categoria_id = p.categoria_id)
                LEFT JOIN ideiaerp.pessoa p2 ON
                  (p2.pessoa_id = p.fornecedor_pessoa_id)
                WHERE
                  de.naturezaoperacao_id = 'DBA758CC-2E10-4F1A-9455-6E1DD67ADA1B'
                  AND 	
                  COALESCE(de.flagexcluido, 0)= 0
                  AND
                  COALESCE(de.flagcancelado, 0)= 0
                  AND
	              p2.pessoa_id = '2F2D3278-98C9-438F-90A8-FDF4EF6BFE8E'
                  AND
                  de.dt_doc BETWEEN '{data_inicial}' AND '{data_final}'
                GROUP BY
                  de.empresa_id,
                  di.produto_id
                ORDER BY
                  e.empresa_nome,
                  di.produto_id;"""
            df = pd.read_sql(query, conexao_sqlalchemy)
            salvar_arquivo(df)

        btn_obter_datas = tk.Button(root_data, text="Enviar", command=execucao)
        btn_obter_datas.pack(pady=20)
        contador = 0
        root.mainloop()
        atualizar_mensagem(root, label_progresso, "Aguardando Operação")

    except Exception as e:
        messagebox.showerror("Erro", f"Erro na operação de Vendas: {e}")

#teste 2
def teste_sql():
    try:

        # Configuração da interface Tkinter para seleção de datas
        root_data = tk.Tk()
        root.title("Seleção de Datas")

        centralizar_janela(root_data, 150, 200)

        tk.Label(root_data, text="Data Inicial").pack(pady=5)
        date_entry_inicial = DateEntry(root_data, date_pattern='yyyy-mm-dd', locale='pt_BR')
        date_entry_inicial.pack(pady=5)

        tk.Label(root_data, text="Data Final").pack(pady=5)
        date_entry_final = DateEntry(root_data, date_pattern='yyyy-mm-dd', locale='pt_BR')
        date_entry_final.pack(pady=5)

        def execucao():
            data_inicial = date_entry_inicial.get()
            data_final = date_entry_final.get()
            root_data.quit()
            root_data.destroy()
            atualizar_mensagem(root, label_progresso, "Gerando Arquivo...")
            query = f"""
            SELECT
                m.data,
                emp.empresa_codigo,
                emp.empresa_nome,
                emp.empresa_id,
                p.produto_id,
                c.categoria_id,
                c.codigo categoria_codigo,
                CAST(COALESCE(c.hierarquia_nome, c.nome) AS CHAR(250)) categoria_nome,
                mr.nome marca_nome,
                pf.cnpj fornecedor_cnpj,
                p.codigo produto_codigo,
                p.nome produto_nome,
                p.tpreco01,
                testoque01,
                tcusto01,
                pf.codigo fornecedor_codigo,
                pf.nome fornecedor_nome,
                p.pesobruto,
                p.pesoliquido,
                p.altura,
                p.largura,
                p.comprimento,
                p.quantidadeembalagem,
                SUM(mp.quantidadecomercial) quantidadetotal,
                SUM(mp.quantidadecomercial)* p.pesobruto pesobruto,
                SUM(mp.quantidadecomercial)* p.pesoliquido pesoliquido,
                SUM(COALESCE(mp.valortotalproduto, 0)) valortotalproduto,
                SUM(mp.valortotalcmv) valortotalcmv,
                SUM(mp.valortotal) valortotal,
                SUM(mp.valortotal - mp.valortotalcmv) lucrobruto,
                ((SUM(mp.valortotal) - SUM(mp.valortotalcmv))/ SUM(mp.valortotalcmv))* 100.00 markup,
                ((SUM(mp.valortotal) - SUM(mp.valortotalcmv))/ SUM(mp.valortotal))* 100.00 margem,
                SUM(COALESCE(mp.valortotal, 0) + COALESCE(mp.valorcrescimorateio, 0)- COALESCE(mp.valordescontorateio, 0)) valortotal_vds_liquida,
                SUM(COALESCE(mp.valortotal, 0) + COALESCE(mp.valorcrescimorateio, 0)+ COALESCE(mp.valordescontorateio, 0)) vendaBruta,
                SUM(COALESCE(mp.valoracrescimo, 0)) valoracrescimo,
                SUM(COALESCE(mp.valoracrescimoitem, 0)) valoracrescimoitem,
                SUM(COALESCE(mp.valorcrescimorateio, 0)) valorcrescimorateio,
                SUM(COALESCE(mp.valordesconto, 0)) valordesconto,
                SUM(COALESCE(mp.valordescontoitem, 0)) valordescontoitem,
                SUM(COALESCE(mp.valordescontorateio, 0)) valordescontorateio,
                SUM(COALESCE(mp.valortotal, 0) + COALESCE(mp.valorcrescimorateio, 0) - COALESCE(mp.valortotalcmv, 0) - COALESCE(mp.valoracrescimo, 0) - COALESCE(mp.valoracrescimoitem, 0) - COALESCE(mp.valorcrescimorateio, 0) - COALESCE(mp.valordesconto, 0) - COALESCE(mp.valordescontoitem, 0) - COALESCE(mp.valordescontorateio, 0)) Lucro_Bruto_SemDesc_SemAcres,
                SUM(COALESCE(mp.valortotal, 0.00) - (COALESCE(mp.valordesconto, 0.00) + COALESCE(mp.valoroutrasdespesas, 0.00))) valortotalfinal
            FROM
                ideiaerp.movimentosaida m
            INNER JOIN ideiaerp.movimentosaidaproduto mp ON
                (m.movimentosaida_id = mp.movimentosaida_id)
            INNER JOIN ideiaerp.empresa emp ON
                (emp.empresa_id = m.empresa_id)
            INNER JOIN ideiaerp.produto p ON
                (p.produto_id = mp.produto_id)
            LEFT JOIN ideiaerp.categoria c ON
                (c.categoria_id = p.categoria_id)
            LEFT JOIN ideiaerp.unidadenegocio un ON
                (p.unidadenegocio_id = un.unidadenegocio_id)
            LEFT JOIN ideiaerp.pessoa pes ON
                (pes.pessoa_id = m.pessoa_id)
            LEFT JOIN ideiaerp.pessoa pf ON
                (pf.pessoa_id = p.fornecedor_pessoa_id)
            LEFT JOIN ideiaerp.naturezaoperacao n ON
                (n.naturezaoperacao_id = m.naturezaoperacao_id)
            LEFT JOIN ideiaerp.marca mr ON
                (mr.marca_id = p.marca_id)
            WHERE
                (1 = 1)
                AND COALESCE(mp.flagcancelado, '0') = '0'
                AND (COALESCE(m.flagexcluido, '0')= '0')
                AND (mp.promocaorelampago_id IS NOT NULL)
                AND COALESCE(m.flagcancelado, '0') = '0'
                AND (COALESCE(m.flagtipooperacao, '1') = '1')
                AND m.data >= '{data_inicial}'
                AND m.data <= '{data_final}'
            GROUP BY
                emp.empresa_id,
                5,
                6,
                7,
                8,
                9,
                10,
                11,
                12,
                13,
                14,
                15,
                p.pesobruto,
                p.pesoliquido,
                p.altura,
                p.largura,
                p.comprimento,
                p.quantidadeembalagem
            ORDER BY
                p.nome"""
            
            df = pd.read_sql(query, conexao_sqlalchemy)
            salvar_arquivo(df)
            
        btn_obter_datas = tk.Button(root_data, text="Enviar", command=execucao)
        btn_obter_datas.pack(pady=20)   
        root.mainloop()
        atualizar_mensagem(root, label_progresso, "Aguardando Operação")

    except Exception as e:
        messagebox.showerror("Erro", f"Erro na operação de Vendas: {e}")

def tratamento_txt():

    atualizar_mensagem(root, label_progresso, "Carregando arquivo...")
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

    atualizar_mensagem(root, label_progresso, "Aguardando Operação...")
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

# Submenu de Prevenção
prevencao_menu = tk.Menu(submenu, tearoff=0)
prevencao_menu.add_command(label="Compras", command=compras)
prevencao_menu.add_command(label="Vendas", command=vendas)
prevencao_menu.add_command(label="Pagamento de Maquininhas", command=pagmaquininhas)
prevencao_menu.add_command(label="Despesas", command=despesas)
prevencao_menu.add_command(label="RMA", command=rma)
prevencao_menu.add_command(label="CMV", command=cmv)
submenu.add_cascade(label="Prevenção", menu=prevencao_menu)

# Submenu de Last Mile
lastmile_menu = tk.Menu(submenu, tearoff=0)
lastmile_menu.add_command(label="Vendas Delivery", command=vendas_delivery)
lastmile_menu.add_command(label="Clientes Delivery", command=clientes_delivery)
submenu.add_cascade(label="Last Mile", menu=lastmile_menu)

# Submenu de Fiscal
lastmile_menu = tk.Menu(submenu, tearoff=0)
lastmile_menu.add_command(label="RMA fiscal", command=rma_fiscal)
submenu.add_cascade(label="Fiscal", menu=lastmile_menu)

# Submenu de TI
ti_menu = tk.Menu(submenu, tearoff=0)
ti_menu.add_command(label="Dados Lojas", command=lojas_dados)
ti_menu.add_command(label="Vendas Grandfood", command=vendas_grandfood)
ti_menu.add_command(label="Teste SQL", command=teste_sql)
submenu.add_cascade(label="TI", menu=ti_menu)

#Submeno de Comercial
comercial_menu = tk.Menu(submenu, tearoff=0)
comercial_menu.add_command(label="Vendas por Fornecedor", command=vendas_fornecedor)
submenu.add_cascade(label="Comercial", menu=comercial_menu)

# Submenu de Financeiro
financeiro_menu = tk.Menu(submenu, tearoff=0)
financeiro_menu.add_command(label="Tratamento TXT", command=tratamento_txt)
submenu.add_cascade(label="Financeiro", menu=financeiro_menu)

# Submenu arquivos
submenu2 = tk.Menu(submenu, tearoff=0)
menu.add_cascade(label="Arquivos", menu=submenu2)
submenu2.add_command(label="Tratamento TXT", command=tratamento_txt)

# Submenu de Sobre
submenu3 = tk.Menu(menu, tearoff=0)
menu.add_cascade(label="Sobre", menu=submenu3)
submenu3.add_command(label="Sobre", command=sobre)

menu.add_command(label="Sair", command=root.quit)

rodape = tk.Label(root, text="Tecnologia - American Pet", bd=1, relief=tk.SUNKEN, anchor=tk.W)
rodape.pack(side=tk.BOTTOM, fill=tk.X)

imagem = Image.open("bg.png")
imagem = imagem.resize((150, 100), Image.LANCZOS)
imagem_tk = ImageTk.PhotoImage(imagem)

label_imagem = tk.Label(root, image=imagem_tk)
label_imagem.pack(expand=True, fill=tk.BOTH)

label_progresso = tk.Label(root, text="Status")
label_progresso.pack(pady=20)

icone = Image.open("bg.png")
icone_tk = ImageTk.PhotoImage(icone)
root.iconphoto(True, icone_tk)

root.mainloop()