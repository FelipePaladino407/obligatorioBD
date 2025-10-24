-- mayor cantidad de reservas

SELECT r.nombre_sala, r.edificio, COUNT(id_reserva) AS mas_reservada 
FROM reserva r 
WHERE r.estado IN ('activa', 'finalizada')
GROUP BY r.nombre_sala, r.edificio 
ORDER BY mas_reservada DESC;
