import requests
import polars as pl


def get_patients(api_url):
    response = requests.get(api_url)
    return response.json()

if __name__ == "__main__":
    api_url = "http://localhost:8000/app/patients/"
    data = get_patients(api_url)

    # Criando o DataFrame usando Polars
    df = pl.DataFrame(data)

    # Exibindo o DataFrame
    print(df)


