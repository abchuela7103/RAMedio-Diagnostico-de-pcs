import psycopg2
import os

#SE DEFINE LA CONEXIÓN  A LA BD 
def get_connection():
    conn = psycopg2.connect(
        host="localhost",
        database="diagnostico",
        user="postgres",
        password="123",
        port="5432"
    )
    return conn

#METRICAS DEL AGENTE 
def insert_metrics(device_identifier, cpu, ram, disk):
    
    conn = get_connection()
    cursor = conn.cursor()

    # verificar si el device ya existe
    cursor.execute(
        "SELECT id FROM devices WHERE device_identifier = %s",
        (device_identifier,)
    )

    device = cursor.fetchone()

    if device is None:
        cursor.execute(
            "INSERT INTO devices (device_identifier) VALUES (%s) RETURNING id",
            (device_identifier,)
        )
        device_id = cursor.fetchone()[0]
    else:
        device_id = device[0]

    # insertar métricas
    cursor.execute(
        """
        INSERT INTO metrics (device_id, cpu_percent, ram_percent, disk_percent)
        VALUES (%s, %s, %s, %s)
        """,
        (device_id, cpu, ram, disk)
    )
    conn.commit()
    cursor.close()
    conn.close()



###CUESTIONARIO
    
def insert_questionnaire(device_identifier, answers):

    conn = get_connection()
    cursor = conn.cursor()

    # Buscar el dispositivo
    cursor.execute(
        "SELECT id FROM devices WHERE device_identifier = %s",
        (device_identifier,)
    )

    device = cursor.fetchone()

    if device is None:
        cursor.execute(
            "INSERT INTO devices (device_identifier) VALUES (%s) RETURNING id",
            (device_identifier,)
        )
        device_id = cursor.fetchone()[0]
    else:
        device_id = device[0]

    # Crear registro de cuestionario
    cursor.execute(
        "INSERT INTO questionnaires (device_id) VALUES (%s) RETURNING id",
        (device_id,)
    )

    questionnaire_id = cursor.fetchone()[0]

    # Insertar respuestas
    for question, value in answers.items():

        cursor.execute(
            """
            INSERT INTO questionnaire_answers
            (questionnaire_id, question_code, answer_value)
            VALUES (%s, %s, %s)
            """,
            (questionnaire_id, question, str(value))
        )

    conn.commit()
    cursor.close()
    conn.close()

