USE chatbot_siagie_db;

-- 1. Insertar Estudiantes (Simulación de 5 alumnos)
INSERT INTO estudiantes (codigo_anonimizado, nivel_educativo, grado, seccion) VALUES
('EST-001', 'Secundaria', 3, 'A'),
('EST-002', 'Secundaria', 3, 'A'),
('EST-003', 'Secundaria', 4, 'B'),
('EST-004', 'Secundaria', 5, 'A'),
('EST-005', 'Secundaria', 5, 'B');

-- 2. Insertar Usuarios y Profesores para respetar las llaves foráneas
INSERT INTO usuarios (rol_id, username, password_hash) VALUES 
(2, 'profesor_mate', 'hash123'),
(2, 'profesor_fisica', 'hash456');

INSERT INTO profesores (id_usuario, nombres, especialidad) VALUES 
(1, 'Carlos Mendoza', 'Matemáticas'),
(2, 'Ana Torres', 'Física');

-- 3. Insertar Cursos
INSERT INTO cursos (nombre, grado, id_profesor) VALUES
('Matemática Básica', 3, 1),
('Física Elemental', 4, 2);

-- 4. Insertar Matrículas
INSERT INTO matriculas (id_estudiante, id_curso, anio_escolar) VALUES
(1, 1, 2026), (2, 1, 2026), (3, 2, 2026), (4, 2, 2026), (5, 2, 2026);

-- 5. Insertar Tareas (Para que el modelo calcule tareas pendientes/entregadas)
INSERT INTO tareas (id_curso, titulo, fecha_vencimiento) VALUES
(1, 'Ecuaciones de 1er Grado', '2026-10-01'),
(1, 'Ecuaciones de 2do Grado', '2026-10-08'),
(2, 'Cinemática', '2026-10-05');

-- 6. Insertar Estado de Tareas (Variables de riesgo académico)
-- Estudiante 1: Buen rendimiento (Entregó todo)
INSERT INTO estado_tareas (id_tarea, id_estudiante, estado, calificacion) VALUES
(1, 1, 'Entregada', 18.5),
(2, 1, 'Entregada', 17.0);

-- Estudiante 2: Riesgo Académico (Atrasado y pendiente)
INSERT INTO estado_tareas (id_tarea, id_estudiante, estado, calificacion) VALUES
(1, 2, 'Atrasada', 10.0),
(2, 2, 'Pendiente', NULL);

-- Estudiante 3, 4 y 5: Rendimiento mixto
INSERT INTO estado_tareas (id_tarea, id_estudiante, estado, calificacion) VALUES
(3, 3, 'Entregada', 13.5),
(3, 4, 'Pendiente', NULL),
(3, 5, 'Entregada', 15.0);

-- 7. Insertar Pagos (Necesario para el modelo de perfilamiento y chatbot)
INSERT INTO pagos (id_estudiante, concepto, monto, estado, fecha_vencimiento) VALUES
(1, 'Pensión Marzo', 450.00, 'Pagado', '2026-03-31'),
(2, 'Pensión Marzo', 450.00, 'Pendiente', '2026-03-31'),
(3, 'Pensión Marzo', 450.00, 'Vencido', '2026-03-31');

-- 8. Insertar Horarios
INSERT INTO horarios (id_curso, dia_semana, hora_inicio, hora_fin) VALUES
(1, 'Lunes', '08:00:00', '10:00:00'),
(2, 'Martes', '10:00:00', '12:00:00');

-- 9. Insertar Intenciones Base para el Chatbot de texto/voz
INSERT INTO intenciones_nlp (nombre_intencion, respuesta_predefinida) VALUES
('pagos', 'Aquí tienes el estado de tus pagos:'),
('horarios', 'Este es tu horario programado:'),
('notas', 'Tu rendimiento académico actual es:'),
('tareas', 'Estas son tus tareas asignadas:');