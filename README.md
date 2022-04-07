# Tubes Basdat

Fake data

## Install

Python 3.10, `pipenv` 2022.

```
pipenv install
```

## Usage

Generate data fake:

```
py generator.py > result\load.sql
```

Load data ke MariaDB:

```sql
CREATE DATABASE vaksin;
USE vaksin;
SOURCE schema.sql;
SOURCE result/load.sql;
```

## Reference

- [Provinsi dan Kota](https://sugismart.blogspot.com/2019/12/data-sql-dan-excel-daftar-kota-dan.html)
- [Vaksin](https://en.wikipedia.org/wiki/List_of_COVID-19_vaccine_authorizations)
- [Pekerjaan](https://dindukcapil.rembangkab.go.id/data/pekerjaan)
- [Penyakit](https://www.nhsinform.scot/illnesses-and-conditions/a-to-z)
