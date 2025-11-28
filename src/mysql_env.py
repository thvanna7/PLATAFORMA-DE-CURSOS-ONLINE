from db_connection import create_connection, close_connection

def create_table_usuarios(conn):
    query = """
        CREATE TABLE IF NOT EXISTS usuarios (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nombre VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            password VARCHAR(255),
            tipoUsuario ENUM('estudiante', 'instructor', 'administrador') NOT NULL DEFAULT 'estudiante',
            progreso FLOAT DEFAULT 0.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB;
    """
    cursor = conn.cursor()
    cursor.execute(query)
    conn.commit()
    print("Table 'usuarios' created.")
    cursor.close()


def create_table_cursos(conn):
    query = """
        CREATE TABLE IF NOT EXISTS cursos (
            id INT AUTO_INCREMENT PRIMARY KEY,
            titulo VARCHAR(200) NOT NULL,
            descripcion TEXT,
            precio FLOAT NOT NULL,
            idInstructor INT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (idInstructor) REFERENCES usuarios(id) ON DELETE CASCADE
        ) ENGINE=InnoDB;
    """
    cursor = conn.cursor()
    cursor.execute(query)
    conn.commit()
    print("Table 'cursos' created.")
    cursor.close()


def create_table_inscripciones(conn):
    query = """
        CREATE TABLE IF NOT EXISTS inscripciones (
            id INT AUTO_INCREMENT PRIMARY KEY,
            idEstudiante INT NOT NULL,
            idCurso INT NOT NULL,
            fecha DATE NOT NULL,
            estado ENUM('activa', 'completada', 'cancelada') DEFAULT 'activa',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (idEstudiante) REFERENCES usuarios(id) ON DELETE CASCADE,
            FOREIGN KEY (idCurso) REFERENCES cursos(id) ON DELETE CASCADE,
            UNIQUE KEY unique_inscripcion (idEstudiante, idCurso)
        ) ENGINE=InnoDB;
    """
    cursor = conn.cursor()
    cursor.execute(query)
    conn.commit()
    print("Table 'inscripciones' created.")
    cursor.close()


def main():
    conn = create_connection()
    if conn:
        create_table_usuarios(conn)
        create_table_cursos(conn)
        create_table_inscripciones(conn)
        close_connection(conn)
        print("\n Database setup completed.")


if __name__ == "__main__":
    main()