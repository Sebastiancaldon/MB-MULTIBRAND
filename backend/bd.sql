-- MB Multibrand REST. Importar en MySQL Workbench/phpMyAdmin.
-- ADVERTENCIA: este script elimina y recrea mb_multibrand si ya existe.
DROP DATABASE IF EXISTS mb_multibrand;
CREATE DATABASE mb_multibrand CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE mb_multibrand;

CREATE TABLE marcas (
 id_marca INT AUTO_INCREMENT PRIMARY KEY, nombre VARCHAR(100) NOT NULL UNIQUE,
 descripcion VARCHAR(255), canal_oficial VARCHAR(255), estado ENUM('ACTIVA','INACTIVA') NOT NULL DEFAULT 'ACTIVA'
);
CREATE TABLE productos (
 id_producto INT AUTO_INCREMENT PRIMARY KEY, id_marca INT NOT NULL, nombre VARCHAR(150) NOT NULL,
 categoria VARCHAR(80) NOT NULL, descripcion VARCHAR(255), precio DECIMAL(12,2) NOT NULL,
 stock INT NOT NULL DEFAULT 0, estado ENUM('ACTIVO','INACTIVO') NOT NULL DEFAULT 'ACTIVO',
 CONSTRAINT fk_producto_marca FOREIGN KEY (id_marca) REFERENCES marcas(id_marca),
 CONSTRAINT chk_precio CHECK (precio >= 0), CONSTRAINT chk_stock CHECK (stock >= 0)
);
CREATE TABLE descuentos (
 id_descuento INT AUTO_INCREMENT PRIMARY KEY, id_producto INT NOT NULL, porcentaje DECIMAL(5,2) NOT NULL,
 fecha_inicio DATE NOT NULL, fecha_fin DATE NOT NULL, estado ENUM('ACTIVO','INACTIVO') NOT NULL DEFAULT 'ACTIVO',
 FOREIGN KEY (id_producto) REFERENCES productos(id_producto), CHECK (porcentaje >= 0 AND porcentaje <= 100)
);
CREATE TABLE clientes (
 id_cliente INT AUTO_INCREMENT PRIMARY KEY, nombre VARCHAR(120) NOT NULL,
 correo VARCHAR(150) NOT NULL UNIQUE, estado ENUM('ACTIVO','INACTIVO') NOT NULL DEFAULT 'ACTIVO'
);
CREATE TABLE cuentas (
 id_cuenta INT AUTO_INCREMENT PRIMARY KEY, id_cliente INT NOT NULL UNIQUE, usuario VARCHAR(80) NOT NULL UNIQUE,
 password_hash VARCHAR(255) NULL, estado ENUM('ACTIVA','INACTIVA') NOT NULL DEFAULT 'ACTIVA',
 FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente)
);
CREATE TABLE favoritos (
 id_favorito INT AUTO_INCREMENT PRIMARY KEY, id_cliente INT NOT NULL, id_producto INT NOT NULL,
 fecha_agregado DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP, UNIQUE KEY uq_favorito(id_cliente,id_producto),
 FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente), FOREIGN KEY (id_producto) REFERENCES productos(id_producto)
);
CREATE TABLE calificaciones (
 id_calificacion INT AUTO_INCREMENT PRIMARY KEY, id_cliente INT NOT NULL, id_producto INT NOT NULL,
 puntuacion TINYINT NOT NULL, comentario VARCHAR(255), fecha DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
 UNIQUE KEY uq_calificacion(id_cliente,id_producto), FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente),
 FOREIGN KEY (id_producto) REFERENCES productos(id_producto), CHECK (puntuacion BETWEEN 1 AND 5)
);
CREATE TABLE pagos (
 id_pago INT AUTO_INCREMENT PRIMARY KEY, id_cliente INT NOT NULL, id_producto INT NOT NULL,
 precio_original DECIMAL(12,2) NOT NULL, porcentaje_descuento DECIMAL(5,2) NOT NULL DEFAULT 0,
 total_pagado DECIMAL(12,2) NOT NULL, comision_mb DECIMAL(12,2) NOT NULL, valor_marca DECIMAL(12,2) NOT NULL,
 estado_pago ENUM('PENDIENTE','APROBADO','RECHAZADO','CANCELADO') NOT NULL,
 fecha_pago DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente),
 FOREIGN KEY (id_producto) REFERENCES productos(id_producto)
);
CREATE TABLE sistema (
 id_sistema INT AUTO_INCREMENT PRIMARY KEY, nombre VARCHAR(100) NOT NULL, descripcion VARCHAR(255), version VARCHAR(30) NOT NULL
);

INSERT INTO marcas(nombre,descripcion,canal_oficial) VALUES
('Nike','Marca de ropa y calzado deportivo','https://www.nike.com/co/'),
('Adidas','Ropa y calzado deportivo','https://www.adidas.co/'),
('Puma','Ropa y calzado deportivo','https://co.puma.com/');
INSERT INTO productos(id_marca,nombre,categoria,descripcion,precio,stock) VALUES
(1,'Air Max 270','Calzado','Tenis deportivos Nike',500000,12),
(1,'Tech Fleece Hoodie','Ropa','Buzo deportivo Nike',320000,8),
(2,'Forum Low','Calzado','Tenis casuales Adidas',450000,10),
(2,'Essentials Hoodie','Ropa','Buzo Adidas',280000,15),
(3,'RS-X','Calzado','Tenis Puma',400000,7),
(3,'Classic Logo Tee','Ropa','Camiseta Puma',120000,20);
INSERT INTO descuentos(id_producto,porcentaje,fecha_inicio,fecha_fin,estado) VALUES
(1,30,'2026-09-01','2026-12-31','ACTIVO'),(2,20,'2026-09-01','2026-12-31','ACTIVO'),
(3,25,'2026-09-01','2026-12-31','ACTIVO'),(4,15,'2026-09-01','2026-12-31','ACTIVO'),
(5,35,'2026-09-01','2026-12-31','ACTIVO'),(6,10,'2026-09-01','2026-12-31','ACTIVO');
INSERT INTO clientes(nombre,correo) VALUES ('Sebastian','sebastian@ejemplo.com'),('Cliente Demo','demo@ejemplo.com');
INSERT INTO cuentas(id_cliente,usuario,password_hash) VALUES (1,'sebastian',NULL),(2,'demo',NULL);
INSERT INTO sistema(nombre,descripcion,version) VALUES ('MB Multibrand','Centralizador de productos y ofertas multimarca','2.0-REST');

-- ===== Datos demo del microservicio de calificaciones (puerto 5004) =====
-- Clientes adicionales (sin cuenta de login) para que el ranking y las estadisticas tengan datos.
INSERT INTO clientes(nombre,correo) VALUES
('Laura Gomez','laura@ejemplo.com'),('Carlos Ruiz','carlos@ejemplo.com'),
('Marta Perez','marta@ejemplo.com'),('Andres Lopez','andres@ejemplo.com');
-- Compras simuladas aprobadas (comision MB 5%). Sebastian (1) tiene el producto 1 comprado SIN calificar (queda "pendiente").
INSERT INTO pagos(id_cliente,id_producto,precio_original,porcentaje_descuento,total_pagado,comision_mb,valor_marca,estado_pago) VALUES
(1,1,500000,30,350000,17500,332500,'APROBADO'),
(1,5,400000,35,260000,13000,247000,'APROBADO'),
(2,3,450000,25,337500,16875,320625,'APROBADO'),
(3,1,500000,30,350000,17500,332500,'APROBADO'),
(3,3,450000,25,337500,16875,320625,'APROBADO'),
(4,1,500000,30,350000,17500,332500,'APROBADO'),
(4,5,400000,35,260000,13000,247000,'APROBADO'),
(5,5,400000,35,260000,13000,247000,'APROBADO'),
(5,4,280000,15,238000,11900,226100,'APROBADO'),
(6,2,320000,20,256000,12800,243200,'APROBADO'),
(6,6,120000,10,108000,5400,102600,'APROBADO');
UPDATE productos SET stock=stock-3 WHERE id_producto=1;
UPDATE productos SET stock=stock-1 WHERE id_producto=2;
UPDATE productos SET stock=stock-2 WHERE id_producto=3;
UPDATE productos SET stock=stock-1 WHERE id_producto=4;
UPDATE productos SET stock=stock-3 WHERE id_producto=5;
UPDATE productos SET stock=stock-1 WHERE id_producto=6;
-- Calificaciones (solo de clientes que compraron el producto).
INSERT INTO calificaciones(id_cliente,id_producto,puntuacion,comentario) VALUES
(1,5,5,'Muy comodos, excelente descuento'),
(2,3,4,'Buen diseño casual'),
(3,1,5,'Los mejores para correr'),
(3,3,5,'Calidad impecable'),
(4,1,4,'Buenos, pero tallan pequeño'),
(4,5,2,'Se sintieron duros'),
(5,5,3,'Normales por ese precio'),
(5,4,4,'Abrigado y comodo'),
(6,2,5,'Gran buzo'),
(6,6,3,NULL);

INSERT INTO productos (id_marca,nombre,categoria,descripcion,precio,stock) SELECT m.id_marca,'Court Vision Low','Calzado','Zapatillas urbanas de inspiración clásica',279000,16 FROM marcas m WHERE m.nombre='Nike' AND NOT EXISTS (SELECT 1 FROM productos p WHERE p.id_marca=m.id_marca AND p.nombre='Court Vision Low');
INSERT INTO descuentos (id_producto,porcentaje,fecha_inicio,fecha_fin,estado) SELECT p.id_producto,40,'2026-01-01','2027-12-31','ACTIVO' FROM productos p JOIN marcas m ON m.id_marca=p.id_marca WHERE m.nombre='Nike' AND p.nombre='Court Vision Low' AND NOT EXISTS (SELECT 1 FROM descuentos d WHERE d.id_producto=p.id_producto AND d.estado='ACTIVO');
INSERT INTO productos (id_marca,nombre,categoria,descripcion,precio,stock) SELECT m.id_marca,'Revolution 7','Calzado','Calzado ligero para entrenamientos diarios',329000,18 FROM marcas m WHERE m.nombre='Nike' AND NOT EXISTS (SELECT 1 FROM productos p WHERE p.id_marca=m.id_marca AND p.nombre='Revolution 7');
INSERT INTO descuentos (id_producto,porcentaje,fecha_inicio,fecha_fin,estado) SELECT p.id_producto,35,'2026-01-01','2027-12-31','ACTIVO' FROM productos p JOIN marcas m ON m.id_marca=p.id_marca WHERE m.nombre='Nike' AND p.nombre='Revolution 7' AND NOT EXISTS (SELECT 1 FROM descuentos d WHERE d.id_producto=p.id_producto AND d.estado='ACTIVO');
INSERT INTO productos (id_marca,nombre,categoria,descripcion,precio,stock) SELECT m.id_marca,'Air Force 1','Calzado','Tenis urbanos de estilo atemporal',549000,9 FROM marcas m WHERE m.nombre='Nike' AND NOT EXISTS (SELECT 1 FROM productos p WHERE p.id_marca=m.id_marca AND p.nombre='Air Force 1');
INSERT INTO descuentos (id_producto,porcentaje,fecha_inicio,fecha_fin,estado) SELECT p.id_producto,22,'2026-01-01','2027-12-31','ACTIVO' FROM productos p JOIN marcas m ON m.id_marca=p.id_marca WHERE m.nombre='Nike' AND p.nombre='Air Force 1' AND NOT EXISTS (SELECT 1 FROM descuentos d WHERE d.id_producto=p.id_producto AND d.estado='ACTIVO');
INSERT INTO productos (id_marca,nombre,categoria,descripcion,precio,stock) SELECT m.id_marca,'Dri-FIT Training Tee','Ropa','Camiseta deportiva de entrenamiento',149000,22 FROM marcas m WHERE m.nombre='Nike' AND NOT EXISTS (SELECT 1 FROM productos p WHERE p.id_marca=m.id_marca AND p.nombre='Dri-FIT Training Tee');
INSERT INTO descuentos (id_producto,porcentaje,fecha_inicio,fecha_fin,estado) SELECT p.id_producto,45,'2026-01-01','2027-12-31','ACTIVO' FROM productos p JOIN marcas m ON m.id_marca=p.id_marca WHERE m.nombre='Nike' AND p.nombre='Dri-FIT Training Tee' AND NOT EXISTS (SELECT 1 FROM descuentos d WHERE d.id_producto=p.id_producto AND d.estado='ACTIVO');
INSERT INTO productos (id_marca,nombre,categoria,descripcion,precio,stock) SELECT m.id_marca,'Club Fleece Jogger','Ropa','Pantalón cómodo de estilo deportivo',259000,13 FROM marcas m WHERE m.nombre='Nike' AND NOT EXISTS (SELECT 1 FROM productos p WHERE p.id_marca=m.id_marca AND p.nombre='Club Fleece Jogger');
INSERT INTO descuentos (id_producto,porcentaje,fecha_inicio,fecha_fin,estado) SELECT p.id_producto,30,'2026-01-01','2027-12-31','ACTIVO' FROM productos p JOIN marcas m ON m.id_marca=p.id_marca WHERE m.nombre='Nike' AND p.nombre='Club Fleece Jogger' AND NOT EXISTS (SELECT 1 FROM descuentos d WHERE d.id_producto=p.id_producto AND d.estado='ACTIVO');
INSERT INTO productos (id_marca,nombre,categoria,descripcion,precio,stock) SELECT m.id_marca,'Heritage Backpack','Accesorios','Morral de uso diario',189000,11 FROM marcas m WHERE m.nombre='Nike' AND NOT EXISTS (SELECT 1 FROM productos p WHERE p.id_marca=m.id_marca AND p.nombre='Heritage Backpack');
INSERT INTO descuentos (id_producto,porcentaje,fecha_inicio,fecha_fin,estado) SELECT p.id_producto,50,'2026-01-01','2027-12-31','ACTIVO' FROM productos p JOIN marcas m ON m.id_marca=p.id_marca WHERE m.nombre='Nike' AND p.nombre='Heritage Backpack' AND NOT EXISTS (SELECT 1 FROM descuentos d WHERE d.id_producto=p.id_producto AND d.estado='ACTIVO');
INSERT INTO productos (id_marca,nombre,categoria,descripcion,precio,stock) SELECT m.id_marca,'Sportswear Cap','Accesorios','Gorra deportiva ajustable',119000,19 FROM marcas m WHERE m.nombre='Nike' AND NOT EXISTS (SELECT 1 FROM productos p WHERE p.id_marca=m.id_marca AND p.nombre='Sportswear Cap');
INSERT INTO descuentos (id_producto,porcentaje,fecha_inicio,fecha_fin,estado) SELECT p.id_producto,25,'2026-01-01','2027-12-31','ACTIVO' FROM productos p JOIN marcas m ON m.id_marca=p.id_marca WHERE m.nombre='Nike' AND p.nombre='Sportswear Cap' AND NOT EXISTS (SELECT 1 FROM descuentos d WHERE d.id_producto=p.id_producto AND d.estado='ACTIVO');
INSERT INTO productos (id_marca,nombre,categoria,descripcion,precio,stock) SELECT m.id_marca,'Grand Court Base','Calzado','Tenis casuales de perfil clásico',319000,12 FROM marcas m WHERE m.nombre='Adidas' AND NOT EXISTS (SELECT 1 FROM productos p WHERE p.id_marca=m.id_marca AND p.nombre='Grand Court Base');
INSERT INTO descuentos (id_producto,porcentaje,fecha_inicio,fecha_fin,estado) SELECT p.id_producto,42,'2026-01-01','2027-12-31','ACTIVO' FROM productos p JOIN marcas m ON m.id_marca=p.id_marca WHERE m.nombre='Adidas' AND p.nombre='Grand Court Base' AND NOT EXISTS (SELECT 1 FROM descuentos d WHERE d.id_producto=p.id_producto AND d.estado='ACTIVO');
INSERT INTO productos (id_marca,nombre,categoria,descripcion,precio,stock) SELECT m.id_marca,'Runfalcon 3','Calzado','Tenis para uso deportivo diario',289000,20 FROM marcas m WHERE m.nombre='Adidas' AND NOT EXISTS (SELECT 1 FROM productos p WHERE p.id_marca=m.id_marca AND p.nombre='Runfalcon 3');
INSERT INTO descuentos (id_producto,porcentaje,fecha_inicio,fecha_fin,estado) SELECT p.id_producto,38,'2026-01-01','2027-12-31','ACTIVO' FROM productos p JOIN marcas m ON m.id_marca=p.id_marca WHERE m.nombre='Adidas' AND p.nombre='Runfalcon 3' AND NOT EXISTS (SELECT 1 FROM descuentos d WHERE d.id_producto=p.id_producto AND d.estado='ACTIVO');
INSERT INTO productos (id_marca,nombre,categoria,descripcion,precio,stock) SELECT m.id_marca,'Superstar','Calzado','Tenis urbanos de diseño icónico',499000,10 FROM marcas m WHERE m.nombre='Adidas' AND NOT EXISTS (SELECT 1 FROM productos p WHERE p.id_marca=m.id_marca AND p.nombre='Superstar');
INSERT INTO descuentos (id_producto,porcentaje,fecha_inicio,fecha_fin,estado) SELECT p.id_producto,20,'2026-01-01','2027-12-31','ACTIVO' FROM productos p JOIN marcas m ON m.id_marca=p.id_marca WHERE m.nombre='Adidas' AND p.nombre='Superstar' AND NOT EXISTS (SELECT 1 FROM descuentos d WHERE d.id_producto=p.id_producto AND d.estado='ACTIVO');
INSERT INTO productos (id_marca,nombre,categoria,descripcion,precio,stock) SELECT m.id_marca,'Entrada 22 Jersey','Ropa','Camiseta de entrenamiento',139000,25 FROM marcas m WHERE m.nombre='Adidas' AND NOT EXISTS (SELECT 1 FROM productos p WHERE p.id_marca=m.id_marca AND p.nombre='Entrada 22 Jersey');
INSERT INTO descuentos (id_producto,porcentaje,fecha_inicio,fecha_fin,estado) SELECT p.id_producto,55,'2026-01-01','2027-12-31','ACTIVO' FROM productos p JOIN marcas m ON m.id_marca=p.id_marca WHERE m.nombre='Adidas' AND p.nombre='Entrada 22 Jersey' AND NOT EXISTS (SELECT 1 FROM descuentos d WHERE d.id_producto=p.id_producto AND d.estado='ACTIVO');
INSERT INTO productos (id_marca,nombre,categoria,descripcion,precio,stock) SELECT m.id_marca,'Tiro Track Pants','Ropa','Pantalón deportivo de corte cómodo',249000,14 FROM marcas m WHERE m.nombre='Adidas' AND NOT EXISTS (SELECT 1 FROM productos p WHERE p.id_marca=m.id_marca AND p.nombre='Tiro Track Pants');
INSERT INTO descuentos (id_producto,porcentaje,fecha_inicio,fecha_fin,estado) SELECT p.id_producto,32,'2026-01-01','2027-12-31','ACTIVO' FROM productos p JOIN marcas m ON m.id_marca=p.id_marca WHERE m.nombre='Adidas' AND p.nombre='Tiro Track Pants' AND NOT EXISTS (SELECT 1 FROM descuentos d WHERE d.id_producto=p.id_producto AND d.estado='ACTIVO');
INSERT INTO productos (id_marca,nombre,categoria,descripcion,precio,stock) SELECT m.id_marca,'Classic Backpack','Accesorios','Morral para universidad y ciudad',179000,17 FROM marcas m WHERE m.nombre='Adidas' AND NOT EXISTS (SELECT 1 FROM productos p WHERE p.id_marca=m.id_marca AND p.nombre='Classic Backpack');
INSERT INTO descuentos (id_producto,porcentaje,fecha_inicio,fecha_fin,estado) SELECT p.id_producto,48,'2026-01-01','2027-12-31','ACTIVO' FROM productos p JOIN marcas m ON m.id_marca=p.id_marca WHERE m.nombre='Adidas' AND p.nombre='Classic Backpack' AND NOT EXISTS (SELECT 1 FROM descuentos d WHERE d.id_producto=p.id_producto AND d.estado='ACTIVO');
INSERT INTO productos (id_marca,nombre,categoria,descripcion,precio,stock) SELECT m.id_marca,'Baseball Cap','Accesorios','Gorra casual con visera',109000,21 FROM marcas m WHERE m.nombre='Adidas' AND NOT EXISTS (SELECT 1 FROM productos p WHERE p.id_marca=m.id_marca AND p.nombre='Baseball Cap');
INSERT INTO descuentos (id_producto,porcentaje,fecha_inicio,fecha_fin,estado) SELECT p.id_producto,27,'2026-01-01','2027-12-31','ACTIVO' FROM productos p JOIN marcas m ON m.id_marca=p.id_marca WHERE m.nombre='Adidas' AND p.nombre='Baseball Cap' AND NOT EXISTS (SELECT 1 FROM descuentos d WHERE d.id_producto=p.id_producto AND d.estado='ACTIVO');
INSERT INTO productos (id_marca,nombre,categoria,descripcion,precio,stock) SELECT m.id_marca,'Smash V2','Calzado','Tenis urbanos de estilo minimalista',259000,15 FROM marcas m WHERE m.nombre='Puma' AND NOT EXISTS (SELECT 1 FROM productos p WHERE p.id_marca=m.id_marca AND p.nombre='Smash V2');
INSERT INTO descuentos (id_producto,porcentaje,fecha_inicio,fecha_fin,estado) SELECT p.id_producto,46,'2026-01-01','2027-12-31','ACTIVO' FROM productos p JOIN marcas m ON m.id_marca=p.id_marca WHERE m.nombre='Puma' AND p.nombre='Smash V2' AND NOT EXISTS (SELECT 1 FROM descuentos d WHERE d.id_producto=p.id_producto AND d.estado='ACTIVO');
INSERT INTO productos (id_marca,nombre,categoria,descripcion,precio,stock) SELECT m.id_marca,'Carina Street','Calzado','Tenis casuales de plataforma',329000,12 FROM marcas m WHERE m.nombre='Puma' AND NOT EXISTS (SELECT 1 FROM productos p WHERE p.id_marca=m.id_marca AND p.nombre='Carina Street');
INSERT INTO descuentos (id_producto,porcentaje,fecha_inicio,fecha_fin,estado) SELECT p.id_producto,33,'2026-01-01','2027-12-31','ACTIVO' FROM productos p JOIN marcas m ON m.id_marca=p.id_marca WHERE m.nombre='Puma' AND p.nombre='Carina Street' AND NOT EXISTS (SELECT 1 FROM descuentos d WHERE d.id_producto=p.id_producto AND d.estado='ACTIVO');
INSERT INTO productos (id_marca,nombre,categoria,descripcion,precio,stock) SELECT m.id_marca,'Future Rider','Calzado','Tenis retro de estilo deportivo',379000,8 FROM marcas m WHERE m.nombre='Puma' AND NOT EXISTS (SELECT 1 FROM productos p WHERE p.id_marca=m.id_marca AND p.nombre='Future Rider');
INSERT INTO descuentos (id_producto,porcentaje,fecha_inicio,fecha_fin,estado) SELECT p.id_producto,41,'2026-01-01','2027-12-31','ACTIVO' FROM productos p JOIN marcas m ON m.id_marca=p.id_marca WHERE m.nombre='Puma' AND p.nombre='Future Rider' AND NOT EXISTS (SELECT 1 FROM descuentos d WHERE d.id_producto=p.id_producto AND d.estado='ACTIVO');
INSERT INTO productos (id_marca,nombre,categoria,descripcion,precio,stock) SELECT m.id_marca,'Essentials Small Logo Tee','Ropa','Camiseta básica de algodón',129000,23 FROM marcas m WHERE m.nombre='Puma' AND NOT EXISTS (SELECT 1 FROM productos p WHERE p.id_marca=m.id_marca AND p.nombre='Essentials Small Logo Tee');
INSERT INTO descuentos (id_producto,porcentaje,fecha_inicio,fecha_fin,estado) SELECT p.id_producto,52,'2026-01-01','2027-12-31','ACTIVO' FROM productos p JOIN marcas m ON m.id_marca=p.id_marca WHERE m.nombre='Puma' AND p.nombre='Essentials Small Logo Tee' AND NOT EXISTS (SELECT 1 FROM descuentos d WHERE d.id_producto=p.id_producto AND d.estado='ACTIVO');
INSERT INTO productos (id_marca,nombre,categoria,descripcion,precio,stock) SELECT m.id_marca,'Evostripe Hoodie','Ropa','Buzo deportivo con capucha',289000,13 FROM marcas m WHERE m.nombre='Puma' AND NOT EXISTS (SELECT 1 FROM productos p WHERE p.id_marca=m.id_marca AND p.nombre='Evostripe Hoodie');
INSERT INTO descuentos (id_producto,porcentaje,fecha_inicio,fecha_fin,estado) SELECT p.id_producto,36,'2026-01-01','2027-12-31','ACTIVO' FROM productos p JOIN marcas m ON m.id_marca=p.id_marca WHERE m.nombre='Puma' AND p.nombre='Evostripe Hoodie' AND NOT EXISTS (SELECT 1 FROM descuentos d WHERE d.id_producto=p.id_producto AND d.estado='ACTIVO');
INSERT INTO productos (id_marca,nombre,categoria,descripcion,precio,stock) SELECT m.id_marca,'Phase Backpack','Accesorios','Morral urbano compacto',159000,16 FROM marcas m WHERE m.nombre='Puma' AND NOT EXISTS (SELECT 1 FROM productos p WHERE p.id_marca=m.id_marca AND p.nombre='Phase Backpack');
INSERT INTO descuentos (id_producto,porcentaje,fecha_inicio,fecha_fin,estado) SELECT p.id_producto,44,'2026-01-01','2027-12-31','ACTIVO' FROM productos p JOIN marcas m ON m.id_marca=p.id_marca WHERE m.nombre='Puma' AND p.nombre='Phase Backpack' AND NOT EXISTS (SELECT 1 FROM descuentos d WHERE d.id_producto=p.id_producto AND d.estado='ACTIVO');
INSERT INTO productos (id_marca,nombre,categoria,descripcion,precio,stock) SELECT m.id_marca,'Metal Cat Cap','Accesorios','Gorra casual ajustable',99000,18 FROM marcas m WHERE m.nombre='Puma' AND NOT EXISTS (SELECT 1 FROM productos p WHERE p.id_marca=m.id_marca AND p.nombre='Metal Cat Cap');
INSERT INTO descuentos (id_producto,porcentaje,fecha_inicio,fecha_fin,estado) SELECT p.id_producto,29,'2026-01-01','2027-12-31','ACTIVO' FROM productos p JOIN marcas m ON m.id_marca=p.id_marca WHERE m.nombre='Puma' AND p.nombre='Metal Cat Cap' AND NOT EXISTS (SELECT 1 FROM descuentos d WHERE d.id_producto=p.id_producto AND d.estado='ACTIVO');
COMMIT;
