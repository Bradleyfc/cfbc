@echo off
echo Aplicando migraciones para los cambios en el modelo...
python manage.py makemigrations
python manage.py migrate
echo Migraciones completadas.
echo.
echo Para crear un nuevo curso academico, ejecute:
echo python manage.py nuevo_curso
pause