-- Criar tabelas.

CREATE TABLE loteria (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL UNIQUE,
    min_numeros INTEGER NOT NULL,
    max_numeros INTEGER NOT NULL,
    numeros_total INTEGER NOT NULL
);


CREATE TABLE valor_aposta (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    loteria_id INTEGER NOT NULL,
    qtd_numeros INTEGER NOT NULL,
    valor REAL NOT NULL,
    FOREIGN KEY (loteria_id) REFERENCES loteria(id),
    UNIQUE (loteria_id, qtd_numeros)
);


CREATE TABLE jogo (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    loteria_id INTEGER NOT NULL,
    data_criacao DATE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (loteria_id) REFERENCES loteria(id)
);


CREATE TABLE jogo_numero (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    jogo_id INTEGER NOT NULL,
    numero INTEGER NOT NULL,
    FOREIGN KEY (jogo_id) REFERENCES jogo(id),
    UNIQUE (jogo_id, numero)
);


-- Inserindo valores fixos.

INSERT INTO loteria (nome, min_numeros, max_numeros, numeros_total) VALUES
('lotofacil', 15, 20, 25),
('megasena', 6, 15, 60);


INSERT INTO valor_aposta (loteria_id, qtd_numeros, valor) VALUES
    (1, 15, 3.5),
    (1, 16, 56),
    (1, 17, 476),
    (1, 18, 2856),
    (1, 19, 13566),
    (1, 20, 54264),
    (2, 6, 6),
    (2, 7, 42),
    (2, 8, 168),
    (2, 9, 504),
    (2, 10, 1260),
    (2, 11, 2772),
    (2, 12, 5544),
    (2, 13, 10296),
    (2, 14, 18018);


