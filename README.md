# 🧮 Tutor de Sistemas de Ecuaciones con Skills

Aplicación web interactiva y pedagógica construida con **Python** y **Streamlit** para la enseñanza y resolución de sistemas de ecuaciones lineales y álgebra matricial mediante el patrón de **Skills**.

---

## 🌟 Características Principales

1. **Pedagogía de Tutor (6 Secciones Estructuradas)**:
   Cada ejercicio se resuelve explicando el *porqué*, no solo entregando números:
   - **1. Planteamiento:** Ecuaciones reescritas, número de variables e incógnitas y forma matricial $A\mathbf{x} = \mathbf{b}$.
   - **2. Método y Justificación:** Explicación sencilla de por qué se usa Gauss-Jordan, Cramer, Inversa o Métodos Iterativos.
   - **3. Paso a Paso Detallado:** Operaciones elementales de fila con los números reales y matrices intermedias en LaTeX KaTeX-safe.
   - **4. Resultado e Interpretación:** Clasificación (solución única, infinitas soluciones, sistema incompatible, convergencia o invertibilidad).
   - **5. Verificación Formal:** Sustitución de la solución en cada ecuación original ($A\mathbf{x} = \mathbf{b}$) con comprobación exacta de fracciones o cálculo de residuo.
   - **6. Idea Clave y Próximo Ejercicio:** Síntesis didáctica y sugerencia para comparar con otros métodos.

2. **Digitalización con Visión Multimodal (Fotos / Cámara)**:
   - Sube una foto manuscrita o captura del ejercicio, o tómala con la cámara web.
   - **Confirmación interactiva:** La aplicación te muestra el sistema que entendió y te permite confirmarlo o editarlo antes de calcular.

3. **Arquitectura de Skills de Cálculo Exacto**:
   - `skills/resolver-sistema-lineal`: Algoritmo de Gauss-Jordan con `fractions.Fraction` (solo librería estándar).
   - `skills/regla-de-cramer`: Cálculo exacto por determinantes.
   - `skills/matriz-inversa`: Inversión de matrices por Gauss-Jordan $[A \mid I]$.
   - `skills/metodos-iterativos`: Algoritmos de Jacobi y Gauss-Seidel con control de convergencia y matriz diagonal dominante.

4. **Transparencia y Resiliencia**:
   - Modo IA con **Google Antigravity SDK / Gemini API** (Gemini 4 Argon, con Gemini 4 Carbon como alternativa) y fallback automático al **Motor Matemático Local Resiliente**.
   - La interfaz indica siempre de forma transparente qué motor generó la respuesta: `🤖 Respondió Gemini` o `⚙️ Respondió Motor Matemático Local`.
   - Si no hay clave, hay timeout o falla la conexión, la aplicación nunca se bloquea ni muestra alarmas intrusivas: resuelve inmediatamente en local.

---

## 🚀 Instalación y Ejecución en 3 Pasos

### En Windows:
1. **Descomprimir o clonar** este repositorio.
2. Hacer doble clic en `instalar.bat` (crea el `.venv` e instala las dependencias automáticamente).
3. Hacer doble clic en `ejecutar.bat` (abre la aplicación en tu navegador web).

### En Linux o macOS:
```bash
# 1. Clonar o descomprimir
cd Sistema-numerico

# 2. Instalar dependencias en el entorno virtual
chmod +x instalar.sh ejecutar.sh
./instalar.sh

# 3. Iniciar la aplicación
./ejecutar.sh
```

---

## 🔑 Configuración de la Clave API de Gemini (Opcional)

> **Nota:** La aplicación funciona al 100% sin clave API gracias a su motor algebraico local determinista.

Si deseas activar la comprensión multimodal avanzada y el agente con IA:
1. Copia `.env.example` a `.env`:
   ```bash
   cp .env.example .env
   ```
2. Abre `.env` e ingresa tu clave gratuita de [Google AI Studio](https://aistudio.google.com/apikey):
   ```env
   GEMINI_API_KEY=tu_clave_aqui
   ```
3. O si despliegas en **Streamlit Cloud**, ve a **App Settings $\rightarrow$ Secrets** y añade:
   ```toml
   GEMINI_API_KEY = "tu_clave_aqui"
   ```

---

## 🧪 Ejecución de Pruebas Automatizadas

La suite de pruebas unitarias no requiere internet ni clave API:

```bash
# Activar el entorno virtual
# En Windows:
.venv\Scripts\activate
# En Linux/macOS:
source .venv/bin/activate

# Ejecutar pruebas con pytest
python -m pytest tests
```

---

## 📂 Estructura del Proyecto

```
├── app.py                     # Punto de entrada de Streamlit
├── requirements.txt           # Dependencias fijadas y compatibles
├── .env.example               # Plantilla segura de configuración
├── .gitignore                 # Control estricto de secretos y caches
├── .gitattributes             # Normalización de saltos de línea LF/CRLF
├── instalar.bat / instalar.sh # Scripts de instalación en 1 clic
├── ejecutar.bat / ejecutar.sh # Scripts de ejecución en 1 clic
├── .streamlit/
│   └── config.toml            # Tema oscuro moderno
├── skills/                    # Las 4 skills estándar (scripts independientes)
│   ├── resolver-sistema-lineal/
│   ├── metodos-iterativos/
│   ├── regla-de-cramer/
│   └── matriz-inversa/
├── src/
│   └── tutor_ecuaciones/      # Módulos del sistema
│       ├── config.py          # Constantes y rutas relativas
│       ├── claves.py          # Búsqueda segura de credenciales (solo lectura)
│       ├── herramientas.py    # Wrapper seguro de skills y cálculo aislado
│       ├── agente.py          # Agente Antigravity SDK con políticas de seguridad
│       ├── explicacion.py     # Generador determinista de las 6 secciones del tutor
│       ├── vision.py          # Lector de imágenes con confirmación interactiva
│       ├── motor_local/       # Parser algebraico resiliente (sin IA)
│       └── interfaz/          # Componentes visuales desacoplados de Streamlit
├── tests/                     # 59 pruebas unitarias automatizadas
├── ejemplos/                  # Casos de prueba en formato JSON
└── docs/                      # Documentación y fases del proyecto
```

---

## 🛡️ Seguridad y Buenas Prácticas
- Ninguna clave API se versiona ni se escribe en disco automáticamente.
- El agente opera bajo la política de seguridad estricta `deny("*")`, permitiendo únicamente la lectura de archivos de skills (`view_file`) y las 4 herramientas matemáticas, sin acceso a la terminal ni ejecución de comandos.
