# Guía de entrega: Git y GitHub

## Antes de empezar
1. Un integrante crea el repositorio GitHub y añade a los otros seis colaboradores.
2. Cada integrante configura su nombre/correo Git con su identidad real.
3. Cada integrante trabaja en una rama propia o de su célula; no se debe compartir una sola cuenta.

## Ejemplo para iniciar el repositorio (lo ejecuta quien lo creó)
```bash
git init
git add .
git commit -m "chore: estructura inicial del sistema POS"
git branch -M main
git remote add origin URL_REAL_DEL_REPOSITORIO
git push -u origin main
```

## Trabajo individual (cada estudiante)
```bash
git switch main
git pull origin main
git switch -c feat/nombre-tarea
# Editar y probar los archivos asignados
python -m unittest discover -s tests -v
git status
git add ARCHIVO_QUE_MODIFICASTE
git commit -m "feat: describe el cambio realizado"
git push -u origin feat/nombre-tarea
```
Luego, en GitHub, abre un Pull Request desde `feat/nombre-tarea` hacia `main`, completa `.github/PULL_REQUEST_TEMPLATE.md`, revisa el diff y solicita revisión. Tras aprobación y pruebas, fusiona el PR según las reglas del equipo.

## Ejemplo de distribución de trabajo (7 integrantes)
- GitMaster/DevOps: repositorio, protección de `main`, plantilla PR, `README.md`, `architecture.md` y `main.py`.
- Célula Dominio (2): `src/domain/models.py`, `src/domain/exceptions.py`.
- Célula Servicios y Datos (2): `src/services/app_service.py`, `src/services/data_manager.py`.
- Célula Interfaz (2): `src/ui/cli_interface.py` y pruebas/documentación de uso.
- Todos: cada integrante debe hacer un cambio real, commit propio y PR propio. Ajusten esta distribución para que no haya dos personas editando el mismo archivo a la vez.

## Evidencias que pide la consigna
Guarda capturas reales de:
- Perfil/commit propio visible en GitHub.
- Pull Request fusionado y sus archivos modificados.
- Network Graph o historial de ramas.
- Pruebas unitarias ejecutadas en la terminal.
- Aplicación ejecutándose correctamente.
- `architecture.md` con el diagrama Mermaid.
- Publicación de evidencias en Moodle, según indique el docente.

No publiques contraseñas, tokens ni claves personales.
