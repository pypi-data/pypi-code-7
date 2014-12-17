procedures={}

procedures['SIC_ARTICULOS_CATALOGO'] = '''
    CREATE OR ALTER PROCEDURE SIC_ARTICULOS_CATALOGO
    as
    begin
     if (not exists(
        select 1 from RDB$RELATION_FIELDS rf
        where rf.RDB$RELATION_NAME = 'ARTICULOS' and rf.RDB$FIELD_NAME = 'SIC_IMAGEN_URL')) then
        execute statement 'ALTER TABLE ARTICULOS ADD SIC_IMAGEN_URL VARCHAR(100)';
	end  
    '''