# REVIEW

## Decisiones creativas
- Historia fija de 13 escenas tal como la pidió la persona; no se propusieron otras storylines. Duración 177 s (los tiempos sugeridos sumaban 195 s, se recortaron para no pasar de 3 min).
- Fondo oscuro pese a la lista BANNED de la skill: lo pidió la persona. Se evitó el "vacío": las imágenes y curvas reales llenan el cuadro, sin brillos ni degradados.
- Datos reales: firmas, longitudes de arco y río salen de assets/datos.json (curvas generadas desde el JSON). Ejemplo de la escena 7 calculado con la fórmula sobre los arcos reales (agua vs vegetación: 17 %, 7 %, promedio 12 %).
- Escena 8 usa las 197 muestras limpias del río (con ruido quedan en la escena 9/10).
- Sin sonido: se ignora la regla de música de la skill (aviso `film_silent` mantenido a propósito).

## Medido
- `check --json`: ok=true, 0 errores. Avisos: `film_silent` (intencional) y `duplicate_media_discovery_risk` (la misma imagen despues_c3 sale en dos filas de la tabla, intencional). Los `dead_stretch` se resolvieron marcando los bloques de lectura con `data-hold`: son pausas para leer.
- snapshot --review y fotogramas finales de cada escena revisados a mano; sin solapes.

## Solo mirado / no verificado
- No se renderizó el mp4. Sin audio que verificar.
- Los recuadros de la escena 4 (agua, vegetación) sobre cartagena4 son ilustrativos, no las zonas reales de muestreo; están rotulados así. Las 3 barras RGB de la escena 2 son ilustrativas (no un píxel real); las 380 barras sí son la firma real de vegetación.
- La curva en bandas 225–240 (escena 6) es un tramo real de la vegetación elegido por tener un salto claro.
- Los textos de cada bloque cumplen ~3 palabras/s en su mayoría; las escenas 4 y 12 son las más densas.

## Lo más débil
- Escena 7 (fórmula + ejemplo en texto): es la más "de texto"; con más tiempo se animaría el cálculo paso a paso.
- Al inicio de cada escena (0,3 s) el cuadro está casi vacío porque el contenido entra escalonado.

## Para la siguiente vuelta
- Generador de las escenas: no está en el proyecto (se escribió fuera de video/); editar los HTML de compositions/ directamente.
