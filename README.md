# 🧩 SOA Serverless DBMS con Docker, RabbitMQ y Autenticación Google

**Equipo:**
- **Coyotzi Juarez Jose Antonio**
- **Aguilar Macias Javier**

Este proyecto implementa un sistema de gestión de bases de datos serverless de propósito general, utilizando una arquitectura orientada a servicios (SOA) y una arquitectura de paso de mensajes basada en RabbitMQ. El sistema es completamente transparente para el usuario y permite operar con bases de datos sin necesidad de conocer un sistema gestor de bases de datos (SGBD) específico.

<img src="https://eitpl.in/assets/img/service/database.gif" alt="App Platform" width="300"/>

---

## 🚀 Características Principales

- Arquitectura **SOA** con comunicación basada en mensajes (**RabbitMQ + SOAP**)
- Contenedores **Docker** para despliegue modular
- Interfaz dual: **SQL (PostgreSQL)** y **NoSQL (MongoDB)**
- Autenticación mediante **APIs públicas de Google**
- Seguridad basada en **roles de usuario**
- CRUD completo sobre bases de datos y tablas/estructuras
- Soporte para operaciones avanzadas:
  - **JOINS**
  - Agrupaciones: `SUM`, `COUNT`, `DISTINCT`, `AVG`
- Método `listAll` para descubrir la interfaz del servicio

---

## 🧱 Funcionalidades del Servicio

### Gestión de Bases de Datos

- Crear, modificar, listar y eliminar bases de datos

### Gestión de Tablas/Estructuras

- Crear, modificar, listar y eliminar tablas (SQL) o estructuras (NoSQL)

### Operaciones CRUD

- Insertar, consultar, actualizar y eliminar registros

### Consultas Avanzadas

- Soporte para **JOINs** y funciones de **agregación**

### Seguridad

- Autenticación mediante **Google OAuth**
- Control de acceso basado en **roles**

### Interfaces Intercambiables

- **SQL Based**: PostgreSQL
- **NoSQL Based**: MongoDB

---

## 🧪 Tecnologías Utilizadas

- **Docker**: Contenerización de servicios
- **RabbitMQ**: Sistema de mensajería
- **SOAP**: Protocolo de comunicación entre servicios
- **PostgreSQL**: Motor SQL
- **MongoDB**: Motor NoSQL
- **Google OAuth**: Autenticación de usuarios
