import oci
import os

CONFIG_PATH = "OracleBucket/config"
PROFILE_NAME = "DEFAULT"
BUCKET_NAME = "loterias"


def fazer_conexao_bucket():
    try:
        config = oci.config.from_file(CONFIG_PATH, PROFILE_NAME)
        client = oci.object_storage.ObjectStorageClient(config)

        namespace = client.get_namespace().data

        return client, namespace
    except Exception as e:
        print(f"Erro conexão OCI: {e}")
        return None, None


def baixar_excel_bucket(nome_objeto: str, destino: str):
    client, namespace = fazer_conexao_bucket()

    if not client:
        return
    else:
        print("Conectado ao OCI")

    try:
        response = client.get_object(
            namespace,
            BUCKET_NAME,
            f"resultados/{nome_objeto}"
        )

        with open(destino, "wb") as f:
            f.write(response.data.content)

        print(f"✅ Baixado: {destino}")

    except Exception as e:
        print(f"❌ Erro ao baixar: {e}")
