from db_connection import get_conn

class Curso:
    def __init__(self, id_, titulo, descripcion, precio, idInstructor):
        self.id = id_
        self.titulo = titulo
        self.descripcion = descripcion
        self.precio = precio
        self.idInstructor = idInstructor
    
    @classmethod
    def crear(cls, titulo, descripcion, precio, idInstructor):
        conn = get_conn()
        try:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO cursos (titulo, descripcion, precio, idInstructor) VALUES (%s, %s, %s, %s)",
                (titulo, descripcion, precio, idInstructor)
            )
            conn.commit()
            cid = cur.lastrowid
            return cls(cid, titulo, descripcion, precio, idInstructor)
        finally:
            cur.close()
            conn.close()
    
    @classmethod
    def listar_todos(cls):
        conn = get_conn()
        try:
            cur = conn.cursor()
            cur.execute("SELECT id, titulo, descripcion, precio, idInstructor FROM cursos ORDER BY titulo")
            rows = cur.fetchall()
            return [cls(r[0], r[1], r[2], r[3], r[4]) for r in rows]
        finally:
            cur.close()
            conn.close()
    
    @classmethod
    def buscar_por_id(cls, id_):
        conn = get_conn()
        try:
            cur = conn.cursor()
            cur.execute("SELECT id, titulo, descripcion, precio, idInstructor FROM cursos WHERE id = %s", (id_,))
            r = cur.fetchone()
            return cls(r[0], r[1], r[2], r[3], r[4]) if r else None
        finally:
            cur.close()
            conn.close()
    
    @classmethod
    def buscar_por_instructor(cls, idInstructor):
        conn = get_conn()
        try:
            cur = conn.cursor()
            cur.execute("SELECT id, titulo, descripcion, precio, idInstructor FROM cursos WHERE idInstructor = %s ORDER BY titulo", (idInstructor,))
            rows = cur.fetchall()
            return [cls(r[0], r[1], r[2], r[3], r[4]) for r in rows]
        finally:
            cur.close()
            conn.close()
    
    def agregar_contenido(self, contenido):
        """Agregar contenido al curso (placeholder)"""
        pass
    
    def inscribir(self, id_estudiante):
        """Inscribir un estudiante al curso"""
        from inscripcion import Inscripcion
        return Inscripcion.crear(id_estudiante, self.id)
    
    def __str__(self):
        return f"{self.titulo} - ${self.precio}"