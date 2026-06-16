# Operación Santiago - Documentación del Proyecto

## Descripción General
"Operación Santiago" es un videojuego de investigación deductiva inspirado en la mecánica clásica de *Carmen Sandiego*, pero ambientado exclusivamente en las 17 Comunidades Autónomas de España. El jugador asume el rol del Teniente Santiago de la Guardia Civil, quien debe resolver casos contrarreloj atrapando a diversos criminales tras seguir su rastro por toda la geografía española.

## Arquitectura Tecnológica
El proyecto está desarrollado en **Python** utilizando el framework reactivo **Flet**, lo que permite que el juego pueda ejecutarse de tres formas distintas con el mismo código base:
1.  Como aplicación de escritorio.
2.  Como aplicación web (ideal para ser alojada de forma estática en **Netlify**).
3.  Como APK empaquetado para Android (a futuro, mediante las herramientas de exportación de Flet/Flutter).

La lógica de negocio se ha separado de la interfaz gráfica y los datos están persistidos en archivos JSON estáticos, garantizando que el juego pueda distribuirse como un paquete sin necesidad de backend o bases de datos complejas.

## Estructura de Directorios
```text
cajasFuertes/
│
├── assets/                 # Recursos gráficos y multimedia
│   └── images/
│       ├── cities/         # Fotos (.jpg/.png) de monumentos de las ciudades (ej. madrid.jpg)
│       └── suspects/       # Retratos (.png) generados de los 8 criminales (ej. s1.png)
│
├── data/                   # Bases de datos del juego en formato JSON
│   ├── cities.json         # Las 17 capitales autonómicas, descripciones y lugares visitables.
│   ├── items.json          # Botines robados y armas homicidas.
│   ├── suspects.json       # Fichas de los 8 criminales (físico, vehículo, hobbies, etc.).
│   └── words.json          # Diccionario de palabras (5, 6 y 7 letras) para el minijuego.
│
├── src/                    # Código fuente
│   ├── core/
│   │   └── case_manager.py # Motor procedimental: Genera rutas, asigna botines y controla el tiempo.
│   ├── minigames/          # Lógicas independientes de cada puzzle
│   │   ├── safe_box.py     # Minijuego: Mastermind numérico.
│   │   ├── sudoku_game.py  # Minijuego: Sudoku 9x9 interactivo.
│   │   └── word_game.py    # Minijuego: Descifrador tipo Wordle.
│   ├── generate_placeholders.py # Script auxiliar para generar imágenes base si faltan assets.
│   └── main.py             # Interfaz Gráfica (Flet) y bucle de la aplicación.
│
├── PROMPT_ASSETS.md        # Guía para generar las imágenes finales usando IAs externas.
└── requirements.txt        # Dependencias de Python (Flet, Pillow, etc.).
```

## Mecánicas del Juego (Core Loop)

El flujo de una partida se divide en las siguientes etapas:

1.  **Inicio del Caso:**
    El `CaseManager` selecciona al azar a un criminal, un botín robado y un arma. A continuación, traza una "ruta de escape" procedimental uniendo 4 ciudades españolas de forma secuencial. El jugador empieza en la ciudad 1 con **120 horas** de tiempo límite.
2.  **Investigación y Minijuegos:**
    En cada ciudad, el Teniente puede visitar hasta 3 lugares característicos. Al intentarlo (coste: 2 horas), el jugador debe superar un minijuego aleatorio para convencer a un testigo. El juego implementa un **escalado dinámico de dificultad**:
    *   *Nivel Fácil (Ciudad 1):* Caja fuerte de 4 números, Wordle de 5 letras, Sudoku con 30 casillas vacías.
    *   *Nivel Medio (Ciudad 2):* Caja fuerte de 5 números, Wordle de 6 letras, Sudoku con 45 casillas vacías.
    *   *Nivel Difícil (Ciudad 3+):* Caja fuerte de 6 números, Wordle de 7 letras, Sudoku con 60 casillas vacías.
3.  **Sistema de Pistas (Texto vs Visuales):**
    Si el minijuego se supera, el testigo entrega una pista. Esta puede ser:
    *   *Pista de Destino:* (Texto o **Fotografía real del monumento**) que insinúa a qué ciudad ha huido el ladrón.
    *   *Pista Física:* Información sobre los rasgos, aficiones, o vehículo del criminal para identificarlo.
4.  **Base de Datos SIGO (Orden de Arresto):**
    Con las pistas físicas, el jugador debe acceder al ordenador SIGO para filtrar a los 8 posibles sospechosos. Una vez tenga claro quién es, debe **Emitir una Orden de Arresto**.
5.  **Viaje:**
    El jugador elige viajar a otra ciudad entre 3 destinos aleatorios (donde siempre está el correcto si aún quedan pasos en la ruta). Viajar consume **8 horas**.
6.  **Resolución (Victoria o Derrota):**
    *   Si el jugador se queda sin tiempo (0 horas), el caso se pierde.
    *   Si el jugador llega a la última ciudad de la ruta, el testigo no da pistas de viaje, sino que señala el escondite. En ese momento, se valida la Orden de Arresto. Si es correcta, ¡el caso se gana! Si es para la persona equivocada o no hay orden, el criminal escapa amparado por su abogado.

## Estado Actual y Próximos Pasos (Pendientes)
El código base, el motor procedimental y la interfaz gráfica están terminados al 100%.

**Tareas Pendientes del Usuario (Arte Final):**
El juego actualmente funciona con "Placeholders" (cuadrados de color con texto). Para obtener el resultado final, el propietario del proyecto debe:
1.  Leer el archivo `PROMPT_ASSETS.md` para generar/buscar las imágenes definitivas.
2.  Sobreescribir los archivos `.jpg` de la carpeta `assets/images/cities/` con las fotos reales de los lugares.
3.  Sobreescribir los archivos `.png` de la carpeta `assets/images/suspects/` con los retratos generados por IA de los criminales.