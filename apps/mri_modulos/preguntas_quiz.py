"""
apps/mri_modulos/preguntas_quiz.py
==================================
Banco de preguntas estructuradas para autoevaluación en Resonancia Magnética.
"""

CATEGORIAS = [
    "Todas",
    "Física Básica",
    "Secuencias de Pulsos",
    "Espacio K",
    "Procesamiento de Imagen",
    "Clínica Aplicada",
    "Seguridad",
]

PREGUNTAS = [
    ("¿Por qué se utiliza el núcleo de hidrógeno para la imagen clínica de RM?",
     ["Porque es el único núcleo con espín", "Por su abundancia en el cuerpo y su elevada razón giromagnética",
      "Porque no tiene momento magnético", "Porque es ferromagnético"], 1,
     "El ¹H combina la mayor razón giromagnética (42,58 MHz/T) con una abundancia enorme en agua y grasa biológica.", "Física Básica"),

    ("¿Cuál es la frecuencia de Larmor del protón a 3 T?",
     ["42,58 MHz", "63,9 MHz", "127,7 MHz", "298 MHz"], 2,
     "f₀ = γ̄ · B₀ = 42,58 MHz/T × 3 T ≈ 127,74 MHz.", "Física Básica"),

    ("A 1,5 T y 37 °C, el exceso de protones paralelos es del orden de:",
     ["50 %", "1 por cada mil", "5 por cada millón", "1 por cada mil millones"], 2,
     "ΔN/N ≈ γħB₀/(2kT) ≈ 4,9·10⁻⁶: unos 5 por millón a 1.5 T (se duplica a 3 T).", "Física Básica"),

    ("Tras un pulso de 90°, el tiempo T1 es el tiempo en el que Mz recupera el…",
     ["37 % de M₀", "50 % de M₀", "63 % de M₀", "100 % de M₀"], 2,
     "Mz(t) = M₀(1 − e^(−t/T1)). Para t = T1: 1 − e⁻¹ ≈ 0,632 (63,2%).", "Física Básica"),

    ("¿Qué relación temporal se cumple siempre entre tiempos de relajación?",
     ["T1 ≤ T2 ≤ T2*", "T2* ≤ T2 ≤ T1", "T2 ≤ T2* ≤ T1", "T1 = T2"], 1,
     "Las inhomogeneidades aceleran el desfase transversal (T2* ≤ T2) y la relajación longitudinal limita la coherencia (T2 ≤ T1).", "Física Básica"),

    ("Una imagen con TR corto y TE corto está ponderada en:",
     ["T1", "T2", "Densidad protónica", "T2*"], 0,
     "TR corto maximiza las diferencias de recuperación T1 entre tejidos; TE corto minimiza el decaimiento T2.", "Secuencias de Pulsos"),

    ("En una imagen potenciada en T2, el Líquido Cefalorraquídeo (LCR) aparece:",
     ["Negro (hipointenso)", "Gris intermedio", "Brillante (hiperintenso)", "Igual que el hueso"], 2,
     "El agua libre del LCR tiene un T2 muy largo (~2000 ms), por lo que retiene gran señal transversal en TE largos.", "Secuencias de Pulsos"),

    ("¿Qué función cumple el pulso de 180° en una secuencia Spin Echo?",
     ["Excita el corte inicial", "Reenfoca los desfases producidos por inhomogeneidades estáticas de campo", "Anula la grasa", "Codifica la frecuencia"], 1,
     "Invierte las fases relativas de las isocromatas para que vuelvan a coincidir exactamente en TE, cancelando T2'.", "Secuencias de Pulsos"),

    ("La secuencia FLAIR (Fluid Attenuated Inversion Recovery) se caracteriza por:",
     ["Suprimir la grasa con TI ≈ 160 ms", "Anular la señal del LCR con un TI largo (≈ 2000–2500 ms)", "No emitir pulso de radiofrecuencia", "Ponderación en T1 puro"], 1,
     "Usa un pulso de inversión de 180° con TI ajustado al cruce por cero de la magnetización longitudinal del LCR.", "Secuencias de Pulsos"),

    ("El grosor de corte (Δz) disminuye si…",
     ["Disminuye el gradiente de selección", "Aumenta el ancho de banda del pulso RF", "Aumenta la amplitud del gradiente de selección", "Aumenta el TR"], 2,
     "Δz = Δf / (γ̄ · Gz): un gradiente más potente separa más las frecuencias por unidad de longitud, afinando el corte.", "Espacio K"),

    ("El centro del espacio K (bajas frecuencias espaciales) contiene principalmente:",
     ["Los bordes y contornos finos", "El contraste y la señal de fondo", "El ruido térmico de alta frecuencia", "La orientación del imán"], 1,
     "Las bajas frecuencias determinan la intensidad global y el contraste tisular; las altas frecuencias codifican la resolución y los bordes.", "Espacio K"),

    ("Si se adquiere sólo 1 de cada 2 líneas de fase en el espacio K (R=2 sin compensar), se produce:",
     ["Artefacto de desplazamiento químico", "Aliasing o plegamiento en la dirección de fase", "Artefacto de Gibbs", "Quench"], 1,
     "Violar el criterio de muestreo de Nyquist (Δky = 1/FOV) reduce el campo de visión a la mitad, plegando la anatomía periférica.", "Espacio K"),

    ("En un ictus isquémico hiperagudo, el patrón característico en RM es:",
     ["DWI hipointensa y ADC alto", "DWI hiperintensa y ADC marcadamente bajo", "Sólo FLAIR hiperintenso", "Realce en anillo"], 1,
     "El edema citotóxico restringe la difusión del agua intracelular: señal brillante en difusión (DWI) y oscura en el mapa cuantitativo ADC.", "Clínica Aplicada"),

    ("El filtro digital más adecuado para eliminar ruido de tipo 'sal y pimienta' preservando bordes es:",
     ["Promedio lineal (caja)", "Gaussiano", "Filtro de mediana", "Laplaciano"], 2,
     "La mediana es un filtro de orden no lineal que reemplaza valores extremos impulsivos sin difuminar transiciones abruptas.", "Procesamiento de Imagen"),

    ("En la ecualización de histograma, la función de transformación acumulada es:",
     ["Una recta horizontal", "La función de distribución acumulada (CDF) normalizada", "Una función logarítmica pura", "El negativo directo"], 1,
     "Mapear las intensidades con la CDF genera una distribución de salida aproximadamente uniforme, maximizando el contraste global.", "Procesamiento de Imagen"),

    ("Promediar K adquisiciones idénticas (NEX = K) reduce la desviación del ruido en:",
     ["K", "√K", "K²", "No produce cambios"], 1,
     "El ruido incoherente suma sus varianzas (σ²/K), por lo que la desviación estándar disminuye con √K y la SNR aumenta proporcional a √K.", "Procesamiento de Imagen"),

    ("El principal peligro biofísico del campo magnético estático B₀ en la sala es:",
     ["Quemaduras térmicas por resonancia", "Efecto proyectil sobre objetos ferromagnéticos", "Estimulación nerviosa periférica", "Radiación ionizante"], 1,
     "El intenso gradiente espacial de atracción magnética convierte objetos de hierro/acero en proyectiles de alta velocidad.", "Seguridad"),

    ("El agente de contraste basado en Gadolinio (Gd³⁺) produce realce en T1 porque:",
     ["Atenúa los fotones X", "Es fuertemente paramagnético y acorta drásticamente el T1 de los protones vecinos", "Emite radiofrecuencia espontánea", "Duplica la densidad de agua"], 1,
     "Sus 7 electrones desapareados facilitan la transferencia de energía espín-red, acelerando la recuperación longitudinal T1.", "Clínica Aplicada"),

    ("¿Qué codifica el gradiente de fase Gy antes de la lectura?",
     ["Frecuencia basal única", "Un desfase dependiente de la posición en Y", "El grosor de corte", "El ángulo de inclinación"], 1,
     "Se aplica durante un lapso fijo con amplitud variable: los espines giran más o menos rápido según su coordenada Y, acumulando una fase característica.", "Espacio K"),

    ("En secuencias Gradient Echo (GRE), el desfasamiento transversal espontáneo sigue:",
     ["T1", "T2 puro", "T2*", "Densidad de espines"], 2,
     "Al no disponer de pulso refocalizador de 180°, la pérdida de coherencia transversal incluye las inhomogeneidades locales (1/T2* = 1/T2 + 1/T2').", "Secuencias de Pulsos"),

    ("¿Qué determina la máxima frecuencia espacial adquirida (k_max)?",
     ["El tamaño de vóxel y la resolución espacial", "El campo de visión FOV", "El tren de ecos ETL", "El tiempo TR"], 0,
     "La resolución espacial límite está dada por Δx = 1 / (2 · k_max). Cuanto más lejos se muestree el espacio K, mayor resolución de detalle se logra.", "Espacio K"),

    ("El artefacto de truncamiento (anillado de Gibbs) se debe a:",
     ["Corte brusco en los extremos del espacio K con matriz limitada", "Movimiento pulsátil arterial", "Presencia de titanio", "Fallo de la jaula de Faraday"], 0,
     "Es la manifestación del fenómeno de Gibbs al truncar la serie de Fourier en una transición abrupta de señal (p. ej. médula-LCR o cráneo-cerebro).", "Espacio K"),

    ("Las secuencias STIR (Short TI Inversion Recovery) anulan selectivamente:",
     ["El agua libre", "El LCR", "La grasa", "El flujo sanguíneo lento"], 2,
     "Emplean un TI corto (~150-180 ms a 1.5 T) que coincide con el paso por cero de la magnetización longitudinal de los lípidos.", "Secuencias de Pulsos"),

    ("La Jaula de Faraday de la sala de resonancia tiene como misión:",
     ["Contener el campo magnético B0", "Blindar contra interferencias externas de radiofrecuencia", "Enfriar el helio líquido", "Evitar el efecto proyectil"], 1,
     "Evita que señales externas (radio comercial, telecomunicaciones, motores) contaminen las señales de microvoltios detectadas por las antenas.", "Seguridad"),

    ("En una secuencia Echo Planar Imaging (EPI), el espacio K se adquiere:",
     ["Línea por línea en cada TR", "En un único disparo con tren veloz de gradientes oscilantes", "Mediante lectura continua radial", "Sin usar gradientes"], 1,
     "Modula velozmente el gradiente de lectura en zig-zag tras una única excitación, permitiendo capturar un corte completo en ~50-100 ms.", "Espacio K"),

    ("La Tasa de Absorción Específica (SAR, Specific Absorption Rate) mide:",
     ["Fuerza de atracción del proyectil", "Potencia de radiofrecuencia absorbida por unidad de masa (W/kg)", "Ruido acústico de gradientes", "Voltaje de bobinas"], 1,
     "Monitorea el depósito de energía de RF en el paciente para prevenir calentamiento tisular no deseado.", "Seguridad"),

    ("El Tiempo de Repetición (TR) es el intervalo entre:",
     ["El pulso de 90° y el centro del eco", "Dos pulsos sucesivos de excitación en el mismo corte", "El inicio del gradiente y el ADC", "La inversión y la lectura"], 1,
     "Controla el tiempo que se permite a la magnetización longitudinal Mz para recuperarse antes del siguiente ciclo.", "Secuencias de Pulsos"),

    ("¿Cuál de estos componentes tisulares tiene el T1 más corto a 1.5 T?",
     ["Líquido Cefalorraquídeo", "Grasa subcutánea", "Hueso cortical", "Músculo esquelético"], 1,
     "Las moléculas de grasa tienen frecuencias de rotación cercanas a la de Larmor, transfiriendo energía eficientemente al medio (~260 ms).", "Física Básica"),

    ("El artefacto de desplazamiento químico ocurre principalmente en el eje de:",
     ["Codificación de frecuencia (lectura)", "Codificación de fase", "Selección de corte", "Tiempo de adquisición"], 0,
     "La diferencia de resonancia entre agua y grasa (~3.5 ppm) altera su frecuencia de emisión, desplazando su asignación espacial en el eje de lectura.", "Física Básica"),

    ("Reducir a la mitad el ancho de banda del receptor (BW) por píxel:",
     ["Aumenta la SNR en un factor √2 pero incrementa el desplazamiento químico", "Disminuye la SNR a la mitad", "Acelera el escaneo al doble", "Elimina el aliasing"], 0,
     "SNR ∝ 1/√BW: al admitir menos ruido térmico mejora la calidad de señal, aunque la menor pendiente de muestreo acentúa el artefacto de desplazamiento químico.", "Procesamiento de Imagen"),
]

