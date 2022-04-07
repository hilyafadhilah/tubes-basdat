CREATE TABLE Penyakit(
id int not null,
nama varchar(255) unique not null,
primary key(id)
);
CREATE TABLE Penduduk(
nik int unique not null,
nama_depan varchar(255) not null,
nama_belakang varchar(255) not null,
no_telp varchar(13) not null,
jenis_kelamin varchar(255) not null,
pekerjaan varchar(255) not null,
kategori varchar(255) not null,
status_vaksinasi varchar(255) not null,
tanggal_lahir date not null,
id_penyakit int,
primary key(nik),
foreign key(id_penyakit) references Penyakit(id)
);
CREATE TABLE Provinsi(
id int auto_increment,
nama varchar(255) not null,
primary key(id)
);
CREATE TABLE Kabupaten_Kota(
id int unique not null,
id_provinsi int auto_increment,
nama varchar(255) not null,
primary key(id_provinsi),
foreign key(id_provinsi) references Provinsi(id)
);
CREATE TABLE Faskes(
id int auto_increment,
id_kota int not null,
nama varchar(255) not null,
kapasitas_vaksin int not null,
primary key(id),
foreign key(id_kota) references Kabupaten_Kota(id)
);
CREATE TABLE Puskesmas(
id int not null,
rawat_inap varchar(15) not null,
primary key(id),
foreign key(id) references Faskes(id)
);

CREATE TABLE Rumah_Sakit(
id int not null,
kepemilikan varchar(15) not null,
kelas_rs int not null,
primary key(id),
foreign key(id) references Faskes(id)
);
CREATE TABLE Klinik(
id int not null,
kelas_klinik varchar(15) not null,
primary key(id),
foreign key(id) references Faskes(id)
);
CREATE TABLE Faskes_No_Telp(
id int auto_increment,
no_telp varchar(15) not null,
primary key(id, no_telp),
foreign key(id) references Faskes(id)
);
CREATE TABLE Vaksin(
id int auto_increment,
produsen varchar(255) not null,
nama varchar(255) unique not null,
id_batasan int not null,
primary key(id),
foreign key(id_batasan) references penyakit(id)
);
CREATE TABLE Batch(
id int auto_increment,
jumlah_vaksin int not null,
vaksin_terpakai int not null,
expired_date date not null,
id_faskes int not null,
id_vaksin int not null,
primary key(id),
foreign key(id_faskes) references Faskes(id),
foreign key(id_vaksin) references Vaksin(id)
);
CREATE TABLE Log(
id int not null,
timestamp timestamp not null,
status varchar(255) not null,
primary key(id),
foreign key(id) references Batch(id)
);
CREATE TABLE Disuntik(
id int not null,
nik int unique not null,
tahap_vaksin int not null,
tanggal_vaksinasi date not null,
primary key(id, nik),
foreign key(id) references Batch(id),
foreign key(nik) references Penduduk(nik)
);