VisionLab — Detección y conteo de rostros en tiempo real
Universidad Estatal de Milagro (UNEMI) · Construcción de Software · Práctica N.º 3 (G003-S12-SOFTWARE2019-PRESENCIAL-CONSTRUCCIÓN DE SOFTWARE-A2)
Descripción
VisionLab es una aplicación web educativa desarrollada con Python, Django, OpenCV y PostgreSQL. Utiliza la cámara del navegador, transmite fotogramas al servidor Django, detecta rostros frontales mediante un clasificador Haar Cascade y muestra el conteo y los recuadros en un dashboard. A petición del usuario, guarda un conteo agregado en PostgreSQL.

El sistema no identifica personas, no registra asistencia individual ni almacena fotografías o imágenes biométricas.
Integrantes
- Morquecho Rodas Cesar
- Velez Correa Moises
- Choez Mora Jose
- Cabrera Bajaña Caleb
- Arroyo Cevillano Tiffany
Docente de práctica: Ing. Almache Sanisaca Mariana Madeleine
Periodo: Agosto 2026 – Diciembre 2026
Funcionalidades
- Activación y detención de cámara desde el navegador.
- Detección de rostros y visualización de recuadros en tiempo real.
- Conteo actual, indicadores y estadísticas de sesión.
- Registro manual de conteos en PostgreSQL.
- Página adaptable a pantallas de diferentes tamaños.
- Pruebas automatizadas de endpoints y persistencia.
Tecnologías
- Python 3.12 recomendado en Windows
- Django 5.2.x (según requirements.txt)
- OpenCV (cv2), detector Haar Cascade
- PostgreSQL
- HTML, CSS y JavaScript
- Git y GitHub
Requisitos previos
Instalar Python, Git y PostgreSQL. Crear la base de datos detector_rostros y disponer de credenciales válidas. La webcam requiere permiso del navegador; para ejecución local usar http://127.0.0.1:8000/.
Instalación en Windows
Abrir una terminal dentro de la carpeta que contiene manage.py:
py -m venv .venv
.venv\Scripts\activate.bat
python -m pip install -r requirements.txt
Crear un archivo .env a partir de .env.example y asignar los valores de la base de datos y la clave secreta, sin subir ese archivo al repositorio:
DJANGO_SECRET_KEY=GENERAR_UNA_CLAVE_PRIVADA
DJANGO_DEBUG=True
DB_NAME=detector_rostros
DB_USER=postgres
DB_PASSWORD=REEMPLAZAR_POR_CONTRASENA_LOCAL
DB_HOST=localhost
DB_PORT=5433
DB_PORT=5433 corresponde al equipo utilizado para la práctica. En otros equipos debe reemplazarse por el puerto real del servidor PostgreSQL. No se incluyen contraseñas ni credenciales privadas en el repositorio.

Ejecutar:
python manage.py check
python manage.py migrate
python manage.py runserver
Abrir http://127.0.0.1:8000/ en el navegador.
Uso
1. Abrir VisionLab y autorizar el permiso de cámara.
2. Presionar Iniciar cámara.
3. Comprobar los recuadros y el número de rostros visibles.
4. Presionar Guardar conteo cuando se quiera almacenar el resultado.
5. Presionar Detener cámara.
Pruebas
Desde la carpeta del proyecto y con el entorno virtual activado:
python manage.py test detector
Este comando utiliza una base de pruebas temporal de Django. Requiere permisos adecuados de PostgreSQL para crearla. No implica que las pruebas ya se hayan ejecutado en el equipo del lector.

Para verificar registros guardados en pgAdmin:
SELECT id, face_count, created_at
FROM detector_detectionrecord
ORDER BY created_at DESC;
Arquitectura resumida
Webcam → JavaScript (fotograma) → Django (/api/analyze/) → OpenCV → JSON (recuadros y conteo) → dashboard

El botón Guardar conteo envía un registro a /api/save/, persistido mediante el modelo DetectionRecord en PostgreSQL.
Limitaciones y privacidad
- Haar Cascade es sensible a la iluminación, orientación, tamaño del rostro y oclusiones.
- El conteo representa rostros detectados en un fotograma, no individuos únicos.
- El usuario debe permitir el acceso a la cámara y obtener consentimiento de otros participantes.
- No se almacenan fotografías; solo cantidades y marcas temporales cuando el usuario solicita guardar.
- No publicar .env, .venv, contraseñas, claves secretas ni bases de datos personales.
Entrega académica
- Repositorio en GitHub que contiene este README y requirements.txt.
- Video demostrativo de hasta tres minutos grabado desde un computador, compartido por Google Drive.
- Informe PDF institucional con evidencias reales y enlaces.
Como ejecutarlo de manera correcta:
cd VisionLab_Proyecto_Guiado
.venv\Scripts\activate.bat
python manage.py check
python manage.py runserver