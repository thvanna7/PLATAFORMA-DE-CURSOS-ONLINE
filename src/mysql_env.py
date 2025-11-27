from db_connection import create_connection, close_connection


def create_table_usuarios(conn):
    """Crea la tabla usuarios (base para estudiantes e instructores)"""
    query = """
        CREATE TABLE IF NOT EXISTS usuarios (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nombre VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            tipo_usuario ENUM('estudiante', 'instructor') NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB;
    """
    cursor = conn.cursor()
    cursor.execute(query)
    conn.commit()
    print("Table 'usuarios' created.")
    cursor.close()


def create_table_estudiantes(conn):
    """Crea la tabla estudiantes"""
    query = """
        CREATE TABLE IF NOT EXISTS estudiantes (
            id INT AUTO_INCREMENT PRIMARY KEY,
            usuario_id INT NOT NULL UNIQUE,
            progreso FLOAT DEFAULT 0.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
        ) ENGINE=InnoDB;
    """
    cursor = conn.cursor()
    cursor.execute(query)
    conn.commit()
    print("Table 'estudiantes' created.")
    cursor.close()


def create_table_instructores(conn):
    """Crea la tabla instructores"""
    query = """
        CREATE TABLE IF NOT EXISTS instructores (
            id INT AUTO_INCREMENT PRIMARY KEY,
            usuario_id INT NOT NULL UNIQUE,
            especialidad VARCHAR(100),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
        ) ENGINE=InnoDB;
    """
    cursor = conn.cursor()
    cursor.execute(query)
    conn.commit()
    print("Table 'instructores' created.")
    cursor.close()


def create_table_cursos(conn):
    """Crea la tabla cursos"""
    query = """
        CREATE TABLE IF NOT EXISTS cursos (
            id INT AUTO_INCREMENT PRIMARY KEY,
            instructor_id INT NOT NULL,
            titulo VARCHAR(200) NOT NULL,
            descripcion TEXT,
            precio DECIMAL(10, 2) NOT NULL,
            estado ENUM('borrador', 'publicado') DEFAULT 'borrador',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (instructor_id) REFERENCES instructores(id) ON DELETE CASCADE
        ) ENGINE=InnoDB;
    """
    cursor = conn.cursor()
    cursor.execute(query)
    conn.commit()
    print("Table 'cursos' created.")
    cursor.close()


def create_table_contenidos(conn):
    """Crea la tabla contenidos del curso"""
    query = """
        CREATE TABLE IF NOT EXISTS contenidos (
            id INT AUTO_INCREMENT PRIMARY KEY,
            curso_id INT NOT NULL,
            tipo ENUM('video', 'documento', 'lectura') NOT NULL,
            nombre VARCHAR(200) NOT NULL,
            url VARCHAR(500),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (curso_id) REFERENCES cursos(id) ON DELETE CASCADE
        ) ENGINE=InnoDB;
    """
    cursor = conn.cursor()
    cursor.execute(query)
    conn.commit()
    print("Table 'contenidos' created.")
    cursor.close()


def create_table_inscripciones(conn):
    """Crea la tabla inscripciones"""
    query = """
        CREATE TABLE IF NOT EXISTS inscripciones (
            id INT AUTO_INCREMENT PRIMARY KEY,
            estudiante_id INT NOT NULL,
            curso_id INT NOT NULL,
            fecha_inscripcion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            estado ENUM('activo', 'completado') DEFAULT 'activo',
            FOREIGN KEY (estudiante_id) REFERENCES estudiantes(id) ON DELETE CASCADE,
            FOREIGN KEY (curso_id) REFERENCES cursos(id) ON DELETE CASCADE,
            UNIQUE KEY (estudiante_id, curso_id)
        ) ENGINE=InnoDB;
    """
    cursor = conn.cursor()
    cursor.execute(query)
    conn.commit()
    print("Table 'inscripciones' created.")
    cursor.close()


def main():
    """Función principal"""
    conn = create_connection()
    if conn:
        # Crear tablas
        create_table_usuarios(conn)
        create_table_estudiantes(conn)
        create_table_instructores(conn)
        create_table_cursos(conn)
        create_table_contenidos(conn)
        create_table_inscripciones(conn)
        close_connection(conn)


if __name__ == "__main__":
    main()