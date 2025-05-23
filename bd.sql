-- phpMyAdmin SQL Dump
-- version 5.1.2
-- https://www.phpmyadmin.net/
--
-- Servidor: localhost:3307
-- Tiempo de generación: 14-05-2025 a las 20:43:08
-- Versión del servidor: 5.7.24
-- Versión de PHP: 8.3.1

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `bd`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `tcategorias`
--

CREATE TABLE `tcategorias` (
  `Id` int(11) NOT NULL,
  `categoria` varchar(100) NOT NULL,
  `creado_en` datetime DEFAULT CURRENT_TIMESTAMP,
  `actualizado_en` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `requiere_inventario` tinyint(1) NOT NULL DEFAULT '0'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Volcado de datos para la tabla `tcategorias`
--

INSERT INTO `tcategorias` (`Id`, `categoria`, `creado_en`, `actualizado_en`, `requiere_inventario`) VALUES
(1, 'Bebidas Calientes', '2025-03-09 00:44:07', '2025-03-09 00:44:07', 0),
(2, 'Bebidas Frías', '2025-03-09 00:44:07', '2025-03-09 00:44:07', 0),
(3, 'Snacks', '2025-03-09 00:44:07', '2025-04-09 01:50:56', 1),
(4, 'Postres', '2025-03-09 00:44:07', '2025-03-15 19:24:32', 1),
(5, 'Todos', '2025-03-09 00:44:07', '2025-03-09 00:44:07', 0),
(6, 'Otras Bebidas', '2025-03-09 00:44:07', '2025-04-09 02:42:11', 0);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `tclientes`
--

CREATE TABLE `tclientes` (
  `Id` int(11) NOT NULL,
  `nombre` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Volcado de datos para la tabla `tclientes`
--

INSERT INTO `tclientes` (`Id`, `nombre`) VALUES
(36, 'Juan'),
(37, 'Isma'),
(38, 'a'),
(39, 'j'),
(40, 'qaq'),
(41, 'asa'),
(42, 'wasa'),
(43, 'qaza'),
(44, 'Ana'),
(45, 'Lalo'),
(46, 'Me'),
(47, 'Pina'),
(48, 'titi'),
(49, 'Lola'),
(50, 'pepe'),
(51, 'Reyna'),
(52, 'ESPE'),
(53, 'IRMA'),
(54, 'Juliette'),
(55, 'Yo'),
(56, 'Bri'),
(57, 'Cami'),
(58, 'Camim'),
(59, 'iris');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `tcodigosrecuperacion`
--

CREATE TABLE `tcodigosrecuperacion` (
  `Id` int(11) NOT NULL,
  `usuario_id` int(11) NOT NULL,
  `codigo` varchar(10) NOT NULL,
  `fecha_expiracion` datetime NOT NULL,
  `fecha_creacion` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `tcortescaja`
--

CREATE TABLE `tcortescaja` (
  `Id` int(11) NOT NULL,
  `vendedor_id` int(11) DEFAULT NULL,
  `fecha_hora_inicio` datetime DEFAULT NULL,
  `fecha_hora_cierre` datetime DEFAULT NULL,
  `total_ventas` decimal(10,2) NOT NULL,
  `total_efectivo` decimal(10,2) NOT NULL,
  `total_transferencias` decimal(10,2) NOT NULL,
  `total_paypal` decimal(10,2) NOT NULL,
  `total_contado` decimal(10,2) NOT NULL DEFAULT '0.00',
  `pagos_realizados` decimal(10,2) NOT NULL DEFAULT '0.00',
  `fondo` varchar(255) DEFAULT NULL,
  `ganancia_o_perdida` float DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Volcado de datos para la tabla `tcortescaja`
--

INSERT INTO `tcortescaja` (`Id`, `vendedor_id`, `fecha_hora_inicio`, `fecha_hora_cierre`, `total_ventas`, `total_efectivo`, `total_transferencias`, `total_paypal`, `total_contado`, `pagos_realizados`, `fondo`, `ganancia_o_perdida`) VALUES
(4, NULL, '2025-04-08 15:44:00', '2025-04-10 15:44:00', '102.00', '2.00', '60.00', '40.00', '102.00', '0.00', '900', 102),
(5, NULL, '2025-05-06 15:33:00', '2025-05-06 19:33:00', '195.00', '50.00', '120.00', '25.00', '455.00', '0.00', '500', 195),
(6, NULL, '2025-05-01 13:12:00', '2025-05-14 13:12:00', '1965.00', '1245.00', '720.00', '0.00', '1965.00', '400.00', '3000', 1565),
(7, NULL, '2025-05-01 13:12:00', '2025-05-14 13:12:00', '1965.00', '1245.00', '720.00', '0.00', '1965.00', '400.00', '3000', 1565),
(8, NULL, '2025-05-01 14:41:00', '2025-05-14 14:41:00', '2100.00', '1350.00', '750.00', '0.00', '2100.00', '0.00', '300', 2100);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `tdetalleventas`
--

CREATE TABLE `tdetalleventas` (
  `Id` int(11) NOT NULL,
  `venta_id` int(11) DEFAULT NULL,
  `producto_id` int(11) DEFAULT NULL,
  `cantidad` int(11) NOT NULL,
  `precio` decimal(10,2) NOT NULL,
  `creado_en` datetime DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Volcado de datos para la tabla `tdetalleventas`
--

INSERT INTO `tdetalleventas` (`Id`, `venta_id`, `producto_id`, `cantidad`, `precio`, `creado_en`) VALUES
(50, 52, 42, 1, '2.00', '2025-04-10 15:34:05'),
(51, 53, 48, 1, '60.00', '2025-04-10 15:43:27'),
(52, 54, 45, 1, '40.00', '2025-04-10 15:43:44'),
(53, 55, 50, 1, '25.00', '2025-04-10 16:02:06'),
(54, 56, 50, 1, '25.00', '2025-04-10 16:17:28'),
(55, 57, 50, 4, '25.00', '2025-04-10 18:00:22'),
(56, 58, 45, 6, '40.00', '2025-04-10 18:06:53'),
(57, 59, 50, 9, '25.00', '2025-05-02 23:00:06'),
(59, 61, 50, 2, '25.00', '2025-05-06 17:33:15'),
(60, 62, 48, 2, '60.00', '2025-05-06 17:33:35'),
(61, 63, 50, 1, '25.00', '2025-05-10 00:01:54'),
(62, 64, 47, 4, '90.00', '2025-05-10 01:07:31'),
(63, 65, 48, 4, '60.00', '2025-05-10 01:10:23'),
(64, 66, 45, 1, '40.00', '2025-05-10 01:10:48'),
(65, 67, 45, 10, '40.00', '2025-05-10 01:52:09'),
(66, 68, 48, 1, '60.00', '2025-05-12 00:30:01'),
(67, 68, 45, 1, '40.00', '2025-05-12 00:30:01'),
(68, 68, 50, 1, '25.00', '2025-05-12 00:30:01'),
(69, 68, 52, 1, '30.00', '2025-05-12 00:30:01'),
(70, 68, 46, 1, '90.00', '2025-05-12 00:30:01'),
(71, 68, 47, 1, '90.00', '2025-05-12 00:30:01'),
(72, 68, 49, 1, '70.00', '2025-05-12 00:30:01'),
(73, 69, 50, 4, '25.00', '2025-05-14 12:48:14'),
(74, 70, 50, 3, '25.00', '2025-05-14 14:24:36'),
(75, 71, 53, 1, '30.00', '2025-05-14 14:31:12'),
(76, 72, 53, 1, '30.00', '2025-05-14 14:40:27'),
(77, 73, 48, 2, '60.00', '2025-05-14 14:41:08'),
(78, 74, 48, 1, '60.00', '2025-05-14 14:42:38');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `tdevoluciones`
--

CREATE TABLE `tdevoluciones` (
  `Id` int(11) NOT NULL,
  `venta_id` int(11) DEFAULT NULL,
  `producto_id` int(11) DEFAULT NULL,
  `cantidad` int(11) NOT NULL,
  `tipo_devolucion_id` int(11) DEFAULT NULL,
  `estado_devolucion_id` int(11) DEFAULT NULL,
  `creado_en` datetime DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `testadosdevolucion`
--

CREATE TABLE `testadosdevolucion` (
  `Id` int(11) NOT NULL,
  `estado` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Volcado de datos para la tabla `testadosdevolucion`
--

INSERT INTO `testadosdevolucion` (`Id`, `estado`) VALUES
(1, 'Pendiente'),
(2, 'Aprobada'),
(3, 'Rechazada'),
(4, 'Cancelada');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `testadosventa`
--

CREATE TABLE `testadosventa` (
  `Id` int(11) NOT NULL,
  `estado` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Volcado de datos para la tabla `testadosventa`
--

INSERT INTO `testadosventa` (`Id`, `estado`) VALUES
(1, 'Pendiente'),
(2, 'En proceso'),
(3, 'Cancelado'),
(4, 'Completado'),
(5, 'Reembolsada');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `tmetodospago`
--

CREATE TABLE `tmetodospago` (
  `Id` int(11) NOT NULL,
  `tipo_de_pago` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Volcado de datos para la tabla `tmetodospago`
--

INSERT INTO `tmetodospago` (`Id`, `tipo_de_pago`) VALUES
(1, 'Efectivo'),
(2, 'Transferencia Bancaria'),
(3, 'PayPal');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `tmovimientosinventario`
--

CREATE TABLE `tmovimientosinventario` (
  `Id` int(11) NOT NULL,
  `producto_id` int(11) NOT NULL,
  `cantidad` int(11) NOT NULL,
  `tipo_movimiento_id` int(11) NOT NULL,
  `motivo` text,
  `creado_en` datetime DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `tpagos`
--

CREATE TABLE `tpagos` (
  `Id` int(11) NOT NULL,
  `venta_id` int(11) DEFAULT NULL,
  `monto` decimal(10,2) NOT NULL,
  `metodo_pago_id` int(11) DEFAULT NULL,
  `estado_pago_id` int(11) DEFAULT NULL,
  `fecha_pago` datetime DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `tproductos`
--

CREATE TABLE `tproductos` (
  `Id` int(11) NOT NULL,
  `nombre_producto` varchar(255) NOT NULL,
  `descripcion` text,
  `precio` decimal(10,2) NOT NULL,
  `stock` int(11) NOT NULL,
  `stock_minimo` int(11) NOT NULL DEFAULT '10',
  `stock_maximo` int(11) NOT NULL DEFAULT '100',
  `categoria_id` int(11) DEFAULT NULL,
  `ruta_imagen` varchar(255) DEFAULT NULL,
  `creado_en` datetime DEFAULT CURRENT_TIMESTAMP,
  `actualizado_en` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `activo` tinyint(1) DEFAULT '1'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Volcado de datos para la tabla `tproductos`
--

INSERT INTO `tproductos` (`Id`, `nombre_producto`, `descripcion`, `precio`, `stock`, `stock_minimo`, `stock_maximo`, `categoria_id`, `ruta_imagen`, `creado_en`, `actualizado_en`, `activo`) VALUES
(41, '1', '1', '1.00', 0, 0, 0, 1, '/static/images/productos/20250410141333.png', '2025-04-10 14:13:33', '2025-04-10 14:15:27', 0),
(42, '2', '2', '2.00', 0, 0, 0, 2, '/static/images/productos/20250410141351.png', '2025-04-10 14:13:51', '2025-04-10 15:39:17', 0),
(43, '3', '3', '3.00', 0, 0, 0, 6, '/static/images/productos/20250410141410.png', '2025-04-10 14:14:10', '2025-04-10 15:24:25', 0),
(44, '4', '4', '4.00', 0, 0, 0, 6, '/static/images/productos/20250410141505.png', '2025-04-10 14:15:05', '2025-04-10 15:39:10', 0),
(45, 'Café Americano ☕', 'Café negro preparado con espresso y agua caliente. Sabor intenso y aromático.', '40.00', 0, 0, 0, 1, '/static/images/productos/20250410150447.png', '2025-04-10 15:04:47', '2025-04-10 15:04:47', 1),
(46, 'Pastel de Chocolate 🍰', 'Bizcocho esponjoso con cobertura de chocolate y relleno cremoso.', '90.00', 19, 10, 30, 4, '/static/images/productos/20250410152411.jpeg', '2025-04-10 15:24:11', '2025-05-12 00:30:01', 1),
(47, 'Pastel de Vainilla 🍰', 'Bizcocho esponjoso con cobertura de vainilla y relleno cremoso.', '90.00', 5, 5, 30, 4, '/static/images/productos/20250410152622.png', '2025-04-10 15:26:22', '2025-05-12 00:30:01', 1),
(48, 'Croissant de Mantequilla 🥐', 'Hojaldre crujiente con sabor a mantequilla, perfecto para acompañar un café.', '60.00', 0, 0, 0, 5, '/static/images/productos/20250410153211.jpeg', '2025-04-10 15:32:11', '2025-04-10 15:32:11', 1),
(49, 'Té Matcha Latte 🍵', 'Bebida cremosa hecha con té matcha y leche, endulzada naturalmente.', '70.00', 0, 0, 0, 1, '/static/images/productos/20250410153720.jpg', '2025-04-10 15:37:20', '2025-04-10 15:38:03', 1),
(50, 'Galleta Chispas 🍪', 'Galletas crujientes y doradas con chispas de chocolate semi-amargo.', '25.00', 63, 10, 150, 3, '/static/images/productos/20250410154234.jpeg', '2025-04-10 15:42:34', '2025-05-14 14:24:36', 1),
(51, 'kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkddwodkwokdowdkwodkwokdowkdowkdowkdowkodkwodkwokdowkodwkodk', 'wdkoooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooowodkwodkowkdowkok', '100.00', 0, 0, 0, 6, '/static/images/productos/20250506172126.png', '2025-05-06 17:21:26', '2025-05-06 17:22:54', 0),
(52, 'Galleta Doble Chocolate 🍪', 'Crujiente masa de chocolate con chispas de un cremoso manjar de cacao.', '30.00', 98, 10, 999, 3, '/static/images/productos/20250509192738.png', '2025-05-09 19:27:38', '2025-05-12 00:30:01', 1),
(53, 'Dona de chocolate 🍩', 'Esponjoso pan frito cubierto con crema de avellana.', '30.00', 18, 10, 100, 4, '/static/images/productos/20250514143045.png', '2025-05-14 14:28:04', '2025-05-14 14:40:27', 1);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `tproductos_variantes`
--

CREATE TABLE `tproductos_variantes` (
  `Id` int(11) NOT NULL,
  `producto_id` int(11) NOT NULL,
  `tamano_id` int(11) NOT NULL,
  `precio` decimal(10,2) NOT NULL,
  `creado_en` datetime DEFAULT CURRENT_TIMESTAMP,
  `actualizado_en` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Volcado de datos para la tabla `tproductos_variantes`
--

INSERT INTO `tproductos_variantes` (`Id`, `producto_id`, `tamano_id`, `precio`, `creado_en`, `actualizado_en`) VALUES
(83, 45, 1, '40.00', '2025-04-10 15:04:47', '2025-04-10 15:04:47'),
(84, 48, 1, '60.00', '2025-04-10 15:32:11', '2025-04-10 15:32:11'),
(85, 49, 1, '70.00', '2025-04-10 15:38:03', '2025-04-10 15:38:03');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `troles`
--

CREATE TABLE `troles` (
  `Id` int(11) NOT NULL,
  `rol` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Volcado de datos para la tabla `troles`
--

INSERT INTO `troles` (`Id`, `rol`) VALUES
(1, 'Administrador'),
(2, 'Vendedor');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `ttamanos`
--

CREATE TABLE `ttamanos` (
  `Id` int(11) NOT NULL,
  `tamano` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Volcado de datos para la tabla `ttamanos`
--

INSERT INTO `ttamanos` (`Id`, `tamano`) VALUES
(1, 'Pequeño'),
(2, 'Mediano'),
(3, 'Grande'),
(4, 'No Aplica');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `ttiposdevolucion`
--

CREATE TABLE `ttiposdevolucion` (
  `Id` int(11) NOT NULL,
  `tipo_cancelacion` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Volcado de datos para la tabla `ttiposdevolucion`
--

INSERT INTO `ttiposdevolucion` (`Id`, `tipo_cancelacion`) VALUES
(1, 'Total'),
(2, 'Devolución por transferencia'),
(3, 'Devolución por PayPal'),
(4, 'Defecto de producto'),
(5, 'Insatisfacción del cliente');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `ttiposmovimiento`
--

CREATE TABLE `ttiposmovimiento` (
  `Id` int(11) NOT NULL,
  `tipo_de_movimiento` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Volcado de datos para la tabla `ttiposmovimiento`
--

INSERT INTO `ttiposmovimiento` (`Id`, `tipo_de_movimiento`) VALUES
(1, 'Entrada'),
(2, 'Salida'),
(3, 'Ajuste Positivo'),
(4, 'Ajuste Negativo');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `tusuarios`
--

CREATE TABLE `tusuarios` (
  `Id` int(11) NOT NULL,
  `usuario` varchar(255) NOT NULL,
  `contrasena` varchar(255) NOT NULL,
  `correo` varchar(100) NOT NULL,
  `rol_id` int(11) NOT NULL,
  `creado_en` datetime DEFAULT CURRENT_TIMESTAMP,
  `activo` tinyint(1) DEFAULT '1',
  `modificado_en` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Volcado de datos para la tabla `tusuarios`
--

INSERT INTO `tusuarios` (`Id`, `usuario`, `contrasena`, `correo`, `rol_id`, `creado_en`, `activo`, `modificado_en`) VALUES
(6, 'Isma', '123', 'ismaelcm18182@gmail.com', 1, '2025-03-10 23:19:36', 1, '2025-05-14 20:31:45'),
(13, 'Isma2', 'abc123..', 'ismaelcm1818@gmail.com', 2, '2025-03-15 17:16:44', 1, '2025-05-14 20:18:33'),
(14, 'Bri', '123', 'brithanymil@gmail.com', 1, '2025-04-07 01:06:17', 1, '2025-05-14 20:18:33'),
(16, 'Bri2', '123', 'brithanyherrera04@gmail.com', 2, '2025-04-10 15:45:44', 0, '2025-05-14 20:22:34'),
(19, 'Brithany', '1234.67a', 'brithany2mil4@gmail.com', 1, '2025-05-09 23:48:33', 1, '2025-05-14 20:18:33');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `tventas`
--

CREATE TABLE `tventas` (
  `Id` int(11) NOT NULL,
  `cliente_id` int(11) DEFAULT NULL,
  `total` decimal(10,2) NOT NULL,
  `fecha_hora` datetime DEFAULT CURRENT_TIMESTAMP,
  `vendedor_id` int(11) DEFAULT NULL,
  `metodo_pago_id` int(11) DEFAULT NULL,
  `estado_id` int(11) DEFAULT NULL,
  `numero_mesa` varchar(50) DEFAULT NULL,
  `creado_en` datetime DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Volcado de datos para la tabla `tventas`
--

INSERT INTO `tventas` (`Id`, `cliente_id`, `total`, `fecha_hora`, `vendedor_id`, `metodo_pago_id`, `estado_id`, `numero_mesa`, `creado_en`) VALUES
(52, 44, '2.00', '2025-04-10 15:34:05', 14, 1, 4, '', '2025-04-10 15:34:05'),
(53, 36, '60.00', '2025-04-10 15:43:27', 14, 2, 4, '', '2025-04-10 15:43:27'),
(54, 45, '40.00', '2025-04-10 15:43:44', 14, 3, 3, '', '2025-04-10 15:43:44'),
(55, 37, '25.00', '2025-04-10 16:02:06', 14, 1, 3, '', '2025-04-10 16:02:06'),
(56, 46, '25.00', '2025-04-10 16:17:28', 16, 1, 3, '', '2025-04-10 16:17:28'),
(57, 47, '100.00', '2025-04-10 18:00:22', 14, 1, 3, '19', '2025-04-10 18:00:22'),
(58, 48, '240.00', '2025-04-10 18:06:53', 14, 1, 4, '', '2025-04-10 18:06:53'),
(59, 49, '225.00', '2025-05-02 23:00:06', 6, 1, 1, '', '2025-05-02 23:00:06'),
(61, 36, '50.00', '2025-05-06 17:33:15', 6, 1, 1, '', '2025-05-06 17:33:15'),
(62, 50, '120.00', '2025-05-06 17:33:35', 6, 2, 1, '', '2025-05-06 17:33:35'),
(63, 49, '25.00', '2025-05-10 00:01:54', 6, 1, 4, '26', '2025-05-10 00:01:54'),
(64, 51, '360.00', '2025-05-10 01:07:31', 6, 2, 1, '', '2025-05-10 01:07:31'),
(65, 36, '240.00', '2025-05-10 01:10:23', 6, 2, 1, '', '2025-05-10 01:10:23'),
(66, 52, '40.00', '2025-05-10 01:10:48', 6, 1, 2, '', '2025-05-10 01:10:48'),
(67, 53, '400.00', '2025-05-10 01:52:09', 6, 1, 4, '', '2025-05-10 01:52:09'),
(68, 54, '405.00', '2025-05-12 00:30:01', 6, 1, 4, '3', '2025-05-12 00:30:01'),
(69, 49, '100.00', '2025-05-14 12:48:14', 16, 1, 4, '', '2025-05-14 12:48:14'),
(70, 55, '75.00', '2025-05-14 14:24:36', 6, 1, 4, '', '2025-05-14 14:24:36'),
(71, 56, '30.00', '2025-05-14 14:31:12', 6, 1, 1, '5', '2025-05-14 14:31:12'),
(72, 57, '30.00', '2025-05-14 14:40:27', 14, 2, 1, '5', '2025-05-14 14:40:27'),
(73, 58, '120.00', '2025-05-14 14:41:08', 14, 3, 1, '', '2025-05-14 14:41:08'),
(74, 59, '60.00', '2025-05-14 14:42:38', 14, 1, 1, '', '2025-05-14 14:42:38');

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `tcategorias`
--
ALTER TABLE `tcategorias`
  ADD PRIMARY KEY (`Id`);

--
-- Indices de la tabla `tclientes`
--
ALTER TABLE `tclientes`
  ADD PRIMARY KEY (`Id`);

--
-- Indices de la tabla `tcodigosrecuperacion`
--
ALTER TABLE `tcodigosrecuperacion`
  ADD PRIMARY KEY (`Id`),
  ADD KEY `usuario_id` (`usuario_id`);

--
-- Indices de la tabla `tcortescaja`
--
ALTER TABLE `tcortescaja`
  ADD PRIMARY KEY (`Id`),
  ADD KEY `vendedor_id` (`vendedor_id`);

--
-- Indices de la tabla `tdetalleventas`
--
ALTER TABLE `tdetalleventas`
  ADD PRIMARY KEY (`Id`),
  ADD KEY `venta_id` (`venta_id`),
  ADD KEY `tdetalleventas_ibfk_2` (`producto_id`);

--
-- Indices de la tabla `tdevoluciones`
--
ALTER TABLE `tdevoluciones`
  ADD PRIMARY KEY (`Id`),
  ADD KEY `venta_id` (`venta_id`),
  ADD KEY `producto_id` (`producto_id`),
  ADD KEY `tipo_devolucion_id` (`tipo_devolucion_id`),
  ADD KEY `estado_devolucion_id` (`estado_devolucion_id`);

--
-- Indices de la tabla `testadosdevolucion`
--
ALTER TABLE `testadosdevolucion`
  ADD PRIMARY KEY (`Id`);

--
-- Indices de la tabla `testadosventa`
--
ALTER TABLE `testadosventa`
  ADD PRIMARY KEY (`Id`);

--
-- Indices de la tabla `tmetodospago`
--
ALTER TABLE `tmetodospago`
  ADD PRIMARY KEY (`Id`);

--
-- Indices de la tabla `tmovimientosinventario`
--
ALTER TABLE `tmovimientosinventario`
  ADD PRIMARY KEY (`Id`),
  ADD KEY `producto_id` (`producto_id`),
  ADD KEY `tipo_movimiento_id` (`tipo_movimiento_id`);

--
-- Indices de la tabla `tpagos`
--
ALTER TABLE `tpagos`
  ADD PRIMARY KEY (`Id`),
  ADD KEY `venta_id` (`venta_id`),
  ADD KEY `metodo_pago_id` (`metodo_pago_id`),
  ADD KEY `estado_pago_id` (`estado_pago_id`);

--
-- Indices de la tabla `tproductos`
--
ALTER TABLE `tproductos`
  ADD PRIMARY KEY (`Id`),
  ADD KEY `categoria_id` (`categoria_id`);

--
-- Indices de la tabla `tproductos_variantes`
--
ALTER TABLE `tproductos_variantes`
  ADD PRIMARY KEY (`Id`),
  ADD UNIQUE KEY `uc_producto_tamano` (`producto_id`,`tamano_id`),
  ADD KEY `producto_id` (`producto_id`),
  ADD KEY `tamano_id` (`tamano_id`);

--
-- Indices de la tabla `troles`
--
ALTER TABLE `troles`
  ADD PRIMARY KEY (`Id`);

--
-- Indices de la tabla `ttamanos`
--
ALTER TABLE `ttamanos`
  ADD PRIMARY KEY (`Id`);

--
-- Indices de la tabla `ttiposdevolucion`
--
ALTER TABLE `ttiposdevolucion`
  ADD PRIMARY KEY (`Id`);

--
-- Indices de la tabla `ttiposmovimiento`
--
ALTER TABLE `ttiposmovimiento`
  ADD PRIMARY KEY (`Id`);

--
-- Indices de la tabla `tusuarios`
--
ALTER TABLE `tusuarios`
  ADD PRIMARY KEY (`Id`),
  ADD UNIQUE KEY `usuario_UNIQUE` (`usuario`),
  ADD UNIQUE KEY `unique_correo` (`correo`),
  ADD KEY `rol_id` (`rol_id`);

--
-- Indices de la tabla `tventas`
--
ALTER TABLE `tventas`
  ADD PRIMARY KEY (`Id`),
  ADD KEY `cliente_id` (`cliente_id`),
  ADD KEY `vendedor_id` (`vendedor_id`),
  ADD KEY `metodo_pago_id` (`metodo_pago_id`),
  ADD KEY `estado_id` (`estado_id`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `tcategorias`
--
ALTER TABLE `tcategorias`
  MODIFY `Id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT de la tabla `tclientes`
--
ALTER TABLE `tclientes`
  MODIFY `Id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=60;

--
-- AUTO_INCREMENT de la tabla `tcodigosrecuperacion`
--
ALTER TABLE `tcodigosrecuperacion`
  MODIFY `Id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `tcortescaja`
--
ALTER TABLE `tcortescaja`
  MODIFY `Id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;

--
-- AUTO_INCREMENT de la tabla `tdetalleventas`
--
ALTER TABLE `tdetalleventas`
  MODIFY `Id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=79;

--
-- AUTO_INCREMENT de la tabla `testadosventa`
--
ALTER TABLE `testadosventa`
  MODIFY `Id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT de la tabla `tproductos`
--
ALTER TABLE `tproductos`
  MODIFY `Id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=54;

--
-- AUTO_INCREMENT de la tabla `tproductos_variantes`
--
ALTER TABLE `tproductos_variantes`
  MODIFY `Id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=86;

--
-- AUTO_INCREMENT de la tabla `troles`
--
ALTER TABLE `troles`
  MODIFY `Id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT de la tabla `ttamanos`
--
ALTER TABLE `ttamanos`
  MODIFY `Id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT de la tabla `tusuarios`
--
ALTER TABLE `tusuarios`
  MODIFY `Id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=20;

--
-- AUTO_INCREMENT de la tabla `tventas`
--
ALTER TABLE `tventas`
  MODIFY `Id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=75;

--
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `tcodigosrecuperacion`
--
ALTER TABLE `tcodigosrecuperacion`
  ADD CONSTRAINT `tcodigosrecuperacion_ibfk_1` FOREIGN KEY (`usuario_id`) REFERENCES `tusuarios` (`Id`);

--
-- Filtros para la tabla `tcortescaja`
--
ALTER TABLE `tcortescaja`
  ADD CONSTRAINT `tcortescaja_ibfk_1` FOREIGN KEY (`vendedor_id`) REFERENCES `tusuarios` (`Id`);

--
-- Filtros para la tabla `tdetalleventas`
--
ALTER TABLE `tdetalleventas`
  ADD CONSTRAINT `tdetalleventas_ibfk_1` FOREIGN KEY (`venta_id`) REFERENCES `tventas` (`Id`),
  ADD CONSTRAINT `tdetalleventas_ibfk_2` FOREIGN KEY (`producto_id`) REFERENCES `tproductos` (`Id`);

--
-- Filtros para la tabla `tdevoluciones`
--
ALTER TABLE `tdevoluciones`
  ADD CONSTRAINT `tdevoluciones_ibfk_1` FOREIGN KEY (`venta_id`) REFERENCES `tventas` (`Id`),
  ADD CONSTRAINT `tdevoluciones_ibfk_2` FOREIGN KEY (`producto_id`) REFERENCES `tproductos` (`Id`),
  ADD CONSTRAINT `tdevoluciones_ibfk_3` FOREIGN KEY (`tipo_devolucion_id`) REFERENCES `ttiposdevolucion` (`Id`),
  ADD CONSTRAINT `tdevoluciones_ibfk_4` FOREIGN KEY (`estado_devolucion_id`) REFERENCES `testadosdevolucion` (`Id`);

--
-- Filtros para la tabla `tmovimientosinventario`
--
ALTER TABLE `tmovimientosinventario`
  ADD CONSTRAINT `tmovimientosinventario_ibfk_1` FOREIGN KEY (`producto_id`) REFERENCES `tproductos` (`Id`),
  ADD CONSTRAINT `tmovimientosinventario_ibfk_2` FOREIGN KEY (`tipo_movimiento_id`) REFERENCES `ttiposmovimiento` (`Id`);

--
-- Filtros para la tabla `tpagos`
--
ALTER TABLE `tpagos`
  ADD CONSTRAINT `tpagos_ibfk_1` FOREIGN KEY (`venta_id`) REFERENCES `tventas` (`Id`),
  ADD CONSTRAINT `tpagos_ibfk_2` FOREIGN KEY (`metodo_pago_id`) REFERENCES `tmetodospago` (`Id`),
  ADD CONSTRAINT `tpagos_ibfk_3` FOREIGN KEY (`estado_pago_id`) REFERENCES `testadosdevolucion` (`Id`);

--
-- Filtros para la tabla `tproductos`
--
ALTER TABLE `tproductos`
  ADD CONSTRAINT `tproductos_ibfk_1` FOREIGN KEY (`categoria_id`) REFERENCES `tcategorias` (`Id`);

--
-- Filtros para la tabla `tproductos_variantes`
--
ALTER TABLE `tproductos_variantes`
  ADD CONSTRAINT `tproductos_variantes_ibfk_1` FOREIGN KEY (`producto_id`) REFERENCES `tproductos` (`Id`) ON DELETE CASCADE,
  ADD CONSTRAINT `tproductos_variantes_ibfk_2` FOREIGN KEY (`tamano_id`) REFERENCES `ttamanos` (`Id`);

--
-- Filtros para la tabla `tusuarios`
--
ALTER TABLE `tusuarios`
  ADD CONSTRAINT `tusuarios_ibfk_1` FOREIGN KEY (`rol_id`) REFERENCES `troles` (`Id`);

--
-- Filtros para la tabla `tventas`
--
ALTER TABLE `tventas`
  ADD CONSTRAINT `tventas_ibfk_1` FOREIGN KEY (`cliente_id`) REFERENCES `tclientes` (`Id`),
  ADD CONSTRAINT `tventas_ibfk_2` FOREIGN KEY (`vendedor_id`) REFERENCES `tusuarios` (`Id`),
  ADD CONSTRAINT `tventas_ibfk_3` FOREIGN KEY (`metodo_pago_id`) REFERENCES `tmetodospago` (`Id`),
  ADD CONSTRAINT `tventas_ibfk_4` FOREIGN KEY (`estado_id`) REFERENCES `testadosventa` (`Id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
