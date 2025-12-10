# 📐 Guía de Visualización de Diagramas de Dominio - CacaoScan

Este documento explica cómo visualizar e interpretar los diagramas de dominio generados.

---

## 📋 Diagramas Disponibles

### 1. Diagrama de Entidad-Relación Completo
**Archivo**: `DIAGRAMA_DOMINIO_CACAOSCAN.mmd`

Este diagrama muestra:
- Todas las entidades del dominio
- Atributos principales de cada entidad
- Relaciones con cardinalidades
- Claves primarias (PK) y foráneas (FK)

**Cómo visualizar:**
- Usa cualquier visualizador de Mermaid (GitHub, GitLab, Mermaid Live Editor)
- O instala una extensión de Mermaid en tu IDE (VS Code, Cursor)
- URL: https://mermaid.live/

---

### 2. Diagrama de Agregados (DDD)
**Archivo**: `DIAGRAMA_AGREGADOS_DOMINIO.mmd`

Este diagrama muestra:
- Los agregados del dominio (según DDD)
- La raíz de cada agregado
- Relaciones entre agregados (líneas punteadas)
- Entidades de soporte

**Agregados identificados:**
1. **Agregado Usuario** - Raíz: `User`
2. **Agregado Imagen** - Raíz: `CacaoImage`
3. **Agregado Finca** - Raíz: `Finca`
4. **Agregado Reporte** - Raíz: `ReporteGenerado`
5. **Agregado Entrenamiento** - Raíz: `TrainingJob`

---

## 🔍 Interpretación del Diagrama de Dominio

### Convenciones de Cardinalidad

En el diagrama ER, las cardinalidades se representan con:

```
||--o{  = Uno a Muchos (1:N)
||--||  = Uno a Uno (1:1)
||--o|  = Uno a Cero o Uno (1:0..1)
}o--o{  = Muchos a Muchos (N:M)
}o--o|  = Muchos a Cero o Uno (N:0..1)
}o--||  = Muchos a Uno (N:1)
```

### Entidades Principales

#### 1. User (Usuario)
- **Raíz del Agregado Usuario**
- Contiene información básica de autenticación y autorización
- Relaciones: tiene perfil, persona, tokens, genera imágenes, fincas, reportes

#### 2. CacaoImage (Imagen de Cacao)
- **Raíz del Agregado Imagen**
- Almacena las imágenes subidas por usuarios
- Puede pertenecer a una Finca y/o Lote
- Genera una CacaoPrediction

#### 3. CacaoPrediction (Predicción)
- Pertenece al Agregado Imagen
- Contiene resultados del análisis ML
- Relación 1:1 con CacaoImage

#### 4. Finca (Finca)
- **Raíz del Agregado Finca**
- Pertenece a un User (agricultor)
- Contiene múltiples Lotes

#### 5. Lote (Lote)
- Pertenece al Agregado Finca
- Pertenece a una Finca
- Puede tener múltiples CacaoImages asociadas

#### 6. ReporteGenerado (Reporte)
- **Raíz del Agregado Reporte**
- Generado por un User
- Puede incluir datos de múltiples entidades (CacaoPrediction, Finca, Lote)

#### 7. TrainingJob (Trabajo de Entrenamiento)
- **Raíz del Agregado Entrenamiento**
- Iniciado por un User (admin/técnico)
- Usa CacaoImage y CacaoPrediction como datos de entrenamiento

---

## 📊 Relaciones Clave del Dominio

### Flujo Principal de Negocio

```
User → Sube → CacaoImage → Procesa → CacaoPrediction
User → Crea → Finca → Contiene → Lote → Asociado a → CacaoImage
User → Genera → ReporteGenerado (con datos de CacaoPrediction/Finca/Lote)
User → Inicia → TrainingJob (usando CacaoImage/CacaoPrediction)
```

### Relaciones de Agregados

```
Agregado Usuario:
  User (raíz)
    ├── UserProfile (1:1)
    ├── Persona (1:0..1)
    └── EmailVerificationToken (1:0..1)

Agregado Imagen:
  CacaoImage (raíz)
    └── CacaoPrediction (1:1)

Agregado Finca:
  Finca (raíz)
    └── Lote (1:N)
```

---

## 🎨 Colores en el Diagrama de Agregados

- 🔵 **Azul claro** (User): Agregado Usuario
- 🟠 **Naranja claro** (CacaoImage): Agregado Imagen
- 🟢 **Verde claro** (Finca): Agregado Finca
- 🩷 **Rosa claro** (ReporteGenerado): Agregado Reporte
- 🟣 **Morado claro** (TrainingJob): Agregado Entrenamiento

---

## 📝 Atributos Clave por Entidad

### User
- `id`, `username`, `email`, `password`, `first_name`, `last_name`, `is_active`

### CacaoImage
- `id`, `user_id`, `image`, `processed`, `finca_id`, `lote_id`, `uploaded_at`

### CacaoPrediction
- `id`, `image_id`, `alto_mm`, `ancho_mm`, `grosor_mm`, `peso_g`, `confidence_*`, `model_version`

### Finca
- `id`, `agricultor_id`, `nombre`, `ubicacion`, `municipio`, `departamento`, `hectareas`

### Lote
- `id`, `finca_id`, `identificador`, `nombre`, `variedad`, `fecha_plantacion`, `area_hectareas`

### ReporteGenerado
- `id`, `user_id`, `tipo_reporte`, `formato`, `estado`, `archivo`, `fecha_generacion`

### TrainingJob
- `id`, `job_id`, `user_id`, `status`, `config`, `progress`, `model_path`

---

## 🔗 Entidades de Soporte

Estas entidades proporcionan catálogos y funcionalidades auxiliares:

- **Group**: Roles del sistema (admin, analyst, farmer)
- **TipoDocumento**: Tipos de documentos de identidad
- **Genero**: Géneros
- **Departamento**: Departamentos geográficos
- **Municipio**: Municipios (pertenecen a Departamentos)
- **LoginHistory**: Historial de inicios de sesión
- **ActivityLog**: Logs de auditoría

---

## 🛠️ Herramientas para Visualizar

### Online
1. **Mermaid Live Editor**: https://mermaid.live/
2. **GitHub/GitLab**: Renderiza automáticamente archivos `.mmd`

### Extensiones IDE
- **VS Code**: Extensión "Markdown Preview Mermaid Support"
- **Cursor**: Soporte nativo de Mermaid
- **IntelliJ IDEA**: Plugin "Mermaid"

### Línea de Comandos
```bash
# Instalar Mermaid CLI
npm install -g @mermaid-js/mermaid-cli

# Generar imagen PNG
mmdc -i DIAGRAMA_DOMINIO_CACAOSCAN.mmd -o diagrama.png

# Generar SVG
mmdc -i DIAGRAMA_DOMINIO_CACAOSCAN.mmd -o diagrama.svg
```

---

## 📌 Notas Importantes

1. **Cardinalidades**: Las relaciones muestran la cardinalidad exacta del modelo de datos
2. **Agregados**: En DDD, las entidades dentro de un agregado solo se acceden a través de la raíz
3. **Opcionalidad**: Las relaciones opcionales (0..1) se muestran con `o|`
4. **Atributos**: Solo se muestran los atributos más relevantes; consulta los modelos para la lista completa

---

**Última actualización**: Generado junto con el modelo de dominio de CacaoScan

