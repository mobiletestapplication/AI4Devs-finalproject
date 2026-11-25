# Spec Delta

## ADDED Requirements

### Requirement: Comprobación del fichero en pantalla antes de enviarlo
El sistema SHALL comprobar en pantalla, antes de enviar el fichero, que su nombre termina en `.xlsx` sin distinguir mayúsculas y que no supera 5 MB; si no cumple alguna de las dos condiciones, SHALL mostrar el motivo como texto sin enviar el fichero y sin modificar la cartera. Esta comprobación SHALL no sustituir a la validación del servidor, que sigue decidiendo si el fichero se acepta.

#### Scenario: Extensión no admitida
- **WHEN** la persona selecciona el fichero `cartera.csv`
- **THEN** ve el mensaje "Solo se admiten ficheros .xlsx", el fichero no se envía y la Watchlist sigue mostrando la cartera anterior

#### Scenario: Fichero de más de 5 MB
- **WHEN** la persona selecciona un fichero `cartera.xlsx` de 6 MB
- **THEN** ve el mensaje "El fichero supera el tamaño máximo de 5 MB", el fichero no se envía y la Watchlist sigue mostrando la cartera anterior

#### Scenario: Rechazo del servidor tras la comprobación en pantalla
- **WHEN** la persona selecciona un fichero CSV renombrado como `cartera.xlsx`, de 10 KB, que supera la comprobación en pantalla
- **THEN** el fichero se envía, la persona ve como texto el motivo del rechazo `415` del servidor y la Watchlist sigue mostrando la cartera anterior
