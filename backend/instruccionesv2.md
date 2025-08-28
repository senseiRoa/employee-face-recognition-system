con el fin de optimizar el rendimiento, hacer:


# ✅ TODO - Gestión de encodings (máx. 30 y 30 días)

## 1. Modificar la tabla de encodings
- [ ] Agregar columna `created_at` en el modelo `FaceEncoding`
  

* [ ] Crear migración en BD

  ```sql
  ALTER TABLE face_encoding ADD COLUMN created_at TIMESTAMP DEFAULT NOW();
  ```

---

## 2. Actualizar la lógica de guardado de encodings

* [ ] Cuando se agregue un nuevo encoding, guardar `created_at`:

  ```python
  new_encoding = FaceEncoding(encoding=enc_s, created_at=datetime.utcnow())
  recognized_employee.encodings.append(new_encoding)
  ```

* [ ] Llamar a una función de limpieza justo después de añadir uno nuevo:

  ```python
  prune_old_encodings(session, recognized_employee.id)
  ```

---

## 3. Crear función de limpieza (`prune_old_encodings`)

* [ ] Implementar función para:

  1. Borrar encodings con más de 30 días
  2. Mantener solo los últimos 30 más recientes

  

---

## 4. Optimizar consultas al obtener empleados

* [ ] Solo traer encodings válidos (últimos 30 días):

  ```python
  cutoff = datetime.utcnow() - timedelta(days=30)
  employees = session.execute(
      select(Employee)
      .options(selectinload(Employee.encodings))
      .join(Employee.encodings)
      .filter(FaceEncoding.created_at >= cutoff)
  ).scalars().all()
  ```

---

## 5. Mejoras de mantenimiento

* [ ] Crear un **índice en la BD** para acelerar consultas:

  ```sql
  CREATE INDEX idx_face_encoding_emp_date 
  ON face_encoding (employee_id, created_at DESC);
  ```

* [ ] (Opcional) Programar un **job nocturno** que ejecute `prune_old_encodings` sobre todos los empleados.

---

## 6. Pruebas

* [ ] Registrar encodings de prueba durante más de 30 días.
* [ ] Verificar que encodings viejos se borran automáticamente.
* [ ] Verificar que nunca haya más de 30 encodings por empleado.
* [ ] Medir que las comparaciones son más rápidas que antes.

---

## 🚀 Resultado esperado

* Encodings limitados a **30 por empleado**.
* Encodings más antiguos que **30 días eliminados**.
* Tabla `face_encoding` controlada en tamaño.
* Comparaciones mucho más rápidas y eficientes.

```
