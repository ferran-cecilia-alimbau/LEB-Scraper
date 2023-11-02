import os
import logging
from logger import setupLogging
from scraper import webScraper
from scraper_exceptions import ScraperError


def main():
    # TODO: Añadir marcas de tiempo en el log para calcular tiempo promedio partido y tiempo de extracción de datos.
    setupLogging()
    logging.info("Iniciando programa")

    config_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config", "config.json")

    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Output")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    scraper = webScraper(config_file_path, output_dir)

    try:
        scraper.process_games()
    except ScraperError as e:
        logging.error(e)
        print(e)


if __name__ == "__main__":
    main()
