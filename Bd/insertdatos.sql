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


--USE chatbot_siagie_db;

-- 1. Ampliar Roles y Usuarios (Añadiendo tutores y más alumnos)
INSERT IGNORE INTO usuarios (id_usuario, rol_id, username, password_hash) VALUES 
(3, 3, 'tutor_maria', 'hash789'),
(4, 4, 'alumno_nuevo', 'hash111');

-- 2. Insertar Estudiantes con diferentes perfiles
INSERT IGNORE INTO estudiantes (id_estudiante, codigo_anonimizado, nivel_educativo, grado, seccion) VALUES
(6, 'EST-006', 'Primaria', 6, 'A'),
(7, 'EST-007', 'Secundaria', 1, 'B'),
(8, 'EST-008', 'Secundaria', 5, 'C');

-- 3. Nuevos Profesores y Cursos
INSERT IGNORE INTO profesores (id_profesor, id_usuario, nombres, especialidad) VALUES 
(3, 3, 'Luis Ramos', 'Historia y Geografía');

INSERT IGNORE INTO cursos (id_curso, nombre, grado, id_profesor) VALUES
(3, 'Historia del Perú', 5, 3),
(4, 'Comunicación Integral', 1, 3);

-- 4. Matricular a los nuevos estudiantes
INSERT IGNORE INTO matriculas (id_matricula, id_estudiante, id_curso, anio_escolar) VALUES
(6, 6, 4, 2026), (7, 7, 4, 2026), (8, 8, 3, 2026);

-- 5. Expandir el historial de Tareas
INSERT IGNORE INTO tareas (id_tarea, id_curso, titulo, fecha_vencimiento) VALUES
(4, 3, 'Ensayo sobre la Independencia', '2026-11-15'),
(5, 4, 'Comprensión Lectora: Tradiciones Peruanas', '2026-11-20');

-- Insertar Estados de Tareas Variados (Para mejorar el modelo predictivo)
INSERT IGNORE INTO estado_tareas (id_tarea, id_estudiante, estado, calificacion) VALUES
(4, 8, 'Atrasada', 08.0),
(4, 8, 'Entregada', 14.5),
(5, 7, 'Pendiente', NULL);

-- 6. Ampliar el registro de Pagos y Deudas
INSERT IGNORE INTO pagos (id_pago, id_estudiante, concepto, monto, estado, fecha_vencimiento) VALUES
(4, 6, 'Matrícula 2026', 200.00, 'Pagado', '2026-02-15'),
(5, 7, 'Pensión Abril', 450.00, 'Vencido', '2026-04-30'),
(6, 8, 'Cuota APAFA', 50.00, 'Pendiente', '2026-12-01');

-- 7. Nuevos Horarios
INSERT IGNORE INTO horarios (id_horario, id_curso, dia_semana, hora_inicio, hora_fin) VALUES
(3, 3, 'Miércoles', '14:00:00', '16:00:00'),
(4, 4, 'Jueves', '09:00:00', '11:00:00');

-- 8. Alimentar las inasistencias (Para activar el modelo de riesgo)
INSERT IGNORE INTO asistencias (id_asistencia, id_matricula, fecha, estado) VALUES
(1, 8, '2026-09-10', 'Ausente'),
(2, 8, '2026-09-12', 'Ausente'),
(3, 7, '2026-09-15', 'Tardanza');

-- 9. Expandir el Motor de NLP: Nuevas Intenciones
INSERT IGNORE INTO intenciones_nlp (nombre_intencion, respuesta_predefinida) VALUES
('matricula', 'Para el proceso de matrícula, necesitas adjuntar el DNI del apoderado y el voucher de pago.'),
('soporte', 'Si tienes problemas de acceso, por favor contacta a soporte_siagie@colegio.edu.pe.'),
('asistencias', 'Este es tu reporte de inasistencias y tardanzas:');

--USE chatbot_siagie_db;

-- =========================================================
-- 1. MÁS ROLES Y USUARIOS (Padres, Docentes y Administrativos)
-- =========================================================
INSERT IGNORE INTO usuarios (id_usuario, rol_id, username, password_hash) VALUES 
(5, 1, 'admin_central', 'hash_admin'),
(6, 2, 'prof_ciencias', 'hash_ciencias'),
(7, 2, 'prof_letras', 'hash_letras'),
(8, 3, 'padre_familia1', 'hash_padre1'),
(9, 4, 'alumno_riesgo', 'hash_riesgo'),
(10, 4, 'alumno_excelente', 'hash_excelente');

-- =========================================================
-- 2. ESTUDIANTES CON DIVERSOS PERFILES
-- =========================================================
INSERT IGNORE INTO estudiantes (id_estudiante, codigo_anonimizado, nivel_educativo, grado, seccion, estado_riesgo) VALUES
(9, 'EST-009', 'Secundaria', 2, 'A', 'Evaluando'),
(10, 'EST-010', 'Secundaria', 4, 'B', 'Evaluando'),
(11, 'EST-011', 'Primaria', 5, 'A', 'Evaluando'),
(12, 'EST-012', 'Primaria', 6, 'B', 'Evaluando');

-- =========================================================
-- 3. PROFESORES Y CURSOS VARIADOS
-- =========================================================
INSERT IGNORE INTO profesores (id_profesor, id_usuario, nombres, especialidad) VALUES 
(4, 6, 'Carmen Rojas', 'Ciencia y Tecnología'),
(5, 7, 'Jorge Luna', 'Comunicación');

INSERT IGNORE INTO cursos (id_curso, nombre, grado, id_profesor) VALUES
(5, 'Ciencia y Tecnología', 2, 4),
(6, 'Biología', 4, 4),
(7, 'Razonamiento Verbal', 5, 5),
(8, 'Literatura Peruana', 6, 5);

-- =========================================================
-- 4. MATRÍCULAS
-- =========================================================
INSERT IGNORE INTO matriculas (id_matricula, id_estudiante, id_curso, anio_escolar) VALUES
(9, 9, 5, 2026), (10, 10, 6, 2026), (11, 11, 7, 2026), (12, 12, 8, 2026);

-- =========================================================
-- 5. ASISTENCIAS (Crucial para predecir deserción escolar)
-- =========================================================
-- Alumno en riesgo (EST-009) con faltas repetitivas
INSERT IGNORE INTO asistencias (id_asistencia, id_matricula, fecha, estado) VALUES
(4, 9, '2026-10-01', 'Ausente'),
(5, 9, '2026-10-02', 'Ausente'),
(6, 9, '2026-10-03', 'Ausente'),
(7, 10, '2026-10-01', 'Presente'),
(8, 11, '2026-10-01', 'Tardanza'),
(9, 12, '2026-10-01', 'Presente');

-- =========================================================
-- 6. TAREAS Y ESTADOS (Entrenamiento para Regresión Lineal)
-- =========================================================
INSERT IGNORE INTO tareas (id_tarea, id_curso, titulo, fecha_vencimiento) VALUES
(6, 5, 'El Ciclo del Agua', '2026-10-10'),
(7, 6, 'Célula Eucariota', '2026-10-12'),
(8, 7, 'Sinónimos y Antónimos', '2026-10-15'),
(9, 8, 'Ensayo: Los Heraldos Negros', '2026-10-20');

-- EST-009: Tareas pendientes y atrasadas (Aumenta su riesgo)
INSERT IGNORE INTO estado_tareas (id_tarea, id_estudiante, estado, calificacion) VALUES
(6, 9, 'Atrasada', 05.0),
(7, 9, 'Pendiente', NULL);

-- EST-010: Alumno excelente
INSERT IGNORE INTO estado_tareas (id_tarea, id_estudiante, estado, calificacion) VALUES
(6, 10, 'Entregada', 19.0),
(7, 10, 'Entregada', 20.0);

-- =========================================================
-- 7. PAGOS (APAFA y Qali Warma)
-- =========================================================
INSERT IGNORE INTO pagos (id_pago, id_estudiante, concepto, monto, estado, fecha_vencimiento) VALUES
(7, 9, 'Cuota APAFA Anual', 80.00, 'Pendiente', '2026-03-01'),
(8, 10, 'Cuota APAFA Anual', 80.00, 'Pagado', '2026-03-01'),
(9, 11, 'Aporte Qali Warma (Menú)', 15.00, 'Pendiente', '2026-10-05'),
(10, 12, 'Certificado de Estudios', 25.00, 'Pagado', '2026-11-01');

-- =========================================================
-- 8. HORARIOS 
-- =========================================================
INSERT IGNORE INTO horarios (id_horario, id_curso, dia_semana, hora_inicio, hora_fin) VALUES
(5, 5, 'Lunes', '08:00:00', '09:30:00'),
(6, 6, 'Martes', '10:00:00', '11:30:00'),
(7, 7, 'Miércoles', '12:00:00', '13:30:00'),
(8, 8, 'Viernes', '08:00:00', '10:00:00');

-- =========================================================
-- 9. EXPANDIENDO LAS INTENCIONES NLP (Descongestionamiento)
-- =========================================================
INSERT IGNORE INTO intenciones_nlp (nombre_intencion, respuesta_predefinida) VALUES
('apafa', 'Para trámites de APAFA, por favor adjunte el voucher de pago en la sección de validación.'),
('qali_warma', 'El programa Qali Warma se está distribuyendo en el patio principal. Recuerda estar al día con tu aporte mensual.'),
('certificados', 'Para la emisión de certificados de estudios a través del SIAGIE, debes no tener deudas pendientes e ingresar tu DNI.'),
('desconocido', 'Lo siento, soy un asistente académico. Solo puedo ayudarte con notas, pagos, horarios y trámites del colegio.');

-- =========================================================
-- 10. HISTORIAL DE CONSULTAS Y VALIDACIÓN MULTIMODAL
-- =========================================================
-- Simulamos que el usuario 8 (Padre de familia) hizo una consulta por voz y subió un voucher
INSERT IGNORE INTO historial_consultas (id_consulta, id_usuario, id_intencion, mensaje_texto, modalidad, fecha_consulta) VALUES
(1, 8, (SELECT id_intencion FROM intenciones_nlp WHERE nombre_intencion = 'apafa' LIMIT 1), 'quiero pagar la apafa', 'Voz', CURRENT_TIMESTAMP),
(2, 9, (SELECT id_intencion FROM intenciones_nlp WHERE nombre_intencion = 'notas' LIMIT 1), 'estoy jalando biologia', 'Texto', CURRENT_TIMESTAMP);

INSERT IGNORE INTO archivos_validacion (id_archivo, id_consulta, tipo_documento, ruta_archivo, resultado_ia_visual) VALUES
(1, 1, 'Voucher', '/static/uploads/voucher_apafa_001.jpg', '✅ Comprobante de pago validado correctamente.');