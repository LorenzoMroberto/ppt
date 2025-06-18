import tkinter as tk
from tkinter import filedialog, colorchooser, messagebox, Menu
from PIL import Image, ImageTk, ImageDraw, ImageOps
import sys
import math

class PaintApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Paint.NET Clone")
        self.root.geometry("700x700")
        
        # Configurações iniciais
        self.cor_caneta = "black"
        self.tamanho_caneta = 3
        self.ferramenta_atual = "lápis"
        self.forma_selecionada = None
        self.posicao_inicial_x = None
        self.posicao_inicial_y = None
        self.angulo_rotacao = 0
        self.modo_rotacao = False
        self.tamanho_imagem = (800, 600)
        self.fator_zoom = 1.0
        self.deslocamento_x = 0
        self.deslocamento_y = 0
        self.modo_arrastar = False
        self.ultima_posicao_x = 0
        self.ultima_posicao_y = 0
        self.cursor_circulo = None
        self.formas = []  # Armazenar formas para rotação
        self.indice_forma_atual = -1
        self.arquivo_atual = None
        self.arrastando = False
        self.posicao_imagem_x = 0
        self.posicao_imagem_y = 0
        
        # Configurar menu superior
        self.menu_bar = Menu(root)
        
        # Menu Arquivo
        self.menu_arquivo = Menu(self.menu_bar, tearoff=0)
        self.menu_arquivo.add_command(label="Novo", command=self.nova_imagem, accelerator="Ctrl+N")
        self.menu_arquivo.add_command(label="Abrir...", command=self.abrir_imagem, accelerator="Ctrl+O")
        self.menu_arquivo.add_command(label="Salvar", command=self.salvar_imagem, accelerator="Ctrl+S")
        self.menu_arquivo.add_command(label="Salvar como...", command=self.salvar_imagem_como)
        self.menu_arquivo.add_separator()
        self.menu_arquivo.add_command(label="Sair", command=root.quit)
        self.menu_bar.add_cascade(label="Arquivo", menu=self.menu_arquivo)
        
        # Menu Editar
        self.menu_editar = Menu(self.menu_bar, tearoff=0)
        self.menu_editar.add_command(label="Tamanho da Imagem...", command=self.alterar_tamanho_imagem)
        self.menu_bar.add_cascade(label="Editar", menu=self.menu_editar)
        
        # Menu Ferramentas
        self.menu_ferramentas = Menu(self.menu_bar, tearoff=0)
        self.menu_ferramentas.add_command(label="Lápis (P)", command=lambda: self.selecionar_ferramenta("lápis"))
        self.menu_ferramentas.add_command(label="Quadrado (Q)", command=lambda: self.selecionar_ferramenta("quadrado"))
        self.menu_ferramentas.add_command(label="Círculo (C)", command=lambda: self.selecionar_ferramenta("círculo"))
        self.menu_ferramentas.add_command(label="Triângulo (T)", command=lambda: self.selecionar_ferramenta("triângulo"))
        self.menu_ferramentas.add_command(label="Mão (H)", command=lambda: self.selecionar_ferramenta("mão"))
        self.menu_bar.add_cascade(label="Ferramentas", menu=self.menu_ferramentas)
        
        # Menu Visualizar
        self.menu_visualizar = Menu(self.menu_bar, tearoff=0)
        self.menu_visualizar.add_command(label="Aumentar Zoom", command=self.aumentar_zoom, accelerator="Ctrl++")
        self.menu_visualizar.add_command(label="Diminuir Zoom", command=self.diminuir_zoom, accelerator="Ctrl+-")
        self.menu_visualizar.add_command(label="Resetar Zoom", command=self.resetar_zoom)
        self.menu_bar.add_cascade(label="Visualizar", menu=self.menu_visualizar)
        
        root.config(menu=self.menu_bar)
        
        # Frame principal
        self.frame_principal = tk.Frame(root)
        self.frame_principal.pack(fill=tk.BOTH, expand=True)
        
        # Frame para o canvas e barra de rolagem vertical
        self.frame_canvas = tk.Frame(self.frame_principal)
        self.frame_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Barra de rolagem vertical
        self.barra_rolagem_v = tk.Scrollbar(self.frame_canvas, orient=tk.VERTICAL)
        self.barra_rolagem_v.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Barra de rolagem horizontal
        self.barra_rolagem_h = tk.Scrollbar(self.frame_canvas, orient=tk.HORIZONTAL)
        self.barra_rolagem_h.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Canvas com barras de rolagem
        self.canvas = tk.Canvas(
            self.frame_canvas, 
            width=self.tamanho_imagem[0], 
            height=self.tamanho_imagem[1], 
            bg="white",
            yscrollcommand=self.barra_rolagem_v.set,
            xscrollcommand=self.barra_rolagem_h.set
        )
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.barra_rolagem_v.config(command=self.canvas.yview)
        self.barra_rolagem_h.config(command=self.canvas.xview)
        
        # Frame para ferramentas (lado direito)
        self.frame_ferramentas = tk.Frame(self.frame_principal, width=100, padx=5, pady=5)
        self.frame_ferramentas.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Botão de cor
        self.botao_cor = tk.Button(self.frame_ferramentas, text="Escolher Cor", command=self.escolher_cor)
        self.botao_cor.pack(pady=10)
        
        # Visualizador de cor
        self.exibidor_cor = tk.Canvas(self.frame_ferramentas, width=30, height=30, bg=self.cor_caneta)
        self.exibidor_cor.pack(pady=5)
        
        # Tamanho do pincel
        tk.Label(self.frame_ferramentas, text="Tamanho do Pincel:").pack(pady=(10, 0))
        self.escala_tamanho = tk.Scale(self.frame_ferramentas, from_=1, to=20, orient=tk.HORIZONTAL)
        self.escala_tamanho.set(self.tamanho_caneta)
        self.escala_tamanho.pack(pady=5)
        
        # Botão para centralizar imagem
        self.botao_centralizar = tk.Button(self.frame_ferramentas, text="Centralizar Imagem", command=self.centralizar_imagem)
        self.botao_centralizar.pack(pady=10)
        
        # Barra de status
        self.barra_status = tk.Label(root, text="Pronto | Zoom: 100% | Ferramenta: Lápis", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.barra_status.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Criar imagem
        self.imagem = Image.new("RGB", self.tamanho_imagem, "white")
        self.desenho = ImageDraw.Draw(self.imagem)
        self.imagem_tk = ImageTk.PhotoImage(self.imagem)
        self.imagem_canvas = self.canvas.create_image(0, 0, anchor=tk.NW, image=self.imagem_tk)
        
        # Eventos
        self.canvas.bind("<Button-1>", self.iniciar_desenho)
        self.canvas.bind("<B1-Motion>", self.desenhar_ferramenta)
        self.canvas.bind("<ButtonRelease-1>", self.finalizar_desenho)
        self.canvas.bind("<Double-Button-1>", self.duplo_clique)
        self.canvas.bind("<Motion>", self.atualizar_cursor)
        
        # Atalhos de teclado
        self.root.bind("<Control-s>", self.salvar_imagem)
        self.root.bind("<Control-plus>", self.aumentar_zoom)
        self.root.bind("<Control-minus>", self.diminuir_zoom)
        self.root.bind("<Control-0>", self.resetar_zoom)
        self.root.bind("p", lambda e: self.selecionar_ferramenta("lápis"))
        self.root.bind("q", lambda e: self.selecionar_ferramenta("quadrado"))
        self.root.bind("c", lambda e: self.selecionar_ferramenta("círculo"))
        self.root.bind("t", lambda e: self.selecionar_ferramenta("triângulo"))
        self.root.bind("h", lambda e: self.selecionar_ferramenta("mão"))
        
        # Abrir imagem por argumento
        if len(sys.argv) > 1:
            self.abrir_imagem(sys.argv[1])
        
        self.atualizar_status()
        self.centralizar_imagem()
        
        # Configurar região de rolagem
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

    def escolher_cor(self):
        cor = colorchooser.askcolor(title="Escolher Cor")
        if cor[1]:
            self.cor_caneta = cor[1]
            self.exibidor_cor.config(bg=self.cor_caneta)

    def selecionar_ferramenta(self, ferramenta):
        self.ferramenta_atual = ferramenta
        self.modo_rotacao = False
        self.modo_arrastar = (ferramenta == "mão")
        self.atualizar_status()
        
        if hasattr(self, 'alca_rotacao'):
            self.canvas.delete(self.alca_rotacao)
        
        self.atualizar_cursor()

    def atualizar_cursor(self, event=None):
        if self.cursor_circulo:
            self.canvas.delete(self.cursor_circulo)
            self.cursor_circulo = None
        
        if self.ferramenta_atual == "lápis" and event:
            # Obter a posição atual do canvas
            canvas_x = self.canvas.canvasx(event.x)
            canvas_y = self.canvas.canvasy(event.y)
            
            tamanho = self.escala_tamanho.get()
            self.cursor_circulo = self.canvas.create_oval(
                canvas_x - tamanho/2, canvas_y - tamanho/2,
                canvas_x + tamanho/2, canvas_y + tamanho/2,
                outline=self.cor_caneta, fill="", width=1
            )

    def iniciar_desenho(self, event):
        if self.modo_arrastar:
            self.ultima_posicao_x = event.x
            self.ultima_posicao_y = event.y
            self.arrastando = True
            self.canvas.config(cursor="fleur")
            return
        
        if self.modo_rotacao and self.forma_selecionada:
            handle_x, handle_y = self.canvas.coords(self.alca_rotacao)
            if (event.x >= handle_x - 10 and event.x <= handle_x + 10 and 
                event.y >= handle_y - 10 and event.y <= handle_y + 10):
                self.posicao_inicial_x = event.x
                self.posicao_inicial_y = event.y
                self.angulo_original = self.angulo_rotacao
            return
        
        # Obter a posição atual do canvas
        canvas_x = self.canvas.canvasx(event.x)
        canvas_y = self.canvas.canvasy(event.y)
        
        self.posicao_inicial_x = canvas_x
        self.posicao_inicial_y = canvas_y
        
        if self.ferramenta_atual != "lápis":
            self.forma_selecionada = None
            self.angulo_rotacao = 0
            self.modo_rotacao = False

    def desenhar_ferramenta(self, event):
        if self.modo_arrastar and self.arrastando:
            # Calcular o deslocamento
            dx = event.x - self.ultima_posicao_x
            dy = event.y - self.ultima_posicao_y
            
            # Atualizar a posição da imagem
            self.posicao_imagem_x += dx
            self.posicao_imagem_y += dy
            
            # Mover a imagem
            self.canvas.coords(self.imagem_canvas, self.posicao_imagem_x, self.posicao_imagem_y)
            
            # Atualizar a última posição
            self.ultima_posicao_x = event.x
            self.ultima_posicao_y = event.y
            
            # Atualizar a região de rolagem
            self.atualizar_regiao_rolagem()
            return
        
        if self.modo_rotacao and self.forma_selecionada:
            if self.posicao_inicial_x is not None and self.posicao_inicial_y is not None:
                coords_forma = self.canvas.coords(self.forma_selecionada)
                centro_x = (coords_forma[0] + coords_forma[2]) / 2
                centro_y = (coords_forma[1] + coords_forma[3]) / 2
                
                angulo_orig = math.atan2(self.posicao_inicial_y - centro_y, self.posicao_inicial_x - centro_x)
                angulo_novo = math.atan2(event.y - centro_y, event.x - centro_x)
                self.angulo_rotacao = self.angulo_original + math.degrees(angulo_novo - angulo_orig)
                
                self.redesenhar_forma()
                self.desenhar_alca_rotacao()
            return
        
        if self.ferramenta_atual == "lápis":
            if self.posicao_inicial_x is not None and self.posicao_inicial_y is not None:
                # Obter a posição atual do canvas
                canvas_x = self.canvas.canvasx(event.x)
                canvas_y = self.canvas.canvasy(event.y)
                
                # Converter coordenadas do canvas para coordenadas da imagem
                x1 = int((self.posicao_inicial_x - self.posicao_imagem_x) / self.fator_zoom)
                y1 = int((self.posicao_inicial_y - self.posicao_imagem_y) / self.fator_zoom)
                x2 = int((canvas_x - self.posicao_imagem_x) / self.fator_zoom)
                y2 = int((canvas_y - self.posicao_imagem_y) / self.fator_zoom)
                
                # Desenhar na imagem
                self.desenho.line([x1, y1, x2, y2], 
                                fill=self.cor_caneta, 
                                width=self.escala_tamanho.get())
                
                self.posicao_inicial_x = canvas_x
                self.posicao_inicial_y = canvas_y
                self.atualizar_canvas()
        else:
            if hasattr(self, 'forma_temporaria'):
                self.canvas.delete(self.forma_temporaria)
            
            if self.ferramenta_atual == "quadrado":
                self.forma_temporaria = self.canvas.create_rectangle(
                    self.posicao_inicial_x, self.posicao_inicial_y, event.x, event.y,
                    outline=self.cor_caneta, width=self.escala_tamanho.get()
                )
            elif self.ferramenta_atual == "círculo":
                self.forma_temporaria = self.canvas.create_oval(
                    self.posicao_inicial_x, self.posicao_inicial_y, event.x, event.y,
                    outline=self.cor_caneta, width=self.escala_tamanho.get()
                )
            elif self.ferramenta_atual == "triângulo":
                pontos = [
                    self.posicao_inicial_x + (event.x - self.posicao_inicial_x) / 2, self.posicao_inicial_y,
                    self.posicao_inicial_x, event.y,
                    event.x, event.y
                ]
                self.forma_temporaria = self.canvas.create_polygon(
                    pontos, outline=self.cor_caneta, width=self.escala_tamanho.get(), fill=""
                )

    def finalizar_desenho(self, event):
        if self.modo_arrastar:
            self.arrastando = False
            self.canvas.config(cursor="arrow")
            return
        
        if self.modo_rotacao and self.forma_selecionada:
            if self.indice_forma_atual >= 0:
                self.formas[self.indice_forma_atual]['rotacao'] = self.angulo_rotacao
            return
        
        if self.ferramenta_atual != "lápis" and hasattr(self, 'forma_temporaria'):
            coords = self.canvas.coords(self.forma_temporaria)
            self.canvas.delete(self.forma_temporaria)
            
            info_forma = {
                "tipo": self.ferramenta_atual,
                "coords": coords,
                "cor": self.cor_caneta,
                "largura": self.escala_tamanho.get(),
                "rotacao": 0
            }
            self.formas.append(info_forma)
            self.indice_forma_atual = len(self.formas) - 1
            
            self.forma_selecionada = self.desenhar_forma(info_forma)
            self.desenhar_forma_final(coords)
            self.atualizar_canvas()

    def duplo_clique(self, event):
        if self.ferramenta_atual != "lápis" and self.ferramenta_atual != "mão" and self.forma_selecionada:
            self.modo_rotacao = not self.modo_rotacao
            if self.modo_rotacao:
                self.desenhar_alca_rotacao()
            else:
                self.remover_alca_rotacao()

    def desenhar_forma(self, info_forma):
        if info_forma["tipo"] == "quadrado":
            return self.canvas.create_rectangle(
                info_forma["coords"], 
                outline=info_forma["cor"], 
                width=info_forma["largura"]
            )
        elif info_forma["tipo"] == "círculo":
            return self.canvas.create_oval(
                info_forma["coords"], 
                outline=info_forma["cor"], 
                width=info_forma["largura"]
            )
        elif info_forma["tipo"] == "triângulo":
            return self.canvas.create_polygon(
                info_forma["coords"], 
                outline=info_forma["cor"], 
                width=info_forma["largura"], 
                fill=""
            )

    def desenhar_alca_rotacao(self):
        if hasattr(self, 'alca_rotacao'):
            self.canvas.delete(self.alca_rotacao)
        
        coords_forma = self.canvas.coords(self.forma_selecionada)
        x1, y1, x2, y2 = coords_forma[:4]
        
        handle_x = x2 + 10
        handle_y = y2 + 10
        
        self.alca_rotacao = self.canvas.create_oval(
            handle_x - 5, handle_y - 5, handle_x + 5, handle_y + 5,
            fill="red", outline="black", tags="alca_rotacao"
        )

    def remover_alca_rotacao(self):
        if hasattr(self, 'alca_rotacao'):
            self.canvas.delete(self.alca_rotacao)
            del self.alca_rotacao

    def redesenhar_forma(self):
        if self.indice_forma_atual < 0:
            return
            
        self.formas[self.indice_forma_atual]['rotacao'] = self.angulo_rotacao
        self.canvas.delete(self.forma_selecionada)
        self.forma_selecionada = self.desenhar_forma(self.formas[self.indice_forma_atual])

    def desenhar_forma_final(self, coords):
        if self.ferramenta_atual == "quadrado":
            self.desenho.rectangle(coords, outline=self.cor_caneta, width=self.escala_tamanho.get())
        elif self.ferramenta_atual == "círculo":
            self.desenho.ellipse(coords, outline=self.cor_caneta, width=self.escala_tamanho.get())
        elif self.ferramenta_atual == "triângulo":
            pontos = [(coords[i], coords[i+1]) for i in range(0, len(coords), 2)]
            self.desenho.polygon(pontos, outline=self.cor_caneta, width=self.escala_tamanho.get())

    def atualizar_canvas(self):
        if self.fator_zoom != 1.0:
            nova_largura = int(self.tamanho_imagem[0] * self.fator_zoom)
            nova_altura = int(self.tamanho_imagem[1] * self.fator_zoom)
            imagem_redimensionada = self.imagem.resize((nova_largura, nova_altura), Image.LANCZOS)
            self.imagem_tk = ImageTk.PhotoImage(imagem_redimensionada)
        else:
            self.imagem_tk = ImageTk.PhotoImage(self.imagem)
        
        self.canvas.itemconfig(self.imagem_canvas, image=self.imagem_tk)

    def alterar_tamanho_imagem(self):
        janela_tamanho = tk.Toplevel(self.root)
        janela_tamanho.title("Alterar Tamanho da Imagem")
        janela_tamanho.transient(self.root)
        janela_tamanho.grab_set()
        
        tk.Label(janela_tamanho, text="Largura:").grid(row=0, column=0, padx=5, pady=5)
        entrada_largura = tk.Entry(janela_tamanho)
        entrada_largura.grid(row=0, column=1, padx=5, pady=5)
        entrada_largura.insert(0, str(self.tamanho_imagem[0]))
        
        tk.Label(janela_tamanho, text="Altura:").grid(row=1, column=0, padx=5, pady=5)
        entrada_altura = tk.Entry(janela_tamanho)
        entrada_altura.grid(row=1, column=1, padx=5, pady=5)
        entrada_altura.insert(0, str(self.tamanho_imagem[1]))
        
        def aplicar_mudancas():
            try:
                nova_largura = int(entrada_largura.get())
                nova_altura = int(entrada_altura.get())
                
                if nova_largura <= 0 or nova_altura <= 0:
                    messagebox.showerror("Erro", "Dimensões devem ser números positivos")
                    return
                
                nova_imagem = Image.new("RGB", (nova_largura, nova_altura), "white")
                nova_imagem.paste(self.imagem, (0, 0))
                
                self.imagem = nova_imagem
                self.desenho = ImageDraw.Draw(self.imagem)
                self.tamanho_imagem = (nova_largura, nova_altura)
                
                self.canvas.config(width=nova_largura, height=nova_altura)
                self.atualizar_canvas()
                self.centralizar_imagem()
                
                janela_tamanho.destroy()
                
            except ValueError:
                messagebox.showerror("Erro", "Por favor, insira números válidos para largura e altura")
        
        tk.Button(janela_tamanho, text="Aplicar", command=aplicar_mudancas).grid(row=2, column=0, columnspan=2, pady=10)

    def salvar_imagem(self, event=None):
        if not hasattr(self, 'arquivo_atual') or self.arquivo_atual is None:
            self.salvar_imagem_como()
        else:
            try:
                self.imagem.save(self.arquivo_atual)
                messagebox.showinfo("Sucesso", "Imagem salva com sucesso")
            except Exception as e:
                messagebox.showerror("Erro", f"Falha ao salvar imagem: {str(e)}")

    def salvar_imagem_como(self):
        caminho_arquivo = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[
                ("PNG files", "*.png"),
                ("JPEG files", "*.jpg;*.jpeg"),
                ("BMP files", "*.bmp"),
                ("All files", "*.*")
            ]
        )
        
        if caminho_arquivo:
            try:
                self.imagem.save(caminho_arquivo)
                self.arquivo_atual = caminho_arquivo
                messagebox.showinfo("Sucesso", "Imagem salva com sucesso")
            except Exception as e:
                messagebox.showerror("Erro", f"Falha ao salvar imagem: {str(e)}")

    def abrir_imagem(self, caminho_arquivo=None):
        if not caminho_arquivo:
            caminho_arquivo = filedialog.askopenfilename(
                filetypes=[
                    ("Image files", "*.png;*.jpg;*.jpeg;*.bmp"),
                    ("All files", "*.*")
                ]
            )
            if not caminho_arquivo:
                return
        
        try:
            img = Image.open(caminho_arquivo)
            self.imagem = img.copy()
            self.desenho = ImageDraw.Draw(self.imagem)
            self.tamanho_imagem = img.size
            self.arquivo_atual = caminho_arquivo
            
            # Atualizar canvas
            self.canvas.config(width=self.tamanho_imagem[0], height=self.tamanho_imagem[1])
            self.atualizar_canvas()
            
            # Forçar atualização do layout
            self.root.update_idletasks()
            
            # Centralizar imagem
            self.centralizar_imagem()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao abrir imagem: {str(e)}")

    def centralizar_imagem(self):
        self.canvas.update_idletasks()
        largura_canvas = self.canvas.winfo_width()
        altura_canvas = self.canvas.winfo_height()
        
        # Calcular o tamanho da imagem com zoom
        largura_imagem = int(self.tamanho_imagem[0] * self.fator_zoom)
        altura_imagem = int(self.tamanho_imagem[1] * self.fator_zoom)
        
        # Configurar a região de rolagem para incluir toda a imagem
        self.canvas.config(scrollregion=(0, 0, largura_imagem, altura_imagem))
        
        # Calcular deslocamento para centralizar
        if largura_canvas > largura_imagem:
            self.posicao_imagem_x = (largura_canvas - largura_imagem) // 2
        else:
            self.posicao_imagem_x = 0
            
        if altura_canvas > altura_imagem:
            self.posicao_imagem_y = (altura_canvas - altura_imagem) // 2
        else:
            self.posicao_imagem_y = 0
        
        # Aplicar deslocamento
        self.canvas.coords(self.imagem_canvas, self.posicao_imagem_x, self.posicao_imagem_y)
        
        # Atualizar região de rolagem
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

    def nova_imagem(self):
        self.imagem = Image.new("RGB", self.tamanho_imagem, "white")
        self.desenho = ImageDraw.Draw(self.imagem)
        self.atualizar_canvas()
        
        # Forçar atualização do layout
        self.root.update_idletasks()
        
        # Centralizar imagem
        self.centralizar_imagem()
        
        self.arquivo_atual = None
        self.formas = []
        self.indice_forma_atual = -1

    def aumentar_zoom(self, event=None):
        self.fator_zoom *= 1.1
        self.aplicar_zoom()

    def diminuir_zoom(self, event=None):
        self.fator_zoom /= 1.1
        self.aplicar_zoom()

    def resetar_zoom(self, event=None):
        self.fator_zoom = 1.0
        self.aplicar_zoom()

    def aplicar_zoom(self):
        self.atualizar_canvas()
        self.centralizar_imagem()
        self.atualizar_status()

    def atualizar_status(self):
        nomes_ferramentas = {
            "lápis": "Lápis",
            "quadrado": "Quadrado",
            "círculo": "Círculo",
            "triângulo": "Triângulo",
            "mão": "Mão"
        }
        zoom_percentual = int(self.fator_zoom * 100)
        self.barra_status.config(text=f"Pronto | Zoom: {zoom_percentual}% | Ferramenta: {nomes_ferramentas.get(self.ferramenta_atual, 'Lápis')}")

    def atualizar_regiao_rolagem(self):
        # Calcular o tamanho da imagem com zoom
        largura_imagem = int(self.tamanho_imagem[0] * self.fator_zoom)
        altura_imagem = int(self.tamanho_imagem[1] * self.fator_zoom)
        
        # Calcular os limites da região de rolagem
        min_x = min(0, self.posicao_imagem_x)
        min_y = min(0, self.posicao_imagem_y)
        max_x = max(largura_imagem, self.posicao_imagem_x + largura_imagem)
        max_y = max(altura_imagem, self.posicao_imagem_y + altura_imagem)
        
        # Configurar a região de rolagem
        self.canvas.config(scrollregion=(min_x, min_y, max_x, max_y))

if __name__ == "__main__":
    root = tk.Tk()
    app = PaintApp(root)
    root.mainloop()
