import sqlite3
import pandas as pd
from collections import Counter

DB_PATH = "../data/jobs.db"


def cargar_datos():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM ofertas", conn)
    conn.close()
    return df


def top_tecnologias(df):
    todas = []
    for techs in df["tecnologias"].dropna():
        if techs.strip():
            todas.extend([t.strip() for t in techs.split(",")])
    conteo = Counter(todas)
    return pd.DataFrame(conteo.most_common(10), columns=["tecnologia", "menciones"])


def ofertas_por_empresa(df):
    return df["empresa"].value_counts().head(10).reset_index()


def ofertas_por_ubicacion(df):
    return df["ubicacion"].value_counts().head(10).reset_index()


def resumen(df):
    print(f"\n{'='*40}")
    print(f"  RESUMEN GENERAL")
    print(f"{'='*40}")
    print(f"  Total ofertas:     {len(df)}")
    print(f"  Empresas únicas:   {df['empresa'].nunique()}")
    print(f"  Última extracción: {df['fecha_scraping'].max()}")

    print(f"\n{'='*40}")
    print(f"  TOP 10 TECNOLOGÍAS MÁS PEDIDAS")
    print(f"{'='*40}")
    print(top_tecnologias(df).to_string(index=False))

    print(f"\n{'='*40}")
    print(f"  TOP 10 EMPRESAS CON MÁS OFERTAS")
    print(f"{'='*40}")
    print(ofertas_por_empresa(df).to_string(index=False))

    print(f"\n{'='*40}")
    print(f"  OFERTAS POR UBICACIÓN")
    print(f"{'='*40}")
    print(ofertas_por_ubicacion(df).to_string(index=False))


if __name__ == "__main__":
    df = cargar_datos()
    resumen(df)