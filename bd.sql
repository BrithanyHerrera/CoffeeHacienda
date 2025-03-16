-- phpMyAdmin SQL Dump
-- version 5.1.2
-- https://www.phpmyadmin.net/
--
-- Servidor: localhost:3307
-- Tiempo de generación: 16-03-2025 a las 05:05:04
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
(3, 'Snacks', '2025-03-09 00:44:07', '2025-03-09 00:44:07', 0),
(4, 'Postres', '2025-03-09 00:44:07', '2025-03-15 19:24:32', 1),
(5, 'Todos', '2025-03-09 00:44:07', '2025-03-09 00:44:07', 0),
(6, 'Otras Bebidas', '2025-03-09 00:44:07', '2025-03-09 00:44:07', 0);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `tclientes`
--

CREATE TABLE `tclientes` (
  `Id` int(11) NOT NULL,
  `nombre` varchar(255) NOT NULL,
  `apellidoP` varchar(255) NOT NULL,
  `apellidoM` varchar(20) NOT NULL,
  `correo` varchar(255) NOT NULL,
  `telefono` varchar(20) NOT NULL,
  `creado_en` datetime DEFAULT CURRENT_TIMESTAMP,
  `actualizado_en` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `tcortescaja`
--

CREATE TABLE `tcortescaja` (
  `Id` int(11) NOT NULL,
  `vendedor_id` int(11) DEFAULT NULL,
  `fecha_hora_inicio` datetime DEFAULT CURRENT_TIMESTAMP,
  `fecha_hora_cierre` datetime DEFAULT CURRENT_TIMESTAMP,
  `total_ventas` decimal(10,2) NOT NULL,
  `total_devoluciones` decimal(10,2) NOT NULL,
  `total_efectivo` decimal(10,2) NOT NULL,
  `total_transferencias` decimal(10,2) NOT NULL,
  `total_paypal` decimal(10,2) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

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
  `descuento` decimal(10,2) DEFAULT '0.00',
  `impuesto` decimal(10,2) DEFAULT '0.00',
  `creado_en` datetime DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

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
(1, 'Completada'),
(2, 'En proceso'),
(3, 'Cancelada'),
(4, 'Pendiente'),
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
  `actualizado_en` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Volcado de datos para la tabla `tproductos`
--

INSERT INTO `tproductos` (`Id`, `nombre_producto`, `descripcion`, `precio`, `stock`, `stock_minimo`, `stock_maximo`, `categoria_id`, `ruta_imagen`, `creado_en`, `actualizado_en`) VALUES
(1, 'Cappuccino', 'fsd', '12.00', 100, 10, 100, 2, '/static/images/productos/20250315172012.png', '2025-03-15 15:09:31', '2025-03-15 18:09:02');

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
(1, 1, 1, '12.00', '2025-03-15 15:09:31', '2025-03-15 15:09:31');

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
  `creado_en` datetime DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Volcado de datos para la tabla `tusuarios`
--

INSERT INTO `tusuarios` (`Id`, `usuario`, `contrasena`, `correo`, `rol_id`, `creado_en`) VALUES
(6, 'Isma', '123', 'ismaelcm18182@gmail.com', 1, '2025-03-10 23:19:36'),
(13, 'Isma2', '123', 'ismaelcm181821@gmail.com', 2, '2025-03-15 17:16:44');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `tventas`
--

CREATE TABLE `tventas` (
  `Id` int(11) NOT NULL,
  `cliente_id` int(11) DEFAULT NULL,
  `total` decimal(10,2) NOT NULL,
  `transaccion_id` varchar(255) DEFAULT NULL,
  `fecha_hora` datetime DEFAULT CURRENT_TIMESTAMP,
  `vendedor_id` int(11) DEFAULT NULL,
  `metodo_pago_id` int(11) DEFAULT NULL,
  `estado_id` int(11) DEFAULT NULL,
  `numero_mesa` varchar(50) DEFAULT NULL,
  `descuento_total` decimal(10,2) DEFAULT '0.00',
  `impuesto_total` decimal(10,2) DEFAULT '0.00',
  `creado_en` datetime DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

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
  ADD PRIMARY KEY (`Id`),
  ADD UNIQUE KEY `telefono_UNIQUE` (`telefono`),
  ADD UNIQUE KEY `correo_UNIQUE` (`correo`);

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
  ADD UNIQUE KEY `transaccion_id` (`transaccion_id`),
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
  MODIFY `Id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `tcortescaja`
--
ALTER TABLE `tcortescaja`
  MODIFY `Id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `testadosventa`
--
ALTER TABLE `testadosventa`
  MODIFY `Id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT de la tabla `tproductos`
--
ALTER TABLE `tproductos`
  MODIFY `Id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT de la tabla `tproductos_variantes`
--
ALTER TABLE `tproductos_variantes`
  MODIFY `Id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

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
  MODIFY `Id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=16;

--
-- AUTO_INCREMENT de la tabla `tventas`
--
ALTER TABLE `tventas`
  MODIFY `Id` int(11) NOT NULL AUTO_INCREMENT;

--
-- Restricciones para tablas volcadas
--

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
  ADD CONSTRAINT `tdevoluciones_ibfk_2` FOREIGN KEY (`producto_id`) REFERENCES `tproductos` (`id`),
  ADD CONSTRAINT `tdevoluciones_ibfk_3` FOREIGN KEY (`tipo_devolucion_id`) REFERENCES `ttiposdevolucion` (`id`),
  ADD CONSTRAINT `tdevoluciones_ibfk_4` FOREIGN KEY (`estado_devolucion_id`) REFERENCES `testadosdevolucion` (`id`);

--
-- Filtros para la tabla `tmovimientosinventario`
--
ALTER TABLE `tmovimientosinventario`
  ADD CONSTRAINT `tmovimientosinventario_ibfk_1` FOREIGN KEY (`producto_id`) REFERENCES `tproductos` (`id`),
  ADD CONSTRAINT `tmovimientosinventario_ibfk_2` FOREIGN KEY (`tipo_movimiento_id`) REFERENCES `ttiposmovimiento` (`id`);

--
-- Filtros para la tabla `tpagos`
--
ALTER TABLE `tpagos`
  ADD CONSTRAINT `tpagos_ibfk_1` FOREIGN KEY (`venta_id`) REFERENCES `tventas` (`Id`),
  ADD CONSTRAINT `tpagos_ibfk_2` FOREIGN KEY (`metodo_pago_id`) REFERENCES `tmetodospago` (`id`),
  ADD CONSTRAINT `tpagos_ibfk_3` FOREIGN KEY (`estado_pago_id`) REFERENCES `testadosdevolucion` (`id`);

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
  ADD CONSTRAINT `tventas_ibfk_3` FOREIGN KEY (`metodo_pago_id`) REFERENCES `tmetodospago` (`id`),
  ADD CONSTRAINT `tventas_ibfk_4` FOREIGN KEY (`estado_id`) REFERENCES `testadosventa` (`Id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
