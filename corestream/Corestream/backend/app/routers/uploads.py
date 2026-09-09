"""
Router para manejo de carga y descarga de archivos (código y documentación).
Endpoints para upload, download, listado y eliminación de archivos.
"""


from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse

from app.middleware import get_current_user
from app.services.file_service import FileService

router = APIRouter(
    prefix="/api/uploads",
    tags=["uploads"],
)


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    current_user = Depends(get_current_user),
) -> dict:
    """
    Cargar un archivo de código o documentación.

    **Tipos de archivo permitidos:**
    - Código: .py, .js, .ts, .jsx, .tsx, .java, .cpp, .c, .cs, .rb, .go, .rs
    - Documentación: .md, .pdf, .docx, .txt, .rst
    - Datos: .json, .yaml, .yml, .xml, .sql, .csv

    **Límite de tamaño:** 50 MB

    **Parámetros:**
    - file: Archivo a cargar

    **Respuesta:**
    - id: ID único del archivo
    - filename: Nombre original del archivo
    - size: Tamaño en bytes
    - uploaded_by: ID del usuario que lo cargó
    - uploaded_at: Timestamp de carga
    - download_url: URL para descargar
    """
    try:
        user_id = str(current_user.id)
        metadata = await FileService.upload_file(file, user_id)

        return {
            "status": "success",
            "message": "Archivo cargado exitosamente",
            "data": metadata,
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al cargar archivo: {str(e)}",
        )


@router.get("/download/{file_id}")
async def download_file(
    file_id: str,
    current_user = Depends(get_current_user),
) -> FileResponse:
    """
    Descargar un archivo cargado.

    **Parámetros:**
    - file_id: ID único del archivo a descargar

    **Respuesta:**
    - Archivo en stream
    """
    file_path = FileService.get_file_path(file_id, str(current_user.id))

    if not file_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Archivo no encontrado",
        )

    return FileResponse(
        path=file_path,
        filename=FileService.get_original_filename(file_path),
        media_type="application/octet-stream",
    )


@router.get("/info/{file_id}")
async def get_file_info(
    file_id: str,
    current_user = Depends(get_current_user),
) -> dict:
    """
    Obtener información sobre un archivo.

    **Parámetros:**
    - file_id: ID único del archivo

    **Respuesta:**
    - id, filename, size, extension, created_at
    """
    file_info = FileService.get_file_info(file_id, str(current_user.id))

    if not file_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Archivo no encontrado",
        )

    return {
        "status": "success",
        "data": file_info,
    }


@router.get("/list")
async def list_files(
    current_user = Depends(get_current_user),
) -> dict:
    """
    Listar todos los archivos cargados.

    **Respuesta:**
    - Lista de archivos con metadatos
    """
    files = FileService.list_files(str(current_user.id))

    return {
        "status": "success",
        "count": len(files),
        "data": files,
    }


@router.delete("/{file_id}")
async def delete_file(
    file_id: str,
    current_user = Depends(get_current_user),
) -> dict:
    """
    Eliminar un archivo cargado.

    **Parámetros:**
    - file_id: ID único del archivo a eliminar

    **Respuesta:**
    - Confirmación de eliminación
    """
    if FileService.delete_file(file_id, str(current_user.id)):
        return {
            "status": "success",
            "message": f"Archivo {file_id} eliminado exitosamente",
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Archivo no encontrado",
        )
