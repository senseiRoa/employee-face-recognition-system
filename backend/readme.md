

### 📄 `README.md`

```markdown
# Backend de Reconocimiento Facial con FastAPI

Este proyecto utiliza **FastAPI** y **face_recognition** para construir una API de reconocimiento facial. Debido a que `dlib` (una dependencia clave) no se instala fácilmente en Windows mediante `pip`, este README incluye instrucciones detalladas para la instalación correcta en entornos Windows.

---

## 🛠 Requisitos Previos

- [Python 3.9](https://www.python.org/downloads/) (recomendado, pero versiones 3.7–3.11 también pueden funcionar)
- `pip` actualizado
- Git (opcional, para clonar el repositorio)
- Terminal (Git Bash, CMD o PowerShell)

> ⚠️ **Nota**: Este proyecto está probado en **Windows 10/11 (64 bits)**.

---

## 📦 Dependencias Principales

- `fastapi`: Framework web moderno para APIs.
- `uvicorn[standard]`: Servidor ASGI para ejecutar FastAPI.
- `dlib`: Biblioteca de aprendizaje automático (requiere instalación especial en Windows).
- `face_recognition`: API simple para reconocimiento facial.
- `numpy`: Cálculos numéricos.
- `SQLAlchemy>=2`: ORM para bases de datos.
- `pillow`: Manejo de imágenes.
- `python-multipart`: Para subir archivos (como imágenes) en FastAPI.

---

## 🧰 Instalación Paso a Paso



### 2. Crear un entorno virtual

```bash
python -m venv venv
```

### 3. Activar el entorno virtual

En **Git Bash**:
```bash
source venv/Scripts/activate
```

En **CMD o PowerShell**:
```cmd
venv\Scripts\activate
```

> ✅ Verifica que el entorno está activado (verás `(venv)` al inicio del prompt).

### 4. Actualizar pip

```bash
pip install --upgrade pip
```

### 5. Instalar `dlib` desde archivo `.whl` (paso crítico en Windows)

Debido a que `dlib` no se instala fácilmente en Windows con `pip install dlib`, usamos una versión precompilada.

#### Descarga el archivo `.whl` compatible

> 🔎 Asegúrate de que tu versión de Python sea la que tienes en tu equipo ejemplo **3.9** y sistema **64 bits**. Si usas otra versión, busca un `.whl` compatible.


- Descarga: [`dlib-xxxxxxxxxxxxxxx.whl`](https://github.com/z-mahmud22/Dlib_Windows_Python3.x/tree/main)
- Guarda el archivo en la raíz del proyecto (junto a `venv/`).


#### Instálalo manualmente

```bash
pip install dlib-versiondescargada.whl 
ejemplo
pip install dlib-19.22.99-cp39-cp39-win_amd64.whl
```

> ✅ Si ves "Successfully installed dlib", ¡todo va bien!

### 6. Instalar el resto de dependencias

```bash
pip install fastapi uvicorn[standard] face_recognition numpy SQLAlchemy>=2 pillow python-multipart
```

> ✅ `face_recognition` ya no intentará reinstalar `dlib`.

---

## ✅ Verificar la instalación

Ejecuta este comando para probar que todo funciona:

```bash
python -c "import face_recognition, numpy, sqlalchemy, PIL, fastapi; print('✅ Todas las dependencias se instalaron correctamente')"
```

---

## ▶️ Ejecutar el servidor FastAPI

Si tienes un archivo `main.py`, inícialo con:

```bash
uvicorn main:app --reload
```

> El servidor se ejecutará en `http://127.0.0.1:8081`

---

## 📁 Estructura del Proyecto (ejemplo)

```
backend/
│
├── venv/                  # Entorno virtual
├── dlib-19.22.99-cp39-cp39-win_amd64.whl  # Archivo dlib (opcional mantener)
├── main.py                # Archivo principal de FastAPI
├── requirements.txt       # (Opcional) lista de dependencias
└── README.md
```

---

## 📝 Notas Importantes

- ⚠️ **No uses `dlib-bin`**: no es un paquete válido.
- 💡 Si cambias de versión de Python, necesitarás un `.whl` diferente.
- 🔗 Más `.whl` para otras versiones: [https://www.lfd.uci.edu/~gohlke/pythonlibs/#dlib](https://www.lfd.uci.edu/~gohlke/pythonlibs/#dlib)
- 🐍 Recomendamos usar Python 3.9 en Windows para compatibilidad con `dlib`.

---

## 🧹 Limpiar (opcional)

Una vez instalado, puedes eliminar el archivo `.whl` si no lo necesitas conservar:

```bash
rm dlib-19.22.99-cp39-cp39-win_amd64.whl
```

---

## 🤝 Soporte

Si tienes problemas, abre un issue o contacta al equipo de desarrollo.

> ✨ ¡Listo! Tu backend de reconocimiento facial está listo para funcionar.
```

---

### ✅ ¿Qué incluye este `README.md`?

- Instrucciones claras para Windows.
- Enlace directo al `.whl` que ya probaste.
- Comandos para Git Bash.
- Verificación de instalación.
- Estructura limpia y profesional.

---
