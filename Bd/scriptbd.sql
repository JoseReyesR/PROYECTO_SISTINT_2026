CREATE DATABASE IF NOT EXISTS chatbot_siagie_db DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE chatbot_siagie_db;

-- ==============================================================================
-- 1. GESTIÓN DE USUARIOS Y ROLES
-- ==============================================================================

CREATE TABLE roles (
    id_rol INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL UNIQUE
) ENGINE=InnoDB;

INSERT INTO roles (nombre) VALUES ('Administrativo'), ('Docente'), ('Tutor_Padre'), ('Estudiante');

CREATE TABLE usuarios (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    rol_id INT NOT NULL,
    username VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (rol_id) REFERENCES roles(id_rol)
) ENGINE=InnoDB;

-- ==============================================================================
-- 2. ENTORNO ACADÉMICO (SIMULACIÓN SIAGIE)
-- ==============================================================================

-- Cumpliendo con la Ley de Protección de Datos Personales, los estudiantes se registran de forma anonimizada.
CREATE TABLE estudiantes (
    id_estudiante INT AUTO_INCREMENT PRIMARY KEY,
    codigo_anonimizado VARCHAR(50) NOT NULL UNIQUE,
    nivel_educativo VARCHAR(20) NOT NULL, -- Primaria, Secundaria
    grado INT NOT NULL,
    seccion VARCHAR(5) NOT NULL,
    estado_riesgo VARCHAR(20) DEFAULT 'Evaluando' -- Para almacenar la predicción (Bajo, Medio, Alto)
) ENGINE=InnoDB;

CREATE TABLE profesores (
    id_profesor INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NOT NULL,
    nombres VARCHAR(100) NOT NULL,
    especialidad VARCHAR(100),
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
) ENGINE=InnoDB;

CREATE TABLE cursos (
    id_curso INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    grado INT NOT NULL,
    id_profesor INT NOT NULL,
    FOREIGN KEY (id_profesor) REFERENCES profesores(id_profesor)
) ENGINE=InnoDB;

CREATE TABLE matriculas (
    id_matricula INT AUTO_INCREMENT PRIMARY KEY,
    id_estudiante INT NOT NULL,
    id_curso INT NOT NULL,
    anio_escolar INT NOT NULL,
    FOREIGN KEY (id_estudiante) REFERENCES estudiantes(id_estudiante),
    FOREIGN KEY (id_curso) REFERENCES cursos(id_curso)
) ENGINE=InnoDB;

-- ==============================================================================
-- 3. VARIABLES PARA EL MODELO PREDICTIVO DE RIESGO ACADÉMICO (REGRESIÓN LINEAL)
-- ==============================================================================

CREATE TABLE asistencias (
    id_asistencia INT AUTO_INCREMENT PRIMARY KEY,
    id_matricula INT NOT NULL,
    fecha DATE NOT NULL,
    estado ENUM('Presente', 'Ausente', 'Tardanza', 'Justificado') NOT NULL, -- Detecta patrones de inasistencia
    FOREIGN KEY (id_matricula) REFERENCES matriculas(id_matricula)
) ENGINE=InnoDB;

CREATE TABLE tareas (
    id_tarea INT AUTO_INCREMENT PRIMARY KEY,
    id_curso INT NOT NULL,
    titulo VARCHAR(150) NOT NULL,
    fecha_vencimiento DATE NOT NULL,
    FOREIGN KEY (id_curso) REFERENCES cursos(id_curso)
) ENGINE=InnoDB;

CREATE TABLE estado_tareas (
    id_estado_tarea INT AUTO_INCREMENT PRIMARY KEY,
    id_tarea INT NOT NULL,
    id_estudiante INT NOT NULL,
    estado ENUM('Entregada', 'Pendiente', 'Atrasada') NOT NULL, -- Variables de riesgo (tareas pendientes/entregadas)[cite: 2]
    calificacion DECIMAL(4,2) DEFAULT NULL,
    FOREIGN KEY (id_tarea) REFERENCES tareas(id_tarea),
    FOREIGN KEY (id_estudiante) REFERENCES estudiantes(id_estudiante)
) ENGINE=InnoDB;

-- ==============================================================================
-- 4. GESTIÓN DEL CHATBOT Y CAPACIDADES MULTIMODALES
-- ==============================================================================

CREATE TABLE intenciones_nlp (
    id_intencion INT AUTO_INCREMENT PRIMARY KEY,
    nombre_intencion VARCHAR(50) NOT NULL UNIQUE, -- Ej: pagos, matricula, horarios, soporte[cite: 2]
    respuesta_predefinida TEXT NOT NULL
) ENGINE=InnoDB;

-- Almacena las interacciones del agente dinámico y episódico[cite: 4].
CREATE TABLE historial_consultas (
    id_consulta INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NOT NULL, -- Identifica si es tutor, docente o administrativo
    id_intencion INT,
    mensaje_texto TEXT, -- Entrada procesada o convertida vía Speech-to-Text[cite: 4]
    modalidad ENUM('Texto', 'Voz', 'Imagen') NOT NULL,
    fecha_consulta TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario),
    FOREIGN KEY (id_intencion) REFERENCES intenciones_nlp(id_intencion)
) ENGINE=InnoDB;

-- Tabla para la validación básica de formatos físicos (ej. DNI, Vouchers de APAFA/Matrícula)[cite: 4].
CREATE TABLE archivos_validacion (
    id_archivo INT AUTO_INCREMENT PRIMARY KEY,
    id_consulta INT NOT NULL,
    tipo_documento ENUM('DNI', 'Voucher', 'Otro') NOT NULL,
    ruta_archivo VARCHAR(255) NOT NULL,
    resultado_ia_visual VARCHAR(100), -- Resultado de la extracción de características visuales[cite: 2]
    fecha_subida TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_consulta) REFERENCES historial_consultas(id_consulta) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ==============================================================================
-- 5. TABLAS FALTANTES PARA EL MODELO DE PERFILAMIENTO E INTENCIONES
-- ==============================================================================

CREATE TABLE pagos (
    id_pago INT AUTO_INCREMENT PRIMARY KEY,
    id_estudiante INT NOT NULL,
    concepto VARCHAR(100) NOT NULL, -- Ej: 'Pensión de Marzo'
    monto DECIMAL(10,2) NOT NULL,
    estado ENUM('Pagado', 'Pendiente', 'Vencido') NOT NULL,
    fecha_vencimiento DATE NOT NULL,
    fecha_pago DATE DEFAULT NULL,
    FOREIGN KEY (id_estudiante) REFERENCES estudiantes(id_estudiante)
) ENGINE=InnoDB;

CREATE TABLE horarios (
    id_horario INT AUTO_INCREMENT PRIMARY KEY,
    id_curso INT NOT NULL,
    dia_semana ENUM('Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado') NOT NULL,
    hora_inicio TIME NOT NULL,
    hora_fin TIME NOT NULL,
    FOREIGN KEY (id_curso) REFERENCES cursos(id_curso)
) ENGINE=InnoDB;


-- ==============================================================================
-- 6. VISTAS PARA EL ENTRENAMIENTO DE LOS MODELOS DE MACHINE LEARNING
-- ==============================================================================

-- Vista para el Modelo Predictivo de Notas (Regresión Lineal)
CREATE VIEW dataset_rendimiento AS
SELECT 
    e.id_estudiante,
    c.id_curso,
    AVG(et.calificacion) AS promedio_actual,
    SUM(CASE WHEN et.estado = 'Entregada' THEN 1 ELSE 0 END) AS tareas_entregadas,
    SUM(CASE WHEN et.estado = 'Pendiente' OR et.estado = 'Atrasada' THEN 1 ELSE 0 END) AS tareas_pendientes
FROM estudiantes e
JOIN matriculas m ON e.id_estudiante = m.id_estudiante
JOIN cursos c ON m.id_curso = c.id_curso
LEFT JOIN estado_tareas et ON e.id_estudiante = et.id_estudiante
GROUP BY e.id_estudiante, c.id_curso;

-- Vista para el Modelo de Perfilamiento de Usuario (Regresión Logística)
CREATE VIEW dataset_perfil_usuario AS
SELECT 
    e.id_estudiante,
    COUNT(DISTINCT m.id_curso) AS cursos_matriculados,
    (SELECT COUNT(*) FROM pagos p WHERE p.id_estudiante = e.id_estudiante AND p.estado = 'Pagado') AS pagos_realizados,
    (SELECT COUNT(*) FROM estado_tareas et WHERE et.id_estudiante = e.id_estudiante AND et.estado = 'Entregada') AS tareas_entregadas_total
FROM estudiantes e
LEFT JOIN matriculas m ON e.id_estudiante = m.id_estudiante
GROUP BY e.id_estudiante;