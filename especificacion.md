# Especificación · Gabo el Garrobo

> Una buena especificación es la que otro asistente de IA podría construir sin haceros preguntas. Rellenadla en la semana 2 y usadla como prompt principal con vuestro asistente o agente. De ella sale la ficha del **hito de la semana 2**.

## 1. Problema y usuario

- **Quién tiene el problema:** Una junta directiva tiene problemas manejando, aplicando y diriginedo una asociacion deportiva
- **Cómo lo resuelve hoy:** Manejo de torneos a mano, resumen de actas, incumplimiento de acuerdos operativos
- **Qué le molesta de cómo lo hace hoy:** el tiempo que se toma buscando un acuerdo, el proceso lento y a mano que lleva organizar un torneo
- **Qué parte resuelve la IA:** facilidad para consultar informacion y cumplir acuerdo. Rapidez a la hora de organizar torneos

## 2. Qué hace el producto


1. Leer documentos de un google Drive.
2. Hacer consultas sobre esos documentos para toma de decisiones. 
3. Facilitar el trabajo logistico de organizacion de un torneo

## 3. Entradas y salidas

El usuario puede preguntar por la cantidad de categorias que se deben abrir de acuerdo a los formularios de inscripcion. La app devuelve el resumen de categorias

El usuario pide las categorias del Torneo ASTICA 2 y la app responde con la app solicitada que fue tomada de un archivo de excel 

## 4. La pieza de IA

- **Opción elegida:** Un RAG sobre documentos almacenados en Google Drive de la Asociacion Deportiva de Tiro con Arco de Alajuela
- **Por qué:** Es una forma de manejar documentos
- **Instrucciones para el modelo (system prompt):** Eres Gabo el Garrobo, la mascota oficial y asistente experto de IA de la Asociación de Tiro con Arco de Alajuela (ASTICA).
Responde de manera amigable, entusiasta y muy clara en español, usando ocasionalmente analogías divertidas de lagartijas o tiro con arco sin perder el profesionalismo

## 5. Flujo del usuario

1. El usuario entra y ve un chat
2. Escribe su pregunta
3. Recibe una respuesta de Gabo con la informacion solicitada

## 6. Restricciones

- Coste cero: capa gratuita de la API y despliegue gratuito (ruta A o B).
- La clave de la API va en secretos, nunca en el código.
- Lenguaje sencillo, para alguien sin conocimientos técnicos.
- [Otras restricciones de vuestro problema]

## 7. Criterios de aceptación

La app está bien si:

| Entrada | Resultado esperado |
|---|---|
| [caso normal] | [qué debe pasar] |
| [caso límite: texto vacío, pregunta fuera de tema…] | [qué debe pasar] |
| [error: se acaba la cuota] | [mensaje claro para el usuario] |

## 8. Fuera de alcance (por ahora)

- Poder leer la totalidad del Google Drive de la Aasociacion. Por el tema de tamaño de archivos, solo se pudo cargar una parte
- Mover la base de datos vectorial a un lugar correcto para su almacenamiento que no se GitHub
- Hacer una funcionalidad para actualizar la base de datos vectorial omitiendo los archivos ya indexados y tomar solo los nuevos
- Hacer una conexion a whatsApp para poder consultar desde ahi

## 9. Despliegue

- **Ruta:** https://gabo-astica.streamlit.app