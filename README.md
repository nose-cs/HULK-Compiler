# HULK-compiler

| **Nombre**              | **Grupo** | **Github**                                     |
|-------------------------|-----------|------------------------------------------------|
| Daniel Abad Fundora     | C411      | [@DanielAbadF](https://github.com/DanielAbadF) |
| Anabel Benítez González | C411      | [@anabel02](https://github.com/anabel02)       |
| Enzo Rojas D'Toste      | C411      | [@EnzoDtoste](https://github.com/EnzoDtoste)   |           

## Descripción

Este proyecto consiste en la implementación de un compilador para el lenguaje HULK en el lenguaje de programación
Python.

__HULK (Havana University Language for Kompilers)__ es un lenguaje de programación didáctico, seguro en cuanto a tipos,
orientado a objetos e incremental. Ofrece herencia simple, polimorfismo y encapsulamiento a nivel de
clase. Además, permite definir funciones globales fuera del ámbito de todas las clases y establecer una única expresión
global como punto de entrada al programa. HULK es un lenguaje de tipado estático con inferencia de tipos.
Para más información sobre el lenguaje puede consultar el siguiente [enlace](https://matcom.in/hulk/).

## ¿Cómo usar el compilador?

Para ejecutar el proyecto necesita tener instalada la versión 3.10 de python o superior. Además para instalar los
paquetes necesarios ejecute el siguiente comando:

```bash
pip install -r requirements.txt
```

Para compilar y ejecutar un fichero con extensión `.hulk` se debe ejecutar el siguiente comando:

```bash
python3 src/main.py <archivo.hulk>
```

El fichero de C generado por el compilador tendrá el mismo nombre que el fichero de
entrada y estará ubicado en la misma carpeta, pero tendrá la extensión `.c` por supuesto.