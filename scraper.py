import csv
import json
import logging
import os

from bs4 import BeautifulSoup
from http_request import HTTPRequest
from scraper_exceptions import HTTPRequestError, ParsingError


class webScraper(HTTPRequest):
    def __init__(self, config_file, outputDir):
        with open(config_file) as f:
            self.config = json.load(f)
        
        super().__init__(self.config["user_agent"])  # Llamada al constructor de la clase base
        self.outputHeaders = self.config.get("output_headers", {})
        self.outputDir = outputDir

    def process_games(self):
        partidosFilePath = os.path.join(self.outputDir, 'partidos.csv')
        playerStatsFilePath = os.path.join(self.outputDir, 'player_stats.csv')
        teamStatsFilePath = os.path.join(self.outputDir, 'estadisticas_total_equipo.csv')

        with open(partidosFilePath, 'w', newline='', encoding='utf-8') as partidosFile, \
             open(playerStatsFilePath, 'w', newline='', encoding='utf-8') as playerStatsFile, \
             open(teamStatsFilePath, 'w', newline='', encoding='utf-8') as teamStatsFile:

            partidos_writer = csv.writer(partidosFile)
            player_stats_writer = csv.writer(playerStatsFile)
            team_stats_writer = csv.writer(teamStatsFile)

            partidos_writer.writerow(self.outputHeaders.get("partidos.csv", []))
            player_stats_writer.writerow(self.outputHeaders.get("player_stats.csv", []))
            team_stats_writer.writerow(self.outputHeaders.get("estadisticas_total_equipo.csv", []))

            for game_id in range(self.config["url_num_inicial"], self.config["url_num_final"]):
                try:
                    logging.info(f"Procesando partido {game_id}")
                    game_info, player_stats, team_stats = self.extract_game_info(game_id)
                    self.write_csv_rows(game_id, game_info, player_stats, team_stats, partidos_writer,
                                        player_stats_writer, team_stats_writer)
                    # time.sleep(1)  # Espera un segundo antes de realizar la siguiente solicitud
                    logging.info(f"Partido {game_id} procesado correctamente")
                except HTTPRequestError as e:
                    logging.error(f"Error en la solicitud HTTP para el partido {game_id}: {e}")
                except ParsingError as e:
                    logging.error(f"Error al parsear la información para el partido {game_id}: {e}")
                except Exception as e:
                    logging.error(f"Error inesperado para el partido {game_id}: {e}")
                    logging.error('Detalle del error:', exc_info=True)
            print("Estadísticas guardadas en player_stats.csv, partidos.csv y estadisticas_total_equipo.csv")
            logging.info("Programa finalizado con exito")

    def write_csv_rows(self, game_id, game_info, player_stats, team_stats, partidos_writer, player_stats_writer,
                       team_stats_writer):

        partidos_writer.writerow([game_id] + game_info)

        for stat_row in player_stats:
            player_stats_writer.writerow([game_id, stat_row[0]] + stat_row[1])

        for stat_row in team_stats:
            team_stats_writer.writerow([game_id, stat_row[0]] + stat_row[1])

    def extract_game_info(self, game_id):
        url_partido = f"{self.config['url_base']}{game_id}"
        response = self.session.get(url_partido)

        if response.status_code != 200:
            raise HTTPRequestError(response.status_code)

        soup = BeautifulSoup(response.content, 'html.parser')

        try:
            game_info = self.extract_game_details(soup)
            player_stats = self.extract_player_stats(soup)
            team_stats = self.extract_team_stats(soup)
        except Exception as e:
            raise ParsingError(f"Error al analizar el contenido HTML del partido {game_id}") from e

        return game_info, player_stats, team_stats

    def extract_game_details(self, soup):
        local = soup.find(class_="columna equipo local")
        nombre_local = local.find(class_="nombre").getText(strip=True)
        resultado_local = local.find(class_="resultado").getText(strip=True)

        visitante = soup.find(class_="columna equipo visitante")
        nombre_visitante = visitante.find(class_="nombre").getText(strip=True)
        resultado_visitante = visitante.find(class_="resultado").getText(strip=True)

        parciales = soup.find(class_="fila parciales").find_all('span')
        parciales_local = [parciales[i].getText(strip=True) for i in range(0, 4)]
        parciales_visitante = [parciales[i].getText(strip=True) for i in range(4, 8)]

        # TODO: Separar fecha y hora de partido en dos variables
        fecha_partido = soup.find(class_="fecha").find(class_="txt").getText(strip=True)

        # TODO: Separar los 3 arbitros en 3 variables (arbitro1, 2 y 3)
        arbitros = soup.find(class_="arbitros").findAll(class_="txt referee")
        arbitro1, arbitro2, arbitro3 = [arbitro.getText(strip=True) for arbitro in arbitros]

        pista_partido = soup.find(class_="pista").find(class_="txt pabellon").getText(strip=True)
        direccion_partido = soup.find(class_="pista").find(class_="txt direccion").getText(strip=True)

        return [
            nombre_local, resultado_local,
            nombre_visitante, resultado_visitante,
            ','.join(parciales_local), ','.join(parciales_visitante),
            fecha_partido, arbitro1, arbitro2, arbitro3,
            pista_partido, direccion_partido
        ]

    def extract_player_stats(self, soup):
        player_stats = []

        local = soup.find(class_="columna equipo local")
        nombre_local = local.find(class_="nombre").getText(strip=True)

        visitante = soup.find(class_="columna equipo visitante")
        nombre_visitante = visitante.find(class_="nombre").getText(strip=True)

        estadisticas_equipos = soup.find_all(class_="responsive-scroll")
        for index, estadisticas_equipo in enumerate(estadisticas_equipos):
            table = estadisticas_equipo.find('table')
            rows = table.find_all('tr')[2:-1]

            for row in rows:
                cells = row.find_all('td')
                player_stat_row = []
                for cell in cells:
                    if '/' in cell.text:
                        encestados, intentados_pct = cell.text.strip().split(' ')
                        encestados, intentados = encestados.split('/')

                        """ Extraemos el porcentaje, substituimos la coma por un punto y lo pasamos a float (con la coma no se puede convertir) """
                        pctRaw = intentados_pct.strip('%')
                        pct = float(pctRaw.replace(',', '.'))
                        player_stat_row.extend([encestados, intentados, pct])
                    else:
                        # Ponemos el replace porque hay nombres de jugadores que contienen tilde en vez de comilla (EJ: Lucas N'Guessan)
                        player_stat_row.append(cell.text.strip().replace("´", "'"))

                equipo = nombre_local if index == 0 else nombre_visitante
                player_stats.append((equipo, player_stat_row))

        return player_stats

    def extract_team_stats(self, soup):
        team_stats = []

        local = soup.find(class_="columna equipo local")
        nombre_local = local.find(class_="nombre").getText(strip=True)

        visitante = soup.find(class_="columna equipo visitante")
        nombre_visitante = visitante.find(class_="nombre").getText(strip=True)

        estadisticas_equipos = soup.find_all(class_="responsive-scroll")

        for index, estadisticas_equipo in enumerate(estadisticas_equipos):
            table = estadisticas_equipo.find('table')
            row = table.find_all('tr')[-1]
            cells = row.find_all('td')
            team_stat_row = []
            for i, cell in enumerate(cells):
                # TODO: Buscar manera mas elegante de saltarnos las celdas vacías/que solo tienen un espacio en blanco dentro
                if i in [0, 1, 2, 21]:  # Saltamos las celdas vacías
                    continue

                if '/' in cell.text:
                    encestados, intentados_pct = cell.text.strip().split(' ')
                    encestados, intentados = encestados.split('/')

                    """ Extraemos el porcentaje, substituimos la coma por un punto
                      y lo pasamos a float (con la coma no se puede convertir) """

                    pct_raw = intentados_pct.strip('%')
                    pct = float(pct_raw.replace(',', '.'))
                    team_stat_row.extend([encestados, intentados, pct])
                else:
                    team_stat_row.append(cell.text.strip())

            equipo = nombre_local if index == 0 else nombre_visitante
            # Agregamos el nombre del equipo al principio
            team_stats.append((equipo, team_stat_row))

        return team_stats


def load_config(file_path):
    with open(file_path, "r") as config_file:
        return json.load(config_file)
