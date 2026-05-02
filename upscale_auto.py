import os
import sys
import requests
import zipfile
import subprocess
import argparse
import shutil
from tqdm import tqdm

EXECUTABLE_MAP = {
    "linux": "realesrgan-ncnn-vulkan",
    "win32": "realesrgan-ncnn-vulkan.exe",
    "darwin": "realesrgan-ncnn-vulkan"
}
DEFAULT_MODEL = "realesrgan-x4plus"

def get_platform_info():
    platform = sys.platform
    if platform.startswith('linux'):
        return "linux"
    elif platform == "win32":
        return "win32"
    elif platform == "darwin":
        return "darwin"
    raise NotImplementedError(f"Plataforma não suportada: {platform}")

def setup_realesrgan(install_dir):
    platform = get_platform_info()
    platform_keyword = 'ubuntu' if platform == 'linux' else ('windows' if platform == 'win32' else platform)
    
    exe_name = EXECUTABLE_MAP.get(sys.platform)
    if not exe_name:
         print(f"[ERRO CRÍTICO] Plataforma '{platform}' não tem um nome de executável mapeado.")
         sys.exit(1)
    
    exe_path = os.path.join(install_dir, exe_name)

    if os.path.exists(exe_path):
        print(f"[INFO] Real-ESRGAN encontrado em: {exe_path}")
        return exe_path

    print("[SETUP] Real-ESRGAN não encontrado. Consultando a API do GitHub...")
    
    try:
        api_url = "https://api.github.com/repos/xinntao/Real-ESRGAN-ncnn-vulkan/releases/tags/v0.2.0"
        response = requests.get(api_url)
        response.raise_for_status()
        assets = response.json().get("assets", [])
        
        download_url, zip_name = "", ""
        for asset in assets:
            name = asset.get("name", "").lower()
            if platform_keyword in name:
                download_url, zip_name = asset.get("browser_download_url"), asset.get("name")
                break
        
        if not download_url:
            print(f"[ERRO CRÍTICO] Não foi possível encontrar um release para a plataforma '{platform_keyword}'.")
            sys.exit(1)

        print(f"[SETUP] Encontrado: {zip_name}. Iniciando download...")
        zip_path = os.path.join(install_dir, zip_name)
        os.makedirs(install_dir, exist_ok=True)

        with requests.get(download_url, stream=True) as r:
            r.raise_for_status()
            total_size = int(r.headers.get('content-length', 0))
            with open(zip_path, 'wb') as f, tqdm(desc=zip_name, total=total_size, unit='iB', unit_scale=True, unit_divisor=1024) as bar:
                for chunk in r.iter_content(chunk_size=8192):
                    bar.update(f.write(chunk))
        
        print("\n[SETUP] Extraindo arquivos...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(install_dir)
        os.remove(zip_path)

        subfolder_path = os.path.join(install_dir, os.path.splitext(zip_name)[0])
        if os.path.isdir(subfolder_path):
            for item in os.listdir(subfolder_path):
                shutil.move(os.path.join(subfolder_path, item), install_dir)
            shutil.rmtree(subfolder_path)

        if platform in ["linux", "darwin"] and os.path.exists(exe_path):
            print("[SETUP] Adicionando permissão de execução...")
            os.chmod(exe_path, 0o755)

        print(f"[SETUP] Real-ESRGAN instalado com sucesso em {exe_path}!")
        return exe_path

    except Exception as e:
        print(f"[ERRO CRÍTICO] Falha no setup do Real-ESRGAN: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Automatiza o upscale de imagens usando Real-ESRGAN.")
    parser.add_argument("-i", "--input", required=True, help="Pasta contendo as imagens de entrada.")
    parser.add_argument("-o", "--output", required=True, help="Pasta para salvar as imagens processadas.")
    parser.add_argument("-s", "--scale", type=int, choices=[2, 4], default=4, help="Fator de escala para o upscale (2x ou 4x).")
    parser.add_argument("-f", "--format", type=str, choices=['png', 'jpg', 'webp'], default='png', help="Formato da imagem de saída.")
    parser.add_argument("-m", "--model", default=DEFAULT_MODEL, help=f"Modelo do Real-ESRGAN (padrão: {DEFAULT_MODEL}).")
    parser.add_argument("--install-dir", default=os.path.join(os.path.expanduser("~"), ".local", "bin"), help="Diretório de instalação do Real-ESRGAN.")
    
    args = parser.parse_args()

    os.makedirs(args.output, exist_ok=True)
    realesrgan_exe = setup_realesrgan(args.install_dir)
    
    image_files = [f for f in os.listdir(args.input) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]
    if not image_files:
        print("[AVISO] Nenhuma imagem encontrada na pasta de entrada.")
        return

    print(f"\n[INFO] {len(image_files)} imagens encontradas. Iniciando processo em lote (batch processing)...")

    # Cria um diretório temporário para a saída bruta do Real-ESRGAN
    import tempfile
    import shutil
    temp_out_dir = tempfile.mkdtemp()

    try:
        # Executa o Real-ESRGAN em todo o diretório de entrada
        command = [realesrgan_exe, "-i", args.input, "-o", temp_out_dir, "-n", args.model, "-s", str(args.scale), "-f", args.format]
        print(f"[INFO] Executando comando: {' '.join(command)}")
        
        # O Real-ESRGAN não tem uma barra de progresso fácil de capturar via CLI no batch mode para o tqdm do Python de forma simples.
        # Então rodamos o comando inteiro.
        result = subprocess.run(command, capture_output=True, text=True, check=False)

        if result.returncode != 0:
            print(f"[ERRO] Falha no processamento em lote:\n{result.stderr}")
        else:
            print("[INFO] Processamento pelo Real-ESRGAN concluído. Renomeando e movendo arquivos...")

            # Renomeia os arquivos gerados e os move para a pasta de destino final
            for filename in tqdm(image_files, desc="Finalizando imagens"):
                base_name = os.path.splitext(filename)[0]
                temp_filename = f"{base_name}.{args.format}"
                temp_filepath = os.path.join(temp_out_dir, temp_filename)

                final_filename = f"{base_name}_upscaled_{args.scale}x.{args.format}"
                final_filepath = os.path.join(args.output, final_filename)

                if os.path.exists(temp_filepath):
                    shutil.move(temp_filepath, final_filepath)
                    # tqdm.write(f"[INFO] Movido para -> '{final_filename}'.")
                else:
                    tqdm.write(f"[AVISO] Arquivo esperado '{temp_filename}' não encontrado na saída do Real-ESRGAN.")

            print("\n[SUCESSO] Processo concluído.")
    finally:
        # Limpa a pasta temporária
        shutil.rmtree(temp_out_dir, ignore_errors=True)

if __name__ == "__main__":
    main()
