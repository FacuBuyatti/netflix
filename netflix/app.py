from flask import Flask, render_template, request
import mysql.connector

app = Flask(__name__)

# Configuración de la base de datos
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '1289',  # CAMBIÁ ESTO
    'database': 'streaming_db'
}

def get_db():
    return mysql.connector.connect(**DB_CONFIG)

@app.route('/')
def index():
    # Obtener filtros
    busqueda = request.args.get('busqueda', '')
    tipo = request.args.get('tipo', '')
    genero = request.args.get('genero', '')
    anio = request.args.get('anio', '')
    rating = request.args.get('rating', '')
    
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    # Estadísticas
    cursor.execute("""
        SELECT 
            (SELECT COUNT(*) FROM contenido) as total_contenido,
            (SELECT COUNT(*) FROM contenido WHERE type = 'Movie') as total_peliculas,
            (SELECT COUNT(*) FROM contenido WHERE type = 'TV Show') as total_series,
            (SELECT COUNT(*) FROM directores) as total_directores,
            (SELECT COUNT(*) FROM actores) as total_actores,
            (SELECT COUNT(*) FROM generos) as total_generos
    """)
    stats = cursor.fetchone()
    
    # Construir consulta
    query = "SELECT * FROM contenido WHERE 1=1"
    params = []
    
    if busqueda:
        query += " AND title LIKE %s"
        params.append(f'%{busqueda}%')
    
    if tipo:
        query += " AND type = %s"
        params.append(tipo)
    
    if anio:
        query += " AND release_year = %s"
        params.append(anio)
    
    if rating:
        query += " AND rating = %s"
        params.append(rating)
    
    if genero:
        query = """
            SELECT DISTINCT c.* FROM contenido c
            JOIN contenido_generos cg ON c.show_id = cg.show_id
            JOIN generos g ON cg.genero_id = g.id
            WHERE g.nombre LIKE %s
        """
        params = [f'%{genero}%']
        
        if busqueda:
            query += " AND c.title LIKE %s"
            params.append(f'%{busqueda}%')
        if tipo:
            query += " AND c.type = %s"
            params.append(tipo)
        if anio:
            query += " AND c.release_year = %s"
            params.append(anio)
        if rating:
            query += " AND c.rating = %s"
            params.append(rating)
    
    query += " LIMIT 100"
    
    cursor.execute(query, params)
    contenido = cursor.fetchall()
    
    # Obtener opciones para los filtros
    cursor.execute("SELECT DISTINCT release_year FROM contenido WHERE release_year IS NOT NULL ORDER BY release_year DESC")
    anios = [row['release_year'] for row in cursor.fetchall()]
    
    cursor.execute("SELECT DISTINCT rating FROM contenido WHERE rating IS NOT NULL AND rating != '' ORDER BY rating")
    ratings = [row['rating'] for row in cursor.fetchall()]
    
    cursor.execute("SELECT nombre FROM generos ORDER BY nombre LIMIT 50")
    generos_lista = [row['nombre'] for row in cursor.fetchall()]
    
    cursor.close()
    db.close()
    
    return render_template('index.html', 
                         contenido=contenido,
                         stats=stats,
                         anios=anios,
                         ratings=ratings,
                         generos_lista=generos_lista,
                         busqueda=busqueda,
                         tipo=tipo,
                         genero=genero,
                         anio=anio,
                         rating=rating)

@app.route('/detalle/<show_id>')
def detalle(show_id):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    cursor.execute('SELECT * FROM contenido WHERE show_id = %s', (show_id,))
    contenido = cursor.fetchone()
    
    cursor.execute("""
        SELECT d.nombre FROM directores d
        JOIN contenido_directores cd ON d.id = cd.director_id
        WHERE cd.show_id = %s
    """, (show_id,))
    directores = cursor.fetchall()
    
    cursor.execute("""
        SELECT a.nombre FROM actores a
        JOIN contenido_actores ca ON a.id = ca.actor_id
        WHERE ca.show_id = %s LIMIT 10
    """, (show_id,))
    actores = cursor.fetchall()
    
    cursor.execute("""
        SELECT p.nombre FROM paises p
        JOIN contenido_paises cp ON p.id = cp.pais_id
        WHERE cp.show_id = %s
    """, (show_id,))
    paises = cursor.fetchall()
    
    cursor.execute("""
        SELECT g.nombre FROM generos g
        JOIN contenido_generos cg ON g.id = cg.genero_id
        WHERE cg.show_id = %s
    """, (show_id,))
    generos = cursor.fetchall()
    
    cursor.close()
    db.close()
    
    return render_template('detalle.html',
                         contenido=contenido,
                         directores=directores,
                         actores=actores,
                         paises=paises,
                         generos=generos)

if __name__ == '__main__':
    app.run(debug=True)