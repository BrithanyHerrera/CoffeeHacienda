-- MySQL dump 10.13  Distrib 8.0.19, for Win64 (x86_64)
--
-- Host: mysql-2d029af-coffee-hacienda.l.aivencloud.com    Database: bd
-- ------------------------------------------------------
-- Server version	8.0.45

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;
SET @MYSQLDUMP_TEMP_LOG_BIN = @@SESSION.SQL_LOG_BIN;
SET @@SESSION.SQL_LOG_BIN= 0;

--
-- GTID state at the beginning of the backup 
--

SET @@GLOBAL.GTID_PURGED=/*!80000 '+'*/ 'b1400fcf-3547-11f1-b174-127bef6f313a:1-195,
ed822e13-3767-11f1-b635-d6cb7dcb9ec1:1-104';

--
-- Table structure for table `tcategorias`
--

DROP TABLE IF EXISTS `tcategorias`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tcategorias` (
  `Id` int NOT NULL AUTO_INCREMENT,
  `categoria` varchar(100) NOT NULL,
  `creado_en` datetime DEFAULT CURRENT_TIMESTAMP,
  `actualizado_en` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `requiere_inventario` tinyint(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (`Id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tcategorias`
--

LOCK TABLES `tcategorias` WRITE;
/*!40000 ALTER TABLE `tcategorias` DISABLE KEYS */;
INSERT INTO `tcategorias` VALUES (1,'Bebidas Calientes','2025-03-09 00:44:07','2025-03-09 00:44:07',0),(2,'Bebidas Frías','2025-03-09 00:44:07','2025-03-09 00:44:07',0),(3,'Snacks','2025-03-09 00:44:07','2025-04-09 01:50:56',1),(4,'Postres','2025-03-09 00:44:07','2025-03-15 19:24:32',1),(5,'Todos','2025-03-09 00:44:07','2025-03-09 00:44:07',0),(6,'Otras Bebidas','2025-03-09 00:44:07','2025-04-09 02:42:11',0);
/*!40000 ALTER TABLE `tcategorias` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tclientes`
--

DROP TABLE IF EXISTS `tclientes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tclientes` (
  `Id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(255) NOT NULL,
  PRIMARY KEY (`Id`)
) ENGINE=InnoDB AUTO_INCREMENT=66 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tclientes`
--

LOCK TABLES `tclientes` WRITE;
/*!40000 ALTER TABLE `tclientes` DISABLE KEYS */;
INSERT INTO `tclientes` VALUES (36,'Juan'),(37,'Isma'),(40,'qaq'),(41,'asa'),(42,'wasa'),(43,'qaza'),(44,'Ana'),(45,'Lalo'),(46,'Me'),(47,'Pina'),(48,'titi'),(49,'Lola'),(50,'pepe'),(51,'Reyna'),(52,'ESPE'),(53,'IRMA'),(54,'Juliette'),(55,'Yo'),(56,'Bri'),(57,'Cami'),(58,'Camim'),(59,'iris'),(60,'Ismael'),(62,'efdeaaadbddefdeaaadbddefdeaaadbddefdeaaadbddefdeaaadbddefdeaaadbddefdeaaadbddefdeaaadbddefdeaaadbddefdeaaadbdd'),(63,'isamel'),(64,'d                                                                                 f'),(65,'Test Client');
/*!40000 ALTER TABLE `tclientes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tcodigosrecuperacion`
--

DROP TABLE IF EXISTS `tcodigosrecuperacion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tcodigosrecuperacion` (
  `Id` int NOT NULL AUTO_INCREMENT,
  `usuario_id` int NOT NULL,
  `codigo` varchar(10) NOT NULL,
  `fecha_expiracion` datetime NOT NULL,
  `fecha_creacion` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`Id`),
  KEY `usuario_id` (`usuario_id`),
  CONSTRAINT `tcodigosrecuperacion_ibfk_1` FOREIGN KEY (`usuario_id`) REFERENCES `tusuarios` (`Id`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tcodigosrecuperacion`
--

LOCK TABLES `tcodigosrecuperacion` WRITE;
/*!40000 ALTER TABLE `tcodigosrecuperacion` DISABLE KEYS */;
/*!40000 ALTER TABLE `tcodigosrecuperacion` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tcortescaja`
--

DROP TABLE IF EXISTS `tcortescaja`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tcortescaja` (
  `Id` int NOT NULL AUTO_INCREMENT,
  `vendedor_id` int DEFAULT NULL,
  `fecha_hora_inicio` datetime DEFAULT NULL,
  `fecha_hora_cierre` datetime DEFAULT NULL,
  `total_ventas` decimal(10,2) NOT NULL,
  `total_efectivo` decimal(10,2) NOT NULL,
  `total_transferencias` decimal(10,2) NOT NULL,
  `total_paypal` decimal(10,2) NOT NULL,
  `total_contado` decimal(10,2) NOT NULL DEFAULT '0.00',
  `pagos_realizados` decimal(10,2) NOT NULL DEFAULT '0.00',
  `fondo` varchar(255) DEFAULT NULL,
  `ganancia_o_perdida` float DEFAULT NULL,
  PRIMARY KEY (`Id`),
  KEY `vendedor_id` (`vendedor_id`),
  CONSTRAINT `tcortescaja_ibfk_1` FOREIGN KEY (`vendedor_id`) REFERENCES `tusuarios` (`Id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tcortescaja`
--

LOCK TABLES `tcortescaja` WRITE;
/*!40000 ALTER TABLE `tcortescaja` DISABLE KEYS */;
INSERT INTO `tcortescaja` VALUES (4,NULL,'2025-04-08 15:44:00','2025-04-10 15:44:00',102.00,2.00,60.00,40.00,102.00,0.00,'900',102),(5,NULL,'2025-05-06 15:33:00','2025-05-06 19:33:00',195.00,50.00,120.00,25.00,455.00,0.00,'500',195),(6,NULL,'2025-05-01 13:12:00','2025-05-14 13:12:00',1965.00,1245.00,720.00,0.00,1965.00,400.00,'3000',1565),(7,NULL,'2025-05-01 13:12:00','2025-05-14 13:12:00',1965.00,1245.00,720.00,0.00,1965.00,400.00,'3000',1565),(8,NULL,'2025-05-01 14:41:00','2025-05-14 14:41:00',2100.00,1350.00,750.00,0.00,2100.00,0.00,'300',2100);
/*!40000 ALTER TABLE `tcortescaja` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tdetalleventas`
--

DROP TABLE IF EXISTS `tdetalleventas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tdetalleventas` (
  `Id` int NOT NULL AUTO_INCREMENT,
  `venta_id` int DEFAULT NULL,
  `producto_id` int DEFAULT NULL,
  `cantidad` int NOT NULL,
  `precio` decimal(10,2) NOT NULL,
  `creado_en` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`Id`),
  KEY `venta_id` (`venta_id`),
  KEY `tdetalleventas_ibfk_2` (`producto_id`),
  CONSTRAINT `tdetalleventas_ibfk_1` FOREIGN KEY (`venta_id`) REFERENCES `tventas` (`Id`) ON DELETE CASCADE,
  CONSTRAINT `tdetalleventas_ibfk_2` FOREIGN KEY (`producto_id`) REFERENCES `tproductos` (`Id`),
  CONSTRAINT `chk_cantidad_positiva` CHECK ((`cantidad` > 0)),
  CONSTRAINT `chk_precio_detalle_positivo` CHECK ((`precio` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=107 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tdetalleventas`
--

LOCK TABLES `tdetalleventas` WRITE;
/*!40000 ALTER TABLE `tdetalleventas` DISABLE KEYS */;
INSERT INTO `tdetalleventas` VALUES (50,52,42,1,2.00,'2025-04-10 15:34:05'),(51,53,48,1,60.00,'2025-04-10 15:43:27'),(52,54,45,1,40.00,'2025-04-10 15:43:44'),(53,55,50,1,25.00,'2025-04-10 16:02:06'),(54,56,50,1,25.00,'2025-04-10 16:17:28'),(55,57,50,4,25.00,'2025-04-10 18:00:22'),(56,58,45,6,40.00,'2025-04-10 18:06:53'),(60,62,48,2,60.00,'2025-05-06 17:33:35'),(61,63,50,1,25.00,'2025-05-10 00:01:54'),(62,64,47,4,90.00,'2025-05-10 01:07:31'),(64,66,45,1,40.00,'2025-05-10 01:10:48'),(65,67,45,10,40.00,'2025-05-10 01:52:09'),(66,68,48,1,60.00,'2025-05-12 00:30:01'),(67,68,45,1,40.00,'2025-05-12 00:30:01'),(68,68,50,1,25.00,'2025-05-12 00:30:01'),(69,68,52,1,30.00,'2025-05-12 00:30:01'),(70,68,46,1,90.00,'2025-05-12 00:30:01'),(71,68,47,1,90.00,'2025-05-12 00:30:01'),(72,68,49,1,70.00,'2025-05-12 00:30:01'),(73,69,50,4,25.00,'2025-05-14 12:48:14'),(74,70,50,3,25.00,'2025-05-14 14:24:36'),(78,74,50,1,25.00,'2026-04-20 16:58:32'),(79,75,48,1,60.00,'2026-04-20 21:51:50'),(103,98,52,8,30.00,'2026-04-20 22:29:36'),(104,99,48,1,60.00,'2026-04-20 22:30:12'),(105,100,45,1,40.00,'2026-04-23 03:43:39'),(106,101,45,1,40.00,'2026-04-23 03:59:11');
/*!40000 ALTER TABLE `tdetalleventas` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tdevoluciones`
--

DROP TABLE IF EXISTS `tdevoluciones`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tdevoluciones` (
  `Id` int NOT NULL,
  `venta_id` int DEFAULT NULL,
  `producto_id` int DEFAULT NULL,
  `cantidad` int NOT NULL,
  `tipo_devolucion_id` int DEFAULT NULL,
  `estado_devolucion_id` int DEFAULT NULL,
  `creado_en` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`Id`),
  KEY `venta_id` (`venta_id`),
  KEY `producto_id` (`producto_id`),
  KEY `tipo_devolucion_id` (`tipo_devolucion_id`),
  KEY `estado_devolucion_id` (`estado_devolucion_id`),
  CONSTRAINT `tdevoluciones_ibfk_1` FOREIGN KEY (`venta_id`) REFERENCES `tventas` (`Id`),
  CONSTRAINT `tdevoluciones_ibfk_2` FOREIGN KEY (`producto_id`) REFERENCES `tproductos` (`Id`),
  CONSTRAINT `tdevoluciones_ibfk_3` FOREIGN KEY (`tipo_devolucion_id`) REFERENCES `ttiposdevolucion` (`Id`),
  CONSTRAINT `tdevoluciones_ibfk_4` FOREIGN KEY (`estado_devolucion_id`) REFERENCES `testadosdevolucion` (`Id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tdevoluciones`
--

LOCK TABLES `tdevoluciones` WRITE;
/*!40000 ALTER TABLE `tdevoluciones` DISABLE KEYS */;
/*!40000 ALTER TABLE `tdevoluciones` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `testadosdevolucion`
--

DROP TABLE IF EXISTS `testadosdevolucion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `testadosdevolucion` (
  `Id` int NOT NULL,
  `estado` varchar(50) NOT NULL,
  PRIMARY KEY (`Id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `testadosdevolucion`
--

LOCK TABLES `testadosdevolucion` WRITE;
/*!40000 ALTER TABLE `testadosdevolucion` DISABLE KEYS */;
INSERT INTO `testadosdevolucion` VALUES (1,'Pendiente'),(2,'Aprobada'),(3,'Rechazada'),(4,'Cancelada');
/*!40000 ALTER TABLE `testadosdevolucion` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `testadosventa`
--

DROP TABLE IF EXISTS `testadosventa`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `testadosventa` (
  `Id` int NOT NULL AUTO_INCREMENT,
  `estado` varchar(50) NOT NULL,
  PRIMARY KEY (`Id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `testadosventa`
--

LOCK TABLES `testadosventa` WRITE;
/*!40000 ALTER TABLE `testadosventa` DISABLE KEYS */;
INSERT INTO `testadosventa` VALUES (1,'Pendiente'),(2,'En proceso'),(3,'Cancelado'),(4,'Completado'),(5,'Reembolsada');
/*!40000 ALTER TABLE `testadosventa` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tmetodospago`
--

DROP TABLE IF EXISTS `tmetodospago`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tmetodospago` (
  `Id` int NOT NULL,
  `tipo_de_pago` varchar(50) NOT NULL,
  PRIMARY KEY (`Id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tmetodospago`
--

LOCK TABLES `tmetodospago` WRITE;
/*!40000 ALTER TABLE `tmetodospago` DISABLE KEYS */;
INSERT INTO `tmetodospago` VALUES (1,'Efectivo'),(2,'Transferencia Bancaria'),(3,'PayPal');
/*!40000 ALTER TABLE `tmetodospago` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tmovimientosinventario`
--

DROP TABLE IF EXISTS `tmovimientosinventario`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tmovimientosinventario` (
  `Id` int NOT NULL,
  `producto_id` int NOT NULL,
  `cantidad` int NOT NULL,
  `tipo_movimiento_id` int NOT NULL,
  `motivo` text,
  `creado_en` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`Id`),
  KEY `producto_id` (`producto_id`),
  KEY `tipo_movimiento_id` (`tipo_movimiento_id`),
  CONSTRAINT `tmovimientosinventario_ibfk_1` FOREIGN KEY (`producto_id`) REFERENCES `tproductos` (`Id`),
  CONSTRAINT `tmovimientosinventario_ibfk_2` FOREIGN KEY (`tipo_movimiento_id`) REFERENCES `ttiposmovimiento` (`Id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tmovimientosinventario`
--

LOCK TABLES `tmovimientosinventario` WRITE;
/*!40000 ALTER TABLE `tmovimientosinventario` DISABLE KEYS */;
INSERT INTO `tmovimientosinventario` VALUES (1,47,2,3,'Actualización desde panel de inventario','2026-04-20 17:11:00'),(2,46,3,3,'Actualización desde panel de inventario','2026-04-20 17:11:18'),(3,47,17,3,'Actualización desde panel de inventario','2026-04-21 18:00:16'),(4,50,50,4,'Actualización desde panel de inventario','2026-04-21 18:01:08'),(5,52,50,3,'Actualización desde panel de inventario','2026-04-21 18:01:26'),(6,46,3,4,'Actualización desde panel de inventario','2026-04-21 18:01:40');
/*!40000 ALTER TABLE `tmovimientosinventario` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tpagos`
--

DROP TABLE IF EXISTS `tpagos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tpagos` (
  `Id` int NOT NULL,
  `venta_id` int DEFAULT NULL,
  `monto` decimal(10,2) NOT NULL,
  `metodo_pago_id` int DEFAULT NULL,
  `estado_pago_id` int DEFAULT NULL,
  `fecha_pago` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`Id`),
  KEY `venta_id` (`venta_id`),
  KEY `metodo_pago_id` (`metodo_pago_id`),
  KEY `estado_pago_id` (`estado_pago_id`),
  CONSTRAINT `tpagos_ibfk_1` FOREIGN KEY (`venta_id`) REFERENCES `tventas` (`Id`),
  CONSTRAINT `tpagos_ibfk_2` FOREIGN KEY (`metodo_pago_id`) REFERENCES `tmetodospago` (`Id`),
  CONSTRAINT `tpagos_ibfk_3` FOREIGN KEY (`estado_pago_id`) REFERENCES `testadosdevolucion` (`Id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tpagos`
--

LOCK TABLES `tpagos` WRITE;
/*!40000 ALTER TABLE `tpagos` DISABLE KEYS */;
/*!40000 ALTER TABLE `tpagos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tproductos`
--

DROP TABLE IF EXISTS `tproductos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tproductos` (
  `Id` int NOT NULL AUTO_INCREMENT,
  `nombre_producto` varchar(255) NOT NULL,
  `descripcion` text,
  `precio` decimal(10,2) NOT NULL,
  `stock` int NOT NULL,
  `stock_minimo` int NOT NULL DEFAULT '10',
  `stock_maximo` int NOT NULL DEFAULT '100',
  `categoria_id` int DEFAULT NULL,
  `ruta_imagen` varchar(255) DEFAULT NULL,
  `creado_en` datetime DEFAULT CURRENT_TIMESTAMP,
  `actualizado_en` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `activo` tinyint(1) DEFAULT '1',
  PRIMARY KEY (`Id`),
  KEY `categoria_id` (`categoria_id`),
  CONSTRAINT `tproductos_ibfk_1` FOREIGN KEY (`categoria_id`) REFERENCES `tcategorias` (`Id`),
  CONSTRAINT `chk_precio_positivo` CHECK ((`precio` >= 0)),
  CONSTRAINT `chk_stock_positivo` CHECK ((`stock` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=55 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tproductos`
--

LOCK TABLES `tproductos` WRITE;
/*!40000 ALTER TABLE `tproductos` DISABLE KEYS */;
INSERT INTO `tproductos` VALUES (42,'2','2',2.00,0,0,0,2,'/static/images/productos/20250410141351.png','2025-04-10 14:13:51','2025-04-10 15:39:17',0),(45,'Café Americano ☕','Café negro preparado con espresso y agua caliente. Sabor intenso y aromático.',40.00,0,0,0,1,'/static/images/productos/20250410150447.png','2025-04-10 15:04:47','2025-04-10 15:04:47',1),(46,'Pastel de Chocolate 🍰','Bizcocho esponjoso con cobertura de chocolate y relleno cremoso.',90.00,19,10,35,4,'/static/images/productos/20250410152411.jpeg','2025-04-10 15:24:11','2026-04-21 18:01:40',1),(47,'Pastel de Vainilla 🍰','Bizcocho esponjoso con cobertura de vainilla y relleno cremoso.',90.00,34,10,30,4,'/static/images/productos/20250410152622.png','2025-04-10 15:26:22','2026-04-21 18:00:15',1),(48,'Croissant de Mantequilla 🥐','Hojaldre crujiente con sabor a mantequilla, perfecto para acompañar un café.',60.00,0,0,0,5,'/static/images/productos/20250410153211.jpeg','2025-04-10 15:32:11','2025-04-10 15:32:11',1),(49,'Té Matcha Latte 🍵','Bebida cremosa hecha con té matcha y leche, endulzada naturalmente.',70.00,0,0,0,1,'/static/images/productos/20250410153720.jpg','2025-04-10 15:37:20','2025-04-10 15:38:03',1),(50,'Galleta Chispas 🍪','Galletas crujientes y doradas con chispas de chocolate semi-amargo.',25.00,10,10,50,3,'/static/images/productos/20250410154234.jpeg','2025-04-10 15:42:34','2026-04-21 18:01:08',1),(52,'Galleta Doble Chocolate 🍪','Crujiente masa de chocolate con chispas de un cremoso manjar de cacao.',30.00,139,10,999,3,'/static/images/productos/20250509192738.png','2025-05-09 19:27:38','2026-04-21 18:01:25',1),(54,'Dona de chocolate UWU1','fadfa1',201.00,0,0,0,2,'/static/images/productos/20260420110105.jpg','2026-04-20 17:01:06','2026-04-20 17:10:49',1);
/*!40000 ALTER TABLE `tproductos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tproductos_variantes`
--

DROP TABLE IF EXISTS `tproductos_variantes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tproductos_variantes` (
  `Id` int NOT NULL AUTO_INCREMENT,
  `producto_id` int NOT NULL,
  `tamano_id` int NOT NULL,
  `precio` decimal(10,2) NOT NULL,
  `creado_en` datetime DEFAULT CURRENT_TIMESTAMP,
  `actualizado_en` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`Id`),
  UNIQUE KEY `uc_producto_tamano` (`producto_id`,`tamano_id`),
  KEY `producto_id` (`producto_id`),
  KEY `tamano_id` (`tamano_id`),
  CONSTRAINT `tproductos_variantes_ibfk_1` FOREIGN KEY (`producto_id`) REFERENCES `tproductos` (`Id`) ON DELETE CASCADE,
  CONSTRAINT `tproductos_variantes_ibfk_2` FOREIGN KEY (`tamano_id`) REFERENCES `ttamanos` (`Id`)
) ENGINE=InnoDB AUTO_INCREMENT=90 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tproductos_variantes`
--

LOCK TABLES `tproductos_variantes` WRITE;
/*!40000 ALTER TABLE `tproductos_variantes` DISABLE KEYS */;
INSERT INTO `tproductos_variantes` VALUES (83,45,1,40.00,'2025-04-10 15:04:47','2025-04-10 15:04:47'),(84,48,1,60.00,'2025-04-10 15:32:11','2025-04-10 15:32:11'),(85,49,1,70.00,'2025-04-10 15:38:03','2025-04-10 15:38:03'),(89,54,1,201.00,'2026-04-20 17:10:49','2026-04-20 17:10:49');
/*!40000 ALTER TABLE `tproductos_variantes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `troles`
--

DROP TABLE IF EXISTS `troles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `troles` (
  `Id` int NOT NULL AUTO_INCREMENT,
  `rol` varchar(50) NOT NULL,
  PRIMARY KEY (`Id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `troles`
--

LOCK TABLES `troles` WRITE;
/*!40000 ALTER TABLE `troles` DISABLE KEYS */;
INSERT INTO `troles` VALUES (1,'Administrador'),(2,'Vendedor');
/*!40000 ALTER TABLE `troles` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ttamanos`
--

DROP TABLE IF EXISTS `ttamanos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ttamanos` (
  `Id` int NOT NULL AUTO_INCREMENT,
  `tamano` varchar(50) NOT NULL,
  PRIMARY KEY (`Id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ttamanos`
--

LOCK TABLES `ttamanos` WRITE;
/*!40000 ALTER TABLE `ttamanos` DISABLE KEYS */;
INSERT INTO `ttamanos` VALUES (1,'Pequeño'),(2,'Mediano'),(3,'Grande'),(4,'No Aplica');
/*!40000 ALTER TABLE `ttamanos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ttiposdevolucion`
--

DROP TABLE IF EXISTS `ttiposdevolucion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ttiposdevolucion` (
  `Id` int NOT NULL,
  `tipo_cancelacion` varchar(50) NOT NULL,
  PRIMARY KEY (`Id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ttiposdevolucion`
--

LOCK TABLES `ttiposdevolucion` WRITE;
/*!40000 ALTER TABLE `ttiposdevolucion` DISABLE KEYS */;
INSERT INTO `ttiposdevolucion` VALUES (1,'Total'),(2,'Devolución por transferencia'),(3,'Devolución por PayPal'),(4,'Defecto de producto'),(5,'Insatisfacción del cliente');
/*!40000 ALTER TABLE `ttiposdevolucion` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ttiposmovimiento`
--

DROP TABLE IF EXISTS `ttiposmovimiento`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ttiposmovimiento` (
  `Id` int NOT NULL,
  `tipo_de_movimiento` varchar(50) NOT NULL,
  PRIMARY KEY (`Id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ttiposmovimiento`
--

LOCK TABLES `ttiposmovimiento` WRITE;
/*!40000 ALTER TABLE `ttiposmovimiento` DISABLE KEYS */;
INSERT INTO `ttiposmovimiento` VALUES (1,'Entrada'),(2,'Salida'),(3,'Ajuste Positivo'),(4,'Ajuste Negativo');
/*!40000 ALTER TABLE `ttiposmovimiento` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tusuarios`
--

DROP TABLE IF EXISTS `tusuarios`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tusuarios` (
  `Id` int NOT NULL AUTO_INCREMENT,
  `usuario` varchar(255) NOT NULL,
  `contrasena` varchar(255) NOT NULL,
  `correo` varchar(100) NOT NULL,
  `rol_id` int NOT NULL,
  `creado_en` datetime DEFAULT CURRENT_TIMESTAMP,
  `activo` tinyint(1) DEFAULT '1',
  `modificado_en` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`Id`),
  UNIQUE KEY `usuario_UNIQUE` (`usuario`),
  UNIQUE KEY `unique_correo` (`correo`),
  KEY `rol_id` (`rol_id`),
  CONSTRAINT `tusuarios_ibfk_1` FOREIGN KEY (`rol_id`) REFERENCES `troles` (`Id`)
) ENGINE=InnoDB AUTO_INCREMENT=22 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tusuarios`
--

LOCK TABLES `tusuarios` WRITE;
/*!40000 ALTER TABLE `tusuarios` DISABLE KEYS */;
INSERT INTO `tusuarios` VALUES (6,'Isma','Corona22','ismaelcm18182@gmail.com',1,'2025-03-10 23:19:36',1,'2026-04-21 19:24:36'),(13,'Isma2','abc123..','ismaelcm1818@gmail.com',2,'2025-03-15 17:16:44',1,'2025-05-14 20:18:33'),(14,'Bri','123','brithanymil@gmail.com',1,'2025-04-07 01:06:17',1,'2025-05-14 20:18:33'),(16,'Bri2','123','brithanyherrera04@gmail.com',2,'2025-04-10 15:45:44',0,'2025-05-14 20:22:34'),(19,'Brithany','1234.67a','brithany2mil4@gmail.com',1,'2025-05-09 23:48:33',1,'2025-05-14 20:18:33'),(20,'Isma2hgca','12345678sf.','carmelacar12@gmail.com',2,'2025-10-06 14:49:50',0,'2026-04-11 04:29:22'),(21,'Jaime','12345678Jj.','jaimejes92@gmail.com',2,'2025-10-06 15:32:48',0,'2026-04-20 16:54:44');
/*!40000 ALTER TABLE `tusuarios` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tvalidacion_usuarios`
--

DROP TABLE IF EXISTS `tvalidacion_usuarios`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tvalidacion_usuarios` (
  `id` int NOT NULL AUTO_INCREMENT,
  `usuario` varchar(255) NOT NULL,
  `contrasena` varchar(255) NOT NULL,
  `correo` varchar(100) NOT NULL,
  `rol_id` int NOT NULL,
  `codigo` varchar(6) NOT NULL,
  `fecha_creacion` datetime DEFAULT CURRENT_TIMESTAMP,
  `validado` tinyint(1) DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `rol_id` (`rol_id`),
  CONSTRAINT `tvalidacion_usuarios_ibfk_1` FOREIGN KEY (`rol_id`) REFERENCES `troles` (`Id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tvalidacion_usuarios`
--

LOCK TABLES `tvalidacion_usuarios` WRITE;
/*!40000 ALTER TABLE `tvalidacion_usuarios` DISABLE KEYS */;
/*!40000 ALTER TABLE `tvalidacion_usuarios` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tventas`
--

DROP TABLE IF EXISTS `tventas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tventas` (
  `Id` int NOT NULL AUTO_INCREMENT,
  `cliente_id` int DEFAULT NULL,
  `total` decimal(10,2) NOT NULL,
  `fecha_hora` datetime DEFAULT CURRENT_TIMESTAMP,
  `vendedor_id` int DEFAULT NULL,
  `metodo_pago_id` int NOT NULL DEFAULT '1',
  `estado_id` int NOT NULL DEFAULT '1',
  `numero_mesa` varchar(50) DEFAULT NULL,
  `creado_en` datetime DEFAULT CURRENT_TIMESTAMP,
  `dinero_recibido` decimal(10,2) DEFAULT '0.00',
  `cambio` decimal(10,2) DEFAULT '0.00',
  PRIMARY KEY (`Id`),
  KEY `cliente_id` (`cliente_id`),
  KEY `vendedor_id` (`vendedor_id`),
  KEY `metodo_pago_id` (`metodo_pago_id`),
  KEY `estado_id` (`estado_id`),
  CONSTRAINT `tventas_ibfk_1` FOREIGN KEY (`cliente_id`) REFERENCES `tclientes` (`Id`),
  CONSTRAINT `tventas_ibfk_2` FOREIGN KEY (`vendedor_id`) REFERENCES `tusuarios` (`Id`),
  CONSTRAINT `tventas_ibfk_3` FOREIGN KEY (`metodo_pago_id`) REFERENCES `tmetodospago` (`Id`),
  CONSTRAINT `tventas_ibfk_4` FOREIGN KEY (`estado_id`) REFERENCES `testadosventa` (`Id`),
  CONSTRAINT `chk_cambio_positivo` CHECK ((`cambio` >= 0)),
  CONSTRAINT `chk_dinero_recibido_positivo` CHECK ((`dinero_recibido` >= 0)),
  CONSTRAINT `chk_total_positivo` CHECK ((`total` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=102 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tventas`
--

LOCK TABLES `tventas` WRITE;
/*!40000 ALTER TABLE `tventas` DISABLE KEYS */;
INSERT INTO `tventas` VALUES (52,44,2.00,'2025-04-10 15:34:05',14,1,4,'','2025-04-10 15:34:05',0.00,0.00),(53,36,60.00,'2025-04-10 15:43:27',14,2,4,'','2025-04-10 15:43:27',0.00,0.00),(54,45,40.00,'2025-04-10 15:43:44',14,3,3,'','2025-04-10 15:43:44',0.00,0.00),(55,37,25.00,'2025-04-10 16:02:06',14,1,3,'','2025-04-10 16:02:06',0.00,0.00),(56,46,25.00,'2025-04-10 16:17:28',16,1,3,'','2025-04-10 16:17:28',0.00,0.00),(57,47,100.00,'2025-04-10 18:00:22',14,1,3,'19','2025-04-10 18:00:22',0.00,0.00),(58,48,240.00,'2025-04-10 18:06:53',14,1,4,'','2025-04-10 18:06:53',0.00,0.00),(62,50,120.00,'2025-05-06 17:33:35',6,2,1,'','2025-05-06 17:33:35',0.00,0.00),(63,49,25.00,'2025-05-10 00:01:54',6,1,4,'26','2025-05-10 00:01:54',0.00,0.00),(64,51,360.00,'2025-05-10 01:07:31',6,2,1,'','2025-05-10 01:07:31',0.00,0.00),(66,52,40.00,'2025-05-10 01:10:48',6,1,4,'','2025-05-10 01:10:48',0.00,0.00),(67,53,400.00,'2025-05-10 01:52:09',6,1,4,'','2025-05-10 01:52:09',0.00,0.00),(68,54,405.00,'2025-05-12 00:30:01',6,1,4,'3','2025-05-12 00:30:01',0.00,0.00),(69,49,100.00,'2025-05-14 12:48:14',16,1,4,'','2025-05-14 12:48:14',0.00,0.00),(70,55,75.00,'2025-05-14 14:24:36',6,1,4,'','2025-05-14 14:24:36',0.00,0.00),(74,60,25.00,'2026-04-20 16:58:32',6,1,4,'','2026-04-20 16:58:32',0.00,0.00),(75,60,60.00,'2026-04-20 21:51:49',6,1,1,'94','2026-04-20 21:51:49',0.00,0.00),(98,63,240.00,'2026-04-20 22:29:36',6,1,1,'1','2026-04-20 22:29:36',0.00,0.00),(99,64,60.00,'2026-04-20 22:30:12',6,1,1,'42','2026-04-20 22:30:12',0.00,0.00),(100,65,40.00,'2026-04-23 03:43:38',6,1,1,'','2026-04-23 03:43:38',100.00,60.00),(101,36,40.00,'2026-04-23 03:59:11',6,1,1,'','2026-04-23 03:59:11',50.00,10.00);
/*!40000 ALTER TABLE `tventas` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping routines for database 'bd'
--
SET @@SESSION.SQL_LOG_BIN = @MYSQLDUMP_TEMP_LOG_BIN;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-04-29 13:46:47
