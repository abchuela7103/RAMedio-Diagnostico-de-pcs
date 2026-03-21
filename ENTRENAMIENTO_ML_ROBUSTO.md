# Guía: Cómo Lograr Precisión Máxima en el Modelo de Machine Learning

Has añadido exitosamente un total de **10 nuevos síntomas avanzados** a tu formulario web (ahora tienes 15 preguntas en total). Estas preguntas abarcan desde errores de BIOS, corrupción de disco, fallas de GPU, caídas de red, hasta problemas eléctricos.

La Base de Datos ahora recopila todos estos datos fielmente cada vez que un usuario llena el reporte.

### El Reto de la Precisión
Actualmente, tu archivo `ML/classifier.py` está configurado para que la Inteligencia Artificial **ignore** tus 10 preguntas nuevas. Esto se hizo a propósito para evitar que el servidor colapse, ya que el archivo `modelo_decision_tree.pkl` que entrenaste semanas atrás *solo conoce 5 síntomas y 3 métricas*.

### ¿Cómo hacer a la IA más precisa?
Para que el Árbol de Decisión realmente procese toda esta complejidad interactiva (como solicitaste), necesitas **Re-entrenar el Modelo**. 

Sigue estos 3 pasos:

**1. Recolectar o Generar Datos Nuevos**
Necesitarás un archivo CSV o un DataFrame de Pandas que contenga columnas para **todas las 15 variables de síntomas** + las métricas de hardware (`cpu`, `ram`, `disk`).
Puedes generar cientos de filas de datos sintéticos donde simules fallas. Ejemplo:
* Si `visual_artifacts` es True y `gpu` > 90 -> Etiqueta: "Falla inminente de Tarjeta de Video"
* Si `file_corruption` es True y `disk_active` es 100% -> Etiqueta: "Disco duro dañado"
* Si `network_drops` es True -> Etiqueta: "Problema en el controlador de Red"

**2. Crear un nuevo script de Entrenamiento**
Crea un script (ej. `ML/train_new_model.py`) que use `DecisionTreeClassifier` pasándole todas estas columnas:
```python
import pandas as pd
from sklearn.tree import DecisionTreeClassifier
import joblib

# Supongamos que df es tu dataframe de Pandas con tus cientos de ejemplos simulados
X = df[["cpu", "ram", "disk", "is_slow", "random_restarts", "weird_noises", "overheating", "bsod_errors", "screen_flicker", "apps_crashing", "battery_issue", "burnt_smell", "visual_artifacts", "system_freezes", "usb_disconnects", "network_drops", "slow_boot", "file_corruption"]]
y = df["estado_del_sistema"] # "Saludable", "Falla de GPU", "Falla de Disco", etc.

modelo = DecisionTreeClassifier()
modelo.fit(X, y)
joblib.dump(modelo, "ML/modelo_decision_tree.pkl")
```

**3. Actualizar la inyección en FastAPI**
Una vez que tengas tu nuevo archivo `.pkl` altamente complejo, ve a `server/api.py`, dirígete a la ruta `def run_diagnostics`, e incluye dentro del diccionario `symptoms_data` los campos que faltan mapear, por ejemplo: `"visual_artifacts": latest_symptoms.visual_artifacts`, para que viajen hacia la IA. También deberás actualizar el `pd.DataFrame([{...}])` en `ML/classifier.py` para que lea esos nuevos *keys*.

¡Con estos pasos tu Inteligencia Artificial será absurdamente precisa e interpretará el estado real de la computadora como todo un ingeniero de soporte!
