# -*- coding: utf-8 -*-
'''
'''
from bs4 import BeautifulSoup
from ..utils.ADC_function import get_html

class TmdbParser():

    def getPage(self, id):
        """ 抓取页面

        Returns:
            soup (string): HTML source of scraped page.
        """
        movieUrl = "https://www.themoviedb.org/movie/" + id + "?language=zh-CN"
        htmltext = get_html(movieUrl)
        soup = BeautifulSoup(htmltext, 'html.parser')
        return soup

    def getOpenGraphImage(self, soup):
        """ Return the Open Graph image

        Args:
            soup: HTML from Beautiful Soup.
        Returns:
            value: Parsed content. 
        """
        if soup.findAll("meta", property="og:image"):
            endurl = soup.find("meta", property="og:image")["content"]
            return "https://www.themoviedb.org" + endurl
        return

    def getOpenGraphTitle(self, soup):
        """Return the Open Graph title

        Args:
            soup: HTML from Beautiful Soup.
        
        Returns:
            value: Parsed content. 
        """
        if soup.findAll("meta", property="og:title"):
            return soup.find("meta", property="og:title")["content"]
        return

    def getOpenGraphDescription(self, soup):
        """Return the Open Graph description

        Args:
            soup: HTML from Beautiful Soup.
        
        Returns:
            value: Parsed content. 
        """
        if soup.findAll("meta", property="og:description"):
            return soup.find("meta", property="og:description")["content"]
        return

tmdbParser = TmdbParser()
