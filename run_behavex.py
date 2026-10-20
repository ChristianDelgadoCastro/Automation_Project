import os
import sys

from behavex.__main__ import main
from librerias.directorios import DIR_PROYECT

if __name__ == "__main__":
    os.environ["HEADLESS"] = "False"
    os.environ["PDF_GENERAL"] = "True"  # <-- Esto lo cambiamos a "True" si queremos generar el pdf global

    # Toma la variable LINEA desde el TXT de ejecuciones
    linea = os.environ.get("LINEA", "L1")  # Por defecto L1 si no está definida
    # Asignación de variable definida en TXT
    os.environ["LINEA"] = linea

    output_dir = os.path.join(DIR_PROYECT, "output")
    sys.argv = [
        'behavex',
        '--parallel-processes', '1',
        '--parallel-scheme', 'scenario',
        '-ip', 'features',
        '--tags', f'@test_login_scriptlabs, @test_login_qa_practice, @test_login_dojo',
        # '--tags', f'@Scraping',
        '-o', output_dir
    ]

    exit_code = main()
