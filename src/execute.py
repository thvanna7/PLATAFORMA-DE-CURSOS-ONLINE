import sys
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

from usuario import Usuario, Estudiante, Instructor, Administrador, hash_password

current_user = None  # objeto Usuario autenticado

# Código admin
CODIGO_ADMIN = "ADMIN2025"

# --------------------------
# Funciones de la aplicación
# --------------------------

def login_inicial():
    """Solicita credenciales al iniciar la aplicación"""
    global current_user

    tiene = messagebox.askyesno("Bienvenido al Sistema de Cursos", "¿Tienes una cuenta en el sistema?")
    if tiene is None:
        salir()
        return

    if not tiene:
        try:
            u = registrar_usuario_publico()
            if u:
                current_user = u
                lbl_help.config(text=f"Usuario conectado: {current_user.nombre} ({current_user.tipoUsuario})")
                ajustar_menu_por_rol()
                mostrar_bienvenida()
                return
            else:
                messagebox.showinfo("Info", "Registro cancelado. Se solicitará inicio de sesión.")
        except Exception as e:
            messagebox.showerror("Error", f"Error durante el registro:\n{e}")

    # Intentos iniciar sesión (3 intentos)
    for _ in range(3):
        email = simpledialog.askstring("Inicio de sesión", "Email:")
        if email is None:
            salir()
            return
        pwd = simpledialog.askstring("Inicio de sesión", "Contraseña:", show='*')
        if pwd is None:
            salir()
            return
        usuario = Usuario.autenticar(email.strip(), pwd)
        if usuario:
            current_user = usuario
            lbl_help.config(text=f"Usuario conectado: {current_user.nombre} ({current_user.tipoUsuario})")
            ajustar_menu_por_rol()
            mostrar_bienvenida()
            return
        else:
            retry = messagebox.askretrycancel("Error", "Credenciales incorrectas. ¿Deseas intentar de nuevo?")
            if not retry:
                want_reg = messagebox.askyesno("Registro", "¿Deseas registrarte ahora?")
                if want_reg:
                    try:
                        u = registrar_usuario_publico()
                        if u:
                            current_user = u
                            lbl_help.config(text=f"Usuario conectado: {current_user.nombre} ({current_user.tipoUsuario})")
                            ajustar_menu_por_rol()
                            mostrar_bienvenida()
                            return
                    except Exception as e:
                        messagebox.showerror("Error", f"Error durante el registro:\n{e}")
    messagebox.showerror("Error", "Demasiados intentos fallidos. Saliendo.")
    salir()


def registrar_usuario_publico():
    """Permite registrar un usuario (estudiante, instructor, admin)"""
    nombre = simpledialog.askstring("Registrar usuario", "Nombre completo:")
    if not nombre:
        return None
    
    email = simpledialog.askstring("Registrar usuario", "Email:")
    if not email:
        return None
    
    tipo = simpledialog.askstring("Registrar usuario", "Tipo (estudiante/instructor/administrador):", initialvalue="estudiante")
    if tipo is None:
        return None
    tipo = tipo.strip().lower()
    if tipo not in ('estudiante', 'instructor', 'administrador'):
        messagebox.showwarning("Tipo inválido", "Tipo inválido. Se usará 'estudiante'.")
        tipo = 'estudiante'
    
    if tipo == 'administrador':
        codigo = simpledialog.askstring("Código Admin", "Ingrese el código de administrador:", show='*')
        if codigo != CODIGO_ADMIN:
            messagebox.showerror("Código incorrecto", "El código de administrador es incorrecto.")
            return None
    
    pwd = simpledialog.askstring("Registrar usuario", "Contraseña:", show='*')
    if not pwd:
        messagebox.showwarning("Contraseña requerida", "La contraseña es obligatoria.")
        return None
    
    try:
        if tipo == 'estudiante':
            u = Estudiante.crear(nombre.strip(), email.strip(), pwd)
        elif tipo == 'instructor':
            u = Instructor.crear(nombre.strip(), email.strip(), pwd)
        else:
            u = Administrador.crear(nombre.strip(), email.strip(), pwd)
        
        messagebox.showinfo("OK", f"Usuario registrado: {u.nombre}")
        return u
    except Exception as e:
        messagebox.showerror("Error", f"Error al registrar usuario:\n{e}")
        return None


def mostrar_bienvenida():
    """Muestra mensaje de bienvenida según el rol"""
    lb_output.delete(0, tk.END)
    lb_output.insert(tk.END, f"¡Bienvenido/a {current_user.nombre}!")
    lb_output.insert(tk.END, f"Tipo de usuario: {current_user.tipoUsuario}")
    lb_output.insert(tk.END, "")
    
    if current_user.tipoUsuario == 'estudiante':
        lb_output.insert(tk.END, "Puedes:")
        lb_output.insert(tk.END, "  - Ver cursos disponibles")
        lb_output.insert(tk.END, "  - Inscribirte a cursos")
        lb_output.insert(tk.END, "  - Ver tu progreso")
    elif current_user.tipoUsuario == 'instructor':
        lb_output.insert(tk.END, "Puedes:")
        lb_output.insert(tk.END, "  - Crear nuevos cursos")
        lb_output.insert(tk.END, "  - Ver tus cursos")
        lb_output.insert(tk.END, "  - Ver estadísticas")
    else:
        lb_output.insert(tk.END, "Puedes:")
        lb_output.insert(tk.END, "  - Gestionar usuarios")
        lb_output.insert(tk.END, "  - Ver todos los cursos")
        lb_output.insert(tk.END, "  - Generar reportes")


# --- Funciones de Cursos ---

def crear_curso():
    """Permite al instructor crear un curso"""
    if current_user is None or current_user.tipoUsuario != 'instructor':
        messagebox.showerror("Permisos", "Solo los instructores pueden crear cursos.")
        return
    
    from curso import Curso
    
    titulo = simpledialog.askstring("Crear curso", "Título del curso:")
    if not titulo:
        return
    
    descripcion = simpledialog.askstring("Crear curso", "Descripción:")
    if not descripcion:
        return
    
    precio = simpledialog.askfloat("Crear curso", "Precio:", minvalue=0.0)
    if precio is None:
        return
    
    try:
        curso = current_user.crear_curso(titulo.strip(), descripcion.strip(), precio)
        messagebox.showinfo("OK", f"Curso creado: {curso.titulo} (ID: {curso.id})")
        listar_mis_cursos()
    except Exception as e:
        messagebox.showerror("Error", f"Error al crear curso:\n{e}")


def listar_cursos():
    """Lista todos los cursos disponibles"""
    from curso import Curso
    
    try:
        cursos = Curso.listar_todos()
        lb_output.delete(0, tk.END)
        if not cursos:
            lb_output.insert(tk.END, "No hay cursos disponibles.")
            return
        lb_output.insert(tk.END, "Cursos disponibles:")
        for c in cursos:
            lb_output.insert(tk.END, f"  [{c.id}] {c.titulo} - ${c.precio}")
    except Exception as e:
        messagebox.showerror("Error", f"Error al listar cursos:\n{e}")


def listar_mis_cursos():
    """Lista los cursos del instructor actual"""
    if current_user is None or current_user.tipoUsuario != 'instructor':
        return
    
    from curso import Curso
    
    try:
        cursos = Curso.buscar_por_instructor(current_user.id)
        lb_output.delete(0, tk.END)
        lb_output.insert(tk.END, f"Mis cursos ({current_user.nombre}):")
        if not cursos:
            lb_output.insert(tk.END, "  (No has creado cursos)")
            return
        for c in cursos:
            lb_output.insert(tk.END, f"  [{c.id}] {c.titulo} - ${c.precio}")
    except Exception as e:
        messagebox.showerror("Error", f"Error al listar tus cursos:\n{e}")


# --- Funciones de Inscripciones ---

def inscribirse_curso():
    """Permite al estudiante inscribirse a un curso"""
    if current_user is None or current_user.tipoUsuario != 'estudiante':
        messagebox.showerror("Permisos", "Solo los estudiantes pueden inscribirse.")
        return
    
    id_curso = simpledialog.askinteger("Inscribirse", "Ingresa el ID del curso:")
    if not id_curso:
        return
    
    try:
        inscripcion = current_user.inscribirse(id_curso)
        messagebox.showinfo("OK", f"Te has inscrito al curso #{id_curso}")
        ver_mis_inscripciones()
    except ValueError as ve:
        messagebox.showerror("Error", str(ve))
    except Exception as e:
        messagebox.showerror("Error", f"Error al inscribirse:\n{e}")


def ver_mis_inscripciones():
    """Muestra las inscripciones del estudiante"""
    if current_user is None or current_user.tipoUsuario != 'estudiante':
        return
    
    from inscripcion import Inscripcion
    from curso import Curso
    
    try:
        inscripciones = Inscripcion.obtener_por_estudiante(current_user.id)
        lb_output.delete(0, tk.END)
        lb_output.insert(tk.END, f"Mis inscripciones ({current_user.nombre}):")
        if not inscripciones:
            lb_output.insert(tk.END, "  (No estás inscrito en ningún curso)")
            return
        for i in inscripciones:
            curso = Curso.buscar_por_id(i.idCurso)
            lb_output.insert(tk.END, f"  [{i.id}] {curso.titulo} - Estado: {i.estado}")
    except Exception as e:
        messagebox.showerror("Error", f"Error al obtener inscripciones:\n{e}")


def ver_progreso():
    """Muestra el progreso del estudiante"""
    if current_user is None or current_user.tipoUsuario != 'estudiante':
        return
    
    try:
        progreso = current_user.ver_progreso()
        messagebox.showinfo("Mi progreso", f"Progreso actual: {progreso:.1f}%")
    except Exception as e:
        messagebox.showerror("Error", f"Error al obtener progreso:\n{e}")


# --- Funciones de Administrador ---

def ver_estadisticas():
    """Ver estadísticas (instructor)"""
    if current_user is None or current_user.tipoUsuario != 'instructor':
        messagebox.showerror("Permisos", "Solo instructores pueden ver estadísticas.")
        return
    
    try:
        stats = current_user.ver_estadisticas()
        lb_output.delete(0, tk.END)
        lb_output.insert(tk.END, "Estadísticas:")
        lb_output.insert(tk.END, f"  Total de cursos: {stats['total_cursos']}")
        lb_output.insert(tk.END, f"  Total de estudiantes: {stats['total_estudiantes']}")
    except Exception as e:
        messagebox.showerror("Error", f"Error al obtener estadísticas:\n{e}")


def generar_reporte():
    """Generar reporte del sistema (admin)"""
    if current_user is None or current_user.tipoUsuario != 'administrador':
        messagebox.showerror("Permisos", "Solo administradores pueden generar reportes.")
        return
    
    try:
        reporte = current_user.generar_reporte()
        lb_output.delete(0, tk.END)
        lb_output.insert(tk.END, "REPORTE DEL SISTEMA:")
        lb_output.insert(tk.END, f"  Total de usuarios: {reporte['total_usuarios']}")
        lb_output.insert(tk.END, f"  Total de cursos: {reporte['total_cursos']}")
        lb_output.insert(tk.END, f"  Total de inscripciones: {reporte['total_inscripciones']}")
    except Exception as e:
        messagebox.showerror("Error", f"Error al generar reporte:\n{e}")


def listar_usuarios():
    """Listar todos los usuarios (admin)"""
    if current_user is None or current_user.tipoUsuario != 'administrador':
        messagebox.showerror("Permisos", "Solo administradores pueden ver usuarios.")
        return
    
    try:
        usuarios = Usuario.listar_todos()
        lb_output.delete(0, tk.END)
        if not usuarios:
            lb_output.insert(tk.END, "No hay usuarios registrados.")
            return
        lb_output.insert(tk.END, "Usuarios:")
        for u in usuarios:
            lb_output.insert(tk.END, f"  [{u.id}] {u.nombre} - {u.tipoUsuario}")
    except Exception as e:
        messagebox.showerror("Error", f"Error al listar usuarios:\n{e}")


def salir():
    root.destroy()
    sys.exit(0)


def ajustar_menu_por_rol():
    """Habilita/deshabilita opciones según el rol"""
    if current_user is None:
        for i in range(acciones_menu.index(tk.END) + 1):
            try:
                acciones_menu.entryconfig(i, state="disabled")
            except:
                pass
        return

    if current_user.tipoUsuario == 'administrador':
        acciones_menu.entryconfig("Listar usuarios", state="normal")
        acciones_menu.entryconfig("Listar cursos", state="normal")
        acciones_menu.entryconfig("Generar reporte", state="normal")
        acciones_menu.entryconfig("Crear curso", state="disabled")
        acciones_menu.entryconfig("Mis cursos", state="disabled")
        acciones_menu.entryconfig("Ver estadísticas", state="disabled")
        acciones_menu.entryconfig("Inscribirse a curso", state="disabled")
        acciones_menu.entryconfig("Mis inscripciones", state="disabled")
        
    elif current_user.tipoUsuario == 'instructor':
        acciones_menu.entryconfig("Listar usuarios", state="disabled")
        acciones_menu.entryconfig("Listar cursos", state="normal")
        acciones_menu.entryconfig("Generar reporte", state="disabled")
        acciones_menu.entryconfig("Crear curso", state="normal")
        acciones_menu.entryconfig("Mis cursos", state="normal")
        acciones_menu.entryconfig("Ver estadísticas", state="normal")
        acciones_menu.entryconfig("Inscribirse a curso", state="disabled")
        acciones_menu.entryconfig("Mis inscripciones", state="disabled")

        
    else:  # estudiante
        acciones_menu.entryconfig("Listar usuarios", state="disabled")
        acciones_menu.entryconfig("Listar cursos", state="normal")
        acciones_menu.entryconfig("Generar reporte", state="disabled")
        acciones_menu.entryconfig("Crear curso", state="disabled")
        acciones_menu.entryconfig("Mis cursos", state="disabled")
        acciones_menu.entryconfig("Ver estadísticas", state="disabled")
        acciones_menu.entryconfig("Inscribirse a curso", state="normal")
        acciones_menu.entryconfig("Mis inscripciones", state="normal")



# ==================== INTERFAZ GRÁFICA ====================

root = tk.Tk()
root.title("Sistema de Cursos Online")
root.geometry("800x480")
root.minsize(700, 420)

menubar = tk.Menu(root)

# Menú "Acciones"
acciones_menu = tk.Menu(menubar, tearoff=0)
acciones_menu.add_command(label="Listar usuarios", command=listar_usuarios)
acciones_menu.add_command(label="Listar cursos", command=listar_cursos)
acciones_menu.add_command(label="Generar reporte", command=generar_reporte)
acciones_menu.add_separator()
acciones_menu.add_command(label="Crear curso", command=crear_curso)
acciones_menu.add_command(label="Mis cursos", command=listar_mis_cursos)
acciones_menu.add_command(label="Ver estadísticas", command=ver_estadisticas)
acciones_menu.add_separator()
acciones_menu.add_command(label="Inscribirse a curso", command=inscribirse_curso)
acciones_menu.add_command(label="Mis inscripciones", command=ver_mis_inscripciones)

menubar.add_cascade(label="Acciones", menu=acciones_menu)

# Menú "Archivo"
archivo_menu = tk.Menu(menubar, tearoff=0)
archivo_menu.add_command(label="Salir", command=salir)
menubar.add_cascade(label="Archivo", menu=archivo_menu)

root.config(menu=menubar)

# Frame principal
frame_output = ttk.Frame(root, padding=(12, 12))
frame_output.pack(side=tk.TOP, expand=True, fill=tk.BOTH)

lbl_output = ttk.Label(frame_output, text="Sistema de Cursos Online", font=("Segoe UI", 12, "bold"))
lbl_output.pack(anchor="w")

# Listbox con scrollbar
frame_list = ttk.Frame(frame_output)
frame_list.pack(fill=tk.BOTH, expand=True, pady=(6, 0))

sb = ttk.Scrollbar(frame_list, orient=tk.VERTICAL)
lb_output = tk.Listbox(frame_list, yscrollcommand=sb.set, font=("Consolas", 10))
sb.config(command=lb_output.yview)
sb.pack(side=tk.RIGHT, fill=tk.Y)
lb_output.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Mensaje de ayuda
lbl_help = ttk.Label(frame_output, text="Iniciando sistema...", font=("Segoe UI", 9))
lbl_help.pack(anchor="w", pady=(8, 0))

# Iniciar login
root.after(100, login_inicial)

root.mainloop()