import customtkinter as ctk
from tkinter import messagebox, ttk
from app.services import InventoryError, InventoryService

BG, CARD, SIDE, ACCENT, TEXT, MUTED, DANGER = "#F3EEE4", "#FFFDF9", "#211F1C", "#B98935", "#211F1C", "#71675A", "#A84636"
ctk.set_appearance_mode("light")

class CrislenApp(ctk.CTk):
    def __init__(self):
        super().__init__(); self.service=InventoryService(); self.title("Crislen | Inventario"); self.geometry("1240x760"); self.minsize(1050,650); self.configure(fg_color=BG); self.grid_columnconfigure(1,weight=1); self.grid_rowconfigure(0,weight=1); self.sidebar(); self.content=ctk.CTkFrame(self,fg_color=BG,corner_radius=0); self.content.grid(row=0,column=1,sticky="nsew",padx=26,pady=24); self.content.grid_columnconfigure(0,weight=1); self.content.grid_rowconfigure(1,weight=1); self.show("inicio")
    def sidebar(self):
        box=ctk.CTkFrame(self,width=230,fg_color=SIDE,corner_radius=0); box.grid(row=0,column=0,sticky="nsew"); box.grid_propagate(False); ctk.CTkLabel(box,text="CRISLEN",font=("Segoe UI",28,"bold"),text_color="#E3BD72").pack(padx=25,pady=(38,0),anchor="w"); ctk.CTkLabel(box,text="Ropa de mujer · Tallas grandes",font=("Segoe UI",11),text_color="#D8D0C4").pack(padx=25,pady=(0,35),anchor="w")
        for page,label in (("inicio","Inicio"),("productos","Productos"),("movimientos","Movimientos"),("historial","Historial")):
            ctk.CTkButton(box,text=label,anchor="w",command=lambda p=page:self.show(p),fg_color="transparent",hover_color="#3A342C",text_color="#FFFDF9",font=("Segoe UI",14),height=42).pack(fill="x",padx=14,pady=3)
        ctk.CTkLabel(box,text="Inventario SQL Server\nv1.0",text_color="#BFB5A8",justify="left").pack(side="bottom",padx=24,pady=22,anchor="w")
    def show(self,page):
        for w in self.content.winfo_children(): w.destroy()
        try: getattr(self,"page_"+page)()
        except Exception as e: messagebox.showerror("Conexión",f"No se pudo cargar la información.\n{e}")
    def header(self,title,subtitle):
        box=ctk.CTkFrame(self.content,fg_color="transparent"); box.grid(row=0,column=0,sticky="ew",pady=(0,16)); ctk.CTkLabel(box,text=title,font=("Segoe UI",27,"bold"),text_color=TEXT).pack(anchor="w"); ctk.CTkLabel(box,text=subtitle,font=("Segoe UI",13),text_color=MUTED).pack(anchor="w",pady=(2,0))
    def tree(self,parent,cols,widths):
        st=ttk.Style(); st.theme_use("clam"); st.configure("Crislen.Treeview",background=CARD,foreground=TEXT,fieldbackground=CARD,rowheight=32,font=("Segoe UI",10)); st.configure("Crislen.Treeview.Heading",background=ACCENT,foreground="#211F1C",font=("Segoe UI",10,"bold")); st.map("Crislen.Treeview",background=[("selected", "#E8D4A6")],foreground=[("selected", TEXT)]); t=ttk.Treeview(parent,columns=cols,show="headings",style="Crislen.Treeview")
        for c,w in zip(cols,widths): t.heading(c,text=c); t.column(c,width=w,anchor="center")
        sc=ttk.Scrollbar(parent,orient="vertical",command=t.yview); t.configure(yscrollcommand=sc.set); t.pack(side="left",fill="both",expand=True); sc.pack(side="right",fill="y"); return t
    def card(self,parent,col,label,value,color=ACCENT):
        f=ctk.CTkFrame(parent,fg_color=CARD,corner_radius=14); f.grid(row=0,column=col,sticky="ew",padx=7); ctk.CTkLabel(f,text=label,text_color=MUTED,font=("Segoe UI",12)).pack(anchor="w",padx=18,pady=(15,2)); ctk.CTkLabel(f,text=str(value),text_color=color,font=("Segoe UI",30,"bold")).pack(anchor="w",padx=18,pady=(0,15))
    def page_inicio(self):
        self.header("Panel de control","Visión rápida de la logística de Crislen"); d=self.service.resumen(); cards=ctk.CTkFrame(self.content,fg_color="transparent"); cards.grid(row=1,column=0,sticky="new"); [cards.grid_columnconfigure(i,weight=1) for i in range(4)]; self.card(cards,0,"PRODUCTOS",d["productos"]); self.card(cards,1,"VARIANTES",d["variantes"]); self.card(cards,2,"UNIDADES",d["unidades"]); self.card(cards,3,"STOCK BAJO",len(d["bajos"]),DANGER)
        box=ctk.CTkFrame(self.content,fg_color=CARD,corner_radius=14); box.grid(row=2,column=0,sticky="nsew",pady=(20,0)); self.content.grid_rowconfigure(2,weight=1); ctk.CTkLabel(box,text="Alertas de reposición",font=("Segoe UI",16,"bold")).pack(anchor="w",padx=18,pady=16); t=self.tree(box,("SKU","Producto","Talla","Color","Disponible","Mínimo"),(150,260,100,130,110,100))
        for x in d["bajos"]: t.insert("","end",values=(x.sku,x.producto.nombre,x.talla,x.color,x.stock_actual,x.producto.stock_minimo))
    def page_productos(self):
        self.header("Catálogo","Crea productos y sus variantes por talla y color"); f=ctk.CTkFrame(self.content,fg_color=CARD,corner_radius=14); f.grid(row=1,column=0,sticky="ew"); en=[]
        for i,(lab,ph) in enumerate((("Nombre","Ej. Vestido Aurora"),("Categoría","Vestidos"),("Stock mínimo","2"))): ctk.CTkLabel(f,text=lab,text_color=MUTED).grid(row=0,column=i,padx=12,pady=(12,2),sticky="w"); x=ctk.CTkEntry(f,placeholder_text=ph); x.grid(row=1,column=i,padx=12,pady=(0,14),sticky="ew"); f.grid_columnconfigure(i,weight=1); en.append(x)
        def save_product():
            try: self.service.crear_producto(en[0].get(),en[1].get(),int(en[2].get())); self.show("productos")
            except (InventoryError,ValueError) as e: messagebox.showerror("Validación",str(e))
        ctk.CTkButton(f,text="+ Nuevo producto",fg_color=ACCENT,command=save_product).grid(row=1,column=3,padx=12,pady=(0,14))
        f2=ctk.CTkFrame(self.content,fg_color=CARD,corner_radius=14); f2.grid(row=2,column=0,sticky="ew",pady=14); prods=self.service.productos(); cmb=ctk.CTkComboBox(f2,values=[f"{p.id} | {p.nombre}" for p in prods] or ["Primero crea un producto"]); cmb.grid(row=1,column=0,padx=12,pady=(0,14),sticky="ew"); f2.grid_columnconfigure(0,weight=2); ctk.CTkLabel(f2,text="Producto",text_color=MUTED).grid(row=0,column=0,padx=12,pady=(12,2),sticky="w"); fields=[]
        for i,(lab,ph) in enumerate((("SKU","CR-001"),("Talla","XL"),("Color","Negro"),("Precio","89.90"),("Stock inicial","0")),1): ctk.CTkLabel(f2,text=lab,text_color=MUTED).grid(row=0,column=i,padx=8,pady=(12,2),sticky="w"); x=ctk.CTkEntry(f2,placeholder_text=ph,width=110); x.grid(row=1,column=i,padx=8,pady=(0,14),sticky="ew"); fields.append(x)
        def save_variant():
            try: self.service.crear_variante(int(cmb.get().split(" | ")[0]),*[x.get() for x in fields[:4]],int(fields[4].get())); self.show("productos")
            except (InventoryError,ValueError,IndexError) as e: messagebox.showerror("Validación",str(e))
        def delete_product():
            try:
                product_id = int(cmb.get().split(" | ")[0])
            except (ValueError, IndexError):
                messagebox.showerror("Eliminar producto", "Selecciona un producto válido.")
                return
            nombre = cmb.get().split(" | ", 1)[1]
            confirmacion = messagebox.askyesno(
                "Eliminar producto",
                f"¿Eliminar '{nombre}'?\n\nTambién se eliminarán sus variantes y movimientos. Esta acción no se puede deshacer.",
                icon="warning",
            )
            if confirmacion:
                try:
                    self.service.eliminar_producto(product_id)
                    self.show("productos")
                except InventoryError as e:
                    messagebox.showerror("Eliminar producto", str(e))
                except Exception as e:
                    messagebox.showerror("Eliminar producto", f"No se pudo eliminar: {e}")
        ctk.CTkButton(f2,text="+ Variante",fg_color=ACCENT,command=save_variant).grid(row=1,column=6,padx=8,pady=(0,14)); ctk.CTkButton(f2,text="Eliminar producto",fg_color=DANGER,hover_color="#87372B",command=delete_product).grid(row=1,column=7,padx=(0,12),pady=(0,14)); box=ctk.CTkFrame(self.content,fg_color=CARD,corner_radius=14); box.grid(row=3,column=0,sticky="nsew"); self.content.grid_rowconfigure(3,weight=1); t=self.tree(box,("SKU","Producto","Talla","Color","Precio","Stock"),(150,270,100,140,120,100))
        for x in self.service.variantes(): t.insert("","end",values=(x.sku,x.producto.nombre,x.talla,x.color,f"S/ {x.precio_venta:.2f}",x.stock_actual))
    def page_movimientos(self):
        self.header("Movimientos","Registra compras, ventas y ajustes con trazabilidad"); f=ctk.CTkFrame(self.content,fg_color=CARD,corner_radius=14); f.grid(row=1,column=0,sticky="ew"); vs=self.service.variantes(); cmb=ctk.CTkComboBox(f,values=[f"{x.id} | {x.sku} | {x.producto.nombre} ({x.talla}/{x.color})" for x in vs] or ["No hay variantes"]); cmb.grid(row=1,column=0,padx=12,pady=(0,14),sticky="ew"); kind=ctk.CTkComboBox(f,values=["ENTRADA","VENTA","AJUSTE"]); kind.grid(row=1,column=1,padx=8,pady=(0,14)); qty=ctk.CTkEntry(f,placeholder_text="Cantidad"); qty.grid(row=1,column=2,padx=8,pady=(0,14)); why=ctk.CTkEntry(f,placeholder_text="Motivo / comprobante"); why.grid(row=1,column=3,padx=8,pady=(0,14),sticky="ew"); [f.grid_columnconfigure(i,weight=1) for i in (0,3)]
        for i,label in enumerate(("Variante","Tipo","Cantidad","Motivo / referencia")): ctk.CTkLabel(f,text=label,text_color=MUTED).grid(row=0,column=i,padx=12,pady=(12,2),sticky="w")
        def save():
            try: self.service.registrar_movimiento(int(cmb.get().split(" | ")[0]),kind.get(),int(qty.get()),why.get()); self.show("movimientos")
            except (InventoryError,ValueError,IndexError) as e: messagebox.showerror("Validación",str(e))
        ctk.CTkButton(f,text="Registrar",fg_color=ACCENT,command=save).grid(row=1,column=4,padx=12,pady=(0,14)); ctk.CTkLabel(self.content,text="Una venta descuenta stock; entrada y ajuste lo incrementan.",text_color=MUTED).grid(row=2,column=0,sticky="w",pady=12)
    def page_historial(self):
        self.header("Historial","Últimos 100 movimientos de inventario"); box=ctk.CTkFrame(self.content,fg_color=CARD,corner_radius=14); box.grid(row=1,column=0,sticky="nsew"); self.content.grid_rowconfigure(1,weight=1); t=self.tree(box,("Fecha","Tipo","SKU","Producto","Talla","Cantidad","Motivo"),(155,100,115,220,80,90,240))
        for m in self.service.movimientos(): t.insert("","end",values=(m.creado_en.strftime("%d/%m/%Y %H:%M"),m.tipo.value,m.variante.sku,m.variante.producto.nombre,m.variante.talla,m.cantidad,m.motivo))
