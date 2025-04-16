import threading
import psycopg2
import time
import random

# Configuración de conexión a la base de datos
DB_CONFIG = {
    'dbname': 'Proyecto2',
    'user': 'usuario',
    'password': 'password',
    'host': 'localhost',
    'port': 5433
}

# Mapear niveles de aislamiento a psycopg2
ISOLATION_LEVELS = {
    'READ COMMITTED': psycopg2.extensions.ISOLATION_LEVEL_READ_COMMITTED,
    'REPEATABLE READ': psycopg2.extensions.ISOLATION_LEVEL_REPEATABLE_READ,
    'SERIALIZABLE': psycopg2.extensions.ISOLATION_LEVEL_SERIALIZABLE
}

def reservar_asiento(user_id, asiento_id, isolation_level, resultados, lock):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        conn.set_isolation_level(ISOLATION_LEVELS[isolation_level])
        cursor = conn.cursor()

        cursor.execute("BEGIN;")
        try:
            # Añadimos un pequeño retraso aleatorio para aumentar la probabilidad de colisiones
            time.sleep(random.uniform(0.01, 0.05))
            
            # Verificamos primero si el asiento está disponible
            cursor.execute(
                "SELECT id_reserva FROM reservas WHERE id_asiento = %s AND id_estado = 1;",
                (asiento_id,)
            )
            if cursor.fetchone() is None:
                cursor.execute(
                    "INSERT INTO reservas (id_usuario, id_asiento, id_estado) VALUES (%s, %s, %s);",
                    (user_id, asiento_id, 1)
                )
                conn.commit()
                with lock:
                    resultados['exitosas'] += 1

                
                print(f"Usuario {user_id} reservó asiento {asiento_id} exitosamente")
            else:
                with lock:
                    resultados['fallidas'] += 1
                print(f"Usuario {user_id} falló al reservar asiento {asiento_id} (ya ocupado)")
                conn.commit()
        except psycopg2.errors.SerializationFailure as e:
            # Error de serialización: rollback y reintentar
            conn.rollback()
            with lock:
                resultados['fallidas'] += 1
            print(f"Usuario {user_id} - error de serialización al reservar asiento {asiento_id}: {e}")

        except psycopg2.errors.UniqueViolation:
            conn.rollback()
            with lock:
                resultados['fallidas'] += 1
            print(f"Usuario {user_id} tuvo conflicto al reservar asiento {asiento_id}")
    
        except Exception as e:
            conn.rollback()
            with lock:
                resultados['fallidas'] += 1
            print(f"Usuario {user_id} falló al reservar asiento {asiento_id}: {str(e)}")

        cursor.close()
        conn.close()

    except Exception as e:
        with lock:
            resultados['fallidas'] += 1
        print(f"Error de conexión para usuario {user_id}: {str(e)}")

def asegurar_asientos_disponibles(num_asientos):
    """Asegura que existan suficientes asientos en la base de datos"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Primero eliminamos todos los asientos para empezar limpio
        cursor.execute("DELETE FROM asientos;")
        
        # Creamos exactamente el número de asientos necesarios
        for i in range(1, num_asientos + 1):
            cursor.execute(
                "INSERT INTO asientos (id_evento, numero_asiento) VALUES (%s, %s);",
                (i, f"Asiento {i}")
            )
        
        conn.commit()
        cursor.close()
        conn.close()
        print(f"Se han creado {num_asientos} asientos")
    except Exception as e:
        print(f"Error al crear asientos: {str(e)}")

def asegurar_usuarios_disponibles(num_usuarios):
    """Asegura que existan suficientes usuarios en la base de datos"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Primero eliminamos todos los usuarios excepto los primeros dos (si existen)
        cursor.execute("DELETE FROM usuarios WHERE id_usuario >= 3;")
        
        # Creamos exactamente el número de usuarios necesarios
        for i in range(3, 3 + num_usuarios):
            cursor.execute(
                "INSERT INTO usuarios (nombre, email) VALUES (%s, %s);",
                (f"Usuario {i}", f"usuario{i}@example.com")
            )
        
        conn.commit()
        cursor.close()
        conn.close()
        print(f"Se han creado {num_usuarios} usuarios")
    except Exception as e:
        print(f"Error al crear usuarios: {str(e)}")

def crear_distribucion_asientos_con_colisiones(num_concurrente):
    """
    Crea una distribución de asientos con colisiones garantizadas.
    El 50% de los asientos tendrán múltiples usuarios compitiendo por ellos.
    """
    # Calculamos cuántos asientos vamos a crear (la mitad del número de usuarios)
    num_asientos = 10#num_concurrente // 2
    #if num_asientos < 1:
     #   num_asientos = 1
    
    # Creamos las asignaciones
    asignaciones = []
    for i in range(1, num_concurrente + 1):
        # Asignar a cada usuario un asiento entre 1 y num_asientos
        # Esto garantiza que habrá colisiones cuando num_usuarios > num_asientos
        asiento_id = ((i - 1) % num_asientos) + 1
        num = (i + 2)%30;
        if num ==0:
            num = 30
        asignaciones.append((num, asiento_id))  # Usuario ID comienza en 3
    
    # Para aumentar aún más las colisiones, hacemos que algunos usuarios
    # específicamente compitan por el asiento #1
    if num_concurrente >= 5:
        # Asignar el 20% de los usuarios adicionales al asiento #1
        num_competidores = num_concurrente // 5
        for i in range(num_competidores):
            # Reemplazamos algunas asignaciones para apuntar al asiento #1
            indice = random.randint(0, num_concurrente - 1)
            asignaciones[indice] = (asignaciones[indice][0], 1)
    
    print(f"Distribución de asientos (usuario, asiento): {asignaciones}")
    return asignaciones

def ejecutar_prueba(concurrentes, isolation_level):
    print(f"\nEjecutando prueba con {concurrentes} usuarios concurrentes - Nivel: {isolation_level}")
    resultados = {'exitosas': 0, 'fallidas': 0}
    hilos = []
    inicio = time.time()
    lock = threading.Lock()  # Para actualizar resultados de forma segura

    # Aseguramos que tengamos suficientes asientos y usuarios para esta prueba
    num_asientos = concurrentes // 2  # Creamos la mitad de asientos que usuarios
    if num_asientos < 1:
        num_asientos = 1
    
    # Creamos distribución con colisiones garantizadas
    asignaciones = crear_distribucion_asientos_con_colisiones(concurrentes)

    for i in range(concurrentes):
        user_id = asignaciones[i][0]  # Usuario ID
        asiento_id = asignaciones[i][1]  # Asiento ID
        hilo = threading.Thread(target=reservar_asiento, args=(user_id, asiento_id, isolation_level, resultados, lock))
        hilos.append(hilo)
        hilo.start()

    for hilo in hilos:
        hilo.join()

    fin = time.time()
    tiempo_total = round((fin - inicio) * 1000, 2)  # en ms
    tiempo_promedio = round(tiempo_total / concurrentes, 2)

    print(f"Resultado: Exitosas: {resultados['exitosas']} | Fallidas: {resultados['fallidas']} | Tiempo Promedio: {tiempo_promedio} ms")
    resultados['tiempo'] = tiempo_promedio
    return resultados

def printInforme(informe):
    tr = ["SERIALIZABLE", "REPEATABLE READ", "READ COMMITTED"]
    count = 0; cats = {0:5, 1:10, 2:20, 3:30}
    print("\nINFORME DE RESULTADOS")
    for i in informe:
        cat = cats[count%4]
        if count%4 == 0:
            print(tr.pop());
        print(f"{cat}: exitos: {i['exitosas']}, fallidos: {i['fallidas']}, tiempo promedio: {i['tiempo']} ms")
        count += 1

def configure():
    # Solicitar datos al usuario para cada uno de los parámetros de conexión.
    dbname = input("Ingrese el nombre de la base de datos: ")
    user = input("Ingrese el usuario: ")
    password = input("Ingrese la contraseña: ")
    host = input("Ingrese el host: ")
    port = input("Ingrese el puerto: ")

    # Construir el diccionario de configuración.
    DB_CONFIG = {
        'dbname': dbname,
        'user': user,
        'password': password,
        'host': host,
        'port': port
    }

    # Intentar conectar utilizando la configuración proporcionada.
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        conn.close()  # Cerramos la conexión si fue exitosa.
        print("Conexión exitosa.")
        return True
    except Exception as e:
        print("Error al conectar:", e)
        return False


def main():
    if not configure():
        return
    pruebas = [5, 10, 20, 30]
    niveles = ['READ COMMITTED', 'REPEATABLE READ', 'SERIALIZABLE']
    informe = []

    for nivel in niveles:
        for cantidad in pruebas:
            r = ejecutar_prueba(cantidad, nivel)
            limpiar_reservas_prueba()
            informe.append(r)
    printInforme(informe)

def limpiar_reservas_prueba():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM reservas;")
        conn.commit()
        cursor.close()
        conn.close()
        print("Reservas limpiadas para la siguiente prueba")
    except Exception as e:
        print(f"Error al limpiar reservas: {str(e)}")

if __name__ == "__main__":
    main()
