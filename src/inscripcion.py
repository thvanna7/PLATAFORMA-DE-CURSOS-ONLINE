# inscripcion.py
from db_connection import get_conn
from datetime import date

class Inscripcion:
    def __init__(self, id_, idEstudiante, idCurso, fecha, estado='activa'):
        self.id = id_
        self.idEstudiante = idEstudiante
        self.idCurso = idCurso
        self.fecha = fecha
        self.estado = estado
    
    @classmethod
    def crear(cls, idEstudiante, idCurso, fecha=None):
        conn = get_conn()
        try:
            cur = conn.cursor()
            
            # Verificar que no esté ya inscrito
            cur.execute(
                "SELECT id FROM inscripciones WHERE idEstudiante = %s AND idCurso = %s",
                (idEstudiante, idCurso)
            )
            if cur.fetchone():
                raise ValueError("El estudiante ya está inscrito en este curso")
            
            fecha_inscripcion = fecha if fecha else date.today()
            
            cur.execute(
                "INSERT INTO inscripciones (idEstudiante, idCurso, fecha, estado) VALUES (%s, %s, %s, %s)",
                (idEstudiante, idCurso, fecha_inscripcion, 'activa')
            )
            conn.commit()
            iid = cur.lastrowid
            return cls(iid, idEstudiante, idCurso, fecha_inscripcion, 'activa')
        finally:
            cur.close()
            conn.close()
    
    @classmethod
    def listar_todas(cls):
        conn = get_conn()
        try:
            cur = conn.cursor()
            cur.execute("SELECT id, idEstudiante, idCurso, fecha, estado FROM inscripciones ORDER BY fecha DESC")
            rows = cur.fetchall()
            return [cls(r[0], r[1], r[2], r[3], r[4]) for r in rows]
        finally:
            cur.close()
            conn.close()
    
    @classmethod
    def obtener_por_estudiante(cls, idEstudiante):
        conn = get_conn()
        try:
            cur = conn.cursor()
            cur.execute("SELECT id, idEstudiante, idCurso, fecha, estado FROM inscripciones WHERE idEstudiante = %s ORDER BY fecha DESC", (idEstudiante,))
            rows = cur.fetchall()
            return [cls(r[0], r[1], r[2], r[3], r[4]) for r in rows]
        finally:
            cur.close()
            conn.close()
    
    @classmethod
    def obtener_por_curso(cls, idCurso):
        conn = get_conn()
        try:
            cur = conn.cursor()
            cur.execute("SELECT id, idEstudiante, idCurso, fecha, estado FROM inscripciones WHERE idCurso = %s ORDER BY fecha DESC", (idCurso,))
            rows = cur.fetchall()
            return [cls(r[0], r[1], r[2], r[3], r[4]) for r in rows]
        finally:
            cur.close()
            conn.close()
    
    def actualizar_estado(self, nuevo_estado):
        """Actualizar el estado de la inscripción"""
        conn = get_conn()
        try:
            cur = conn.cursor()
            cur.execute("UPDATE inscripciones SET estado = %s WHERE id = %s", (nuevo_estado, self.id))
            conn.commit()
            self.estado = nuevo_estado
            return True
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cur.close()
            conn.close()
    
    def __str__(self):
        return f"Inscripción #{self.id} - Estudiante: {self.idEstudiante}, Curso: {self.idCurso} ({self.estado})"