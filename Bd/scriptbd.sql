-- =====================================================================
-- BASE DE DATOS: chatbot_siagie_db
-- =====================================================================
-- Descripción general:
--   Esquema de datos para el Asistente Virtual Inteligente Multimodal
--   (SISTINT). Almacena usuarios, estudiantes, profesores, cursos,
--   matrículas, asistencias, tareas, pagos, y el historial de
--   interacciones del chatbot (NLP) junto con los archivos que el
--   módulo de visión por computadora valida (vouchers, DNI, etc.).
--
-- Estructura de este archivo:
--   SECCIÓN 1: Configuración inicial y creación de la base de datos.
--   SECCIÓN 2: Creación de tablas (DDL), ordenadas según sus
--              dependencias de llaves foráneas (de "padres" a "hijos").
--   SECCIÓN 3: Creación de vistas (usadas como datasets para los
--              modelos de Machine Learning).
--   SECCIÓN 4: Inserción de datos (DML), en el mismo orden de
--              dependencias que la Sección 2.
--
-- Motor: InnoDB | Charset: utf8mb4 | Collation: utf8mb4_unicode_ci
-- =====================================================================


-- =====================================================================
-- SECCIÓN 0: CONFIGURACIÓN DE SESIÓN
-- =====================================================================
-- Se desactivan temporalmente las validaciones de llaves foráneas y
-- unicidad para permitir cargas masivas de datos sin que el orden
-- estricto de inserción provoque errores. Se restauran al final.
-- =====================================================================

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO';
SET NAMES utf8mb4;

CREATE DATABASE IF NOT EXISTS `chatbot_siagie_db`
  DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE `chatbot_siagie_db`;


-- =====================================================================
-- SECCIÓN 1: CREACIÓN DE TABLAS (DDL)
-- =====================================================================
-- Orden de creación: cada tabla se crea después de las tablas a las
-- que hace referencia mediante FOREIGN KEY, evitando así errores de
-- dependencia. Los DROP TABLE garantizan una recreación limpia.
-- =====================================================================

-- ---------------------------------------------------------------------
-- 1.1 roles
-- Catálogo de perfiles de acceso a la plataforma
-- (Administrativo, Docente, Tutor/Padre, Estudiante).
-- ---------------------------------------------------------------------
DROP TABLE IF EXISTS `archivos_validacion`;
DROP TABLE IF EXISTS `historial_consultas`;
DROP TABLE IF EXISTS `intenciones_nlp`;
DROP TABLE IF EXISTS `estado_tareas`;
DROP TABLE IF EXISTS `tareas`;
DROP TABLE IF EXISTS `pagos`;
DROP TABLE IF EXISTS `asistencias`;
DROP TABLE IF EXISTS `matriculas`;
DROP TABLE IF EXISTS `horarios`;
DROP TABLE IF EXISTS `cursos`;
DROP TABLE IF EXISTS `profesores`;
DROP TABLE IF EXISTS `estudiantes`;
DROP TABLE IF EXISTS `usuarios`;
DROP VIEW  IF EXISTS `dataset_perfil_usuario`;
DROP VIEW  IF EXISTS `dataset_rendimiento`;
DROP TABLE IF EXISTS `roles`;

CREATE TABLE `roles` (
  `id_rol` INT NOT NULL AUTO_INCREMENT,
  `nombre` VARCHAR(50) NOT NULL,
  PRIMARY KEY (`id_rol`),
  UNIQUE KEY `nombre` (`nombre`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='Catálogo de roles de usuario del sistema';


-- ---------------------------------------------------------------------
-- 1.2 usuarios
-- Cuentas de acceso; toda persona (estudiante, docente, tutor o
-- administrativo) tiene una fila aquí. Depende de `roles`.
-- ---------------------------------------------------------------------
CREATE TABLE `usuarios` (
  `id_usuario` INT NOT NULL AUTO_INCREMENT,
  `rol_id` INT NOT NULL,
  `username` VARCHAR(100) NOT NULL,
  `password_hash` VARCHAR(255) NOT NULL,
  `fecha_registro` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_usuario`),
  UNIQUE KEY `username` (`username`),
  KEY `rol_id` (`rol_id`),
  CONSTRAINT `usuarios_ibfk_1` FOREIGN KEY (`rol_id`) REFERENCES `roles` (`id_rol`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='Cuentas de acceso a la plataforma, vinculadas a un rol';


-- ---------------------------------------------------------------------
-- 1.3 intenciones_nlp
-- Catálogo de intenciones que el modelo de clasificación de texto
-- (TF-IDF + Regresión Logística) puede predecir, junto con la
-- respuesta base asociada a cada una. No depende de otras tablas.
-- ---------------------------------------------------------------------
CREATE TABLE `intenciones_nlp` (
  `id_intencion` INT NOT NULL AUTO_INCREMENT,
  `nombre_intencion` VARCHAR(50) NOT NULL,
  `respuesta_predefinida` TEXT NOT NULL,
  PRIMARY KEY (`id_intencion`),
  UNIQUE KEY `nombre_intencion` (`nombre_intencion`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='Catálogo de intenciones NLP y sus respuestas base';


-- ---------------------------------------------------------------------
-- 1.4 estudiantes
-- Datos académicos anonimizados del alumno. Depende de `usuarios`
-- (cada estudiante posee una cuenta de acceso).
-- ---------------------------------------------------------------------
CREATE TABLE `estudiantes` (
  `id_estudiante` INT NOT NULL AUTO_INCREMENT,
  `codigo_anonimizado` VARCHAR(50) NOT NULL,
  `nivel_educativo` VARCHAR(20) NOT NULL,
  `grado` INT NOT NULL,
  `seccion` VARCHAR(5) NOT NULL,
  `estado_riesgo` VARCHAR(20) DEFAULT 'Evaluando',
  `id_usuario` INT DEFAULT NULL,
  PRIMARY KEY (`id_estudiante`),
  UNIQUE KEY `codigo_anonimizado` (`codigo_anonimizado`),
  KEY `fk_estudiantes_usuarios` (`id_usuario`),
  CONSTRAINT `fk_estudiantes_usuarios` FOREIGN KEY (`id_usuario`)
    REFERENCES `usuarios` (`id_usuario`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='Perfil académico del estudiante; estado_riesgo es alimentado por el modelo de regresión lineal';


-- ---------------------------------------------------------------------
-- 1.5 profesores
-- Datos del docente. Depende de `usuarios`.
-- ---------------------------------------------------------------------
CREATE TABLE `profesores` (
  `id_profesor` INT NOT NULL AUTO_INCREMENT,
  `id_usuario` INT NOT NULL,
  `nombres` VARCHAR(100) NOT NULL,
  `especialidad` VARCHAR(100) DEFAULT NULL,
  PRIMARY KEY (`id_profesor`),
  KEY `id_usuario` (`id_usuario`),
  CONSTRAINT `profesores_ibfk_1` FOREIGN KEY (`id_usuario`)
    REFERENCES `usuarios` (`id_usuario`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='Datos del docente responsable de uno o más cursos';


-- ---------------------------------------------------------------------
-- 1.6 cursos
-- Cursos dictados por un profesor. Depende de `profesores`.
-- ---------------------------------------------------------------------
CREATE TABLE `cursos` (
  `id_curso` INT NOT NULL AUTO_INCREMENT,
  `nombre` VARCHAR(100) NOT NULL,
  `grado` INT NOT NULL,
  `id_profesor` INT NOT NULL,
  PRIMARY KEY (`id_curso`),
  KEY `id_profesor` (`id_profesor`),
  CONSTRAINT `cursos_ibfk_1` FOREIGN KEY (`id_profesor`)
    REFERENCES `profesores` (`id_profesor`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='Cursos ofrecidos por grado, cada uno a cargo de un profesor';


-- ---------------------------------------------------------------------
-- 1.7 horarios
-- Bloques de horario semanal de un curso. Depende de `cursos`.
-- ---------------------------------------------------------------------
CREATE TABLE `horarios` (
  `id_horario` INT NOT NULL AUTO_INCREMENT,
  `id_curso` INT NOT NULL,
  `dia_semana` ENUM('Lunes','Martes','Miércoles','Jueves','Viernes','Sábado') NOT NULL,
  `hora_inicio` TIME NOT NULL,
  `hora_fin` TIME NOT NULL,
  PRIMARY KEY (`id_horario`),
  KEY `id_curso` (`id_curso`),
  CONSTRAINT `horarios_ibfk_1` FOREIGN KEY (`id_curso`)
    REFERENCES `cursos` (`id_curso`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='Horario semanal de dictado de cada curso';


-- ---------------------------------------------------------------------
-- 1.8 matriculas
-- Relación estudiante-curso por año escolar. Depende de
-- `estudiantes` y `cursos`.
-- ---------------------------------------------------------------------
CREATE TABLE `matriculas` (
  `id_matricula` INT NOT NULL AUTO_INCREMENT,
  `id_estudiante` INT NOT NULL,
  `id_curso` INT NOT NULL,
  `anio_escolar` INT NOT NULL,
  PRIMARY KEY (`id_matricula`),
  KEY `id_estudiante` (`id_estudiante`),
  KEY `id_curso` (`id_curso`),
  CONSTRAINT `matriculas_ibfk_1` FOREIGN KEY (`id_estudiante`)
    REFERENCES `estudiantes` (`id_estudiante`),
  CONSTRAINT `matriculas_ibfk_2` FOREIGN KEY (`id_curso`)
    REFERENCES `cursos` (`id_curso`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='Matrícula del estudiante en un curso, por año escolar';


-- ---------------------------------------------------------------------
-- 1.9 asistencias
-- Registro diario de asistencia por matrícula. Depende de
-- `matriculas`.
-- ---------------------------------------------------------------------
CREATE TABLE `asistencias` (
  `id_asistencia` INT NOT NULL AUTO_INCREMENT,
  `id_matricula` INT NOT NULL,
  `fecha` DATE NOT NULL,
  `estado` ENUM('Presente','Ausente','Tardanza','Justificado') NOT NULL,
  PRIMARY KEY (`id_asistencia`),
  KEY `id_matricula` (`id_matricula`),
  CONSTRAINT `asistencias_ibfk_1` FOREIGN KEY (`id_matricula`)
    REFERENCES `matriculas` (`id_matricula`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='Registro diario de asistencia del estudiante a un curso matriculado';


-- ---------------------------------------------------------------------
-- 1.10 tareas
-- Actividades académicas asignadas por curso. Depende de `cursos`.
-- ---------------------------------------------------------------------
CREATE TABLE `tareas` (
  `id_tarea` INT NOT NULL AUTO_INCREMENT,
  `id_curso` INT NOT NULL,
  `titulo` VARCHAR(150) NOT NULL,
  `fecha_vencimiento` DATE NOT NULL,
  PRIMARY KEY (`id_tarea`),
  KEY `id_curso` (`id_curso`),
  CONSTRAINT `tareas_ibfk_1` FOREIGN KEY (`id_curso`)
    REFERENCES `cursos` (`id_curso`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='Tareas/actividades asignadas dentro de un curso';


-- ---------------------------------------------------------------------
-- 1.11 estado_tareas
-- Estado y calificación de cada tarea por estudiante. Depende de
-- `tareas` y `estudiantes`. Es la base del modelo de predicción de
-- riesgo académico (regresión lineal).
-- ---------------------------------------------------------------------
CREATE TABLE `estado_tareas` (
  `id_estado_tarea` INT NOT NULL AUTO_INCREMENT,
  `id_tarea` INT NOT NULL,
  `id_estudiante` INT NOT NULL,
  `estado` ENUM('Entregada','Pendiente','Atrasada') NOT NULL,
  `calificacion` DECIMAL(4,2) DEFAULT NULL,
  PRIMARY KEY (`id_estado_tarea`),
  KEY `id_tarea` (`id_tarea`),
  KEY `id_estudiante` (`id_estudiante`),
  CONSTRAINT `estado_tareas_ibfk_1` FOREIGN KEY (`id_tarea`)
    REFERENCES `tareas` (`id_tarea`),
  CONSTRAINT `estado_tareas_ibfk_2` FOREIGN KEY (`id_estudiante`)
    REFERENCES `estudiantes` (`id_estudiante`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='Estado de entrega y calificación de cada tarea por estudiante';


-- ---------------------------------------------------------------------
-- 1.12 pagos
-- Cuentas por cobrar/pagadas del estudiante (pensión, APAFA, Qali
-- Warma, certificados, etc.). Depende de `estudiantes`.
-- ---------------------------------------------------------------------
CREATE TABLE `pagos` (
  `id_pago` INT NOT NULL AUTO_INCREMENT,
  `id_estudiante` INT NOT NULL,
  `concepto` VARCHAR(100) NOT NULL,
  `monto` DECIMAL(10,2) NOT NULL,
  `estado` ENUM('Pagado','Pendiente','Vencido') NOT NULL,
  `fecha_vencimiento` DATE NOT NULL,
  `fecha_pago` DATE DEFAULT NULL,
  PRIMARY KEY (`id_pago`),
  KEY `id_estudiante` (`id_estudiante`),
  CONSTRAINT `pagos_ibfk_1` FOREIGN KEY (`id_estudiante`)
    REFERENCES `estudiantes` (`id_estudiante`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='Conceptos de pago del estudiante y su estado de cobranza';


-- ---------------------------------------------------------------------
-- 1.13 historial_consultas
-- Bitácora de cada interacción con el chatbot (texto, voz o imagen)
-- y la intención detectada por el modelo NLP. Depende de `usuarios`
-- e `intenciones_nlp`.
-- ---------------------------------------------------------------------
CREATE TABLE `historial_consultas` (
  `id_consulta` INT NOT NULL AUTO_INCREMENT,
  `id_usuario` INT NOT NULL,
  `id_intencion` INT DEFAULT NULL,
  `mensaje_texto` TEXT,
  `modalidad` ENUM('Texto','Voz','Imagen') NOT NULL,
  `fecha_consulta` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_consulta`),
  KEY `id_usuario` (`id_usuario`),
  KEY `id_intencion` (`id_intencion`),
  CONSTRAINT `historial_consultas_ibfk_1` FOREIGN KEY (`id_usuario`)
    REFERENCES `usuarios` (`id_usuario`),
  CONSTRAINT `historial_consultas_ibfk_2` FOREIGN KEY (`id_intencion`)
    REFERENCES `intenciones_nlp` (`id_intencion`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='Historial de consultas al chatbot y la intención clasificada por el modelo NLP';


-- ---------------------------------------------------------------------
-- 1.14 archivos_validacion
-- Archivos adjuntos (voucher, DNI, etc.) subidos durante una
-- consulta, junto con el resultado de la validación visual (OCR /
-- OpenCV). Depende de `historial_consultas`.
-- ---------------------------------------------------------------------
CREATE TABLE `archivos_validacion` (
  `id_archivo` INT NOT NULL AUTO_INCREMENT,
  `id_consulta` INT NOT NULL,
  `tipo_documento` ENUM('DNI','Voucher','Otro') NOT NULL,
  `ruta_archivo` VARCHAR(255) NOT NULL,
  `resultado_ia_visual` VARCHAR(100) DEFAULT NULL,
  `fecha_subida` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_archivo`),
  KEY `id_consulta` (`id_consulta`),
  CONSTRAINT `archivos_validacion_ibfk_1` FOREIGN KEY (`id_consulta`)
    REFERENCES `historial_consultas` (`id_consulta`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='Archivos adjuntos (voucher/DNI) y resultado de la validación visual (OCR/OpenCV)';


-- =====================================================================
-- SECCIÓN 2: VISTAS (DATASETS PARA MACHINE LEARNING)
-- =====================================================================
-- Estas vistas no almacenan datos propios: agregan información de
-- las tablas anteriores en el formato que consumen los scripts de
-- entrenamiento (`scripts/entrenar_modelo_*.py`).
-- =====================================================================

-- ---------------------------------------------------------------------
-- 2.1 dataset_rendimiento
-- Insumo del modelo de Regresión Lineal (predicción de riesgo
-- académico): promedio de notas, tareas entregadas/pendientes y una
-- nota final ponderada por estudiante.
-- ---------------------------------------------------------------------
CREATE VIEW `dataset_rendimiento` AS
SELECT
    e.id_estudiante                                                AS id_estudiante,
    COALESCE(AVG(et.calificacion), 10.0)                           AS promedio_actual,
    SUM(CASE WHEN et.estado = 'Entregada' THEN 1 ELSE 0 END)       AS tareas_entregadas,
    SUM(CASE WHEN et.estado IN ('Pendiente','Atrasada') THEN 1 ELSE 0 END)
                                                                    AS tareas_pendientes,
    (COALESCE(AVG(et.calificacion), 10.0) * 0.7)
        + (SUM(CASE WHEN et.estado = 'Entregada' THEN 1 ELSE 0 END) * 0.5)
                                                                    AS nota_final
FROM estudiantes e
LEFT JOIN estado_tareas et ON e.id_estudiante = et.id_estudiante
GROUP BY e.id_estudiante;


-- ---------------------------------------------------------------------
-- 2.2 dataset_perfil_usuario
-- Insumo del modelo K-Means (perfilamiento estudiantil): cantidad de
-- cursos matriculados, pagos realizados y tareas entregadas en total
-- por estudiante, usados como variables de comportamiento.
-- ---------------------------------------------------------------------
CREATE VIEW `dataset_perfil_usuario` AS
SELECT
    e.id_estudiante                                    AS id_estudiante,
    COUNT(DISTINCT m.id_curso)                         AS cursos_matriculados,
    (SELECT COUNT(*) FROM pagos p
       WHERE p.id_estudiante = e.id_estudiante
         AND p.estado = 'Pagado')                      AS pagos_realizados,
    (SELECT COUNT(*) FROM estado_tareas et
       WHERE et.id_estudiante = e.id_estudiante
         AND et.estado = 'Entregada')                  AS tareas_entregadas_total
FROM estudiantes e
LEFT JOIN matriculas m ON e.id_estudiante = m.id_estudiante
GROUP BY e.id_estudiante;


-- =====================================================================
-- SECCIÓN 3: INSERCIÓN DE DATOS (DML)
-- =====================================================================
-- Los datos se insertan respetando el mismo orden de dependencias
-- usado en la Sección 1, para que cada llave foránea encuentre ya
-- creado su registro padre.
-- =====================================================================

-- ---------------------------------------------------------------------
-- 3.1 roles
-- ---------------------------------------------------------------------
INSERT INTO `roles` (`id_rol`, `nombre`) VALUES
(1,'Administrativo'),
(2,'Docente'),
(4,'Estudiante'),
(3,'Tutor_Padre');

-- ---------------------------------------------------------------------
-- 3.2 usuarios
-- ---------------------------------------------------------------------
INSERT INTO `usuarios` (`id_usuario`,`rol_id`,`username`,`password_hash`,`fecha_registro`) VALUES
(1,2,'profesor_mate','profesor_mate','2026-09-22 03:44:12'),
(2,2,'profesor_fisica','profesor_fisica','2026-09-22 03:44:12'),
(3,3,'tutor_maria','tutor_maria','2026-09-22 05:36:19'),
(4,4,'alumno_nuevo','alumno_nuevo','2026-09-22 05:36:19'),
(5,1,'admin_central','admin_central','2026-09-22 05:36:20'),
(6,2,'prof_ciencias','prof_ciencias','2026-09-22 05:36:20'),
(7,2,'prof_letras','prof_letras','2026-09-22 05:36:20'),
(8,3,'padre_familia1','padre_familia1','2026-09-22 05:36:20'),
(9,4,'alumno_riesgo','alumno_riesgo','2026-09-22 05:36:20'),
(10,4,'alumno_excelente','alumno_excelente','2026-09-22 05:36:20'),
(11,4,'estudiante_001','estudiante_001','2026-09-25 02:55:54'),
(12,4,'estudiante_002','estudiante_002','2026-09-25 02:55:54'),
(13,4,'alumno_ausentista','alumno_ausentista','2026-09-25 02:56:27'),
(14,4,'alumno_promedio','alumno_promedio','2026-09-25 02:56:27'),
(15,4,'alumno_destacado','alumno_destacado','2026-09-25 02:56:27'),
(16,4,'alumno_deudor','alumno_deudor','2026-09-25 02:56:27'),
(17,3,'padre_familia2','padre_familia2','2026-09-25 02:56:27'),
(18,4,'estudiante_003','estudiante_003','2026-09-25 03:02:18'),
(19,4,'estudiante_004','estudiante_004','2026-09-25 03:02:18'),
(20,4,'estudiante_005','estudiante_005','2026-09-25 03:02:18'),
(21,4,'estudiante_006','estudiante_006','2026-09-25 03:02:18'),
(22,4,'estudiante_007','estudiante_007','2026-09-25 03:02:18'),
(23,4,'estudiante_008','estudiante_008','2026-09-25 03:02:18'),
(24,4,'estudiante_011','estudiante_011','2026-09-25 03:02:18'),
(25,4,'estudiante_012','estudiante_012','2026-09-25 03:02:18');

-- ---------------------------------------------------------------------
-- 3.3 intenciones_nlp
-- ---------------------------------------------------------------------
INSERT INTO `intenciones_nlp` (`id_intencion`,`nombre_intencion`,`respuesta_predefinida`) VALUES
(1,'pagos','Aquí tienes el estado de tus pagos:'),
(2,'horarios','Este es tu horario programado:'),
(3,'notas','Tu rendimiento académico actual es:'),
(4,'tareas','Estas son tus tareas asignadas:'),
(5,'matricula','Para el proceso de matrícula, necesitas adjuntar el DNI del apoderado y el voucher de pago.'),
(6,'soporte','Si tienes problemas de acceso, por favor contacta a soporte_siagie@colegio.edu.pe.'),
(7,'asistencias','Este es tu reporte de inasistencias y tardanzas:'),
(8,'apafa','Para trámites de APAFA, por favor adjunte el voucher de pago en la sección de validación.'),
(9,'qali_warma','El programa Qali Warma se está distribuyendo en el patio principal. Recuerda estar al día con tu aporte mensual.'),
(10,'certificados','Para la emisión de certificados de estudios a través del SIAGIE, debes no tener deudas pendientes e ingresar tu DNI.'),
(11,'desconocido','Lo siento, soy un asistente académico. Solo puedo ayudarte con notas, pagos, horarios y trámites del colegio.');

-- ---------------------------------------------------------------------
-- 3.4 estudiantes
-- ---------------------------------------------------------------------
INSERT INTO `estudiantes` (`id_estudiante`,`codigo_anonimizado`,`nivel_educativo`,`grado`,`seccion`,`estado_riesgo`,`id_usuario`) VALUES
(1,'EST-001','Secundaria',3,'A','Evaluando',11),
(2,'EST-002','Secundaria',3,'A','Evaluando',12),
(3,'EST-003','Secundaria',4,'B','Evaluando',18),
(4,'EST-004','Secundaria',5,'A','Evaluando',19),
(5,'EST-005','Secundaria',5,'B','Evaluando',20),
(6,'EST-006','Primaria',6,'A','Evaluando',21),
(7,'EST-007','Secundaria',1,'B','Evaluando',22),
(8,'EST-008','Secundaria',5,'C','Evaluando',23),
(9,'EST-009','Secundaria',2,'A','Evaluando',9),
(10,'EST-010','Secundaria',4,'B','Evaluando',10),
(11,'EST-011','Primaria',5,'A','Evaluando',24),
(12,'EST-012','Primaria',6,'B','Evaluando',25),
(13,'EST-013','Secundaria',3,'A','Riesgo Alto',13),
(14,'EST-014','Secundaria',3,'B','Evaluando',14),
(15,'EST-015','Primaria',6,'A','Riesgo Bajo',15),
(16,'EST-016','Secundaria',5,'C','Evaluando',16);

-- ---------------------------------------------------------------------
-- 3.5 profesores
-- ---------------------------------------------------------------------
INSERT INTO `profesores` (`id_profesor`,`id_usuario`,`nombres`,`especialidad`) VALUES
(1,1,'Carlos Mendoza','Matemáticas'),
(2,2,'Ana Torres','Física'),
(3,3,'Luis Ramos','Historia y Geografía'),
(4,6,'Carmen Rojas','Ciencia y Tecnología'),
(5,7,'Jorge Luna','Comunicación');

-- ---------------------------------------------------------------------
-- 3.6 cursos
-- ---------------------------------------------------------------------
INSERT INTO `cursos` (`id_curso`,`nombre`,`grado`,`id_profesor`) VALUES
(1,'Matemática Básica',3,1),
(2,'Física Elemental',4,2),
(3,'Historia del Perú',5,3),
(4,'Comunicación Integral',1,3),
(5,'Ciencia y Tecnología',2,4),
(6,'Biología',4,4),
(7,'Razonamiento Verbal',5,5),
(8,'Literatura Peruana',6,5);

-- ---------------------------------------------------------------------
-- 3.7 horarios
-- ---------------------------------------------------------------------
INSERT INTO `horarios` (`id_horario`,`id_curso`,`dia_semana`,`hora_inicio`,`hora_fin`) VALUES
(1,1,'Lunes','08:00:00','10:00:00'),
(2,2,'Martes','10:00:00','12:00:00'),
(3,3,'Miércoles','14:00:00','16:00:00'),
(4,4,'Jueves','09:00:00','11:00:00'),
(5,5,'Lunes','08:00:00','09:30:00'),
(6,6,'Martes','10:00:00','11:30:00'),
(7,7,'Miércoles','12:00:00','13:30:00'),
(8,8,'Viernes','08:00:00','10:00:00');

-- ---------------------------------------------------------------------
-- 3.8 matriculas
-- ---------------------------------------------------------------------
INSERT INTO `matriculas` (`id_matricula`,`id_estudiante`,`id_curso`,`anio_escolar`) VALUES
(1,1,1,2026),
(2,2,1,2026),
(3,3,2,2026),
(4,4,2,2026),
(5,5,2,2026),
(6,6,4,2026),
(7,7,4,2026),
(8,8,3,2026),
(9,9,5,2026),
(10,10,6,2026),
(11,11,7,2026),
(12,12,8,2026),
(13,13,5,2026),
(14,14,5,2026),
(15,15,8,2026),
(16,16,7,2026);

-- ---------------------------------------------------------------------
-- 3.9 asistencias
-- ---------------------------------------------------------------------
INSERT INTO `asistencias` (`id_asistencia`,`id_matricula`,`fecha`,`estado`) VALUES
(1,8,'2026-09-10','Ausente'),
(2,8,'2026-09-12','Ausente'),
(3,7,'2026-09-15','Tardanza'),
(4,9,'2026-10-01','Ausente'),
(5,9,'2026-10-02','Ausente'),
(6,9,'2026-10-03','Ausente'),
(7,10,'2026-10-01','Presente'),
(8,11,'2026-10-01','Tardanza'),
(9,12,'2026-10-01','Presente'),
(10,13,'2026-10-10','Ausente'),
(11,13,'2026-10-11','Ausente'),
(12,13,'2026-10-12','Ausente'),
(13,13,'2026-10-13','Ausente'),
(14,15,'2026-10-10','Presente'),
(15,15,'2026-10-11','Presente');

-- ---------------------------------------------------------------------
-- 3.10 tareas
-- ---------------------------------------------------------------------
INSERT INTO `tareas` (`id_tarea`,`id_curso`,`titulo`,`fecha_vencimiento`) VALUES
(1,1,'Ecuaciones de 1er Grado','2026-10-01'),
(2,1,'Ecuaciones de 2do Grado','2026-10-08'),
(3,2,'Cinemática','2026-10-05'),
(4,3,'Ensayo sobre la Independencia','2026-11-15'),
(5,4,'Comprensión Lectora: Tradiciones Peruanas','2026-11-20'),
(6,5,'El Ciclo del Agua','2026-10-10'),
(7,6,'Célula Eucariota','2026-10-12'),
(8,7,'Sinónimos y Antónimos','2026-10-15'),
(9,8,'Ensayo: Los Heraldos Negros','2026-10-20'),
(10,1,'Ecuaciones de Primer Grado','2026-10-15'),
(11,1,'Geometría Básica','2026-10-18'),
(12,1,'Estadística y Probabilidad','2026-10-22');

-- ---------------------------------------------------------------------
-- 3.11 estado_tareas
-- ---------------------------------------------------------------------
INSERT INTO `estado_tareas` (`id_estado_tarea`,`id_tarea`,`id_estudiante`,`estado`,`calificacion`) VALUES
(1,1,1,'Entregada',18.50),
(2,2,1,'Entregada',17.00),
(3,1,2,'Atrasada',10.00),
(4,2,2,'Pendiente',0.00),
(5,3,3,'Entregada',13.50),
(6,3,4,'Pendiente',0.00),
(7,3,5,'Entregada',15.00),
(8,4,8,'Atrasada',8.00),
(9,4,8,'Entregada',14.50),
(10,5,7,'Pendiente',0.00),
(11,6,9,'Atrasada',5.00),
(12,7,9,'Pendiente',0.00),
(13,6,10,'Entregada',19.00),
(14,7,10,'Entregada',20.00),
(15,6,13,'Atrasada',0.00),
(16,7,13,'Pendiente',0.00),
(17,6,14,'Entregada',12.00),
(18,7,14,'Atrasada',10.50),
(19,8,15,'Entregada',20.00),
(20,9,15,'Entregada',19.50),
(24,10,15,'Entregada',18.50),
(25,11,15,'Entregada',19.50),
(26,12,15,'Entregada',20.00),
(27,10,1,'Entregada',17.00),
(28,11,1,'Entregada',16.50),
(29,12,1,'Entregada',19.00),
(30,10,2,'Entregada',14.00),
(31,11,2,'Pendiente',0.00),
(32,12,2,'Pendiente',0.00),
(33,10,4,'Pendiente',0.00),
(34,11,4,'Entregada',15.50),
(35,12,4,'Pendiente',0.00),
(36,10,9,'Atrasada',10.00),
(37,11,9,'Entregada',12.00),
(38,12,9,'Pendiente',0.00),
(39,10,13,'Pendiente',0.00),
(40,11,13,'Pendiente',0.00),
(41,12,13,'Atrasada',5.00);

-- ---------------------------------------------------------------------
-- 3.12 pagos
-- ---------------------------------------------------------------------
INSERT INTO `pagos` (`id_pago`,`id_estudiante`,`concepto`,`monto`,`estado`,`fecha_vencimiento`,`fecha_pago`) VALUES
(1,1,'Pensión Marzo',450.00,'Pagado','2026-03-31',NULL),
(2,2,'Pensión Marzo',450.00,'Pendiente','2026-03-31',NULL),
(3,3,'Pensión Marzo',450.00,'Vencido','2026-03-31',NULL),
(4,6,'Matrícula 2026',200.00,'Pagado','2026-02-15',NULL),
(5,7,'Pensión Abril',450.00,'Vencido','2026-04-30',NULL),
(6,8,'Cuota APAFA',50.00,'Pendiente','2026-12-01',NULL),
(7,9,'Cuota APAFA Anual',80.00,'Pendiente','2026-03-01',NULL),
(8,10,'Cuota APAFA Anual',80.00,'Pagado','2026-03-01',NULL),
(9,11,'Aporte Qali Warma (Menú)',15.00,'Pendiente','2026-10-05',NULL),
(10,12,'Certificado de Estudios',25.00,'Pagado','2026-11-01',NULL),
(11,16,'Cuota APAFA Anual',80.00,'Vencido','2026-03-01',NULL),
(12,16,'Aporte Qali Warma (Menú)',30.00,'Vencido','2026-09-05',NULL),
(13,16,'Pensión Octubre',450.00,'Pendiente','2026-10-31',NULL),
(14,15,'Cuota APAFA Anual',80.00,'Pagado','2026-03-01',NULL),
(15,15,'Certificado de Estudios',25.00,'Pagado','2026-10-15',NULL);

-- ---------------------------------------------------------------------
-- 3.13 historial_consultas
-- ---------------------------------------------------------------------
INSERT INTO `historial_consultas` (`id_consulta`,`id_usuario`,`id_intencion`,`mensaje_texto`,`modalidad`,`fecha_consulta`) VALUES
(1,1,1,'cuanto debo de pension','Texto','2026-09-22 04:06:24'),
(2,1,1,'cuanto debo','Texto','2026-09-22 05:05:22'),
(3,1,2,'horario','Texto','2026-09-22 05:05:35'),
(4,1,3,'profesores','Texto','2026-09-22 05:05:43'),
(5,1,2,'cual es mi profesor','Texto','2026-09-22 05:05:50'),
(6,1,3,'mis notas','Texto','2026-09-22 05:05:57'),
(7,1,2,'clases','Texto','2026-09-22 05:06:03'),
(8,1,3,'notas','Texto','2026-09-22 05:09:59'),
(9,1,3,'promedio','Texto','2026-09-22 05:10:04'),
(10,1,3,'horarios','Texto','2026-09-22 05:10:08'),
(11,1,2,'horario','Texto','2026-09-22 05:10:13'),
(12,1,2,'clases','Texto','2026-09-22 05:10:18'),
(13,1,2,'clases','Texto','2026-09-22 05:10:23'),
(14,1,1,'cuánto debo','Texto','2026-09-22 05:10:25'),
(15,8,8,'quiero pagar la apafa','Voz','2026-09-22 05:42:15'),
(16,9,3,'estoy jalando biologia','Texto','2026-09-22 05:42:15'),
(17,1,3,'nota','Texto','2026-09-22 05:44:03'),
(18,1,3,'cual es mi nota','Texto','2026-09-25 01:36:32'),
(19,1,2,'mi horario','Texto','2026-09-25 01:36:39'),
(20,1,11,'profesores','Texto','2026-09-25 01:36:44'),
(21,1,4,'tareas','Texto','2026-09-25 01:36:50'),
(22,1,1,'pagos','Texto','2026-09-25 01:36:58'),
(23,1,11,'l','Texto','2026-09-25 01:37:24'),
(24,1,3,'notas','Texto','2026-09-25 01:37:37'),
(25,1,4,'tareas','Texto','2026-09-25 01:37:42'),
(26,1,1,'cuanto deuvo de pension','Texto','2026-09-25 02:34:49'),
(27,1,11,'oye causa cuentame un chiste','Texto','2026-09-25 02:34:49'),
(28,1,4,'q tareas tngo','Texto','2026-09-25 02:34:49'),
(29,1,3,'hola mis notas','Texto','2026-09-25 02:36:24'),
(30,1,4,'tareas','Texto','2026-09-25 02:36:26'),
(31,1,11,'ola causa que hay de nuevo','Texto','2026-09-25 02:36:38'),
(32,1,3,'cuales son mis paguitos','Texto','2026-09-25 02:36:45'),
(33,1,1,'ola mis pagos','Texto','2026-09-25 02:37:00'),
(34,1,3,'nota','Texto','2026-09-25 03:14:48'),
(35,1,1,'pago','Texto','2026-09-25 03:14:51'),
(36,1,11,'asistencia','Texto','2026-09-25 03:14:54'),
(37,1,2,'horario de atencion','Texto','2026-09-25 03:23:53'),
(38,1,2,'horario de atencion','Texto','2026-09-25 03:24:01'),
(39,1,1,'pago','Texto','2026-09-25 03:24:05'),
(40,1,11,'j','Texto','2026-09-25 03:24:18'),
(41,1,2,'horario','Texto','2026-09-25 03:24:21'),
(42,1,11,'pagoi','Texto','2026-09-25 03:34:16'),
(43,1,1,'pago','Texto','2026-09-25 03:34:19'),
(44,4,1,'apafa','Texto','2026-09-25 03:39:22'),
(45,4,3,'notas','Texto','2026-09-25 03:39:35'),
(46,4,11,'hola','Texto','2026-09-25 03:39:38'),
(47,4,3,'notas','Texto','2026-09-25 03:39:42'),
(48,3,3,'notas','Texto','2026-09-25 03:41:44'),
(49,1,11,'informacion','Texto','2026-09-25 03:49:44'),
(50,1,8,'requisitos para apafa','Texto','2026-09-25 03:49:51'),
(51,3,3,'mis notas','Texto','2026-09-25 03:50:04'),
(52,3,4,'tareas','Texto','2026-09-25 03:50:07'),
(53,1,8,'apafa','Texto','2026-09-25 04:04:03'),
(54,1,8,'apafa','Texto','2026-09-25 04:04:21'),
(55,1,10,'emisión de certificados','Texto','2026-09-25 04:05:57'),
(56,1,10,'emisión de certificados','Texto','2026-09-25 04:06:03'),
(57,8,3,'mi promedio','Texto','2026-09-25 04:07:01'),
(58,8,4,'mi tarea','Texto','2026-09-25 04:07:05'),
(59,8,2,'mis horarios ?','Texto','2026-09-25 04:07:12'),
(60,8,3,'mi asistencia','Texto','2026-09-25 04:07:17'),
(61,8,1,'mis pagos','Texto','2026-09-25 04:07:24'),
(62,16,1,'deudas','Texto','2026-09-25 04:09:25'),
(63,16,3,'mi nivel','Texto','2026-09-25 04:09:35'),
(64,16,3,'mis notas','Texto','2026-09-25 04:09:46'),
(65,16,3,'notas','Texto','2026-09-25 04:24:19'),
(66,16,3,'nota','Texto','2026-09-25 04:24:38'),
(67,14,3,'notas','Texto','2026-09-25 04:26:06'),
(68,14,4,'tarea','Texto','2026-09-25 04:26:10'),
(69,1,3,'nota','Texto','2026-09-25 04:26:49'),
(70,1,1,'pago','Texto','2026-09-25 04:26:52'),
(71,1,4,'tarea','Texto','2026-09-25 04:26:54'),
(72,3,3,'mi asistencia','Texto','2026-09-25 04:31:05'),
(73,1,8,'informacion de apafa','Texto','2026-09-25 04:49:16'),
(74,1,1,'cuanto deuvo de pension','Texto','2026-09-25 04:49:16'),
(75,3,4,'cursos','Texto','2026-09-25 04:49:58'),
(76,3,11,'asistencia','Texto','2026-09-25 04:50:04'),
(77,3,3,'mi asistencia','Texto','2026-09-25 04:50:15'),
(78,3,1,'cuantas faltas tengo','Texto','2026-09-25 04:50:35'),
(79,3,NULL,'cuantas faltas tengo','Texto','2026-09-25 04:52:17'),
(80,13,NULL,'cuantas faltas tengo','Texto','2026-09-25 04:53:12'),
(81,13,NULL,'mi asistencia','Texto','2026-09-25 04:53:25'),
(82,3,NULL,'mi asistencia','Texto','2026-09-25 04:53:34'),
(83,15,NULL,'mi asistencia','Texto','2026-09-25 04:54:13'),
(84,3,3,'notas','Texto','2026-09-25 05:17:05'),
(85,3,3,'notas','Texto','2026-09-25 05:17:10'),
(86,3,3,'mis notas','Texto','2026-09-26 01:47:15'),
(87,3,1,'cuánto debo','Texto','2026-09-26 01:47:21'),
(88,3,1,'Debo pagar','Texto','2026-09-26 01:47:26'),
(89,3,NULL,'mi asistencia','Texto','2026-09-26 01:47:31'),
(90,3,11,'APA','Texto','2026-09-26 01:47:36'),
(91,3,8,'apafa','Texto','2026-09-26 01:47:41'),
(92,3,3,'notas','Texto','2026-09-26 04:30:30'),
(93,3,11,'motos','Texto','2026-09-26 04:30:37'),
(94,3,11,'no','Texto','2026-09-26 04:30:43'),
(95,3,3,'Ver notas','Texto','2026-09-26 04:30:48'),
(96,3,NULL,'cuantas faltas tengo','Texto','2026-09-26 04:34:02'),
(97,14,NULL,'mi asistencia','Texto','2026-09-26 04:34:33'),
(98,13,NULL,'mi asistencia','Texto','2026-09-26 04:35:29'),
(99,10,NULL,'mi asistencia','Texto','2026-09-26 04:36:42'),
(100,10,3,'notas','Texto','2026-09-26 04:36:46');

-- ---------------------------------------------------------------------
-- 3.14 archivos_validacion
-- ---------------------------------------------------------------------
INSERT INTO `archivos_validacion` (`id_archivo`,`id_consulta`,`tipo_documento`,`ruta_archivo`,`resultado_ia_visual`,`fecha_subida`) VALUES
(1,1,'Voucher','/static/uploads/voucher_apafa_001.jpg','✅ Comprobante de pago validado correctamente.','2026-09-22 05:36:20');


-- =====================================================================
-- SECCIÓN 4: AJUSTE DE AUTO_INCREMENT Y RESTAURACIÓN DE SESIÓN
-- =====================================================================
-- Se fija el siguiente valor de AUTO_INCREMENT según el máximo id
-- insertado en cada tabla (equivalente a los valores del dump
-- original) y se restauran las variables de sesión modificadas en
-- la Sección 0.
-- =====================================================================

ALTER TABLE `roles`                AUTO_INCREMENT = 5;
ALTER TABLE `usuarios`             AUTO_INCREMENT = 26;
ALTER TABLE `intenciones_nlp`      AUTO_INCREMENT = 12;
ALTER TABLE `estudiantes`          AUTO_INCREMENT = 17;
ALTER TABLE `profesores`           AUTO_INCREMENT = 6;
ALTER TABLE `cursos`               AUTO_INCREMENT = 9;
ALTER TABLE `horarios`             AUTO_INCREMENT = 9;
ALTER TABLE `matriculas`           AUTO_INCREMENT = 17;
ALTER TABLE `asistencias`          AUTO_INCREMENT = 16;
ALTER TABLE `tareas`               AUTO_INCREMENT = 13;
ALTER TABLE `estado_tareas`        AUTO_INCREMENT = 42;
ALTER TABLE `pagos`                AUTO_INCREMENT = 16;
ALTER TABLE `historial_consultas`  AUTO_INCREMENT = 101;
ALTER TABLE `archivos_validacion`  AUTO_INCREMENT = 2;

SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;

-- =====================================================================
-- FIN DEL SCRIPT
-- =====================================================================
