from scrapy.item import Field
from scrapy.item import Item
from scrapy.spiders import CrawlSpider, Rule
from scrapy.selector import Selector
from scrapy.loader.processors import MapCompose
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from bs4 import BeautifulSoup


class Articulo(Item):
    titulo = Field()
    precio = Field()
    descripcion = Field()


class MercadoLibreCrawler(CrawlSpider):
    name = 'mercadoLibre'

    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/71.0.3578.80 Chrome/71.0.3578.80 Safari/537.36',
        
        'CLOSESPIDER_PAGECOUNT': 20 # Numero maximo de paginas en las cuales voy a descargar items. Scrapy se cierra cuando alcanza este numero
    }

    # Utilizamos 2 dominios permitidos, ya que los articulos utilizan un dominio diferente
    allowed_domains = ['listado.mercadolibre.com.co', 'mercadolibre.com.co']

    start_urls = ['http://listado.mercadolibre.com.co/sillas']

    download_delay = 1

    # Tupla de reglas
    rules = (
        Rule(  # REGLA #1 => HORIZONTALIDAD POR PAGINACION
            LinkExtractor(
                allow=r'/_Desde_\d+',# Patron en donde se utiliza "\d+", expresion que puede tomar el valor de cualquier combinacion de numeros
                # process_value=process_url
            ), follow=True),
        Rule(  # REGLA #2 => VERTICALIDAD AL DETALLE DE LOS PRODUCTOS
            LinkExtractor(
                allow=r'/MCO'
            ), follow=True, callback='parse_items'),  # Al entrar al detalle de los productos, se llama al callback con la respuesta al requerimiento
    )

    def parse_items(self, response):

        item = ItemLoader(Articulo(), response)

        # Utilizo Map Compose con funciones anonimas
        item.add_xpath('titulo', '//h1[@class="ui-pdp-title"]/text()', MapCompose(lambda i: i.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ').strip()))
        item.add_xpath('descripcion', '//p[@class="ui-pdp-description__content"]/text()', MapCompose(lambda i: i.replace('\n', ' ').replace('\t', ' ').strip()))

        soup = BeautifulSoup(response.body)
        precio = soup.find(class_="price-tag ui-pdp-price__part")
        precio_completo = precio.text.replace('\n', ' ').replace('\r', ' ').replace(' ', '') # texto de todos los hijos
        item.add_value('precio', precio_completo)

        yield item.load_item()

# EJECUCION
# scrapy runspider mercadolibre.py -o mercado_libre.json -t json
