from db_connection import get_conn
import hashlib

def hash_password(password: str) -> str:
    if password is None:
        return None
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


class Usuario:
    def __init__(self, id_, nombre, email, tipoUsuario):
        self.id = id_
        self.nombre = nombre
        self.email = email
        self.tipoUsuario = tipoUsuario
    
    @classmethod
    def crear(cls, nombre, email, password, tipoUsuario='estudiante'):
        conn = get_conn()
        try:
            cur = conn.cursor()
            pwd_hash = hash_password(password) if password else None
            cur.execute(
                "INSERT INTO usuarios (nombre, email, password, tipoUsuario) VALUES (%s, %s, %s, %s)",
                (nombre, email, pwd_hash, tipoUsuario)
            )
            conn.commit()
            uid = cur.lastrowid
            return cls(uid, nombre, email, tipoUsuario)
        finally:
            cur.close()
            conn.close()
    
    def login(self):
        """Método login según UML"""
        return True
    
    def logout(self):
        """Método logout según UML"""
        return True
    
    def ver_panel(self):
        """Método ver_panel según UML"""
        pass
    
    @classmethod
    def listar_todos(cls):
        conn = get_conn()
        try:
            cur = conn.cursor()
            cur.execute("SELECT id, nombre, email, tipoUsuario FROM usuarios ORDER BY nombre")
            rows = cur.fetchall()
            return [cls(r[0], r[1], r[2], r[3]) for r in rows]
        finally:
            cur.close()
            conn.close()
    
    @classmethod
    def buscar_por_email(cls, email):
        conn = get_conn()
        try:
            cur = conn.cursor()
            cur.execute("SELECT id, nombre, email, tipoUsuario FROM usuarios WHERE email = %s", (email,))
            r = cur.fetchone()
            return cls(r[0], r[1], r[2], r[3]) if r else None
        finally:
            cur.close()
            conn.close()
    
    @classmethod
    def autenticar(cls, email, password):
        conn = get_conn()
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT id, nombre, email, tipoUsuario, password FROM usuarios WHERE email = %s",
                (email,)
            )
            r = cur.fetchone()
            if not r:
                return None
            stored_hash = r[4]
            if stored_hash is None or hash_password(password) != stored_hash:
                return None
            
            # Devolver Estudiante, Instructor o Administrador según tipo
            if r[3] == 'estudiante':
                return Estudiante.buscar_por_id(r[0])
            elif r[3] == 'instructor':
                return Instructor.buscar_por_id(r[0])
            else:
                return Administrador.buscar_por_id(r[0])
        finally:
            cur.close()
            conn.close()


class Estudiante(Usuario):
    def __init__(self, id_, nombre, email, tipoUsuario, progreso=0.0):
        super().__init__(id_, nombre, email, tipoUsuario)
        self.progreso = progreso
    
    @classmethod
    def crear(cls, nombre, email, password):
        conn = get_conn()
        try:
            cur = conn.cursor()
            pwd_hash = hash_password(password) if password else None
            cur.execute(
                "INSERT INTO usuarios (nombre, email, password, tipoUsuario, progreso) VALUES (%s, %s, %s, %s, %s)",
                (nombre, email, pwd_hash, 'estudiante', 0.0)
            )
            conn.commit()
            uid = cur.lastrowid
            return cls(uid, nombre, email, 'estudiante', 0.0)
        finally:
            cur.close()
            conn.close()
    
    @classmethod
    def buscar_por_id(cls, id_):
        conn = get_conn()
        try:
            cur = conn.cursor()
            cur.execute("SELECT id, nombre, email, tipoUsuario, progreso FROM usuarios WHERE id = %s", (id_,))
            r = cur.fetchone()
            return cls(r[0], r[1], r[2], r[3], r[4]) if r else None
        finally:
            cur.close()
            conn.close()
    
    def inscribirse(self, id_curso):
        """Inscribirse a un curso"""
        from inscripcion import Inscripcion
        return Inscripcion.crear(self.id, id_curso)
    
    def ver_progreso(self):
        """Ver progreso del estudiante"""
        conn = get_conn()
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT COUNT(*) FROM inscripciones WHERE idEstudiante = %s AND estado = 'completada'",
                (self.id,)
            )
            completados = cur.fetchone()[0]
            cur.execute(
                "SELECT COUNT(*) FROM inscripciones WHERE idEstudiante = %s",
                (self.id,)
            )
            total = cur.fetchone()[0]
            if total == 0:
                return 0.0
            return (completados / total) * 100
        finally:
            cur.close()
            conn.close()


class Instructor(Usuario):
    def __init__(self, id_, nombre, email, tipoUsuario):
        super().__init__(id_, nombre, email, tipoUsuario)
    
    @classmethod
    def crear(cls, nombre, email, password):
        conn = get_conn()
        try:
            cur = conn.cursor()
            pwd_hash = hash_password(password) if password else None
            cur.execute(
                "INSERT INTO usuarios (nombre, email, password, tipoUsuario) VALUES (%s, %s, %s, %s)",
                (nombre, email, pwd_hash, 'instructor')
            )
            conn.commit()
            uid = cur.lastrowid
            return cls(uid, nombre, email, 'instructor')
        finally:
            cur.close()
            conn.close()
    
    @classmethod
    def buscar_por_id(cls, id_):
        conn = get_conn()
        try:
            cur = conn.cursor()
            cur.execute("SELECT id, nombre, email, tipoUsuario FROM usuarios WHERE id = %s", (id_,))
            r = cur.fetchone()
            return cls(r[0], r[1], r[2], r[3]) if r else None
        finally:
            cur.close()
            conn.close()
    
    @classmethod
    def listar_instructores(cls):
        conn = get_conn()
        try:
            cur = conn.cursor()
            cur.execute("SELECT id, nombre, email, tipoUsuario FROM usuarios WHERE tipoUsuario = 'instructor' ORDER BY nombre")
            rows = cur.fetchall()
            return [cls(r[0], r[1], r[2], r[3]) for r in rows]
        finally:
            cur.close()
            conn.close()
    
    def crear_curso(self, titulo, descripcion, precio):
        """Crear un nuevo curso"""
        from curso import Curso
        return Curso.crear(titulo, descripcion, precio, self.id)
    
    def publicar_curso(self, id_curso):
        """Publicar un curso (por ahora solo retorna True)"""
        return True
    
    def ver_estadisticas(self):
        """Ver estadísticas de cursos del instructor"""
        conn = get_conn()
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT COUNT(*) FROM cursos WHERE idInstructor = %s",
                (self.id,)
            )
            total_cursos = cur.fetchone()[0]
            cur.execute(
                "SELECT COUNT(*) FROM inscripciones i JOIN cursos c ON i.idCurso = c.id WHERE c.idInstructor = %s",
                (self.id,)
            )
            total_estudiantes = cur.fetchone()[0]
            return {
                'total_cursos': total_cursos,
                'total_estudiantes': total_estudiantes
            }
        finally:
            cur.close()
            conn.close()


class Administrador(Usuario):
    def __init__(self, id_, nombre, email, tipoUsuario):
        super().__init__(id_, nombre, email, tipoUsuario)
    
    @classmethod
    def crear(cls, nombre, email, password):
        conn = get_conn()
        try:
            cur = conn.cursor()
            pwd_hash = hash_password(password) if password else None
            cur.execute(
                "INSERT INTO usuarios (nombre, email, password, tipoUsuario) VALUES (%s, %s, %s, %s)",
                (nombre, email, pwd_hash, 'administrador')
            )
            conn.commit()
            uid = cur.lastrowid
            return cls(uid, nombre, email, 'administrador')
        finally:
            cur.close()
            conn.close()
    
    @classmethod
    def buscar_por_id(cls, id_):
        conn = get_conn()
        try:
            cur = conn.cursor()
            cur.execute("SELECT id, nombre, email, tipoUsuario FROM usuarios WHERE id = %s", (id_,))
            r = cur.fetchone()
            return cls(r[0], r[1], r[2], r[3]) if r else None
        finally:
            cur.close()
            conn.close()
    
    def aprobar_curso(self, id_curso):
        """Aprobar un curso"""
        return True
    
    def generar_reporte(self):
        """Generar reporte del sistema"""
        conn = get_conn()
        try:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM usuarios")
            total_usuarios = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM cursos")
            total_cursos = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM inscripciones")
            total_inscripciones = cur.fetchone()[0]
            return {
                'total_usuarios': total_usuarios,
                'total_cursos': total_cursos,
                'total_inscripciones': total_inscripciones
            }
        finally:
            cur.close()
            conn.close()
    
    def gestionar_usuarios(self):
        """Gestionar usuarios (método placeholder)"""
        pass