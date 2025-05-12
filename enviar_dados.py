import serial
import requests
from datetime import datetime

PORTA_SERIAL = 'COM5'
BAUD_RATE = 9600

URL_API_PESAGEM = 'http://localhost:8080/pesagens'
URL_API_ANIMAL = 'http://localhost:8080/animais'

arduino = serial.Serial(PORTA_SERIAL, BAUD_RATE)
print("🐍 Conectado à porta serial. Aguardando pesagens...\n")

def cadastrar_boi(tag):
    # Verifica se o boi já está cadastrado
    response = requests.get(f"{URL_API_ANIMAL}/{tag}")
    if response.status_code == 200:
        print(f"ℹ️ Boi {tag} já está cadastrado.")
        return

    # Cadastra se ainda não existir
    dados = {
        "tagRFID": tag,
        "nome": f"Boi {tag}",
        "raca": "Miniatura",
        "dataNascimento": "2023-01-01"
    }

    response = requests.post(URL_API_ANIMAL, json=dados)
    if response.status_code in [200, 201]:
        print(f"✅ Boi {tag} cadastrado automaticamente.")
    else:
        print(f"❌ Erro ao cadastrar boi: {response.status_code} - {response.text}")

boi_presente = False

while True:
    try:
        linha = arduino.readline().decode().strip()

        if linha.startswith("ID simulado do boi:") and not boi_presente:
            id_boi = linha.split(":")[1].strip()

            peso_linha = arduino.readline().decode().strip()
            peso = float(peso_linha.split(":")[1].strip())

            if peso < 0.2:
                continue  # Ignora pesos muito baixos

            data_hora = datetime.now().isoformat()

            cadastrar_boi(id_boi)

            print("\n📦 Nova pesagem detectada:")
            print(f"🐮 Boi ID (tagRFID): {id_boi}")
            print(f"⚖️  Peso registrado: {peso:.3f} kg")
            print(f"🕒 Data/Hora: {data_hora}")

            json_dados = {
                "tagRFID": id_boi,
                "peso": peso,
                "dataHora": data_hora
            }

            response = requests.post(URL_API_PESAGEM, json=json_dados)
            if response.status_code in [200, 201]:
                print("✅ Dados enviados com sucesso.")
                boi_presente = True
            else:
                print(f"❌ Erro ao enviar dados: {response.status_code} - {response.text}")

        # Libera nova leitura se balança estiver vazia (< 150g)
        if "Peso (kg):" in linha:
            try:
                peso = float(linha.split(":")[1].strip())
                if peso < 0.15:
                    boi_presente = False
            except ValueError:
                pass  # ignora erro de leitura mal formatada

    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
