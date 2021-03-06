CREATE TABLE CONSULTA (
    CODIGO_UPC TEXT, -- CODIGO UPC
    FECHA_HORA_INICIO TEXT, -- FECHA Y HORA INICIO DE LA CONSULTA
    FECHA_HORA_FIN TEXT, -- FECHA Y HORA FIN DE LA CONSULTA
    IP TEXT, -- IP DEL CONSULTANTE
    RESULTADO INTEGER, -- RESULTADO DEL LOGIN UPC (1/0)
    NOMBRE TEXT, -- NOMBRE DEL ALUMNO (RESULTADO = 1)
    CARRERA TEXT, -- CARRERA DEL ALUMNO (RESULTADO = 1)
    OBS TEXT -- OBSERVACIONES O ERRORES (SEA EL CASO)
);

CREATE TABLE VISITA (
    FECHA_HORA TEXT, -- FECHA Y HORA DE LA VISITA
    IP TEXT -- IP DEL VISITANTE
);
