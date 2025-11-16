# Manual de operación – DMDBike

## Encendido
1. Conectar Raspberry Pi → TV → corriente.
2. Esperar a que abra sola el panel principal.

## Conexión desde celular
- Buscar la red Wi-Fi de la Raspberry.
- Conectarse (Es posible que se pierda el acceso a los datos moviles).
- Ir a: `http://IP:5000/sync`
- Presionar “Sincronizar hora”.

## Durante el uso

### Al subir un participante

1. Ir a `http://IP:5000/pictures`
2. Presionar "Reiniciar Sesión"
3. Cargar nombre y tomar foto
4. Esperar a que finalice de pedalear

### Pedaleo
- La bici y el sensor registran automáticamente.
- No es necesario presionar nada.

### Registrar un participante
1. En `http://IP:5000/pictures`
2. Presionar "Guardar" cuando el participante finalice.
3. Verificar que en la pantalla aparezca la foto del participante, cuando aparezca refrescar la pagina si los datos no se limpiaron automaticamente.

### Carga manual (si es necesario)
- URL: `http://IP:5000/pictures_manual`
- Registrar nombre + km + foto.
    - Los km ingresados aqui no contabilizan para el total de km acumulados.

## Problemas comunes
- **La pantalla no actualiza:** recargar TV o reiniciar Raspberry.
- **Hora incorrecta:** volver a `/sync`.
- **La distancia del participante no aumenta:** Verificar que el sensor no se haya movido y este a la distancia correcta.

## Fin de la jornada
- Generar backup con `backup_bike.sh`.
- Apagar la Raspberry de forma segura si es posible.
