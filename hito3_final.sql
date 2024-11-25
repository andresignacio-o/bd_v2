SET SEARCH_PATH TO 'hito2';

--DROP SCHEMA hito2 CASCADE;

--CREATE SCHEMA hito2;

------------------
--Consultas de pruebas
SELECT *
FROM fact_table; -- tabla de llaves foraneas con 1 mill de transacciones

SELECT *
FROM time_dim;
WHERE item_key = 'T068091';


SELECT TO_DATE(MIN(date), 'DD-MM-YYYY') AS fecha_minima
FROM time_dim;

SELECT 
    MIN(TO_TIMESTAMP(date, 'DD-MM-YYYY HH24:MI')) AS fecha_minima,
    MAX(TO_TIMESTAMP(date, 'DD-MM-YYYY HH24:MI')) AS fecha_maxima
FROM time_dim;


SELECT MAX(year)
FROM time_dim;

-------------------

--Consulta 1

SELECT DISTINCT SPLIT_PART("desc", ' ', 1) AS categoria
FROM item_dim
WHERE "desc" IS NOT NULL
ORDER BY categoria;

SELECT * FROM item_dim WHERE "desc" LIKE 'Coffee%';
SELECT * 
FROM time_dim 
WHERE TO_TIMESTAMP(date, 'DD-MM-YYYY HH24:MI') BETWEEN '2014-01-20 00:00:00' AND '2021-01-23 23:59:59';


 SELECT i.item_key, i.item_name, SUM(f.quantity) AS cantidad_vendida
                    FROM fact_table f
                    JOIN item_dim i ON f.item_key = i.item_key
                    JOIN time_dim t ON f.time_key = t.time_key
                    WHERE i."desc" LIKE %s || '%%'
                    AND TO_TIMESTAMP(t.date, 'DD-MM-YYYY HH24:MI') BETWEEN %s AND %s
                    GROUP BY i.item_key, i.item_name
                    ORDER BY cantidad_vendida DESC;


-- Consulta 2

SELECT * FROM time_dim LIMIT 10;

SELECT * 
FROM item_dim 
WHERE "desc" LIKE 'Beverage%';



SELECT i.item_key AS item_id, 
       i.item_name, 
       SUM(f.quantity) AS cantidad_vendida, 
       t.year
FROM fact_table f
JOIN item_dim i ON f.item_key = i.item_key
JOIN time_dim t ON f.time_key = t.time_key
WHERE i."desc" LIKE 'Beverage%'  -- Filtra por categoría específica
AND CAST(t.month AS INT) = 12  -- Mes específico (diciembre)
AND TO_TIMESTAMP(t.date, 'DD-MM-YYYY HH24:MI') BETWEEN '2014-12-01 00:00:00' AND '2014-12-31 23:59:59'  -- Rango de fechas para diciembre de 2014
GROUP BY i.item_key, i.item_name, t.year
ORDER BY t.year, cantidad_vendida DESC;

-- Consulta 3

SELECT 
    t.bank_name, 
    TO_CHAR(SUM(f.total_price), 'FM999,999,999,999') AS total_ventas_formateado
FROM 
    fact_table f
JOIN 
    trans_dim t ON f.payment_key = t.payment_key
JOIN 
    time_dim ti ON f.time_key = ti.time_key
WHERE 
    ti.year = 2017
GROUP BY 
    t.bank_name
ORDER BY 
    SUM(f.total_price) DESC;


-- Indices

CREATE INDEX idx_time_year ON time_dim(year);
CREATE INDEX idx_fact_total_price ON fact_table(total_price);
CREATE INDEX idx_fact_item_key ON fact_table(item_key);
CREATE INDEX idx_time_date ON time_dim(date);
CREATE INDEX idx_fact_time_key ON fact_table(time_key);



