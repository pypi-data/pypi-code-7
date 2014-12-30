procedures = {}

procedures[ 'SIC_PUNTOS_DEL_TRIGGERS' ] = '''
    CREATE OR ALTER PROCEDURE SIC_PUNTOS_DEL_TRIGGERS 
    as
    begin
        if (exists(
            select 1 from RDB$Triggers
            where RDB$Trigger_name = 'SIC_PUNTOS_PV_CLIENTES_BU')) then
            execute statement 'drop trigger SIC_PUNTOS_PV_CLIENTES_BU';

        if (exists(
            select 1 from RDB$Triggers
            where RDB$Trigger_name = 'SIC_PUNTOS_PV_DOCTOSPVDET_AD')) then
            execute statement 'drop trigger SIC_PUNTOS_PV_DOCTOSPVDET_AD';

        if (exists(
            select 1 from RDB$Triggers
            where RDB$Trigger_name = 'SIC_PUNTOS_PV_DOCTOSPVDET_BU')) then
            execute statement 'drop trigger SIC_PUNTOS_PV_DOCTOSPVDET_BU';

        if (exists(
            select 1 from RDB$Triggers
            where RDB$Trigger_name = 'SIC_PUNTOS_PV_DOCTOSPV_AD')) then
            execute statement 'drop trigger SIC_PUNTOS_PV_DOCTOSPV_AD';

        if (exists(
            select 1 from RDB$Triggers
            where RDB$Trigger_name = 'SIC_PUNTOS_PV_DOCTOSPV_BU')) then
            execute statement 'drop trigger SIC_PUNTOS_PV_DOCTOSPV_BU';
    end
    '''

procedures['SIC_PUNTOS_ARTICULOS_AT'] = '''
    CREATE OR ALTER PROCEDURE SIC_PUNTOS_ARTICULOS_AT
    as
    BEGIN
        if (not exists(
        select 1 from RDB$RELATION_FIELDS rf
        where rf.RDB$RELATION_NAME = 'ARTICULOS' and rf.RDB$FIELD_NAME = 'SIC_PUNTOS')) then
            execute statement 'ALTER TABLE ARTICULOS ADD SIC_PUNTOS SMALLINT';

        if (not exists(
        select 1 from RDB$RELATION_FIELDS rf
        where rf.RDB$RELATION_NAME = 'ARTICULOS' and rf.RDB$FIELD_NAME = 'SIC_DINERO_ELECTRONICO')) then
            execute statement 'ALTER TABLE ARTICULOS ADD SIC_DINERO_ELECTRONICO NUMERIC(15,2)';

        if (not exists(
        select 1 from RDB$RELATION_FIELDS rf
        where rf.RDB$RELATION_NAME = 'ARTICULOS' and rf.RDB$FIELD_NAME = 'SIC_HEREDA_PUNTOS')) then
            execute statement 'ALTER TABLE ARTICULOS ADD SIC_HEREDA_PUNTOS SMALLINT';

        if (not exists(
        select 1 from RDB$RELATION_FIELDS rf
        where rf.RDB$RELATION_NAME = 'ARTICULOS' and rf.RDB$FIELD_NAME = 'SIC_CARPETA_ID')) then
            execute statement 'ALTER TABLE ARTICULOS ADD SIC_CARPETA_ID ENTERO_ID';
    END  
    '''

procedures['SIC_PUNTOS_LINEASARTICULOS_AT'] = '''
    CREATE OR ALTER PROCEDURE SIC_PUNTOS_LINEASARTICULOS_AT
    as
    BEGIN
        if (not exists(
        select 1 from RDB$RELATION_FIELDS rf
        where rf.RDB$RELATION_NAME = 'LINEAS_ARTICULOS' and rf.RDB$FIELD_NAME = 'SIC_DINERO_ELECTRONICO')) then
            execute statement 'ALTER TABLE LINEAS_ARTICULOS ADD SIC_DINERO_ELECTRONICO NUMERIC(15,2)';

        if (not exists(
        select 1 from RDB$RELATION_FIELDS rf
        where rf.RDB$RELATION_NAME = 'LINEAS_ARTICULOS' and rf.RDB$FIELD_NAME = 'SIC_PUNTOS')) then
            execute statement 'ALTER TABLE LINEAS_ARTICULOS ADD SIC_PUNTOS SMALLINT';
        
        if (not exists(
        select 1 from RDB$RELATION_FIELDS rf
        where rf.RDB$RELATION_NAME = 'LINEAS_ARTICULOS' and rf.RDB$FIELD_NAME = 'SIC_HEREDA_PUNTOS')) then
            execute statement 'ALTER TABLE LINEAS_ARTICULOS ADD SIC_HEREDA_PUNTOS SMALLINT';
    END  
    '''

procedures['SIC_PUNTOS_GRUPOSLINEAS_AT'] = '''
    CREATE OR ALTER PROCEDURE SIC_PUNTOS_GRUPOSLINEAS_AT
    as
    BEGIN
        if (not exists(
        select 1 from RDB$RELATION_FIELDS rf
        where rf.RDB$RELATION_NAME = 'GRUPOS_LINEAS' and rf.RDB$FIELD_NAME = 'SIC_DINERO_ELECTRONICO')) then
            execute statement 'ALTER TABLE GRUPOS_LINEAS ADD SIC_DINERO_ELECTRONICO NUMERIC(15,2)';

        if (not exists(
        select 1 from RDB$RELATION_FIELDS rf
        where rf.RDB$RELATION_NAME = 'GRUPOS_LINEAS' and rf.RDB$FIELD_NAME = 'SIC_PUNTOS')) then
            execute statement 'ALTER TABLE GRUPOS_LINEAS ADD SIC_PUNTOS SMALLINT';

        if (not exists(
        select 1 from RDB$RELATION_FIELDS rf
        where rf.RDB$RELATION_NAME = 'GRUPOS_LINEAS' and rf.RDB$FIELD_NAME = 'SIC_HEREDA_PUNTOS')) then
            execute statement 'ALTER TABLE GRUPOS_LINEAS ADD SIC_HEREDA_PUNTOS SMALLINT';
    END  
    '''

procedures['SIC_PUNTOS_CLIENTES_AT'] = '''
    CREATE OR ALTER PROCEDURE SIC_PUNTOS_CLIENTES_AT
    as
    BEGIN
        if (not exists(
        select 1 from RDB$RELATION_FIELDS rf
        where rf.RDB$RELATION_NAME = 'CLIENTES' and rf.RDB$FIELD_NAME = 'SIC_TIPO_TARJETA')) then
            execute statement 'ALTER TABLE CLIENTES ADD SIC_TIPO_TARJETA CHAR(1)';
        
        if (not exists(
        select 1 from RDB$RELATION_FIELDS rf
        where rf.RDB$RELATION_NAME = 'CLIENTES' and rf.RDB$FIELD_NAME = 'SIC_HEREDA_VALORPUNTOS')) then
            execute statement 'ALTER TABLE CLIENTES ADD SIC_HEREDA_VALORPUNTOS SMALLINT DEFAULT 1';

        if (not exists(
        select 1 from RDB$RELATION_FIELDS rf
        where rf.RDB$RELATION_NAME = 'CLIENTES' and rf.RDB$FIELD_NAME = 'SIC_VALOR_PUNTOS')) then
            execute statement 'ALTER TABLE CLIENTES ADD SIC_VALOR_PUNTOS NUMERIC(15,2) DEFAULT 0';
        
        if (not exists(
        select 1 from RDB$RELATION_FIELDS rf
        where rf.RDB$RELATION_NAME = 'CLIENTES' and rf.RDB$FIELD_NAME = 'SIC_HEREDAR_PUNTOS_A')) then
            execute statement 'ALTER TABLE CLIENTES ADD SIC_HEREDAR_PUNTOS_A ENTERO_ID';

        if (not exists(
        select 1 from RDB$RELATION_FIELDS rf
        where rf.RDB$RELATION_NAME = 'CLIENTES' and rf.RDB$FIELD_NAME = 'SIC_FECHA_CORTE')) then
            execute statement 'ALTER TABLE CLIENTES ADD SIC_FECHA_CORTE DATE';

        if (not exists(
        select 1 from RDB$RELATION_FIELDS rf
        where rf.RDB$RELATION_NAME = 'CLIENTES' and rf.RDB$FIELD_NAME = 'SIC_APLICAR_DSCTO')) then
            execute statement 'ALTER TABLE CLIENTES ADD SIC_APLICAR_DSCTO SMALLINT DEFAULT 0';
    END
    '''
procedures['SIC_PUNTOS_LIBRESCLIENTES_AT'] = '''
    CREATE OR ALTER PROCEDURE SIC_PUNTOS_LIBRESCLIENTES_AT
    as
    BEGIN
        if (not exists(
        select 1 from RDB$RELATION_FIELDS rf
        where rf.RDB$RELATION_NAME = 'LIBRES_CLIENTES' and rf.RDB$FIELD_NAME = 'HEREDAR_PUNTOS_A')) then
            execute statement 'ALTER TABLE LIBRES_CLIENTES ADD HEREDAR_PUNTOS_A ENTERO_ID'; 
    END  
    '''

procedures['SIC_PUNTOS_TIPOSCLIENTES_AT'] = '''
    CREATE OR ALTER PROCEDURE SIC_PUNTOS_TIPOSCLIENTES_AT
    as
    BEGIN
        if (not exists(
        select 1 from RDB$RELATION_FIELDS rf
        where rf.RDB$RELATION_NAME = 'TIPOS_CLIENTES' and rf.RDB$FIELD_NAME = 'SIC_VALOR_PUNTOS')) then
            execute statement 'ALTER TABLE TIPOS_CLIENTES ADD SIC_VALOR_PUNTOS NUMERIC(15,2) DEFAULT 0';
    END  
    '''

procedures['SIC_PUNTOS_DOCTOSPVDET_AT'] = '''
    CREATE OR ALTER PROCEDURE SIC_PUNTOS_DOCTOSPVDET_AT
    as
    BEGIN
         if (not exists(
        select 1 from RDB$RELATION_FIELDS rf
        where rf.RDB$RELATION_NAME = 'DOCTOS_PV_DET' and rf.RDB$FIELD_NAME = 'SIC_DINERO_ELECTRONICO')) then
            execute statement 'ALTER TABLE DOCTOS_PV_DET ADD SIC_DINERO_ELECTRONICO NUMERIC(15,2) DEFAULT 0';

        if (not exists(
        select 1 from RDB$RELATION_FIELDS rf
        where rf.RDB$RELATION_NAME = 'DOCTOS_PV_DET' and rf.RDB$FIELD_NAME = 'SIC_PUNTOS')) then
            execute statement 'ALTER TABLE DOCTOS_PV_DET ADD SIC_PUNTOS ENTERO DEFAULT 0';
    END  
    '''

procedures['SIC_PUNTOS_DOCTOS_PV_AT'] = '''
    CREATE OR ALTER PROCEDURE SIC_PUNTOS_DOCTOS_PV_AT
    as
    BEGIN
        if (not exists(
        select 1 from RDB$RELATION_FIELDS rf
        where rf.RDB$RELATION_NAME = 'DOCTOS_PV' and rf.RDB$FIELD_NAME = 'SIC_DINERO_ELECTRONICO')) then
            execute statement 'ALTER TABLE DOCTOS_PV ADD SIC_DINERO_ELECTRONICO NUMERIC(15,2) DEFAULT 0';

        if (not exists(
        select 1 from RDB$RELATION_FIELDS rf
        where rf.RDB$RELATION_NAME = 'DOCTOS_PV' and rf.RDB$FIELD_NAME = 'SIC_PUNTOS')) then
            execute statement 'ALTER TABLE DOCTOS_PV ADD SIC_PUNTOS ENTERO DEFAULT 0';

        if (not exists(
        select 1 from RDB$RELATION_FIELDS rf
        where rf.RDB$RELATION_NAME = 'DOCTOS_PV' and rf.RDB$FIELD_NAME = 'SIC_VALOR_PUNTOS_PAGO')) then
            execute statement 'ALTER TABLE DOCTOS_PV ADD SIC_VALOR_PUNTOS_PAGO NUMERIC(15,2) DEFAULT 0';

        if (not exists(
        select 1 from RDB$RELATION_FIELDS rf
        where rf.RDB$RELATION_NAME = 'DOCTOS_PV' and rf.RDB$FIELD_NAME = 'SIC_PUNTOS_PAGO')) then
            execute statement 'ALTER TABLE DOCTOS_PV ADD SIC_PUNTOS_PAGO ENTERO DEFAULT 0';

        if (not exists(
        select 1 from RDB$RELATION_FIELDS rf
        where rf.RDB$RELATION_NAME = 'DOCTOS_PV' and rf.RDB$FIELD_NAME = 'SIC_DINERO_ELECTRONICO_PAGO')) then
            execute statement 'ALTER TABLE DOCTOS_PV ADD SIC_DINERO_ELECTRONICO_PAGO NUMERIC(15,2) DEFAULT 0';

        if (not exists(
        select 1 from RDB$RELATION_FIELDS rf
        where rf.RDB$RELATION_NAME = 'DOCTOS_PV' and rf.RDB$FIELD_NAME = 'SIC_CLIENTE_TARJETA')) then
            execute statement 'ALTER TABLE DOCTOS_PV ADD SIC_CLIENTE_TARJETA ENTERO_ID';

        /*FATURA GLOBAL*/
        /*if (not exists(
        select 1 from RDB$RELATION_FIELDS rf
        where rf.RDB$RELATION_NAME = 'DOCTOS_PV' and rf.RDB$FIELD_NAME = 'TIPO_GEN_FAC')) then
            execute statement 'ALTER TABLE DOCTOS_PV ADD TIPO_GEN_FAC CHAR(1) CHARACTER SET NONE';
        
        select 1 from RDB$RELATION_FIELDS rf
        where rf.RDB$RELATION_NAME = 'DOCTOS_PV' and rf.RDB$FIELD_NAME = 'ES_FAC_GLOBAL')) then
            execute statement 'ALTER TABLE DOCTOS_PV ADD ES_FAC_GLOBAL CHAR(1) CHARACTER SET NONE';*/
    END  
    '''