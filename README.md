# Base de datos de Streaming

## Descripción
Este proyecto se realizó con la intención de aprender normalización de datos en formato .csv para cargarlos en un motor de base de datos, yo utilize mysql



## Instalación
Cloná el siguiente repositorio:

```bash
git clone https://github.com/tu-usuario/streaming-database
```


## Diagrama de Entidad - Relación
Diagrama Entidad Relación de la base de datos

![Diagrama ER](diagrama.png)

## Explicación sobre Normalización Realizada

Antes que nada, descargamos los archivos .csv y corroboramos como los datos estaban organizados y que tipo de separador usaban para comenzar a planificar la estructura de la base de datos y las tablas.

### Creación de la Base de Datos

Creamos la base de datos con la siguiente consulta

```sql
CREATE DATABASE streaming_db;
USE streaming_db;
```

### Creación de Tablas

Creamos las tablas que iban a contener a los archivos .csv. Utilize tipo de datos INT, VARCHAR y TEXT, y definimos claves primarias y foráneas.

#### Tabla Contenido (Principal)
```sql
CREATE TABLE contenido (
    show_id VARCHAR(20) PRIMARY KEY,
    type VARCHAR(20),
    title VARCHAR(500),
    director TEXT,
    cast TEXT,
    country TEXT,
    date_added VARCHAR(50),
    release_year INT,
    rating VARCHAR(20),
    duration VARCHAR(50),
    listed_in TEXT,
    description TEXT
);
```

#### Tabla Directores
```sql
CREATE TABLE directores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre TEXT NOT NULL
);
```

#### Tabla Actores
```sql
CREATE TABLE actores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre TEXT NOT NULL
);
```

#### Tabla Países
```sql
CREATE TABLE paises (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL
);
```

#### Tabla Géneros
```sql
CREATE TABLE generos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL
);
```

#### Tabla Contenido_Directores (Relación Muchos a Muchos)
```sql
CREATE TABLE contenido_directores (
    show_id VARCHAR(20),
    director_id INT,
    PRIMARY KEY (show_id, director_id),
    FOREIGN KEY (show_id) REFERENCES contenido(show_id) ON DELETE CASCADE,
    FOREIGN KEY (director_id) REFERENCES directores(id) ON DELETE CASCADE
);
```

#### Tabla Contenido_Actores (Relación Muchos a Muchos)
```sql
CREATE TABLE contenido_actores (
    show_id VARCHAR(20),
    actor_id INT,
    PRIMARY KEY (show_id, actor_id),
    FOREIGN KEY (show_id) REFERENCES contenido(show_id) ON DELETE CASCADE,
    FOREIGN KEY (actor_id) REFERENCES actores(id) ON DELETE CASCADE
);
```

#### Tabla Contenido_Paises (Relación Muchos a Muchos)
```sql
CREATE TABLE contenido_paises (
    show_id VARCHAR(20),
    pais_id INT,
    PRIMARY KEY (show_id, pais_id),
    FOREIGN KEY (show_id) REFERENCES contenido(show_id) ON DELETE CASCADE,
    FOREIGN KEY (pais_id) REFERENCES paises(id) ON DELETE CASCADE
);
```

#### Tabla Contenido_Generos (Relación Muchos a Muchos)
```sql
CREATE TABLE contenido_generos (
    show_id VARCHAR(20),
    genero_id INT,
    PRIMARY KEY (show_id, genero_id),
    FOREIGN KEY (show_id) REFERENCES contenido(show_id) ON DELETE CASCADE,
    FOREIGN KEY (genero_id) REFERENCES generos(id) ON DELETE CASCADE
);
```

### Carga de Datos

A partir de ahí comenzamos cargando los datos a la base con el siguiente comando:

```sql
LOAD DATA LOCAL INFILE 'C:\\ruta\\archivo.csv' 
INTO TABLE contenido
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;
```

### Normalización de Datos

Con todos los datos cargados en la tabla principal,normalizamos la información extrayendo los datos únicos de directores, actores, países y géneros.

#### Poblar tabla Directores
```sql
INSERT INTO directores (nombre)
SELECT DISTINCT TRIM(director)
FROM contenido
WHERE director IS NOT NULL AND director != '';
```

#### tabla Actores
```sql
INSERT INTO actores (nombre)
SELECT DISTINCT TRIM(cast)
FROM contenido
WHERE cast IS NOT NULL AND cast != '';
```

#### tabla Países
```sql
INSERT INTO paises (nombre)
SELECT DISTINCT TRIM(country)
FROM contenido
WHERE country IS NOT NULL AND country != '';
```

#### tabla Géneros
```sql
INSERT INTO generos (nombre)
SELECT DISTINCT TRIM(listed_in)
FROM contenido
WHERE listed_in IS NOT NULL AND listed_in != '';
```

### Relaciones

Crear relaciones entre tablas

#### Relaciona Contenido con Directores
```sql
INSERT INTO contenido_directores (show_id, director_id)
SELECT c.show_id, d.id
FROM contenido c
JOIN directores d ON TRIM(c.director) = d.nombre
WHERE c.director IS NOT NULL AND c.director != '';
```

#### Relaciona Contenido con Actores
```sql
INSERT INTO contenido_actores (show_id, actor_id)
SELECT c.show_id, a.id
FROM contenido c
JOIN actores a ON TRIM(c.cast) = a.nombre
WHERE c.cast IS NOT NULL AND c.cast != '';
```

#### Relaciona Contenido con Países
```sql
INSERT INTO contenido_paises (show_id, pais_id)
SELECT c.show_id, p.id
FROM contenido c
JOIN paises p ON TRIM(c.country) = p.nombre
WHERE c.country IS NOT NULL AND c.country != '';
```

#### Relaciona Contenido con Géneros
```sql
INSERT INTO contenido_generos (show_id, genero_id)
SELECT c.show_id, g.id
FROM contenido c
JOIN generos g ON TRIM(c.listed_in) = g.nombre
WHERE c.listed_in IS NOT NULL AND c.listed_in != '';
```

## Consultas

Se muestran las consultas SQL que realizamos con la base de datos.

### Total de contenido por tipo (Películas vs Series)
```sql
SELECT type, COUNT(*) AS total
FROM contenido
GROUP BY type;
```

### Contenido más reciente agregado
```sql
SELECT show_id, title, type, date_added
FROM contenido
ORDER BY date_added DESC
LIMIT 10;
```

### Top 10 directores con más contenido
```sql
SELECT d.nombre AS director, COUNT(*) AS cantidad_contenido
FROM directores d
JOIN contenido_directores cd ON d.id = cd.director_id
GROUP BY d.id
ORDER BY cantidad_contenido DESC
LIMIT 10;
```

### Top 10 actores con más participaciones
```sql
SELECT a.nombre AS actor, COUNT(*) AS cantidad_participaciones
FROM actores a
JOIN contenido_actores ca ON a.id = ca.actor_id
GROUP BY a.id
ORDER BY cantidad_participaciones DESC
LIMIT 10;
```

### Contenido por país (Top 10)
```sql
SELECT p.nombre AS pais, COUNT(*) AS cantidad_contenido
FROM paises p
JOIN contenido_paises cp ON p.id = cp.pais_id
GROUP BY p.id
ORDER BY cantidad_contenido DESC
LIMIT 10;
```

### Géneros más populares
```sql
SELECT g.nombre AS genero, COUNT(*) AS cantidad_contenido
FROM generos g
JOIN contenido_generos cg ON g.id = cg.genero_id
GROUP BY g.id
ORDER BY cantidad_contenido DESC
LIMIT 10;
```

### Películas por año de lanzamiento
```sql
SELECT release_year, COUNT(*) AS cantidad_peliculas
FROM contenido
WHERE type = 'Movie' AND release_year IS NOT NULL
GROUP BY release_year
ORDER BY release_year DESC;
```

### Buscar todo el contenido de un director específico
```sql
SELECT c.title, c.type, c.release_year, c.rating
FROM contenido c
JOIN contenido_directores cd ON c.show_id = cd.show_id
JOIN directores d ON cd.director_id = d.id
WHERE d.nombre LIKE '%Kirsten Johnson%'
ORDER BY c.release_year DESC;
```

### Buscar todo el contenido de un actor específico
```sql
SELECT c.title, c.type, c.release_year, c.rating
FROM contenido c
JOIN contenido_actores ca ON c.show_id = ca.show_id
JOIN actores a ON ca.actor_id = a.id
WHERE a.nombre LIKE '%Robert Cullen%'
ORDER BY c.release_year DESC;
```

### Contenido por rating
```sql
SELECT rating, COUNT(*) AS cantidad
FROM contenido
WHERE rating IS NOT NULL AND rating != ''
GROUP BY rating
ORDER BY cantidad DESC;
```

### Películas de un año específico
```sql
SELECT title, rating, duration
FROM contenido
WHERE type = 'Movie' AND release_year = 2021
ORDER BY title;
```

### Series con descripción que contenga una palabra clave
```sql
SELECT title, description
FROM contenido
WHERE type = 'TV Show' AND description LIKE '%family%'
LIMIT 10;
```

## Tecnologías Utilizadas

- MySQL / MariaDB
- MySQL Workbench
- CSV

## Autor

Buyatti Facundo
