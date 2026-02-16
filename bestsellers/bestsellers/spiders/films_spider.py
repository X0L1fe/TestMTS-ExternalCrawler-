import scrapy
from scrapy_playwright.page import PageMethod

class FilmSpider(scrapy.Spider):
    
    name = "filmer"
    start_urls = ["https://www.kinopoisk.ru/lists/movies/top_1000/"]

    def start_requests(self):
        cookies = {
            "sync_cookie_ok" : "synced",
            "ya_sess_id" : "3:1771100274.5.0.1768214634880:ByXLJQ:ad22.1.2:1|637936768.0.2.3:1768214634.6:2109515404.7:1768483237|30:11715427.688472.00JRwuFQj56a27KyXwEPoT_Rp2A",
            "yabs-sid" : "678929971770831461",
            "yabs-vdrf" : "A0",
            "yandex_expboxes"	: "1477365%2C0%2C48%3B1479353%2C0%2C3%3B1487256%2C0%2C86%3B1357004%2C0%2C66%3B1002325%2C0%2C46%3B901040%2C0%2C17%3B1486131%2C0%2C73%3B1487701%2C0%2C91%3B1487552%2C0%2C11%3B19996%2C0%2C43%3B663872%2C0%2C51%3B1257223%2C0%2C43",
            "yandex_login" : "h4ncola",
            "yandex_login" : "h4ncola",
            "yandexuid" : "1339051031756079822",
            "yandexuid" : "1339051031756079822",
            "yandexuid" : "1339051031756079822",
            "yashr" : "1374601711757009095",
            "yashr" : "8702907491770984730",
            "yclid_src" : "yabs.yandex.ru/resource/spacer.gif:17681520369211277311:1339051031756079822",
            "ymex" : "2072369097.yrts.1757009097",
            "ymex" : "1773761956.oyu.1339051031756079822#2081498398.yrts.1766138398",
            "yp" : "1771256356.yu.1339051031756079822",
            "yp" : "1798217917.dc_neuro.10#1771959330.dlp.2#1771357924.gpauto.55_936847%3A37_358780%3A151%3A1%3A1771185114#1772917127.gph.225_84#1773510436.hdrc.1#2083574321.multib.1#2086542421.pcs.1#1802718433.swntab.3387336707#1783982385.szm.1_5%3A1707x960%3A1682x882%3A15#2083574634.udn.cDrQoNC%2B0LzQsNC9INCb0LjRhNCw0L3QvtCy",
            "ys" : "udn.cDrQoNC%2B0LzQsNC9INCb0LjRhNCw0L3QvtCy#c_chck.2294051025",
            "ys" : "c_chck.2294051025#udn.cDrQoNC%2B0LzQsNC9INCb0LjRhNCw0L3QvtCy#wprid.1771182432433278-9503599452921291036-balancer-l7leveler-kubr-yp-klg-230-BAL",
            "yuidss" : "1339051031756079822",
            }
        for i in range(1, 21):
            next_page = f'https://www.kinopoisk.ru/lists/movies/top_1000/?page={i}'
            yield scrapy.Request(
                url=next_page,
                cookies=cookies,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    "Accept-Language": "ru-RU,ru;q=0.9",
                    },
                meta={
                    'download_delay': 2,
                    "playwright": True,
                    "playwright_context": "default",
                    "playwright_include_page": False,
                    "playwright_page_methods": [
                        PageMethod("wait_for_selector", "div.styles_root__dtojy"),
                        PageMethod("wait_for_timeout", 2000),
                        ],
                    },
                callback=self.parse,
                )

    def parse(self, response):
        films = response.css("div.styles_root__dtojy")
        for film in films:
            title = film.css('span.styles_activeMovieTittle__d3sVG::text').get() # Название
            grade = film.css('span.styles_kinopoiskValue__wuWe_::text').get() # Оценка

            year_el = film.css('span.desktop-list-main-info_secondaryText__gwhDJ').get() # Cтрока с годом выпуска
            if year_el:
                import re
                reg = re.search(r'\b(19|20)\d{2}\b', year_el)
                if reg:
                    year = reg.group(0)
                else:
                    year = None
                    print("YEAR EMPTY! ERROR!")
            else:
                year = None
                print("YEAR EMPTY! ERROR")
            info_CD = film.css('span.desktop-list-main-info_truncatedText__DAuwA::text').get() # ['США', '•', 'фильм-нуар', 'Режиссёр:', 'Билли', 'Уайлдер']
            print("!!!", info_CD)
            if info_CD:
                country = info_CD.split()[0] # Страна
                director = ' '.join(info_CD.split()[-2:]) # Режисёр
            else:
                country = None
                director = None
                print("CD EMPTY! ERROR")

            block_watch = bool(film.css('div.styles_onlineButton__xrATk')) # Наличие кнопки просмотра на кинопоискеы
            
            yield {"title":title,
                "grade":grade,
                "year":year,
                "country":country,
                "director":director,
                "block_watch":block_watch
                } 