# CrashBot <img src="../favicon.ico" alt="Console Window" width="28">


<img src="./images/main_console.png" alt="Console Window" width="800">


> **DESCARGO DE RESPONSABILIDAD IMPORTANTE - PROPÓSITO EDUCATIVO ÚNICAMENTE**
>
> Este proyecto fue creado **exclusivamente con fines educativos y de aprendizaje**. Está destinado a demostrar conceptos de programación, arquitectura de software, automatización de navegadores y desarrollo de interfaces gráficas con Python.
>
> **Este software NO está destinado para apuestas reales o uso comercial.** El autor no fomenta, promueve ni respalda las apuestas en ninguna forma. El autor no asume ninguna responsabilidad por cualquier uso de este software, ya sea legal o ilegal, y declina expresamente cualquier responsabilidad por pérdidas financieras, consecuencias legales o cualquier otro daño que surja de su uso.
>
> Este proyecto no tiene afiliación con Aviator, Spribe, ni con ninguna casa de apuestas o plataforma de casino. Todas las marcas comerciales y nombres de marcas mencionados pertenecen a sus respectivos propietarios.
>
> **Al usar este software, usted reconoce que lo hace bajo su propio riesgo y acepta la responsabilidad total de cualquier consecuencia.**

---

CrashBot es una aplicación de escritorio diseñada para asistir con apuestas automatizadas en juegos de casino tipo "crash". Estos juegos presentan un multiplicador que comienza en 1x y aumenta hasta que aleatoriamente "explota". Los jugadores deben retirarse antes de la explosión para ganar.

## Características Principales

- **Predicciones Impulsadas por IA**: Modelos de ML evaluados en tiempo real con seguimiento de precisión y filtrado automático de modelos de bajo rendimiento
- **Dos Modos de Juego**: Modo IA (predicciones ML + criterio Kelly adaptativo) y modo Estrategia (reglas de apuestas determinísticas)
- **Apuestas Automatizadas**: Configure estrategias de apuestas y deje que el bot coloque apuestas automáticamente
- **Soporte para Múltiples Casas de Apuestas**: Funciona con varias plataformas de apuestas en línea (ver [Casas de Apuestas Soportadas](#casas-de-apuestas-soportadas))
- **Integración con Backend**: Conexión REST API y WebSocket para autenticación, predicciones y recopilación de datos
- **Sistema de Suscripción**: Planes con y sin características de IA, administrados a través de autenticación de usuario
- **Gestión de Riesgos**: Mecanismos integrados de stop loss y take profit
- **Estrategias de Recuperación**: Ajustes inteligentes de apuestas después de pérdidas
- **Monitoreo en Tiempo Real**: Seguimiento de balance en vivo, historial de apuestas y gráficos de tendencias
- **Estrategias Personalizadas**: Cree, configure y cargue bots de apuestas personalizados encriptados
- **Recopilación de Datos**: Historial de multiplicadores y datos de apuestas enviados al backend para análisis y entrenamiento de modelos
- **Soporte Multi-idioma**: Disponible en inglés y español

## Cómo Funcionan los Juegos Crash

1. Cada ronda comienza con un multiplicador en 1.00x
2. El multiplicador aumenta continuamente
3. En un punto aleatorio, el juego "explota"
4. Si retiras antes de la explosión, ganas (apuesta x multiplicador)
5. Si el juego explota antes de que retires, pierdes tu apuesta

---

## Juegos Soportados

| Juego | Descripción |
|-------|-------------|
| **Aviator** | Popular juego crash de Spribe con temática de avión |
| **To The Moon** | Juego crash con temática de cohete y mecánicas similares |

## Casas de Apuestas Soportadas

| Casa de Apuestas | Aviator | To The Moon |
|------------------|:-------:|:-----------:|
| Demo | Sí | - |
| BetPlay | Sí | - |
| OneWin | Sí | Sí |
| Rivalo | Sí | - |
| 1xBet | Sí | - |
| ECUABET | Sí | - |
| Demo To The Moon | - | Sí |

> **Nota:** Las casas de apuestas disponibles dependen de tu plan de suscripción y región.

---

## Modos de Juego

CrashBot soporta dos modos de juego distintos:

| Modo | Descripción |
|------|-------------|
| **Modo IA** | Utiliza predicciones de modelos ML para determinar cuándo apostar y a qué multiplicador. Los modelos son evaluados en tiempo real — los modelos de bajo rendimiento son filtrados automáticamente. El tamaño de apuesta utiliza un criterio Kelly adaptativo. Requiere un plan de suscripción con IA habilitada. |
| **Modo Estrategia** | Apuestas puras basadas en estrategia usando reglas determinísticas configuradas en los parámetros del bot. Sin predicciones de IA — se basa en multiplicadores fijos, condiciones y lógica de recuperación. Disponible en todos los planes. |

Para más detalles sobre el sistema de predicción y evaluación de modelos, consulte la [Documentación Técnica](./technical_documentation.md).

---

## Autenticación y Suscripción

CrashBot se conecta a un servicio backend para autenticación y gestión de características:

1. **Inicio de Sesión**: Los usuarios se autentican con nombre de usuario y contraseña a través de la ventana de inicio de sesión
2. **Planes de Suscripción**: El acceso se gestiona a través de planes que pueden incluir características de IA o modo solo estrategia
3. **Control de Sesión**: El backend valida la versión de la aplicación y previene sesiones duplicadas
4. **Sincronización de Datos**: El historial de multiplicadores y datos de apuestas se envían al backend para análisis y mejora de modelos

> **Nota:** Se requiere una cuenta válida y suscripción activa para usar la aplicación.

---

## Resumen de Arquitectura

```
GUI (PyQt6) ←→ SocketIO ←→ Servidor WebSocket ←→ Lógica de Juego ←→ Bot ←→ Scraper Playwright
                                                      ↑                           ↑
                                               API de Predicción          Sitio Web Casa de Apuestas
                                                      ↑
                                              Backend REST API
                                                      ↑
                                     Auth / Suscripción / Recopilación de Datos
```

Para diagramas detallados de arquitectura, jerarquías de clases y patrones de diseño, consulte [Documentación de Arquitectura](./architecture.md) y [Documentación Técnica](./technical_documentation.md).

---

## Documentación

Para más información detallada sobre el proyecto, consulte:

| Documento | Descripción |
|-----------|-------------|
| [Arquitectura](./architecture.md) | Diagramas de componentes, flujos de datos, jerarquías de clases y patrones de diseño |
| [Documentación Técnica](./technical_documentation.md) | Referencia técnica detallada, integraciones API y guía de desarrollo |
| [Manual de Usuario (Español)](./manual_es.md) | Guía completa del usuario en español |

---

## Requisitos del Sistema

### Requisitos Mínimos

| Componente | Requisito |
|-----------|-----------|
| Sistema Operativo | Windows 10+, macOS 10.14+, o Linux (Ubuntu 18.04+) |
| Python | Versión 3.10 o superior |
| RAM | 4 GB mínimo |
| Almacenamiento | 500 MB de espacio libre |
| Internet | Conexión de banda ancha estable |
| Pantalla | Resolución mínima de 1280x720 |

### Dependencias de Software

- Python 3.10+
- Navegador Chromium (instalado automáticamente vía Playwright)
- Librerías clave: PyQt6, Playwright, requests, cryptography, websocket-client, python-socketio
- Cuenta válida en plataformas de casas de apuestas soportadas
- Suscripción activa de CrashBot

---

## Guía de Instalación

### Paso 1: Instalar Python

Si no tiene Python instalado:

1. Visite [python.org](https://www.python.org/downloads/)
2. Descargue Python 3.10 o más reciente
3. Ejecute el instalador
4. **Importante**: Marque "Add Python to PATH" durante la instalación

### Paso 2: Descargar CrashBot

Descargue los archivos de la aplicación CrashBot y extráigalos en la ubicación deseada.

### Paso 3: Instalar Dependencias

Abra una terminal o símbolo del sistema en el directorio de CrashBot:

```bash
# Crear un entorno virtual (recomendado)
python -m venv .venv

# Activar el entorno virtual
# En Windows:
.venv\Scripts\activate
# En macOS/Linux:
source .venv/bin/activate

# Instalar paquetes requeridos
pip install -r requirements.txt
```

### Paso 4: Instalar Navegador

Instale el navegador Chromium de Playwright:

```bash
playwright install chromium
```

### Paso 5: Verificar Instalación

Ejecute CrashBot para verificar que todo esté instalado correctamente:

```bash
python crashbot.py
```

La ventana de la aplicación debería aparecer con un tema oscuro.

---

## Crear un Ejecutable

Puede crear un ejecutable independiente para distribuir CrashBot sin requerir que los usuarios instalen Python.

### Requisitos Previos

Instale las herramientas requeridas:

```bash
pip install -r requirements_installer.txt
```

Esto instala:
- **PyInstaller**: Empaqueta aplicaciones Python en ejecutables
- **PyArmor**: Ofusca el código para protección

### Proceso de Compilación

Ejecute el siguiente comando:

```bash
make generate-installer
# o: python create_executable.py
```

### Opciones de Compilación

Durante el proceso de compilación, se le solicitará elegir el formato de salida:

| Opción | Descripción | Plataforma |
|--------|-------------|------------|
| **Un archivo** | Archivo ejecutable único con todas las dependencias empaquetadas | Windows, Linux |
| **Múltiples archivos** | Directorio con ejecutable y archivos de soporte | Todas las plataformas |

> **Nota:** La opción de un archivo no está disponible en macOS debido a limitaciones de la plataforma.

### Salida

Después de completar la compilación, encontrará la salida en:

| Tipo de Compilación | Ubicación |
|---------------------|-----------|
| Un archivo | `dist/crashbot.exe` (Windows) o `dist/crashbot` (Linux) |
| Múltiples archivos | Directorio `dist/crashbot/` |

El proceso de compilación incluye automáticamente:
- Archivos de localización (`locales/`)
- Bots personalizados (`custom_bots/`)
- Plantilla de configuración (`conf.ini`)
- Ícono de la aplicación

### Distribución

Para compilaciones de un archivo, distribuya:
- El archivo ejecutable
- Carpeta `locales/`
- Carpeta `custom_bots/`
- `conf.ini`

Para compilaciones de múltiples archivos, distribuya todo el directorio `dist/crashbot/`.

---

## Aplicación CrashBot

### Inicio de Sesión

Cuando la aplicación inicia, se muestra una ventana de inicio de sesión. Ingrese su nombre de usuario y contraseña para autenticarse con el servicio backend. Al iniciar sesión exitosamente, se carga su plan de suscripción y la aplicación principal se vuelve disponible.

---

### Configuración de Casa de Apuestas y Bot

<img src="./images/parameters.png" alt="Main Console" width="400">

En esta pantalla debe configurar:

| Elemento | Descripción |
|----------|-------------|
| **Juego** | Juego a jugar |
| **Casa de apuestas** | Solo aparecerán las casas habilitadas en su servicio |
| **Tipo de bot** | Bots del servicio y sus bots personalizados |
| **Usar credenciales guardadas** | Inicio de sesión automático con credenciales almacenadas |
| **Iniciar** | Botón para inicializar el juego y el bot |

> **Advertencia:** No se recomienda usar el inicio de sesión automático ya que las casas de apuestas podrían detectar que está usando un bot.

---

### Cambiar Idioma

**Menú:** Configuración → Idioma

Cuando cambia el idioma, necesita reiniciar la aplicación para que los cambios surtan efecto.

---

### Credenciales

**Menú:** Configuración → Credenciales

Pantalla para guardar sus credenciales de casas de apuestas.

#### Pestaña: Credenciales Guardadas

<img src="./images/credentials_0.png" alt="Credentials 0" width="400">

| Elemento | Descripción |
|----------|-------------|
| Lista de credenciales | Credenciales almacenadas |
| Botón Eliminar | Elimina la credencial seleccionada |
| Botón Eliminar todas | Elimina todas las credenciales |
| Botón Cerrar | Cierra la pantalla |

#### Pestaña: Agregar Credencial

<img src="./images/credentials_1.png" alt="Credentials 1" width="400">

| Campo | Descripción |
|-------|-------------|
| Casa de apuestas | Seleccione la casa de apuestas |
| Usuario | Su nombre de usuario |
| Contraseña | Su contraseña |
| Botón Guardar | Guarda la credencial |

> **Nota:** No se recomienda el inicio de sesión automático para evitar que la casa de apuestas reconozca comportamientos repetitivos.

---

### Parámetros

**Menú:** Configuración → Parámetros

<img src="./images/configuration.png" alt="Settings Window" width="600">

| Parámetro | Descripción |
|-----------|-------------|
| **Número de rondas en el gráfico** | Número máximo de rondas que mostrará el gráfico. Se recomienda configurar antes de iniciar el juego |
| **Multiplicadores a mostrar** | Multiplicadores a mostrar en el panel de la pantalla principal. Formato: valores separados por comas sin espacios (ej.: `2,5,10,20`) |
| **Tamaño para determinar juego alcista** | Tamaño de muestra de multiplicadores para determinar tendencia alcista |
| **Valor para determinar juego alcista** | Sensibilidad para detectar tendencia alcista (baja, media, alta). Valor más alto = pendiente más alta requerida |

---

### Configurar Bots

**Menú:** Configuración → Bots

Pantalla para crear y modificar bots personalizados.

<img src="./images/bots_config.png" alt="Bot Configuration Window" width="600">

| Elemento | Descripción |
|----------|-------------|
| **Bot Seleccionado** | Selector para el bot a modificar |
| **Botón Nuevo** | Crea un nuevo bot con parámetros por defecto |
| **Botón Clonar** | Clona el bot seleccionado |
| **Botón Guardar** | Guarda el bot nuevo o modificado |
| **Configuraciones del bot** | Sección para configurar parámetros |
| **Sección de Errores** | Muestra errores al intentar guardar |

---

### Pantalla Principal

Pantalla donde el usuario interactúa con el bot durante el juego.

<img src="./images/main_console_0.png" alt="Console Window" width="650">

#### Panel Superior

| Elemento | Descripción |
|----------|-------------|
| **Casa de apuestas** | Nombre de la casa actual |
| **Bot seleccionado** | Bot en uso |
| **Balance** | Balance actual (se actualiza con cada apuesta) |
| **Ganancia** | Ganancia sobre el monto inicial de la sesión |
| **Porcentaje** | Porcentaje de ganancia |

#### Controles de Apuestas

| Control | Descripción |
|---------|-------------|
| **Monto a apostar** | Monto a apostar por ronda |
| **Seleccionar apuesta** | Envía el monto al bot (se reflejará en los logs) |
| **Iniciar/Detener Bot** | Inicia o detiene las apuestas automáticas |
| **Habilitar/Deshabilitar retiro automático** | Controla el retiro automático |

#### Gráfico de Tendencias

Muestra la tendencia de multiplicadores (se actualiza automáticamente después de cada ronda).

**Colores de las barras:**

| Color | Significado |
|-------|-------------|
| Azul | Multiplicador menor a 2x |
| Púrpura | Multiplicador entre 2x y 10x |
| Rojo | Multiplicador mayor a 10x |

> **Consejo:** Pase el mouse sobre las barras para ver el multiplicador exacto de cada ronda.

#### Panel de Multiplicadores

Muestra cuántas rondas atrás apareció cada multiplicador.

**Formato:** `[Multiplicador] → [Rondas]`

**Ejemplo:** `10 → 3` significa que un multiplicador de 10x o mayor apareció hace 3 rondas.

> **Nota:** Si aparece `> 25`, significa que no hay registro reciente de ese multiplicador.

#### Logs

Mensajes del bot para seguimiento de la ejecución.

---

## Bots

Hay dos tipos de bots:

- **Bots oficiales:** Bots por defecto, disponibles para todos los usuarios
- **Bots personalizados:** Creados por usuarios con comportamientos configurables

> **Recomendación:** Antes de jugar con dinero real, verifique el comportamiento de los bots. Puede usar la casa de apuestas "demo" para simular un juego real.

---

### Comportamiento General

Cuando selecciona un monto a apostar, se divide en dos apuestas:

| Apuesta | Proporción | Descripción |
|---------|------------|-------------|
| **Principal (segura)** | 2/3 del monto | Multiplicador más bajo |
| **Secundaria (por valor)** | 1/3 del monto | Multiplicador más alto |

**Ejemplo:** Si apuesta $3 USD → Apuesta principal: $2, Apuesta secundaria: $1

#### Recuperación de Pérdidas

Cuando se pierde una apuesta:
1. El bot coloca **una sola apuesta** para recuperar el dinero perdido
2. Una vez recuperado, regresa a hacer las dos apuestas normales

---

### Bots Personalizados

**Ubicación:** `custom_bots/` dentro de la carpeta CrashBot

Para crear bots personalizados use la pantalla de **Configuración de Bot**.

<img src="./images/bots_config.png" alt="Bot Configuration Window" width="600">

---

### Parámetros del Bot

#### Parámetros Generales

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `name` | string | Nombre del bot |
| `description` | string | Descripción del bot |
| `bot_type` | string | Tipo de bot: `aggressive`, `tight` o `loose` |
| `number_of_min_bets_allowed_in_bank` | int | Número mínimo de apuestas permitidas en balance para usar el bot |
| `only_bullish_games` | bool | Si el bot solo juega cuando el juego es alcista |
| `make_second_bet` | bool | Si hace dos apuestas (segura y valor) o solo una |

#### Parámetros de Multiplicadores

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `min_multiplier_to_bet` | decimal | Multiplicador de apuesta principal |
| `min_multiplier_to_recover_looses` | decimal | Multiplicador para recuperar pérdidas |
| `max_second_multiplier` | decimal | Multiplicador máximo para la segunda apuesta (0 = usar predicción) |

#### Parámetros de Riesgo

| Parámetro | Tipo | Rango | Descripción |
|-----------|------|-------|-------------|
| `risk_factor` | decimal | 0-1 | Factor para aumentar apuestas según la situación |
| `max_recovery_percentage_on_max_bet` | decimal | 0-1 | Porcentaje máximo de apuesta máxima para recuperación |
| `stop_loss_percentage` | decimal | - | % de pérdida sobre balance para detener el bot |
| `take_profit_percentaje` | decimal | - | % de ganancia sobre balance para detener el bot |

#### Parámetros de IA

> **Nota:** Estos parámetros solo aplican a bots que usan inteligencia artificial. Para bots de estrategia, estos valores son ignorados.

| Parámetro | Tipo | Rango | Descripción |
|-----------|------|-------|-------------|
| `min_probability_to_bet` | decimal | 0-1 | Probabilidad mínima de predicción para apostar |
| `min_category_percentage_to_bet` | decimal | 0-1 | Probabilidad mínima de categoría para apostar |
| `min_average_model_prediction` | decimal | 0-1 | Promedio mínimo de predicciones correctas del modelo |

---

### Condiciones

Las condiciones definen cuándo el bot debe ejecutar ciertas acciones.

#### Tipos de Condiciones (`condition_on`)

| Condición | Descripción | `condition_on_value` | `condition_on_value_2` |
|-----------|-------------|----------------------|------------------------|
| `every_win` | Cada vez que gane | (ignorado) | - |
| `every_loss` | Cada vez que pierda | (ignorado) | - |
| `streak_wins` | Racha de X victorias | Número de victorias (int) | - |
| `streak_losses` | Racha de X pérdidas | Número de pérdidas (int) | - |
| `profit_greater_than` | Ganancia mayor a X% | Porcentaje (decimal) | - |
| `profit_less_than` | Ganancia menor a X% | Porcentaje (decimal) | - |
| `streak_n_multiplier_less_than` | Racha de N multiplicadores < X | N (cantidad) | X (multiplicador) |
| `streak_n_multiplier_greater_than` | Racha de N multiplicadores > X | N (cantidad) | X (multiplicador) |

---

### Acciones

Las acciones definen qué hace el bot cuando se cumple una condición.

#### Tipos de Acciones (`condition_action`)

| Acción | Descripción | `action_value` |
|--------|-------------|----------------|
| `increase_bet_amount` | Aumenta la apuesta en X% | Porcentaje |
| `decrease_bet_amount` | Disminuye la apuesta en X% | Porcentaje |
| `reset_bet_amount` | Reinicia la apuesta al valor original | 0 (ignorado) |
| `update_multiplier` | Actualiza el multiplicador | Nuevo multiplicador |
| `reset_multiplier` | Reinicia el multiplicador al original | 0 (ignorado) |
| `ignore_model` | Ignora filtros del modelo de IA | 0=no ignorar, 1=ignorar |
| `make_bet` | Controla si apuesta en la próxima ronda | 0=no apostar, 1=apostar |
| `forget_losses` | Olvida las pérdidas actuales | 0=no, 1=sí |
| `recovery_losses` | Controla la recuperación de pérdidas | 0=no recuperar, 1=recuperar |

---

### Ejemplos de Configuración

#### Ejemplo 1: Cambiar multiplicador en pérdida

**Objetivo:** Cada vez que se pierda una apuesta, actualizar el multiplicador a 2.3x y reiniciar el monto.

<img src="./images/condition_1.png" alt="example 1" width="600">

#### Ejemplo 2: Restaurar configuración en victoria

**Objetivo:** Al ganar, volver a la configuración inicial.

<img src="./images/condition_2.png" alt="example 2" width="600">

#### Ejemplo 3: Reaccionar a racha de multiplicadores bajos

**Objetivo:** Después de 25 multiplicadores consecutivos menores a 5x, aumentar el multiplicador a 6x.

<img src="./images/condition_3.png" alt="example 3" width="600">

**Explicación:**
- `condition_on_value`: 25 (número de multiplicadores en racha)
- `condition_on_value_2`: 5 (valor del multiplicador para la condición)
- `action_value`: 6 (nuevo multiplicador)

---

## Glosario

| Término | Definición |
|---------|------------|
| **Banco** | Balance total del jugador |
| **Ganancia** | Ganancia/pérdida acumulada en la sesión |
| **Alcista** | Tendencia de multiplicadores altos |
| **Segura** | Apuesta principal con multiplicador bajo |
| **Por valor** | Apuesta secundaria con multiplicador alto |
| **Stop loss** | Límite de pérdida para detener el bot |
| **Take profit** | Límite de ganancia para detener el bot |

## Solución de Problemas

### Problemas Comunes

#### La Aplicación No Inicia

**Síntomas**: No aparece ventana, mensajes de error

**Soluciones**:
1. Verifique que Python 3.10+ esté instalado: `python --version`
2. Compruebe que todas las dependencias estén instaladas: `pip install -r requirements.txt`
3. Verifique que `config/app_data.json` exista y sea JSON válido
4. Revise la consola para mensajes de error

#### El Navegador No Se Abre

**Síntomas**: El bot inicia pero no aparece ventana del navegador

**Soluciones**:
1. Reinstale el navegador Playwright: `playwright install chromium`
2. Revise los recursos del sistema (RAM, CPU)
3. Verifique la conexión a internet
4. Intente cerrar otras instancias del navegador

#### Problemas de Conexión

**Síntomas**: No puede conectarse a la casa de apuestas

**Soluciones**:
1. Verifique que la URL de la casa de apuestas sea correcta en `config/app_data.json`
2. Revise su conexión a internet
3. Verifique que el sitio web de la casa de apuestas sea accesible
4. Compruebe si se requiere VPN para su región

#### El Bot No Coloca Apuestas

**Síntomas**: El bot está corriendo pero no apuesta

**Posibles Causas**:
1. **Stop loss alcanzado**: Verifique si alcanzó su límite de stop loss
2. **Take profit alcanzado**: Verifique si alcanzó su objetivo de ganancia
3. **Modo solo alcista**: El mercado puede estar "bajista"
4. **Monto de apuesta no configurado**: Asegúrese de configurar el monto máximo
5. **Condición activada**: Una condición del bot puede haber configurado la apuesta en 0

**Soluciones**:
1. Revise los mensajes de log para razones específicas
2. Verifique que el monto de apuesta esté configurado
3. Revise la configuración y condiciones del bot
4. Reinicie la sesión si es necesario

#### Visualización Incorrecta del Balance

**Síntomas**: El balance mostrado no coincide con la casa de apuestas

**Soluciones**:
1. La aplicación lee el balance de la interfaz del juego
2. Espere a que el balance se sincronice después de que las apuestas se liquiden
3. Actualice la página si el problema persiste

### Mensajes de Error

| Error | Significado | Solución |
|-------|-------------|----------|
| "Config file not found" | Falta app_data.json | Crear config/app_data.json |
| "No bot data found" | Bot no cargado | Revisar directorio custom_bots |
| "Currency not found" | Desajuste de moneda | Revisar límites en app_data.json |
| "Stop loss reached" | Límite de pérdida alcanzado | Reiniciar sesión o ajustar límite |

### Obtener Información de Depuración

Habilite el modo de depuración para logs más detallados:

1. Abra `conf.ini`
2. Agregue: `DEBUG=1`
3. Reinicie la aplicación
4. Revise los logs para información detallada

---

## Preguntas Frecuentes

### Preguntas Generales

**P: ¿CrashBot garantiza ganancias de dinero?**

R: No. Los juegos crash son juegos de azar con ventaja de la casa. CrashBot es una herramienta para automatizar estrategias de apuestas, pero no puede predecir ni garantizar resultados. Siempre apueste responsablemente.

**P: ¿Qué casa de apuestas debo usar?**

R: CrashBot soporta múltiples casas de apuestas. Elija una que sea legal en su jurisdicción y ofrezca los juegos que desea jugar.

**P: ¿Puedo usar CrashBot en múltiples cuentas?**

R: CrashBot ejecuta una instancia a la vez. Ejecutar múltiples instancias puede funcionar pero no está oficialmente soportado y puede violar los términos de servicio de las casas de apuestas.

### Preguntas Técnicas

**P: ¿Por qué el navegador se abre en modo no headless?**

R: El navegador necesita ser visible para interactuar correctamente con la interfaz del juego. Algunos juegos usan medidas anti-bot que los navegadores headless no pueden superar.

**P: ¿Puedo minimizar la ventana del navegador?**

R: Puede minimizarla, pero algunos elementos del juego pueden no actualizarse correctamente. Se recomienda mantener la ventana visible.

**P: ¿Cuánta RAM usa CrashBot?**

R: CrashBot mismo usa RAM mínima (~100-200MB), pero el navegador Chromium agrega uso significativo (~500MB-1GB dependiendo del juego).

### Preguntas sobre Bots

**P: ¿Cuál es la mejor configuración de bot?**

R: No hay una configuración universalmente "mejor". Comience con configuraciones conservadoras (factor de riesgo bajo, stop loss razonable) y ajuste según su experiencia y tolerancia al riesgo.

**P: ¿Por qué el bot a veces omite rondas?**

R: El bot puede omitir rondas debido a:
- Condiciones del mercado (si "solo alcista" está habilitado)
- Cálculos de modo de recuperación
- Límites de stop loss/take profit
- Condiciones del bot activadas que omiten apuestas

**P: ¿Cómo creo mi propio bot?**

R: Cree un archivo de configuración JSON con los parámetros deseados, luego conviértalo a formato encriptado usando las herramientas proporcionadas. Vea la sección de Bots Personalizados para detalles.

### Preguntas de Seguridad

**P: ¿Mis credenciales están seguras?**

R: Las credenciales se almacenan localmente en su máquina y no se transmiten a ningún lugar. Sin embargo, siempre use contraseñas únicas y tenga cuidado sobre dónde ejecuta la aplicación.

**P: ¿Puede la casa de apuestas detectar que estoy usando un bot?**

R: Posiblemente. Las herramientas de apuestas automatizadas pueden violar los términos de servicio de las casas de apuestas. Use bajo su propio riesgo y esté consciente de posibles restricciones de cuenta.

---

## Descargo de Responsabilidad

### Aviso Legal

CrashBot se proporciona "tal cual" sin garantía de ningún tipo, expresa o implícita. El autor no es responsable de ninguna pérdida financiera, consecuencia legal o daños que surjan del uso de este software.

### Términos de Uso

Al usar CrashBot, usted reconoce que:

1. Este software es solo para **fines educativos**
2. Acepta la responsabilidad total por cualquier uso de este software
3. No responsabilizará al autor por ninguna pérdida o problema legal
4. Las apuestas automatizadas pueden violar los términos de servicio de las casas de apuestas
5. Entiende que las apuestas involucran riesgo sin resultados garantizados

### Reconocimiento de Riesgo

- El rendimiento pasado no garantiza resultados futuros
- Los mecanismos de stop loss no pueden prevenir todas las pérdidas
- Los errores de software pueden causar comportamiento inesperado
- Los problemas de red pueden afectar la ejecución de apuestas

### Advertencia sobre Juegos de Azar

- Las apuestas pueden ser adictivas. Juegue responsablemente.
- Solo apueste con dinero que pueda permitirse perder.
- Si tiene un problema con el juego, busque ayuda de una organización profesional.
- Las apuestas pueden ser ilegales en su jurisdicción. Conozca sus leyes locales.

---
