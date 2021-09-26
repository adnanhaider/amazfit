import logging
import scrapy
import os
from scrapy import Spider
from Amazfit.items import Manual


logger = logging.getLogger(__name__)

class Amazfit(Spider):
    name = "amazfit"
    start_urls = [
        "https://support.amazfit.com/en/locale/index"
        ]

    def parse(self, response):
        urls = response.css('.change-box a::attr(href)').getall()
        for url in urls:
            url = 'https://support.amazfit.com' + url

            yield scrapy.Request(url=url, callback=self.do_parse)

    def do_parse(self, response):
        urls = response.css('.product-list.clearfix .product-more a')  
        for url in urls:
            if not url:
                continue
            if 'http' not in url.css('::attr(href)').get():
                _url = 'https://support.amazfit.com' + url.css('::attr(href)').get()
            dictionary = {
                _url : [url.css('img::attr(src)').get(), url.css('img::attr(alt)').get()]
            }
            yield scrapy.Request(url=_url, callback=self.get_pdf, meta={'dic':dictionary})

    
    def get_pdf(self, response):
        dictionary = response.meta.get('dic')
        # for Key, val in dictionary.items():
        #     print(Key,'----key')
        #     print(val, '----val')
        # return

        manual = Manual()
        uls = response.css('.manual-item ul')
        if len(uls) > 1:
            pdfs = uls[0].css('li a')
        else:
            pdfs = uls.css('li a')
       
        c_url = response.request.url
        lang = c_url.split('/')[3]

        if len(pdfs) == 0:
            return

        for pdf in pdfs:            
            type = pdf.css('::text').get()
            
            
            doc_type = self.get_type(type)
            
            pdf = pdf.css('::attr(href)').get()
            if 'zip' == pdf.split('.')[-1]:
                continue
            if ' ' in pdf :
                pdf.replace(' ', '%20')
            for key, val in dictionary.items():
                if key == c_url:
                    thumb = val[0]
                    model = val[1]
            

            manual["product"] = 'No Category'
            manual["brand"] = 'Amazfit'
            manual["thumb"] = thumb
            manual["model"] = model
            manual["source"] = 'amazfit.com'
            manual["file_urls"] = pdf
            manual["url"] = c_url
            manual["type"] = doc_type
            if 'en' in lang:
                manual["product_lang"] =  lang 
            else:
                manual["product_lang"] = ''
            yield manual
    
    def get_type(self, type):
        # types_array = ['datasheet', 'utility user guide', 'user guide', 'guide', 'product introduction', 'quick installation guide' ,' ce doc']
       
        type = type.lower()
        if 'datasheet' in type:
            return "Datasheet"

        elif 'utility' in type and 'user' in type and 'guide' in type:
            return 'Utility User Guide'

        elif 'user' in type and 'guide' in type:
            return "User Guide"

        elif 'product' in type and 'introduction' in type:            
            return "Product Introduction"

        elif 'quick' in type and 'installation' in type:
            return "Quick Installation Guide"

        elif 'guide' in type and 'installation' in type:
            return "Installation Guide"

        elif 'ce' in type and 'doc' in type:
            return 'CE DOC'
        elif 'qsg' in type:
            return 'Quickstart Guide'
        
        elif 'guide' in type:
            if '_' in type:
               type_pieces = type.split('_')
               for _type in type_pieces:
                   if 'guide' in _type:
                       return _type.title()
            else:
                return type.title()
        

        return "User Guide"