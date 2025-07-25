# 🧪 Instrucciones para Probar el Filtro en el Admin

## 🎯 Pasos Específicos para Probar

### **1. Acceder al Admin**
1. Ve a: `http://127.0.0.1:8000/admin/`
2. Inicia sesión con tu cuenta de administrador

### **2. Navegar a Opciones de Respuesta**
1. Busca la sección **"Formularios de Inscripción"**
2. Haz clic en **"✅ Opciones de Respuesta"**
3. Haz clic en **"Añadir ✅ Opción de Respuesta"**

### **3. Abrir Herramientas de Desarrollador**
1. Presiona **F12** o **Ctrl+Shift+I**
2. Ve a la pestaña **"Console"**
3. Busca mensajes que empiecen con **"[ADMIN]"**

### **4. Verificar Inicialización**
Deberías ver logs como:
```
📄 [ADMIN] DOM Content Loaded
🔄 [ADMIN] Intento de inicialización #1
🚀 [ADMIN] Inicializando filtro de preguntas por curso
✅ [ADMIN] Elementos encontrados - Curso: 1 Pregunta: 1
📋 [ADMIN] Guardadas X opciones de pregunta
✅ [ADMIN] Filtro inicializado correctamente
```

### **5. Probar el Filtrado**
1. **Selecciona un curso** en el campo "🎓 Filtrar preguntas por curso"
2. **Observa la consola** - deberías ver:
   ```
   📝 [ADMIN] Cambio detectado en curso_filtro
   🔍 [ADMIN] Filtrando por curso: NombreCurso (ID: X)
   🎯 [ADMIN] Encontradas X preguntas para NombreCurso
   ```
3. **Verifica el dropdown** "❓ Pregunta" - debería mostrar solo preguntas del curso seleccionado

### **6. Verificar Indicador Visual**
- Debería aparecer un mensaje verde: **"✅ Filtro activo: Mostrando solo preguntas de 'NombreCurso'"**

## 🔍 Qué Buscar

### **✅ Señales de que Funciona:**
- Logs con **"[ADMIN]"** en la consola
- Campo de filtro con **fondo azul**
- **Dropdown de preguntas se actualiza** al cambiar curso
- **Indicador verde** aparece cuando seleccionas curso
- **Solo preguntas del curso seleccionado** en la lista

### **❌ Señales de Problemas:**
- **No hay logs** con "[ADMIN]" en la consola
- **Errores en rojo** en la consola
- **Dropdown no cambia** al seleccionar curso
- **Todas las preguntas** siguen apareciendo

## 🛠️ Troubleshooting

### **Si no ves logs [ADMIN]:**
1. **Refresca la página** (F5)
2. **Espera 3-5 segundos** después de cargar
3. **Verifica** que estés en la página correcta: `/admin/principal/opcionrespuesta/add/`

### **Si ves errores en la consola:**
1. **Copia el error completo**
2. **Verifica** que el archivo JavaScript existe: `static/admin/js/opcion_respuesta_filtro.js`
3. **Reinicia el servidor** Django: `python manage.py runserver`

### **Si el filtro no funciona:**
1. **Verifica en la consola** que aparezca:
   ```
   ✅ [ADMIN] Elementos encontrados - Curso: 1 Pregunta: 1
   ```
2. **Si no aparece**, el problema es que los elementos HTML no se encuentran
3. **Verifica** que los campos tengan los IDs correctos: `id_curso_filtro` y `id_pregunta`

## 📊 Datos de Prueba

### **Cursos Disponibles:**
- Ingles (1 pregunta)
- Aleman (1 pregunta)  
- Mate (2 preguntas)
- Quimica (1 pregunta)
- Fisica (1 pregunta)

### **Formato Esperado de Preguntas:**
```
"Texto de la pregunta... - Curso: NombreCurso (Formulario)"
```

**Ejemplos reales:**
- `"una - Curso: Ingles (economia)"`
- `"pruba - Curso: Aleman (ninguno)"`
- `"Estas de acuerdo con las reglas del grupo? - Curso: Mate (Matena)"`

## 🎯 Resultado Esperado

### **Flujo Completo:**
1. ✅ **Cargas la página** → Ves logs de inicialización
2. ✅ **Seleccionas "Mate"** → Solo aparecen 2 preguntas de Matemáticas
3. ✅ **Seleccionas "Ingles"** → Solo aparece 1 pregunta de Inglés
4. ✅ **No seleccionas curso** → Aparecen todas las preguntas (5 total)

### **Indicadores Visuales:**
- 🎯 **Campo de filtro** con fondo azul claro
- ✅ **Mensaje verde** cuando hay filtro activo
- 📝 **Lista actualizada** en tiempo real
- 🔍 **Logs detallados** en la consola

**¡Si ves todo esto, el filtro está funcionando perfectamente!**