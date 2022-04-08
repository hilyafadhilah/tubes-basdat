#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Any, Iterable, TextIO

import csv
import datetime
from enum import Enum
from os import path
import codecs

from faker import Faker
from faker.providers import company, phone_number, person, misc, date_time


input_dir = 'data'
output_dir = 'result'
delim = ','
quote_char = '"'
esc_char = '\\'
newline = '\n'


def load_csv(fname: str) -> list[dict[str]]:
    with open(path.join(input_dir, fname), newline='') as f:
        reader = csv.reader(f, delimiter=';')
        header: list[str] = next(reader)

        rows = []
        for row in reader:
            dict = {}
            for i in range(len(header)):
                dict[header[i]] = row[i]
            rows.append(dict)

        return rows


def open_write(fname: str) -> TextIO:
    return codecs.open(path.join(output_dir, fname), 'w', 'utf-8')


def quote(el: Any) -> str:
    el = str(el).replace(quote_char, esc_char + quote_char)
    return quote_char + el + quote_char


def rowify(*row: Iterable[Any]) -> str:
    if len(row) == 1:
        try:
            row = iter(row[0])
        except TypeError:
            pass
    return delim.join(map(str, row)) + newline


def get_loader(tbl: str, cols: Iterable[str]) -> str:
    fname = path.join(output_dir, tbl + '.csv').replace('\\', '\\\\')
    colnames = ', '.join(cols)
    nlhex = newline.encode('utf-8').hex()

    def esc(x): return x.replace('\\', '\\\\').replace('\'', '\\\'')

    return (
        f"LOAD DATA LOCAL INFILE '{fname}'\n" +
        f"INTO TABLE {tbl}\n" +
        f"FIELDS TERMINATED BY '{esc(delim)}'\n" +
        f"OPTIONALLY ENCLOSED BY '{esc(quote_char)}' ESCAPED BY '{esc(esc_char)}'\n" +
        f"LINES TERMINATED BY 0x{nlhex}\n" +
        f"IGNORE 1 LINES\n" +
        f"({colnames});\n"
    )


# provinsi
cols = ['id', 'nama']
provinces = load_csv('provinsi.csv')
with open_write('provinsi.csv') as f:
    f.write(rowify(cols))
    for p in provinces:
        f.write(rowify((p['id'], quote(p['provinsi']))))
print(get_loader('provinsi', cols))

# kota
cols = ['id', 'id_provinsi', 'nama']
cities = load_csv('kota.csv')
with open_write('kota.csv') as f:
    f.write(rowify(cols))
    for c in cities:
        name = quote(c['type'] + ' ' + c['city_name'])
        f.write(rowify(
            c['province_id'],
            c['city_id'],
            name
        ))
print(get_loader('kota', cols))

# penyakit
cols = ['id', 'nama']
conds = load_csv('penyakit.csv')
with open_write('penyakit.csv') as f:
    f.write(rowify(cols))
    for i in range(len(conds)):
        conds[i]['id'] = i + 1
        f.write(rowify(conds[i]['id'], quote(conds[i]['name'])))
print(get_loader('penyakit', cols))

# faker
fake = Faker('id_ID')
fake.add_provider(person)
fake.add_provider(date_time)
fake.add_provider(company)
fake.add_provider(phone_number)
fake.add_provider(misc)

# pekerjaan (sesuai KTP)
pekerjaan = load_csv('pekerjaan.csv')

# penduduk


class Sex(Enum):
    MALE = 'LAKI-LAKI'
    FEMALE = 'PEREMPUAN'


class Kategori(Enum):
    NAKES = 'Tenaga Kesehatan'
    LANSIA = 'Usia Lanjut'
    SATGAS = 'Petugas Publik'
    SIPIL = 'Masyarakat'


class VaxStatus(Enum):
    YET = 'Belum Vaksin'
    FIRST = 'Vaksin Pertama'
    SECOND = 'Vaksin Kedua'
    THIRD = 'Vaksin Ketiga'


cols = ['nik', 'nama_depan', 'nama_belakang', 'no_telp', 'jenis_kelamin',
        'pekerjaan', 'kategori', 'status_vaksinasi', 'tanggal_lahir']

citizen = []
with open_write('penduduk.csv') as f:
    f.write(rowify(cols))
    for _ in range(9999):
        nik = fake.random_int(1, 9999999999999999)
        sex = fake.random_element(Sex)

        if sex == Sex.FEMALE:
            first = fake.first_name_female()
            last = fake.last_name_female()
        else:
            first = fake.first_name_male()
            last = fake.last_name_male()

        phone = '08' + fake.msisdn()[2:13]
        job = fake.random_element(pekerjaan)['pekerjaan']
        cat = fake.random_element(Kategori)
        stat = fake.random_element(VaxStatus)
        birth = fake.date_between(
            start_date=datetime.datetime(1930, 1, 1),
            end_date=datetime.datetime(2015, 12, 31))

        f.write(rowify(map(quote, [
            nik, first, last, phone, sex.value, job, cat.value, stat.value, birth
        ])))

        citizen.append((nik, stat))
print(get_loader('penduduk', cols))

# faskes


class FaskesType(Enum):
    PUSKESMAS = 1
    RUMAH_SAKIT = 2
    KLINIK = 3


faskes = []
puskesmas = []
rs = []
klinik = []
faskes_telp = []

i = 1
for c in cities:
    for _ in range(fake.random_int(1, 50)):
        type = fake.random_element(FaskesType)

        if type == FaskesType.PUSKESMAS:
            capacity = fake.random_int(100, 1000)
            puskesmas.append((
                i,
                fake.boolean()
            ))
        elif type == FaskesType.RUMAH_SAKIT:
            capacity = fake.random_int(1000, 10000)
            rs.append((
                i,
                fake.random_element(['swasta', 'negri']),
                fake.random_int(1, 10)
            ))
        elif type == FaskesType.KLINIK:
            capacity = fake.random_int(1000, 5000)
            klinik.append((
                i,
                fake.random_element(['pratama', 'utama'])
            ))

        faskes.append((
            i,
            fake.company(),
            capacity,
            c['city_id']
        ))

        faskes_telp.extend([
            (i, fake.phone_number()) for _ in range(fake.random_int(1, 5))
        ])

        i += 1

cols = ['id', 'nama', 'kapasitas', 'id_kota']
with open_write('faskes.csv') as f:
    f.write(rowify(cols))
    for fas in faskes:
        f.write(rowify(
            fas[0],
            quote(fas[1]),
            fas[2],
            fas[3]
        ))
print(get_loader('faskes', cols))

cols = ['id', 'no_telp']
with open_write('faskes_telp.csv') as f:
    f.write(rowify(cols))
    for t in faskes_telp:
        f.write(rowify(t[0], quote(t[1])))
print(get_loader('faskes_telp', cols))

cols = ['id', 'rawat_inap']
with open_write('puskesmas.csv') as f:
    f.write(rowify(cols))
    for p in puskesmas:
        f.write(rowify(p[0], quote(p[1])))
print(get_loader('puskesmas', cols))

cols = ['id', 'kepemilikan', 'kelas_rs']
with open_write('rumah_sakit.csv') as f:
    f.write(rowify(cols))
    for r in rs:
        f.write(rowify(r[0], quote(r[1]), r[2]))
print(get_loader('rumah_sakit', cols))

cols = ['id', 'kelas_klinik']
with open_write('klinik.csv') as f:
    f.write('id,kelas_klinik\n')
    for k in klinik:
        f.write(rowify(k[0], quote(k[1])))
print(get_loader('klinik', cols))

# vaksin

cols = ['id', 'produsen', 'nama']
vaksin = load_csv('vaksin.csv')
with open_write('vaksin.csv') as f:
    f.write(rowify(cols))
    for i in range(len(vaksin)):
        vaksin[i]['id'] = i + 1
        f.write(rowify(
            vaksin[i]['id'],
            vaksin[i]['developer'],
            vaksin[i]['nama']
        ))
print(get_loader('vaksin', cols))

# batch


class LogStatus (Enum):
    SHIP = 'SHIP'
    OUT = 'OUT OF DELIVERY'
    DELIVERED = 'DELIVERED'


start = datetime.datetime(2020, 7, 1)
end = datetime.datetime.now() + datetime.timedelta(6 * 30)

fb = open_write('batch.csv')
fl = open_write('batch_log.csv')

batches = []

i = 0
for fas in faskes:
    fvax = fake.random_elements(
        vaksin,
        length=fake.random_int(1, 3),
        unique=True
    )

    for v in fvax:
        # for _ in range(fake.random_int(1, 100)):
        for _ in range(fake.random_int(1, 5)):
            i += 1
            qty = fake.random_int(100, 5000)
            used = 0
            expire = fake.date_between(start_date=start, end_date=end)

            t1 = expire - datetime.timedelta(9 * 30)
            t2 = expire

            for s in LogStatus:
                if not fake.boolean():
                    break

                t1 = fake.date_between(start_date=t1, end_date=t2)
                fl.write(rowify(
                    i, quote(t1), quote(s.value)
                ))

                if s == LogStatus.DELIVERED:
                    used = fake.random_int(0, qty)
                    batches.append((i, t1, expire))

            fb.write(rowify(
                i,
                qty,
                used,
                quote(expire),
                fas[0],
                v['id']
            ))

fb.close()
fl.close()

# disuntik


class VaxStage (Enum):
    FIRST = 1
    SECOND = 2
    THIRD = 3


cols = ['id', 'nik', 'tahap_vaksin', 'tanggal_vaksinasi']
with open_write('disuntik.csv') as f:
    f.write(rowify(cols))
    for nik, stat in citizen:
        bs = fake.random_elements(batches, length=len(VaxStage), unique=True)
        bs.sort(key=lambda x: x[1])

        if stat != VaxStatus.YET:
            i = 0
            for s in VaxStage:
                f.write(rowify(
                    bs[i][0],
                    quote(nik),
                    VaxStage[s.name].value,
                    quote(fake.date_between(
                        start_date=bs[i][1], end_date=bs[i][2]))
                ))

                if s.name == stat.name:
                    break

                i += 1

print(get_loader('disuntik', cols))
