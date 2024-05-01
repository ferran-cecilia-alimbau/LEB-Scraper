---

# Basketball Stats Scraper

Este proyecto es un scraper diseñado para obtener datos detallados de una liga de baloncesto, incluidas las estadísticas de partidos, jugadores y equipos. Los datos extraídos se almacenan en archivos CSV para análisis posterior.

## Contenido del Proyecto:

- **`http_request.py`**: Proporciona la clase `HTTPRequest` para manejar solicitudes HTTP de manera eficiente. Incluye funciones para crear una sesión persistente con un agente de usuario personalizado, y para realizar solicitudes HTTP con diferentes métodos (GET, POST) de manera controlada.

- **`logger.py`**: Configura un sistema de registro de eventos para la aplicación, utilizando archivos de registro rotativos para mantener un historial de eventos y errores de manera organizada. Los archivos de registro se guardan en un directorio `logs` y cada registro incluye detalles como la marca de tiempo, nivel de severidad, nombre del logger, nombre del archivo y línea de código.

- **`scraper.py`**: Contiene la lógica principal del scraper, extendiendo la funcionalidad de `HTTPRequest`. Incluye la función `process_games` para procesar un rango de juegos especificado en la configuración, extraer información sobre partidos, jugadores y equipos, y escribir estos datos en archivos CSV. También contiene funciones como `extract_game_info` para manejar la lógica de extracción de datos.

- **`scraper_exceptions.py`**: Define una jerarquía de excepciones relacionadas con el scraping, incluyendo `ScraperError` como clase base, `HTTPRequestError` para errores en solicitudes HTTP, y `ParsingError` para problemas durante el análisis de contenido HTML. Esto proporciona un manejo de errores estructurado para el proyecto.

- **`config.json`**: Contiene la configuración del scraper, incluyendo:
  - El rango de IDs de juegos a procesar.
  - El agente de usuario para solicitudes HTTP.
  - Las cabeceras para los archivos CSV de salida (`partidos.csv`, `player_stats.csv`, `estadisticas_total_equipo.csv`).

## Cómo Usarlo:

1. **Configuración**: Asegúrate de que `config.json` esté configurado correctamente con el rango de IDs de juegos a procesar y las cabeceras de salida.

2. **Ejecución**: Ejecuta el archivo `main.py` para iniciar el scraper. Esto procesará los juegos en el rango especificado y almacenará los datos en archivos CSV en el directorio especificado.

3. **Registros**: Los eventos y errores se registrarán en archivos en el directorio `logs`.

## Requerimientos:

- Python 3.x
- Paquetes: `requests`, `beautifulsoup4`, `logging`, entre otros. (Se recomienda revisar e instalar los paquetes listados en `requirements.txt`)

## Contribución:

- **Reportar Bugs**: Si encuentras algún problema, abre un Issue en el repositorio de GitHub.
- **Contribuciones**: Se aceptan PRs (Pull Requests) para mejoras y nuevas características. Asegúrate de seguir las directrices de codificación del proyecto.

---

¿Te gustaría hacer alguna otra modificación o añadir más detalles?