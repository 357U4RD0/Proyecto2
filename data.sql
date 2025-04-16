-- Estados de reserva
INSERT INTO estados_reserva (nombre_estado) VALUES
('reservado'),
('fallido'),
('cancelado');

-- Evento
INSERT INTO eventos (nombre, descripcion, fecha, capacidad) VALUES
('Concierto de prueba', 'Evento de prueba', '2025-05-01 20:00:00', 10);

-- Asientos para el evento
INSERT INTO asientos (id_evento, numero_asiento) VALUES
(1, 'A1'),
(1, 'A2'),
(1, 'A3'),
(1, 'A4'),
(1, 'A5'),
(1, 'A6'),
(1, 'A7'),
(1, 'A8'),
(1, 'A9'),
(1, 'A10');

-- 15 usuarios de prueba
INSERT INTO usuarios (nombre, email) VALUES
('usuario1', 'usuario1@ejemplo.com'),
('usuario2', 'usuario2@ejemplo.com'),
('usuario3', 'usuario3@ejemplo.com'),
('usuario4', 'usuario4@ejemplo.com'),
('usuario5', 'usuario5@ejemplo.com'),
('usuario6', 'usuario6@ejemplo.com'),
('usuario7', 'usuario7@ejemplo.com'),
('usuario8', 'usuario8@ejemplo.com'),
('usuario9', 'usuario9@ejemplo.com'),
('usuario10', 'usuario10@ejemplo.com'),
('usuario11', 'usuario11@ejemplo.com'),
('usuario12', 'usuario12@ejemplo.com'),
('usuario13', 'usuario13@ejemplo.com'),
('usuario14', 'usuario14@ejemplo.com'),
('usuario15', 'usuario15@ejemplo.com'),
('usuario16', 'usuario16@ejemplo.com'),
('usuario17', 'usuario17@ejemplo.com'),
('usuario18', 'usuario18@ejemplo.com'),
('usuario19', 'usuario19@ejemplo.com'),
('usuario20', 'usuario20@ejemplo.com'),
('usuario21', 'usuario21@ejemplo.com'),
('usuario22', 'usuario22@ejemplo.com'),
('usuario23', 'usuario23@ejemplo.com'),
('usuario24', 'usuario24@ejemplo.com'),
('usuario25', 'usuario25@ejemplo.com'),
('usuario26', 'usuario26@ejemplo.com'),
('usuario27', 'usuario27@ejemplo.com'),
('usuario28', 'usuario28@ejemplo.com'),
('usuario29', 'usuario29@ejemplo.com'),
('usuario30', 'usuario30@ejemplo.com');

-- 2 reservas iniciales siendo los asientos A1 y A2
INSERT INTO reservas (id_usuario, id_asiento, id_estado) VALUES
(1, 1, 1),  -- usuario1 reserva A1
(2, 2, 1);  -- usuario2 reserva A2
