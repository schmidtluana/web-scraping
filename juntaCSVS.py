import os
import glob
import pandas as pd

def juntar_csvs(pasta_csv, arquivo_saida):
 
    arquivos_csv = glob.glob(os.path.join(pasta_csv, "*.csv"))

    df_concatenado = pd.read_csv(arquivos_csv[0])

    for arquivo_csv in arquivos_csv[1:]:
        df = pd.read_csv(arquivo_csv)
        df_concatenado = pd.concat([df_concatenado, df], ignore_index=True)

    df_concatenado.to_csv(arquivo_saida, index=False)

    print(f"Arquivos CSV concatenados com sucesso em: {arquivo_saida}")

# Exemplo de uso
pasta_csv = r"C:\Users\luana\hotels"

arquivo_saida = "arquivo_concatenado.csv"
juntar_csvs(pasta_csv, arquivo_saida)
