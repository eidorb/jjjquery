# jjjquery

Triple J-Query 🥁

![](image.jpeg)


## Marimo notebook

I rapidly developed a prototype thanks to [@MatthewBurke1995](https://github.com/MatthewBurke1995/ABC-Radio-Wrapper)'s ABC-Radio-Wrapper and [marimo](https://github.com/marimo-team/marimo) notebook's beautiful UI components.

- You can view a read-only version of the marimo notebook [here](https://static.marimo.app/static/jjjquery-7tix)
- Or play with an interactive version [here](https://weathered-butterfly-5697.ploomberapp.io)


### How to deploy to Ploomer Cloud

- Follow this [guide](https://docs.cloud.ploomber.io/en/latest/apps/marimo.html)
- Zip deployment files with the following command:

  ```bash
  zip jjjquery.zip Dockerfile jjjquery.mo.py
  open .
  ```
- Drag and drop _jjjquery.zip_ to deployment settings


## Roadmap

- [x] Scrape recently played from https://www.abc.net.au/triplej/live/triplej
- [ ] Do this automatically using Git scraping https://simonwillison.net/2020/Oct/9/git-scraping/
- [ ] Front-end the data with Datasette https://datasette.io
- [ ] Build a custom interface
